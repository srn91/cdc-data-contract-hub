from __future__ import annotations

import json

from app.config import CONTRACTS_DIR, EXCEPTIONS_DIR, LINEAGE_PATH
from app.models import (
    ChangeFinding,
    CompatibilityReport,
    CompatibilityStatus,
    ContractSpec,
    FieldSpec,
    PolicyException,
)


def load_contract(filename: str) -> ContractSpec:
    payload = json.loads((CONTRACTS_DIR / filename).read_text(encoding="utf-8"))
    return ContractSpec(
        name=payload["name"],
        fields=[FieldSpec(**field) for field in payload["fields"]],
    )


def load_lineage() -> dict[str, list[str]]:
    return json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))


def load_exceptions(filename: str) -> list[PolicyException]:
    payload = json.loads((EXCEPTIONS_DIR / filename).read_text(encoding="utf-8"))
    return [PolicyException(**item) for item in payload]


def _status_rank(status: CompatibilityStatus) -> int:
    return {"compatible": 0, "warning": 1, "breaking": 2}[status]


def _apply_exception(
    field_name: str,
    status: CompatibilityStatus,
    exceptions: list[PolicyException],
) -> PolicyException | None:
    for exception in exceptions:
        if exception.field_name == field_name and exception.status == status:
            return exception
    return None


def _finding(
    *,
    field_name: str,
    status: CompatibilityStatus,
    reason: str,
    impacted_consumers: list[str],
    exceptions: list[PolicyException],
) -> ChangeFinding:
    exception = _apply_exception(field_name, status, exceptions)
    effective_status: CompatibilityStatus = "warning" if exception is not None else status
    return ChangeFinding(
        field_name=field_name,
        status=status,
        effective_status=effective_status,
        reason=reason,
        impacted_consumers=impacted_consumers,
        exception_id=exception.exception_id if exception else None,
        exception_ticket=exception.ticket if exception else None,
        exception_approved_by=exception.approved_by if exception else None,
        exception_expires_on=exception.expires_on if exception else None,
    )


def compare_contracts(
    current: ContractSpec,
    proposed: ContractSpec,
    lineage: dict[str, list[str]],
    exceptions: list[PolicyException] | None = None,
) -> CompatibilityReport:
    current_fields = {field.name: field for field in current.fields}
    proposed_fields = {field.name: field for field in proposed.fields}
    findings: list[ChangeFinding] = []
    configured_exceptions = exceptions or []

    for field_name, current_field in current_fields.items():
        proposed_field = proposed_fields.get(field_name)
        impacted_consumers = lineage.get(field_name, [])
        if proposed_field is None:
            findings.append(
                _finding(
                    field_name=field_name,
                    status="breaking",
                    reason="required field removed from proposed contract",
                    impacted_consumers=impacted_consumers,
                    exceptions=configured_exceptions,
                )
            )
            continue

        if current_field.type != proposed_field.type:
            status: CompatibilityStatus = "warning" if current_field.type == "int" and proposed_field.type == "double" else "breaking"
            findings.append(
                _finding(
                    field_name=field_name,
                    status=status,
                    reason=f"type changed from {current_field.type} to {proposed_field.type}",
                    impacted_consumers=impacted_consumers,
                    exceptions=configured_exceptions,
                )
            )

        if current_field.nullable and not proposed_field.nullable:
            findings.append(
                _finding(
                    field_name=field_name,
                    status="breaking",
                    reason="nullable field became required",
                    impacted_consumers=impacted_consumers,
                    exceptions=configured_exceptions,
                )
            )

    for field_name, proposed_field in proposed_fields.items():
        if field_name in current_fields:
            continue
        impacted_consumers = lineage.get(field_name, [])
        status: CompatibilityStatus = "compatible" if proposed_field.nullable else "breaking"
        reason = "new nullable field added" if proposed_field.nullable else "new required field added"
        findings.append(
            _finding(
                field_name=field_name,
                status=status,
                reason=reason,
                impacted_consumers=impacted_consumers,
                exceptions=configured_exceptions,
            )
        )

    overall_status = "compatible"
    if findings:
        overall_status = max((finding.effective_status for finding in findings), key=_status_rank)

    exceptions_applied = [
        exception
        for exception in configured_exceptions
        if any(finding.exception_id == exception.exception_id for finding in findings)
    ]

    summary = (
        f"Proposed contract {proposed.name} is {overall_status} against {current.name}. "
        f"Detected {len(findings)} classified change(s) with {len(exceptions_applied)} approved exception(s)."
    )

    return CompatibilityReport(
        current_contract=current.name,
        proposed_contract=proposed.name,
        overall_status=overall_status,
        findings=sorted(
            findings,
            key=lambda finding: (_status_rank(finding.effective_status), finding.field_name),
            reverse=True,
        ),
        exceptions_applied=exceptions_applied,
        summary=summary,
    )

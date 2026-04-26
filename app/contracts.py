from __future__ import annotations

import json

from app.config import CONTRACTS_DIR, LINEAGE_PATH
from app.models import ChangeFinding, CompatibilityReport, CompatibilityStatus, ContractSpec, FieldSpec


def load_contract(filename: str) -> ContractSpec:
    payload = json.loads((CONTRACTS_DIR / filename).read_text(encoding="utf-8"))
    return ContractSpec(
        name=payload["name"],
        fields=[FieldSpec(**field) for field in payload["fields"]],
    )


def load_lineage() -> dict[str, list[str]]:
    return json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))


def _status_rank(status: CompatibilityStatus) -> int:
    return {"compatible": 0, "warning": 1, "breaking": 2}[status]


def compare_contracts(current: ContractSpec, proposed: ContractSpec, lineage: dict[str, list[str]]) -> CompatibilityReport:
    current_fields = {field.name: field for field in current.fields}
    proposed_fields = {field.name: field for field in proposed.fields}
    findings: list[ChangeFinding] = []

    for field_name, current_field in current_fields.items():
        proposed_field = proposed_fields.get(field_name)
        impacted_consumers = lineage.get(field_name, [])
        if proposed_field is None:
            findings.append(
                ChangeFinding(
                    field_name=field_name,
                    status="breaking",
                    reason="required field removed from proposed contract",
                    impacted_consumers=impacted_consumers,
                )
            )
            continue

        if current_field.type != proposed_field.type:
            status: CompatibilityStatus = "warning" if current_field.type == "int" and proposed_field.type == "double" else "breaking"
            findings.append(
                ChangeFinding(
                    field_name=field_name,
                    status=status,
                    reason=f"type changed from {current_field.type} to {proposed_field.type}",
                    impacted_consumers=impacted_consumers,
                )
            )

        if current_field.nullable and not proposed_field.nullable:
            findings.append(
                ChangeFinding(
                    field_name=field_name,
                    status="breaking",
                    reason="nullable field became required",
                    impacted_consumers=impacted_consumers,
                )
            )

    for field_name, proposed_field in proposed_fields.items():
        if field_name in current_fields:
            continue
        impacted_consumers = lineage.get(field_name, [])
        status: CompatibilityStatus = "compatible" if proposed_field.nullable else "breaking"
        reason = "new nullable field added" if proposed_field.nullable else "new required field added"
        findings.append(
            ChangeFinding(
                field_name=field_name,
                status=status,
                reason=reason,
                impacted_consumers=impacted_consumers,
            )
        )

    overall_status = "compatible"
    if findings:
        overall_status = max((finding.status for finding in findings), key=_status_rank)

    summary = (
        f"Proposed contract {proposed.name} is {overall_status} against {current.name}. "
        f"Detected {len(findings)} classified change(s)."
    )

    return CompatibilityReport(
        current_contract=current.name,
        proposed_contract=proposed.name,
        overall_status=overall_status,
        findings=sorted(findings, key=lambda finding: (_status_rank(finding.status), finding.field_name), reverse=True),
        summary=summary,
    )

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


CompatibilityStatus = Literal["compatible", "warning", "breaking"]
AlertSeverity = Literal["expired", "expiring_soon"]


@dataclass(frozen=True)
class FieldSpec:
    name: str
    type: str
    nullable: bool


@dataclass(frozen=True)
class ContractSpec:
    name: str
    fields: list[FieldSpec]


@dataclass(frozen=True)
class ChangeFinding:
    field_name: str
    status: CompatibilityStatus
    effective_status: CompatibilityStatus
    reason: str
    impacted_consumers: list[str]
    exception_id: str | None = None
    exception_ticket: str | None = None
    exception_approved_by: str | None = None
    exception_expires_on: str | None = None


@dataclass(frozen=True)
class PolicyException:
    exception_id: str
    field_name: str
    status: CompatibilityStatus
    approved_by: str
    ticket: str
    rationale: str
    expires_on: str


@dataclass(frozen=True)
class ExceptionAlert:
    exception_id: str
    field_name: str
    severity: AlertSeverity
    days_until_expiry: int
    expires_on: str
    message: str
    impacted_consumers: list[str]


@dataclass(frozen=True)
class CompatibilityReport:
    current_contract: str
    proposed_contract: str
    overall_status: CompatibilityStatus
    findings: list[ChangeFinding]
    exceptions_applied: list[PolicyException]
    exception_alerts: list[ExceptionAlert]
    summary: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

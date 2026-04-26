from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


CompatibilityStatus = Literal["compatible", "warning", "breaking"]


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
    reason: str
    impacted_consumers: list[str]


@dataclass(frozen=True)
class CompatibilityReport:
    current_contract: str
    proposed_contract: str
    overall_status: CompatibilityStatus
    findings: list[ChangeFinding]
    summary: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

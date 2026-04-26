from __future__ import annotations

import json
from pathlib import Path

from app.config import GENERATED_DIR
from app.models import CompatibilityReport


def _portable(path: Path) -> str:
    cwd = Path.cwd()
    try:
        return str(path.relative_to(cwd))
    except ValueError:
        return str(path)


def render_markdown(report: CompatibilityReport) -> str:
    findings = ["None"] if not report.findings else [
        (
            f"- `actual={finding.status}` `effective={finding.effective_status}` `{finding.field_name}`: "
            f"{finding.reason}. Impacted consumers: {', '.join(finding.impacted_consumers) or 'none'}."
            + (
                f" Exception `{finding.exception_id}` approved by {finding.exception_approved_by}"
                f" under ticket `{finding.exception_ticket}` until {finding.exception_expires_on}."
                if finding.exception_id
                else ""
            )
        )
        for finding in report.findings
    ]
    exceptions = ["None"] if not report.exceptions_applied else [
        (
            f"- `{exception.exception_id}` on `{exception.field_name}` "
            f"for `{exception.status}` changes, approved by {exception.approved_by}, "
            f"ticket `{exception.ticket}`, expires {exception.expires_on}: {exception.rationale}"
        )
        for exception in report.exceptions_applied
    ]
    alerts = ["None"] if not report.exception_alerts else [
        (
            f"- `{alert.severity}` `{alert.exception_id}` on `{alert.field_name}`: "
            f"{alert.message} Impacted consumers: {', '.join(alert.impacted_consumers) or 'none'}."
        )
        for alert in report.exception_alerts
    ]
    return "\n".join(
        [
            f"# CDC Contract Alert: {report.proposed_contract}",
            "",
            f"Overall status: `{report.overall_status}`",
            "",
            "## Summary",
            "",
            report.summary,
            "",
            "## Findings",
            "",
            *findings,
            "",
            "## Approved Temporary Exceptions",
            "",
            *exceptions,
            "",
            "## Exception Expiry Alerts",
            "",
            *alerts,
            "",
        ]
    )


def write_outputs(report: CompatibilityReport) -> tuple[str, str]:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    json_path = GENERATED_DIR / "compatibility_report.json"
    markdown_path = GENERATED_DIR / "break_alert.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return _portable(json_path), _portable(markdown_path)

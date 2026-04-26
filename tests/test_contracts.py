from __future__ import annotations

from datetime import date

from app.contracts import compare_contracts, load_contract, load_exceptions, load_lineage


def test_breaking_contract_report_identifies_consumer_impact() -> None:
    report = compare_contracts(
        current=load_contract("order_events_v1.json"),
        proposed=load_contract("order_events_v2_breaking.json"),
        lineage=load_lineage(),
        exceptions=load_exceptions("order_events_v2_breaking_exceptions.json"),
        as_of_date=date(2026, 4, 26),
    )

    assert report.overall_status == "breaking"
    assert any(finding.field_name == "customer_tier" and finding.status == "breaking" for finding in report.findings)
    assert any("fraud_feature_store" in finding.impacted_consumers for finding in report.findings)
    assert any(
        finding.field_name == "order_total"
        and finding.exception_id == "exc-order-total-type-narrowing"
        and finding.effective_status == "warning"
        for finding in report.findings
    )
    assert len(report.exceptions_applied) == 1
    assert len(report.exception_alerts) == 1
    assert report.exception_alerts[0].severity == "expiring_soon"
    assert report.exception_alerts[0].days_until_expiry == 14
    assert "fraud_feature_store" in report.exception_alerts[0].impacted_consumers


def test_additive_nullable_change_is_compatible() -> None:
    report = compare_contracts(
        current=load_contract("order_events_v1.json"),
        proposed=load_contract("order_events_v2_additive_nullable.json"),
        lineage=load_lineage(),
    )

    assert report.overall_status == "compatible"
    assert any(finding.field_name == "promotion_code" and finding.status == "compatible" for finding in report.findings)
    assert report.exception_alerts == []


def test_expired_exception_is_reported() -> None:
    report = compare_contracts(
        current=load_contract("order_events_v1.json"),
        proposed=load_contract("order_events_v2_breaking.json"),
        lineage=load_lineage(),
        exceptions=load_exceptions("order_events_v2_breaking_exceptions.json"),
        as_of_date=date(2026, 5, 20),
    )

    assert report.exception_alerts[0].severity == "expired"
    assert report.exception_alerts[0].days_until_expiry == -10

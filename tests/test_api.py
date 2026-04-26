from __future__ import annotations

from fastapi.testclient import TestClient

import app.main as main


def test_demo_report_endpoint_returns_breaking_report() -> None:
    client = TestClient(main.app)
    response = client.get("/demo/report")

    assert response.status_code == 200
    body = response.json()
    assert body["overall_status"] == "breaking"
    assert body["current_contract"] == "order_events_v1"
    assert body["exceptions_applied"][0]["exception_id"] == "exc-order-total-type-narrowing"
    assert body["exception_alerts"][0]["severity"] == "expiring_soon"
    assert body["exception_alerts"][0]["days_until_expiry"] == 14

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_demo_report_endpoint_returns_breaking_report() -> None:
    response = client.get("/demo/report")

    assert response.status_code == 200
    body = response.json()
    assert body["overall_status"] == "breaking"
    assert body["current_contract"] == "order_events_v1"

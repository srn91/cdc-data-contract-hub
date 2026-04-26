from __future__ import annotations

from fastapi import FastAPI

from app.contracts import compare_contracts, load_contract, load_lineage


CURRENT_CONTRACT = "order_events_v1.json"
PROPOSED_CONTRACT = "order_events_v2_breaking.json"

app = FastAPI(
    title="CDC Data Contract Hub",
    description="A local-first contract compatibility and lineage-impact workflow for CDC schema changes.",
    version="0.1.0",
)


def demo_report() -> dict[str, object]:
    report = compare_contracts(
        current=load_contract(CURRENT_CONTRACT),
        proposed=load_contract(PROPOSED_CONTRACT),
        lineage=load_lineage(),
    )
    return report.to_dict()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/demo/report")
def demo() -> dict[str, object]:
    return demo_report()

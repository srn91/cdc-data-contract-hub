from __future__ import annotations

from datetime import date

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.contracts import compare_contracts, load_contract, load_exceptions, load_lineage


CURRENT_CONTRACT = "order_events_v1.json"
PROPOSED_CONTRACT = "order_events_v2_breaking.json"
EXCEPTIONS_FILE = "order_events_v2_breaking_exceptions.json"

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
        exceptions=load_exceptions(EXCEPTIONS_FILE),
        as_of_date=date(2026, 4, 26),
    )
    return report.to_dict()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CDC Data Contract Hub</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;max-width:860px;margin:48px auto;padding:0 24px;line-height:1.5;color:#111}}a{{color:#0645ad}}code{{background:#f3f4f6;padding:2px 5px;border-radius:4px}}</style></head>
<body>
<h1>CDC Data Contract Hub</h1>
<p>Schema compatibility workflow for CDC contract changes, downstream lineage, temporary exceptions, and break alerts.</p>
<ul><li>Current contract: <code>{CURRENT_CONTRACT}</code></li><li>Proposed contract: <code>{PROPOSED_CONTRACT}</code></li></ul>
<h2>Open endpoints</h2>
<ul>
<li><a href="/demo/report">Contract comparison report</a></li>
<li><a href="/health">Health check</a></li>
<li><a href="/docs">API docs</a></li>
</ul>
</body></html>"""


@app.get("/demo/report")
def demo() -> dict[str, object]:
    return demo_report()

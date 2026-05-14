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
<style>
body{{margin:0;background:#f8fafc;color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;line-height:1.5}}
main{{max-width:1080px;margin:0 auto;padding:56px 24px}}.hero{{background:linear-gradient(135deg,#111827,#0e7490);color:white;border-radius:22px;padding:38px;box-shadow:0 24px 60px rgba(15,23,42,.18)}}
.eyebrow{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#a5f3fc;font-weight:700}}h1{{font-size:42px;line-height:1.05;margin:10px 0 14px}}.hero p{{font-size:17px;color:#cffafe;max-width:780px}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:22px 0}}.card{{background:white;border:1px solid #e2e8f0;border-radius:16px;padding:18px;box-shadow:0 10px 30px rgba(15,23,42,.06)}}
.metric{{font-size:23px;font-weight:800;color:#0f172a}}.label{{font-size:13px;color:#64748b;margin-top:3px}}.links{{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}}
a.button{{background:#0f172a;color:white;text-decoration:none;padding:11px 14px;border-radius:10px;font-weight:700}}a.secondary{{background:white;color:#0f172a;border:1px solid #cbd5e1}}
@media(max-width:800px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}h1{{font-size:34px}}}}
</style></head>
<body><main>
<section class="hero"><div class="eyebrow">Data contract governance</div><h1>CDC Data Contract Hub</h1>
<p>Schema compatibility workflow for CDC contract changes, downstream lineage, temporary exceptions, and break alerts.</p>
<div class="links"><a class="button" href="/demo/report">Comparison report</a><a class="button secondary" href="/docs">API docs</a></div></section>
<section class="grid">
<div class="card"><div class="metric">{CURRENT_CONTRACT}</div><div class="label">current contract</div></div>
<div class="card"><div class="metric">{PROPOSED_CONTRACT}</div><div class="label">proposed contract</div></div>
<div class="card"><div class="metric">lineage</div><div class="label">consumer impact</div></div>
<div class="card"><div class="metric">alerts</div><div class="label">exception expiry</div></div>
</section>
<section class="card"><p>The comparison report explains breaking changes, impacted consumers, approved exceptions, and expiring waivers for a CDC schema update.</p></section>
</main></body></html>"""


@app.get("/demo/report")
def demo() -> dict[str, object]:
    return demo_report()

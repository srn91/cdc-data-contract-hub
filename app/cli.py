from __future__ import annotations

from app.contracts import compare_contracts, load_contract, load_exceptions, load_lineage
from app.main import CURRENT_CONTRACT, EXCEPTIONS_FILE, PROPOSED_CONTRACT
from app.reporting import write_outputs


def build_demo_report():
    return compare_contracts(
        current=load_contract(CURRENT_CONTRACT),
        proposed=load_contract(PROPOSED_CONTRACT),
        lineage=load_lineage(),
        exceptions=load_exceptions(EXCEPTIONS_FILE),
    )


def report() -> None:
    compatibility_report = build_demo_report()
    json_path, markdown_path = write_outputs(compatibility_report)
    print(f"overall_status={compatibility_report.overall_status}")
    print(f"json_path={json_path}")
    print(f"markdown_path={markdown_path}")


def main() -> None:
    import sys

    if len(sys.argv) != 2 or sys.argv[1] != "report":
        raise SystemExit("usage: python3 -m app.cli report")

    report()


if __name__ == "__main__":
    main()

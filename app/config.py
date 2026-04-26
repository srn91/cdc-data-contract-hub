from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT_DIR / "contracts"
LINEAGE_PATH = ROOT_DIR / "lineage" / "downstream_consumers.json"
GENERATED_DIR = ROOT_DIR / "generated"

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from pydantic import TypeAdapter

from app.config import Settings
from app.rag.evaluation import evaluate_cases
from app.rag.models import GoldenCase
from app.rag.runtime import create_rag_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate local RAG against an authorized golden set."
    )
    parser.add_argument("golden_set", type=Path)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow fewer than the required 20 cases during development.",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv(BACKEND_ROOT / ".env")
    args = parse_args()
    with args.golden_set.open("r", encoding="utf-8") as source:
        payload = json.load(source)
    cases = TypeAdapter(list[GoldenCase]).validate_python(payload)
    if len(cases) < 20 and not args.allow_incomplete:
        raise ValueError(
            "The official golden set must contain at least 20 cases. "
            "Use --allow-incomplete only during development."
        )

    service = create_rag_service(Settings.from_env())
    report = evaluate_cases(service, cases)
    print(json.dumps(report.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

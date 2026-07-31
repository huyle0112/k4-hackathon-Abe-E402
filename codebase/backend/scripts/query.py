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

from app.config import Settings
from app.rag.runtime import create_rag_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Query the PDF RAG pipeline with optional OpenAI generation."
        )
    )
    parser.add_argument("query", help="Question to ask.")
    parser.add_argument(
        "--sessions",
        nargs="*",
        type=int,
        help="Optional lesson/session numbers.",
    )
    parser.add_argument("--top-k", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    load_dotenv(BACKEND_ROOT / ".env")
    args = parse_args()
    settings = Settings.from_env()
    service = create_rag_service(settings)
    response = service.ask(
        args.query,
        session_numbers=args.sessions,
        top_k=args.top_k or settings.retrieval_top_k,
    )
    print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

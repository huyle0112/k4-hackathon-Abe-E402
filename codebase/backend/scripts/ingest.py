import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.rag.ingestion.indexer import index_pdf
from app.rag.vector_store import JsonVectorStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Lập chỉ mục một file PDF bài giảng")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--session", required=True, help="Mã buổi học, ví dụ day-01")
    args = parser.parse_args()
    store = JsonVectorStore(get_settings().vector_store_path)
    count = index_pdf(args.pdf, args.session, store)
    print(f"Đã lập chỉ mục {count} chunks cho {args.session} từ {args.pdf.name}")


if __name__ == "__main__":
    main()

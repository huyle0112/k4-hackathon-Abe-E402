from __future__ import annotations

import argparse
import copy
import json
import sys
from uuid import uuid4
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app.main import create_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the endpoint-based VLearn golden set."
    )
    parser.add_argument("golden_set", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "eval" / "latest-results.json",
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow fewer than 20 cases during development.",
    )
    return parser.parse_args()


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _contains(haystack: str, needle: str) -> bool:
    return needle.casefold() in haystack.casefold()


def _actual_status(endpoint: str, body: dict[str, Any]) -> str:
    if endpoint.endswith("/mindmaps"):
        return str(body.get("status", "unknown"))
    if body.get("status"):
        return str(body["status"])
    if body.get("clarification_question"):
        return "clarification_required"
    return "no_context" if body.get("abstained") else "answered"


def _sources(body: dict[str, Any]) -> list[dict[str, Any]]:
    sources = body.get("sources")
    if isinstance(sources, list):
        return sources
    citations = body.get("citations")
    return citations if isinstance(citations, list) else []


def _mindmap_topics(value: Any) -> list[str]:
    topics: list[str] = []
    if isinstance(value, dict):
        topic = value.get("topic")
        if isinstance(topic, str):
            topics.append(topic)
        for child in value.values():
            topics.extend(_mindmap_topics(child))
    elif isinstance(value, list):
        for child in value:
            topics.extend(_mindmap_topics(child))
    return topics


def _mindmap_ids(value: Any) -> list[str]:
    ids: list[str] = []
    if isinstance(value, dict):
        node_id = value.get("id")
        if isinstance(node_id, str):
            ids.append(node_id)
        for child in value.values():
            ids.extend(_mindmap_ids(child))
    elif isinstance(value, list):
        for child in value:
            ids.extend(_mindmap_ids(child))
    return ids


def evaluate_response(
    case: dict[str, Any], status_code: int, body: dict[str, Any]
) -> tuple[bool, list[str]]:
    expected = case["expected"]
    failures: list[str] = []
    if status_code != 200:
        failures.append(f"HTTP status là {status_code}, cần 200")
        return False, failures

    status = _actual_status(case["endpoint"], body)
    allowed_statuses = expected.get("status", [])
    if allowed_statuses and status not in allowed_statuses:
        failures.append(
            f"status={status!r}, cần một trong {allowed_statuses!r}"
        )

    answer = _text(body.get("answer"))
    message = _text(body.get("message"))
    searchable = "\n".join((answer, message, _text(body)))
    for phrase in expected.get("must_include_all", []):
        if not _contains(searchable, phrase):
            failures.append(f"thiếu cụm bắt buộc: {phrase!r}")
    include_any = expected.get("must_include_any", [])
    if include_any and not any(_contains(searchable, x) for x in include_any):
        failures.append(f"không chứa cụm nào trong must_include_any")
    message_any = expected.get("message_must_include_any", [])
    if message_any and not any(_contains(message, x) for x in message_any):
        failures.append("message không đạt message_must_include_any")
    clarification_any = expected.get("clarification_must_include_any", [])
    clarification = _text(body.get("clarification_question"))
    if clarification_any and not any(
        _contains(clarification, x) for x in clarification_any
    ):
        failures.append("câu hỏi làm rõ không chứa nội dung mong đợi")
    for phrase in expected.get("must_not_include", []):
        if _contains(searchable, phrase):
            failures.append(f"chứa cụm bị cấm: {phrase!r}")

    if expected.get("answer_must_be_non_empty") and not answer.strip():
        failures.append("answer đang rỗng")
    if expected.get("answer_must_be_empty") and answer.strip():
        failures.append("answer phải rỗng")
    if (
        expected.get("clarification_question_required")
        and not clarification.strip()
    ):
        failures.append("thiếu clarification_question")
    if (
        expected.get("clarification_question_must_be_null")
        and body.get("clarification_question") is not None
    ):
        failures.append("clarification_question phải null")

    sources = _sources(body)
    if len(sources) < expected.get("sources_min", 0):
        failures.append(f"chỉ có {len(sources)} nguồn")
    if "sources_max" in expected and len(sources) > expected["sources_max"]:
        failures.append(f"có {len(sources)} nguồn, vượt giới hạn")
    allowed_docs = set(expected.get("source_document_ids", []))
    for source in sources:
        document_id = source.get("document_id")
        if allowed_docs and document_id not in allowed_docs:
            failures.append(f"nguồn ngoài tài liệu cho phép: {document_id}")
        slide = source.get("slide", source.get("slide_number"))
        if expected.get("max_source_slide") and (
            not isinstance(slide, int) or slide > expected["max_source_slide"]
        ):
            failures.append(f"nguồn vượt slide hiện tại: {slide}")

    keywords = body.get("important_keywords", body.get("keywords", []))
    if len(keywords or []) < expected.get("important_keywords_min", 0):
        failures.append("thiếu important_keywords")
    for field in expected.get("response_forbidden_fields", []):
        if field in body:
            failures.append(f"response chứa field bị cấm: {field}")

    mindmap = body.get("mindmap")
    if expected.get("mindmap_required") and not mindmap:
        failures.append("thiếu mindmap")
    if expected.get("mindmap_must_be_empty_object") and mindmap != {}:
        failures.append("mindmap phải là object rỗng")
    if expected.get("mindmap_id_must_be_null") and body.get("mindmap_id") is not None:
        failures.append("mindmap_id phải null")
    if expected.get("mindmap_root_required") and not (
        isinstance(mindmap, dict) and mindmap.get("nodeData")
    ):
        failures.append("mindmap thiếu nodeData gốc")
    ids = _mindmap_ids(mindmap)
    if expected.get("mindmap_unique_node_ids") and len(ids) != len(set(ids)):
        failures.append("mindmap có node id trùng")
    topics = "\n".join(_mindmap_topics(mindmap))
    for topic in expected.get("mindmap_topics_must_include", []):
        if not _contains(topics, topic):
            failures.append(f"mindmap thiếu chủ đề: {topic!r}")

    return not failures, failures


def _document_aliases(client: TestClient) -> dict[str, str]:
    service = client.app.state.rag_service
    metadata = service.retriever.vector_store._collection.get(
        include=["metadatas"]
    )["metadatas"]
    by_session: dict[int, str] = {}
    for item in metadata:
        by_session[int(item["session_number"])] = item["document_id"]
    return {
        f"doc_day_{session:02d}": document_id
        for session, document_id in by_session.items()
    }


def _map_request(
    case: dict[str, Any], aliases: dict[str, str]
) -> dict[str, Any]:
    payload = dict(case["input"])
    if "document_ids" in payload:
        payload["document_ids"] = [
            aliases.get(item, item) for item in payload["document_ids"]
        ]
    return payload


def _map_expected_case(
    case: dict[str, Any], aliases: dict[str, str]
) -> dict[str, Any]:
    mapped = copy.deepcopy(case)
    expected = mapped.get("expected", {})
    if "source_document_ids" in expected:
        expected["source_document_ids"] = [
            aliases.get(item, item)
            for item in expected["source_document_ids"]
        ]
    return mapped


def main() -> int:
    load_dotenv(BACKEND_ROOT / ".env")
    args = parse_args()
    payload = json.loads(args.golden_set.read_text(encoding="utf-8"))
    cases = payload.get("cases") if isinstance(payload, dict) else payload
    if not isinstance(cases, list):
        raise ValueError("Golden set phải là array hoặc object chứa field cases")
    if len(cases) < 20 and not args.allow_incomplete:
        raise ValueError("Golden set chính thức phải có ít nhất 20 case")

    results: list[dict[str, Any]] = []
    evaluation_user = f"eval-{uuid4().hex}"
    with TestClient(create_app()) as client:
        aliases = _document_aliases(client)
        for case in cases:
            evaluated_case = _map_expected_case(case, aliases)
            endpoint = case["endpoint"].split()[-1]
            request_body = _map_request(case, aliases)
            try:
                response = client.post(
                    endpoint,
                    json=request_body,
                    headers={
                        "x-user-id": f"{evaluation_user}-{case['id']}"
                    },
                )
                try:
                    response_body = response.json()
                except ValueError:
                    response_body = {"raw_response": response.text}
                status_code = response.status_code
                passed, failures = evaluate_response(
                    evaluated_case, status_code, response_body
                )
            except Exception as error:
                status_code = 500
                response_body = {
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
                passed = False
                failures = [
                    f"endpoint phát sinh {type(error).__name__}: {error}"
                ]
            results.append(
                {
                    "id": case["id"],
                    "endpoint": case["endpoint"],
                    "passed": passed,
                    "failures": failures,
                    "actual_status": _actual_status(
                        case["endpoint"], response_body
                    ),
                    "status_code": status_code,
                    "response": response_body,
                }
            )
            print(f"{case['id']}: {'PASS' if passed else 'FAIL'}")

    passed_count = sum(item["passed"] for item in results)
    report = {
        "golden_set": payload.get("name") if isinstance(payload, dict) else None,
        "run_at": datetime.now(UTC).isoformat(),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "total": len(results),
        "pass_rate": passed_count / len(results) if results else 0,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                key: report[key]
                for key in ("passed", "failed", "total", "pass_rate")
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"Report: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

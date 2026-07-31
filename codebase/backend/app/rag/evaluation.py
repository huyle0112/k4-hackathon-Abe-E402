from __future__ import annotations

from collections.abc import Sequence

from app.rag.models import (
    EvaluationCaseResult,
    EvaluationReport,
    ExpectedSource,
    GoldenCase,
)
from app.rag.service import RAGService


def _matches_source(
    document_id: str,
    slide_number: int,
    expected_sources: Sequence[ExpectedSource],
) -> bool:
    return any(
        expected.document_id == document_id
        and expected.slide_number == slide_number
        for expected in expected_sources
    )


def evaluate_cases(
    service: RAGService,
    cases: Sequence[GoldenCase],
) -> EvaluationReport:
    results: list[EvaluationCaseResult] = []

    for case in cases:
        response = service.ask(
            case.query,
            session_numbers=case.session_numbers,
        )
        abstention_correct = response.abstained == case.expected_abstain

        retrieval_hit: bool | None = None
        citation_hit: bool | None = None
        if case.expected_sources:
            retrieval_hit = any(
                _matches_source(
                    hit.chunk.document_id,
                    hit.chunk.slide_number,
                    case.expected_sources,
                )
                for hit in response.retrieval_hits
            )
            citation_hit = any(
                _matches_source(
                    citation.document_id,
                    citation.slide_number,
                    case.expected_sources,
                )
                for citation in response.citations
            )

        evidence_correct = case.expected_abstain or (
            retrieval_hit is True and citation_hit is True
        )
        results.append(
            EvaluationCaseResult(
                case_id=case.case_id,
                category=case.category,
                passed=abstention_correct and evidence_correct,
                abstention_correct=abstention_correct,
                retrieval_hit=retrieval_hit,
                citation_hit=citation_hit,
            )
        )

    case_count = len(results)
    if case_count == 0:
        raise ValueError("Golden set must contain at least one case")

    retrieval_values = [
        result.retrieval_hit
        for result in results
        if result.retrieval_hit is not None
    ]
    citation_values = [
        result.citation_hit
        for result in results
        if result.citation_hit is not None
    ]
    return EvaluationReport(
        case_count=case_count,
        pass_rate=sum(result.passed for result in results) / case_count,
        abstention_accuracy=(
            sum(result.abstention_correct for result in results) / case_count
        ),
        retrieval_hit_rate=(
            sum(retrieval_values) / len(retrieval_values)
            if retrieval_values
            else None
        ),
        citation_hit_rate=(
            sum(citation_values) / len(citation_values)
            if citation_values
            else None
        ),
        cases=results,
    )

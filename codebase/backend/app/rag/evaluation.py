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
        citation_precision: float | None = None
        citation_completeness: float | None = None
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
            citation_matches = [
                _matches_source(
                    citation.document_id,
                    citation.slide_number,
                    case.expected_sources,
                )
                for citation in response.citations
            ]
            citation_precision = (
                sum(citation_matches) / len(citation_matches)
                if citation_matches
                else 0.0
            )
            matched_expected_sources = sum(
                any(
                    citation.document_id == expected.document_id
                    and citation.slide_number == expected.slide_number
                    for citation in response.citations
                )
                for expected in case.expected_sources
            )
            citation_completeness = (
                matched_expected_sources / len(case.expected_sources)
            )

        cross_session_source_coverage: float | None = None
        if case.category == "cross-session":
            requested_sessions = sorted(set(case.session_numbers or []))
            if len(requested_sessions) >= 2:
                retrieved_sessions = {
                    hit.chunk.session_number
                    for hit in response.retrieval_hits
                }
                cross_session_source_coverage = (
                    len(set(requested_sessions) & retrieved_sessions)
                    / len(requested_sessions)
                )
            else:
                expected_documents = {
                    source.document_id for source in case.expected_sources
                }
                retrieved_documents = {
                    hit.chunk.document_id
                    for hit in response.retrieval_hits
                }
                if expected_documents:
                    cross_session_source_coverage = (
                        len(expected_documents & retrieved_documents)
                        / len(expected_documents)
                    )

        evidence_correct = case.expected_abstain or (
            retrieval_hit is True and citation_hit is True
        )
        if (
            case.category == "cross-session"
            and not case.expected_abstain
        ):
            evidence_correct = (
                evidence_correct
                and cross_session_source_coverage == 1.0
                and citation_completeness == 1.0
            )
        results.append(
            EvaluationCaseResult(
                case_id=case.case_id,
                category=case.category,
                passed=abstention_correct and evidence_correct,
                abstention_correct=abstention_correct,
                retrieval_hit=retrieval_hit,
                citation_hit=citation_hit,
                cross_session_source_coverage=(
                    cross_session_source_coverage
                ),
                citation_precision=citation_precision,
                citation_completeness=citation_completeness,
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
    coverage_values = [
        result.cross_session_source_coverage
        for result in results
        if result.cross_session_source_coverage is not None
    ]
    precision_values = [
        result.citation_precision
        for result in results
        if result.citation_precision is not None
    ]
    completeness_values = [
        result.citation_completeness
        for result in results
        if result.citation_completeness is not None
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
        cross_session_source_coverage=(
            sum(coverage_values) / len(coverage_values)
            if coverage_values
            else None
        ),
        citation_precision=(
            sum(precision_values) / len(precision_values)
            if precision_values
            else None
        ),
        citation_completeness=(
            sum(completeness_values) / len(completeness_values)
            if completeness_values
            else None
        ),
        cases=results,
    )

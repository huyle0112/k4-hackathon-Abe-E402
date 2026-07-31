from app.rag.embeddings import tokenize
from app.rag.models import SearchHit


def rerank(question: str, hits: list[SearchHit]) -> list[SearchHit]:
    query_terms = set(tokenize(question))
    for hit in hits:
        coverage = len(query_terms & set(tokenize(hit.chunk.text))) / max(1, len(query_terms))
        hit.score = min(1.0, 0.75 * hit.score + 0.25 * coverage)
    return sorted(hits, key=lambda item: item.score, reverse=True)

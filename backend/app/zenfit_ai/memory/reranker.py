from app.zenfit_ai.registry import registry


def rerank(query: str, candidates: list[dict], limit: int = 8) -> list[dict]:
    if not candidates:
        return []
    model = registry.get_reranker()
    if model is not None:
        scores = model.predict([(query, item.get("text", "")) for item in candidates])
        ranked = [dict(item, rerank_score=float(score)) for item, score in zip(candidates, scores)]
        return sorted(ranked, key=lambda item: item["rerank_score"], reverse=True)[:limit]
    # Preserve Qdrant ordering when the optional local reranker is unavailable.
    return sorted(candidates, key=lambda item: item.get("score", 0), reverse=True)[:limit]

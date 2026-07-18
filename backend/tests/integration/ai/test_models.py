import math,pytest
from app.ai.memory.bge_embeddings import embed_text
from app.ai.memory.bge_reranker import rerank
from app.ai.registry import registry

pytestmark=[pytest.mark.integration,pytest.mark.model,pytest.mark.slow]

def test_real_bge_embedding_is_cached():
    model=registry.get_embedding_model()
    if model is None:pytest.skip(f"BGE-M3 unavailable: {registry.error('bge_embeddings')}")
    first=embed_text("I usually miss Monday morning workouts because I have college.");second=embed_text("I usually miss Monday morning workouts because I have college.")
    assert len(first)==1024 and all(math.isfinite(x) for x in first);assert max(abs(a-b) for a,b in zip(first,second))<1e-5;assert registry.get_embedding_model() is model

def test_real_reranker_prioritizes_monday_barriers():
    model=registry.get_reranker()
    if model is None:pytest.skip(f"Reranker unavailable: {registry.error('bge_reranker')}")
    texts=["User often sleeps late on Sunday.","User prefers chest workouts.","User has college Monday mornings.","User missed three Monday morning workouts.","User usually completes evening workouts.","User ate pizza last Friday."]
    results=rerank("Why do I keep missing Monday workouts?",[{"text":x,"score":0} for x in texts],6)
    top={x["text"] for x in results[:3]};assert "User has college Monday mornings." in top;assert "User missed three Monday morning workouts." in top

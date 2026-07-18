from types import SimpleNamespace
from app.ai.memory.bge_embeddings import embed_text
from app.ai.memory.bge_reranker import rerank
from app.ai.memory.semantic_retriever import MemoryRetriever, is_durable_memory

class Client:
    def __init__(self): self.last_filter=None
    def search(self,**kwargs): self.last_filter=kwargs["query_filter"]; return []
def test_embedding_dimension(): assert len(embed_text("test"))==1024
def test_reranker_order_and_empty(monkeypatch):
    monkeypatch.setattr("app.ai.memory.bge_reranker.registry.get_reranker",lambda:None)
    assert rerank("q",[])==[]
    assert rerank("q",[{"text":"a","score":.1},{"text":"b","score":.9}])[0]["text"]=="b"
def test_user_scope():
    client=Client(); MemoryRetriever(client).search(user_id="user-a",query="workout")
    assert client.last_filter.must[0].match.value=="user-a"
def test_durable_filter(): assert is_durable_memory("User consistently completed evening workout sessions") and not is_durable_memory("Hello")

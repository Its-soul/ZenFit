from app.ai.memory.bge_embeddings import embed_text
from app.ai.predictions.adherence import predict_adherence
from app.ai.predictions.readiness import predict_readiness
from app.ai.registry import registry

def main():
    assert len(embed_text("evening workout preference"))==1024
    print("embedding_dimension=1024")
    print(predict_adherence({}).model_dump()); print(predict_readiness({}).model_dump()); print(registry.status())
if __name__=="__main__": main()

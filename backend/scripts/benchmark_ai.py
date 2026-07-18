import argparse,statistics,time
from app.ai.memory.bge_embeddings import embed_text
from app.ai.memory.bge_reranker import rerank
from app.ai.pose.analyzer import PoseAnalyzer
from app.ai.predictions.adherence import predict_adherence
from app.ai.predictions.readiness import predict_readiness
from app.ai.predictions.recommendation import rank_recommendations

def measure(name,fn,runs):
    values=[]
    for _ in range(runs):
        start=time.perf_counter();fn();values.append((time.perf_counter()-start)*1000)
    ordered=sorted(values);p95=ordered[min(len(ordered)-1,int(len(ordered)*.95))]
    return {"operation":name,"runs":runs,"average_ms":round(statistics.mean(values),2),"p50_ms":round(statistics.median(values),2),"p95_ms":round(p95,2)}
def main():
    p=argparse.ArgumentParser();p.add_argument("--runs",type=int,default=20);args=p.parse_args();candidates=[{"text":"User has college Monday mornings.","score":.8},{"text":"User ate pizza.","score":.2}]
    pose=PoseAnalyzer();landmarks=[{"name":"hip","x":0,"y":0},{"name":"knee","x":0,"y":1},{"name":"ankle","x":1,"y":1}]
    tests=[("bge_embedding",lambda:embed_text("Monday workout schedule")),("reranker",lambda:rerank("Monday workouts",candidates)),("readiness",lambda:predict_readiness({})),("adherence",lambda:predict_adherence({})),("recommendations",lambda:rank_recommendations({})),("pose",lambda:pose.analyze("squat",landmarks))]
    for item in tests:
        try:print(measure(*item,args.runs))
        except Exception as exc:print({"operation":item[0],"status":"unavailable","error":str(exc)})
    print("Qdrant, USDA cached/uncached, and classifier benchmarks require their live services/models and are intentionally not fabricated.")
if __name__=="__main__":main()

from app.ai.predictions.adherence import predict_adherence, risk_level
from app.ai.predictions.readiness import predict_readiness
from app.ai.predictions.evaluation import evaluate_binary

def test_missing_model_uses_fallback():
    result=predict_adherence({}); assert result.source=="rule_engine"; assert 0<=result.miss_probability<=1
def test_missing_features_do_not_crash(): assert 0<=predict_readiness({}).score<=100
def test_risk_mapping(): assert risk_level(.8)=="high" and risk_level(.5)=="moderate" and risk_level(.1)=="low"
def test_small_evaluation_is_honest(): assert evaluate_binary([0,1],[.2,.8])["status"]=="insufficient_data"

from sqlalchemy import select
from app.db.session import SessionLocal
from app.zenfit_ai.prediction.evaluation import evaluate_binary
from app.zenfit_ai.prediction.models import AIPrediction

def main():
    with SessionLocal() as db:
        rows=db.scalars(select(AIPrediction).where(AIPrediction.prediction_type=="adherence",AIPrediction.outcome.in_(["completed","missed"]))).all()
        print(evaluate_binary([int(r.outcome=="missed") for r in rows],[r.prediction_value for r in rows]))
if __name__=="__main__":main()

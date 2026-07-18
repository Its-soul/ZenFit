from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.zenfit_ai.prediction.models import AIPrediction

class PredictionAuditService:
    def __init__(self,db:Session): self.db=db
    def record(self,*,user_id:UUID,prediction_type:str,entity_id:UUID|None,value:float,risk_level:str|None,features:dict,model_name:str,model_version:str="rules-v1",shadow_mode:bool=True):
        row=AIPrediction(user_id=user_id,prediction_type=prediction_type,entity_id=entity_id,prediction_value=value,risk_level=risk_level,feature_snapshot=features,model_name=model_name,model_version=model_version,shadow_mode=shadow_mode);self.db.add(row);return row
    def record_outcome(self,*,user_id:UUID,entity_id:UUID,outcome:str)->int:
        rows=self.db.scalars(select(AIPrediction).where(AIPrediction.user_id==user_id,AIPrediction.entity_id==entity_id,AIPrediction.outcome.is_(None))).all()
        now=datetime.now(timezone.utc)
        for row in rows: row.outcome=outcome;row.outcome_recorded_at=now
        return len(rows)

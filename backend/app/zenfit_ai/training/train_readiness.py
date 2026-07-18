from pathlib import Path
import pandas as pd
from xgboost import XGBRegressor

FEATURES=["sleep_hours","fatigue","soreness","recent_workload","days_since_rest","recent_adherence"]
def train(csv_path: Path, output: Path):
    data=pd.read_csv(csv_path)
    if "readiness_score" not in data or any(x not in data for x in FEATURES): raise ValueError("Real labeled readiness data is required")
    model=XGBRegressor(n_estimators=150,max_depth=4); model.fit(data[FEATURES].fillna(0),data["readiness_score"])
    output.parent.mkdir(parents=True,exist_ok=True); model.save_model(output)

from pathlib import Path
import pandas as pd
from xgboost import XGBClassifier

def train(csv_path: Path, output: Path):
    data=pd.read_csv(csv_path)
    if "accepted" not in data: raise ValueError("Real accepted/dismissed feedback labels are required")
    features=[c for c in data.select_dtypes("number").columns if c!="accepted"]
    if not features: raise ValueError("No numeric features found")
    model=XGBClassifier(n_estimators=120,max_depth=3); model.fit(data[features].fillna(0),data["accepted"])
    output.parent.mkdir(parents=True,exist_ok=True); model.save_model(output)

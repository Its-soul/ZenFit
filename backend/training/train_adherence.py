from pathlib import Path
import pandas as pd
from xgboost import XGBClassifier
from app.ai.predictions.features import FEATURE_NAMES

def train(csv_path: Path, output: Path):
    data = pd.read_csv(csv_path); required = set(FEATURE_NAMES + ["missed_next_workout"])
    missing = required-set(data.columns)
    if missing: raise ValueError(f"Missing labeled columns: {sorted(missing)}")
    model=XGBClassifier(n_estimators=150,max_depth=4); model.fit(data[FEATURE_NAMES].fillna(0),data["missed_next_workout"])
    output.parent.mkdir(parents=True,exist_ok=True); model.save_model(output)

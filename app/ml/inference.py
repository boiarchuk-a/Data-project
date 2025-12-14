import json
from pathlib import Path

import joblib
import pandas as pd

from app.schemas import PredictRequest

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model_smote_lr.pkl"
CONFIG_PATH = BASE_DIR / "model_config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

FEATURE_COLUMNS = cfg["features"]
MODEL_VERSION = cfg.get("model_version", "unknown")

_model = joblib.load(MODEL_PATH)


def _build_feature_row(req: PredictRequest) -> pd.DataFrame:
    # все остальные фичи = 0
    row = {c: 0 for c in FEATURE_COLUMNS}
    row["Income"] = req.Income
    row["Recency"] = req.Recency
    row["MntWines"] = req.MntWines
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


def predict_single(req: PredictRequest) -> tuple[float, int, str]:
    X = _build_feature_row(req)
    proba = float(_model.predict_proba(X)[:, 1][0])
    label = int(proba >= 0.5)
    return proba, label, MODEL_VERSION

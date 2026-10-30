from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "model.joblib"

FEATURES = [
    "tenure_months",
    "monthly_charges",
    "contract",
    "internet_service",
    "support_calls",
]

model = joblib.load(MODEL_PATH)

app = FastAPI(title="AI381 Lab 2 Churn API")


class ChurnInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenure_months: int = Field(ge=0)
    monthly_charges: float = Field(ge=0)
    contract: str = Field(min_length=1)
    internet_service: str = Field(min_length=1)
    support_calls: int = Field(ge=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(customer: ChurnInput):
    data = pd.DataFrame([customer.model_dump()])[FEATURES]
    probability = float(model.predict_proba(data)[0, 1])
    return {"churn_probability": round(probability, 3)}

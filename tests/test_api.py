from pathlib import Path

import joblib
from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)

ROOT = Path(__file__).resolve().parents[1]

SAMPLE = {
    "tenure_months": 5,
    "monthly_charges": 89.9,
    "contract": "month-to-month",
    "internet_service": "fiber",
    "support_calls": 3,
}


def test_api_contract():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    response = client.post("/predict", json=SAMPLE)
    assert response.status_code == 200
    assert "churn_probability" in response.json()
    assert 0 <= response.json()["churn_probability"] <= 1


def test_model_loads():
    model_path = ROOT / "model.joblib"
    assert model_path.is_file()

    loaded_model = joblib.load(model_path)
    assert hasattr(loaded_model, "predict_proba")


def test_input_schema_rejects_invalid_data():
    invalid_data = SAMPLE.copy()
    invalid_data.pop("support_calls")

    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422


def test_edge_case_unknown_categories_and_zero_values():
    edge_case = {
        "tenure_months": 0,
        "monthly_charges": 0,
        "contract": "unknown-contract",
        "internet_service": "unknown-service",
        "support_calls": 0,
    }

    response = client.post("/predict", json=edge_case)
    assert response.status_code == 200
    assert 0 <= response.json()["churn_probability"] <= 1


def test_prediction_is_deterministic():
    first = client.post("/predict", json=SAMPLE)
    second = client.post("/predict", json=SAMPLE)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()

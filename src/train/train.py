from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]

NUMERIC = ["tenure_months", "monthly_charges", "support_calls"]
CATEGORICAL = ["contract", "internet_service"]
FEATURES = NUMERIC + CATEGORICAL


def train_model(data_path=None, model_path=None):
    data_path = Path(data_path) if data_path else ROOT / "churn_v2.csv"
    model_path = Path(model_path) if model_path else ROOT / "model.joblib"

    df = pd.read_csv(data_path)
    df = df.rename(columns={"monthly_fee": "monthly_charges"})

    required = FEATURES + ["churn"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    X = df[FEATURES]
    y = df["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = Pipeline([
        (
            "prep",
            ColumnTransformer([
                ("num", StandardScaler(), NUMERIC),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore"),
                    CATEGORICAL,
                ),
            ]),
        ),
        ("clf", LogisticRegression(max_iter=1000)),
    ])

    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_test)[:, 1]
    f1 = f1_score(y_test, probabilities > 0.5)
    auc = roc_auc_score(y_test, probabilities)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"F1: {f1:.3f}")
    print(f"AUC: {auc:.3f}")
    print(f"Model saved to: {model_path}")

    return model


if __name__ == "__main__":
    train_model()

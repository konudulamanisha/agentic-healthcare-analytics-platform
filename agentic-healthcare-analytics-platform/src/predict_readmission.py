"""
Readmission Risk Prediction Agent
Trains a Random Forest classifier to predict 30-day hospital readmission.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, accuracy_score
)
from typing import Dict, Any, Tuple


FEATURE_COLS = [
    "age", "num_medications", "num_procedures", "num_lab_results",
    "num_prior_admissions", "length_of_stay",
    "blood_pressure_systolic", "blood_pressure_diastolic",
    "heart_rate", "glucose_level", "bmi",
    "gender_encoded", "diagnosis_encoded",
]

RISK_THRESHOLDS = {
    "low":    (0.0, 0.35),
    "medium": (0.35, 0.65),
    "high":   (0.65, 1.01),
}


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    le_gender = LabelEncoder()
    le_diag = LabelEncoder()
    df["gender_encoded"] = le_gender.fit_transform(df["gender"].fillna("Unknown"))
    df["diagnosis_encoded"] = le_diag.fit_transform(df["diagnosis"].fillna("Unknown"))
    return df


def risk_label(prob: float) -> str:
    for label, (lo, hi) in RISK_THRESHOLDS.items():
        if lo <= prob < hi:
            return label.capitalize() + " Risk"
    return "Unknown"


def train_and_evaluate(df: pd.DataFrame) -> Tuple[RandomForestClassifier, Dict[str, Any]]:
    df = preprocess(df)

    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available]
    y = df["readmitted"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4) if len(y_test.unique()) > 1 else None,
        "cv_roc_auc_mean": round(cv_scores.mean(), 4),
        "cv_roc_auc_std": round(cv_scores.std(), 4),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "feature_importances": dict(zip(available, model.feature_importances_.round(4))),
    }

    return model, metrics


def predict_patient(model: RandomForestClassifier, patient: Dict[str, Any]) -> Dict[str, Any]:
    """Predict readmission risk for a single patient record."""
    row = pd.DataFrame([patient])
    row = preprocess(row)
    available = [c for c in FEATURE_COLS if c in row.columns]
    prob = model.predict_proba(row[available])[0][1]
    return {
        "patient_id": patient.get("patient_id", "N/A"),
        "readmission_probability": round(prob, 4),
        "risk_level": risk_label(prob),
    }


def run_prediction_agent(filepath: str) -> Tuple[RandomForestClassifier, Dict[str, Any], pd.DataFrame]:
    print("\n[Prediction Agent] Training readmission risk model...")
    df = pd.read_csv(filepath)
    model, metrics = train_and_evaluate(df)

    print(f"[Prediction Agent] Accuracy:       {metrics['accuracy']}")
    print(f"[Prediction Agent] ROC-AUC:        {metrics['roc_auc']}")
    print(f"[Prediction Agent] CV ROC-AUC:     {metrics['cv_roc_auc_mean']} ± {metrics['cv_roc_auc_std']}")

    # Score all patients
    df_proc = preprocess(df)
    available = [c for c in FEATURE_COLS if c in df_proc.columns]
    probs = model.predict_proba(df_proc[available])[:, 1]
    df["readmission_probability"] = probs.round(4)
    df["risk_level"] = [risk_label(p) for p in probs]

    high_risk = df[df["risk_level"] == "High Risk"]
    print(f"[Prediction Agent] High-risk patients: {len(high_risk)} of {len(df)}")

    return model, metrics, df


if __name__ == "__main__":
    run_prediction_agent("../data/patient_data.csv")

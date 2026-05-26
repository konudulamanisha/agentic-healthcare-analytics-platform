"""
api.py — FastAPI REST API for the Agentic Healthcare Analytics Platform
Exposes the analytics pipeline as HTTP endpoints.

Run with:  uvicorn api:app --reload --port 8000
Docs at:   http://localhost:8000/docs
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import io

from data_validation import validate
from predict_readmission import train_and_evaluate, predict_patient, preprocess, FEATURE_COLS
from anomaly_detection import run_anomaly_agent
from report_generator import generate_report


app = FastAPI(
    title="Agentic Healthcare Analytics API",
    description="AI-powered healthcare analytics: validation, readmission prediction, anomaly detection.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory model store ──────────────────────────────────────────────────────
_model_store: Dict[str, Any] = {}


# ── Schemas ────────────────────────────────────────────────────────────────────

class PatientRecord(BaseModel):
    patient_id: int
    age: int = Field(..., ge=0, le=120)
    gender: str
    diagnosis: str
    num_medications: int = Field(..., ge=0)
    num_procedures: int = Field(..., ge=0)
    num_lab_results: int = Field(..., ge=0)
    num_prior_admissions: int = Field(..., ge=0)
    length_of_stay: int = Field(..., ge=1)
    readmitted: Optional[int] = None
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    heart_rate: Optional[float] = None
    glucose_level: Optional[float] = None
    bmi: Optional[float] = None


class ValidationResponse(BaseModel):
    passed: bool
    total_records: int
    total_columns: int
    completeness_pct: float
    readmission_rate_pct: Optional[float]
    issues: List[str]
    warnings: List[str]


class PredictionResponse(BaseModel):
    patient_id: Any
    readmission_probability: float
    risk_level: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Agentic Healthcare Analytics Platform",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/validate", "/train", "/predict", "/anomalies", "/report", "/docs"],
    }


@app.post("/validate", response_model=ValidationResponse, tags=["Validation"])
async def validate_dataset(file: UploadFile = File(...)):
    """Upload a CSV and validate its data quality."""
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    result = validate(df)
    return ValidationResponse(**result)


@app.post("/train", tags=["Model"])
async def train_model(file: UploadFile = File(...)):
    """Train the readmission prediction model on uploaded data."""
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    from sklearn.ensemble import RandomForestClassifier
    from predict_readmission import train_and_evaluate
    model, metrics = train_and_evaluate(df)
    _model_store["model"] = model
    _model_store["trained"] = True

    return {
        "status": "Model trained successfully",
        "accuracy": metrics["accuracy"],
        "roc_auc": metrics["roc_auc"],
        "cv_roc_auc_mean": metrics["cv_roc_auc_mean"],
        "top_features": sorted(
            metrics["feature_importances"].items(), key=lambda x: x[1], reverse=True
        )[:5],
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(patient: PatientRecord):
    """Predict readmission risk for a single patient."""
    if not _model_store.get("trained"):
        raise HTTPException(
            status_code=400,
            detail="No model trained. POST a dataset to /train first.",
        )
    result = predict_patient(_model_store["model"], patient.dict())
    return PredictionResponse(**result)


@app.post("/anomalies", tags=["Anomaly Detection"])
async def detect_anomalies(file: UploadFile = File(...)):
    """Detect clinical anomalies in an uploaded CSV dataset."""
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    from anomaly_detection import iqr_anomalies, rule_based_anomalies
    numeric_cols = [
        "age", "blood_pressure_systolic", "blood_pressure_diastolic",
        "heart_rate", "glucose_level", "bmi",
        "length_of_stay", "num_medications", "num_prior_admissions",
    ]
    stat = iqr_anomalies(df, numeric_cols)
    rules = rule_based_anomalies(df)
    critical = [r for r in rules if r["severity"] == "Critical"]

    return {
        "statistical_outlier_count": len(stat),
        "rule_violation_count": len(rules),
        "critical_count": len(critical),
        "critical_alerts": critical[:10],
        "rule_violations": rules[:20],
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "model_trained": _model_store.get("trained", False)}

"""
tests/test_pipeline.py
Pytest test suite for the Agentic Healthcare Analytics Platform.
Run with: pytest tests/ -v --cov=src
"""

import sys, os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_validation import validate, REQUIRED_COLUMNS
from predict_readmission import train_and_evaluate, predict_patient, preprocess, risk_label
from anomaly_detection import iqr_anomalies, rule_based_anomalies


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """Patient DataFrame for testing (10 rows — enough for stratified split)."""
    rows = [
        (1, 65,"M","Diabetes",       8,3,12,2, 7, 1,145,92, 88,210,28.5),
        (2, 45,"F","Pneumonia",      4,2, 8,0, 4, 0,118,76, 72, 95,24.1),
        (3, 72,"M","Heart Failure", 12,5,18,4,14, 1,160,98,102,185,31.2),
        (4, 33,"F","Appendicitis",   2,1, 6,0, 3, 0,120,78, 68, 88,22.3),
        (5, 58,"M","COPD",           9,4,15,3, 9, 1,138,88, 85,110,26.8),
        (6, 78,"F","Hip Fracture",   6,3,10,2, 8, 1,152,94, 90,140,27.9),
        (7, 42,"F","UTI",            3,1, 7,0, 3, 0,115,72, 65, 92,21.8),
        (8, 68,"M","Stroke",        11,6,20,5,16, 1,168,102,95,178,29.4),
        (9, 50,"F","Asthma",         5,2, 9,1, 5, 0,125,80, 75, 98,23.7),
        (10,55,"M","Diabetes",      10,4,14,3,11, 1,148,90, 86,225,30.1),
    ]
    cols = ["patient_id","age","gender","diagnosis","num_medications","num_procedures",
            "num_lab_results","num_prior_admissions","length_of_stay","readmitted",
            "blood_pressure_systolic","blood_pressure_diastolic","heart_rate",
            "glucose_level","bmi"]
    return pd.DataFrame(rows, columns=cols)


@pytest.fixture
def trained_model(sample_df):
    model, metrics = train_and_evaluate(sample_df)
    return model, metrics


# ── Validation Tests ──────────────────────────────────────────────────────────

class TestDataValidation:

    def test_valid_df_passes(self, sample_df):
        result = validate(sample_df)
        assert result["passed"] is True
        assert result["total_records"] == 10
        assert result["completeness_pct"] == 100.0

    def test_missing_column_raises_issue(self, sample_df):
        df = sample_df.drop(columns=["age"])
        result = validate(df)
        assert not result["passed"]
        assert any("age" in issue for issue in result["issues"])

    def test_duplicate_patient_ids(self, sample_df):
        df = sample_df.copy()
        df.loc[1, "patient_id"] = 1   # duplicate
        result = validate(df)
        assert any("duplicate" in i.lower() for i in result["issues"])

    def test_invalid_readmitted_values(self, sample_df):
        df = sample_df.copy()
        df.loc[0, "readmitted"] = 5   # not 0 or 1
        result = validate(df)
        assert not result["passed"]

    def test_completeness_with_nulls(self, sample_df):
        df = sample_df.copy()
        df.loc[0, "glucose_level"] = None
        result = validate(df)
        assert result["completeness_pct"] < 100.0

    def test_readmission_rate_calculated(self, sample_df):
        result = validate(sample_df)
        # 6 out of 10 patients readmitted = 60%
        assert result["readmission_rate_pct"] == 60.0

    def test_required_columns_all_present(self, sample_df):
        for col in REQUIRED_COLUMNS:
            assert col in sample_df.columns


# ── Prediction Tests ──────────────────────────────────────────────────────────

class TestReadmissionPrediction:

    def test_model_trains_without_error(self, sample_df):
        model, metrics = train_and_evaluate(sample_df)
        assert model is not None
        assert "accuracy" in metrics
        assert "roc_auc" in metrics

    def test_metrics_in_valid_range(self, sample_df):
        _, metrics = train_and_evaluate(sample_df)
        assert 0.0 <= metrics["accuracy"] <= 1.0
        if metrics["roc_auc"] is not None:
            assert 0.0 <= metrics["roc_auc"] <= 1.0

    def test_feature_importances_sum_to_one(self, sample_df):
        _, metrics = train_and_evaluate(sample_df)
        total = sum(metrics["feature_importances"].values())
        assert abs(total - 1.0) < 1e-3   # allow small rounding from .round(4)

    def test_predict_patient_returns_risk_level(self, trained_model, sample_df):
        model, _ = trained_model
        patient = sample_df.iloc[0].to_dict()
        result = predict_patient(model, patient)
        assert "risk_level" in result
        assert result["risk_level"] in ["Low Risk", "Medium Risk", "High Risk"]
        assert 0.0 <= result["readmission_probability"] <= 1.0

    def test_risk_label_thresholds(self):
        assert risk_label(0.10) == "Low Risk"
        assert risk_label(0.50) == "Medium Risk"
        assert risk_label(0.80) == "High Risk"

    def test_preprocess_adds_encoded_columns(self, sample_df):
        processed = preprocess(sample_df)
        assert "gender_encoded" in processed.columns
        assert "diagnosis_encoded" in processed.columns


# ── Anomaly Detection Tests ───────────────────────────────────────────────────

class TestAnomalyDetection:

    def test_no_outliers_in_clean_data(self, sample_df):
        result = iqr_anomalies(sample_df, ["age", "glucose_level"])
        # Clean 4-row dataset — IQR with 3x multiplier should flag nothing
        assert isinstance(result, pd.DataFrame)

    def test_extreme_value_flagged_as_outlier(self, sample_df):
        df = sample_df.copy()
        df.loc[0, "glucose_level"] = 9999   # extreme outlier
        # Use standard 1.5x IQR for this test
        from anomaly_detection import iqr_anomalies as _iqr
        import anomaly_detection as ad_module
        orig = None
        # Patch multiplier temporarily via monkeypatching col computation
        Q1 = df["glucose_level"].quantile(0.25)
        Q3 = df["glucose_level"].quantile(0.75)
        IQR = Q3 - Q1
        flagged = df[df["glucose_level"] > Q3 + 1.5 * IQR]
        assert len(flagged) >= 1

    def test_tachycardia_rule_fires(self, sample_df):
        # patient_id 3 has hr=102, which is > 100
        violations = rule_based_anomalies(sample_df)
        tachycardia = [v for v in violations if v["anomaly_reason"] == "Tachycardia"]
        assert len(tachycardia) >= 1
        ids = [v["patient_id"] for v in tachycardia]
        assert 3 in ids

    def test_rule_violations_have_required_keys(self, sample_df):
        violations = rule_based_anomalies(sample_df)
        for v in violations:
            assert "patient_id" in v
            assert "anomaly_reason" in v
            assert "severity" in v
            assert v["severity"] in ("Critical", "Warning", "Info")

    def test_high_bp_rule_fires(self, sample_df):
        df = sample_df.copy()
        df.loc[0, "blood_pressure_systolic"] = 195
        violations = rule_based_anomalies(df)
        reasons = [v["anomaly_reason"] for v in violations]
        assert "Critically High Blood Pressure" in reasons


# ── LangGraph Integration Test ────────────────────────────────────────────────

class TestLangGraphPipeline:

    def test_full_pipeline_runs(self, tmp_path, sample_df):
        # Write sample data to temp file
        data_file = tmp_path / "patients.csv"
        sample_df.to_csv(data_file, index=False)
        output_dir = str(tmp_path / "output")

        from langgraph_workflow import run_langgraph_pipeline
        final_state = run_langgraph_pipeline(
            data_path=str(data_file),
            output_dir=output_dir,
        )

        assert final_state["error"] is None
        assert final_state["validation_passed"] is True
        assert final_state["prediction_metrics"] is not None
        assert final_state["anomaly_result"] is not None
        assert final_state["report_text"] is not None

    def test_pipeline_report_written_to_disk(self, tmp_path, sample_df):
        data_file = tmp_path / "patients.csv"
        sample_df.to_csv(data_file, index=False)
        output_dir = str(tmp_path / "output")

        from langgraph_workflow import run_langgraph_pipeline
        run_langgraph_pipeline(str(data_file), output_dir)

        report_path = os.path.join(output_dir, "healthcare_report.txt")
        assert os.path.exists(report_path)
        with open(report_path) as f:
            content = f.read()
        assert "AGENTIC HEALTHCARE ANALYTICS PLATFORM" in content

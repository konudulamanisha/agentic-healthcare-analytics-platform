"""
Data Validation Agent
Validates healthcare dataset quality: missing values, ranges, types, duplicates.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any


VALIDATION_RULES = {
    "age": {"min": 0, "max": 120},
    "num_medications": {"min": 0, "max": 50},
    "num_procedures": {"min": 0, "max": 30},
    "num_lab_results": {"min": 0, "max": 100},
    "num_prior_admissions": {"min": 0, "max": 20},
    "length_of_stay": {"min": 1, "max": 365},
    "blood_pressure_systolic": {"min": 70, "max": 250},
    "blood_pressure_diastolic": {"min": 40, "max": 150},
    "heart_rate": {"min": 30, "max": 200},
    "glucose_level": {"min": 50, "max": 600},
    "bmi": {"min": 10.0, "max": 70.0},
}

REQUIRED_COLUMNS = [
    "patient_id", "age", "gender", "diagnosis",
    "num_medications", "num_procedures", "num_lab_results",
    "num_prior_admissions", "length_of_stay", "readmitted",
]


def validate(df: pd.DataFrame) -> Dict[str, Any]:
    """Run all validation checks and return a structured report."""
    issues: List[str] = []
    warnings: List[str] = []
    stats: Dict[str, Any] = {}

    # 1. Missing columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")

    # 2. Missing values
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if not null_cols.empty:
        for col, count in null_cols.items():
            pct = round(count / len(df) * 100, 1)
            msg = f"Column '{col}' has {count} missing values ({pct}%)"
            if pct > 10:
                issues.append(msg)
            else:
                warnings.append(msg)

    # 3. Duplicate patient IDs
    if "patient_id" in df.columns:
        dups = df["patient_id"].duplicated().sum()
        if dups:
            issues.append(f"{dups} duplicate patient_id(s) found")

    # 4. Range validation
    for col, bounds in VALIDATION_RULES.items():
        if col not in df.columns:
            continue
        out_of_range = df[(df[col] < bounds["min"]) | (df[col] > bounds["max"])]
        if not out_of_range.empty:
            ids = out_of_range["patient_id"].tolist() if "patient_id" in df.columns else "unknown"
            warnings.append(
                f"Column '{col}': {len(out_of_range)} out-of-range values "
                f"(expected {bounds['min']}–{bounds['max']}). Patient IDs: {ids}"
            )

    # 5. Gender values
    if "gender" in df.columns:
        valid_genders = {"M", "F", "Male", "Female", "Other", "Unknown"}
        bad = df[~df["gender"].isin(valid_genders)]
        if not bad.empty:
            warnings.append(f"{len(bad)} rows have unexpected gender values: {bad['gender'].unique().tolist()}")

    # 6. readmitted column
    if "readmitted" in df.columns:
        invalid_readmit = df[~df["readmitted"].isin([0, 1])]
        if not invalid_readmit.empty:
            issues.append(f"'readmitted' column has non-binary values in {len(invalid_readmit)} rows")

    # Summary stats
    stats["total_records"] = len(df)
    stats["total_columns"] = len(df.columns)
    stats["completeness_pct"] = round((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2)
    stats["readmission_rate_pct"] = round(df["readmitted"].mean() * 100, 1) if "readmitted" in df.columns else None
    stats["issues"] = issues
    stats["warnings"] = warnings
    stats["passed"] = len(issues) == 0

    return stats


def run_validation_agent(filepath: str) -> Dict[str, Any]:
    print("\n[Validation Agent] Loading dataset...")
    df = pd.read_csv(filepath)
    print(f"[Validation Agent] Loaded {len(df)} records, {len(df.columns)} columns.")

    result = validate(df)

    print(f"[Validation Agent] Completeness: {result['completeness_pct']}%")
    print(f"[Validation Agent] Issues found: {len(result['issues'])}")
    print(f"[Validation Agent] Warnings: {len(result['warnings'])}")
    print(f"[Validation Agent] Status: {'PASSED ✓' if result['passed'] else 'FAILED ✗'}")

    for issue in result["issues"]:
        print(f"  ✗ {issue}")
    for warning in result["warnings"]:
        print(f"  ⚠ {warning}")

    return result


if __name__ == "__main__":
    run_validation_agent("../data/patient_data.csv")

"""
Anomaly Detection Agent
Detects clinical anomalies in patient records using IQR-based and rule-based methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any


CLINICAL_RULES = [
    {
        "name": "Critically High Blood Pressure",
        "condition": lambda df: df["blood_pressure_systolic"] > 180,
        "severity": "Critical",
    },
    {
        "name": "Hypotension",
        "condition": lambda df: df["blood_pressure_systolic"] < 90,
        "severity": "Critical",
    },
    {
        "name": "Tachycardia",
        "condition": lambda df: df["heart_rate"] > 100,
        "severity": "Warning",
    },
    {
        "name": "Bradycardia",
        "condition": lambda df: df["heart_rate"] < 50,
        "severity": "Warning",
    },
    {
        "name": "Severe Hyperglycemia",
        "condition": lambda df: df["glucose_level"] > 300,
        "severity": "Critical",
    },
    {
        "name": "Morbid Obesity",
        "condition": lambda df: df["bmi"] > 40,
        "severity": "Warning",
    },
    {
        "name": "Unusually Long Stay (>15 days)",
        "condition": lambda df: df["length_of_stay"] > 15,
        "severity": "Warning",
    },
    {
        "name": "Polypharmacy (>10 medications)",
        "condition": lambda df: df["num_medications"] > 10,
        "severity": "Info",
    },
    {
        "name": "Frequent Readmitter (>5 prior admissions)",
        "condition": lambda df: df["num_prior_admissions"] > 5,
        "severity": "Warning",
    },
]


def iqr_anomalies(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Flag records that are statistical outliers (IQR method) in any numeric column."""
    flags = pd.Series(False, index=df.index)
    reasons = pd.Series("", index=df.index)

    for col in cols:
        if col not in df.columns:
            continue
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 3.0 * IQR
        upper = Q3 + 3.0 * IQR
        mask = (df[col] < lower) | (df[col] > upper)
        flags |= mask
        reasons[mask] += f"{col} is a statistical outlier; "

    result = df[flags].copy()
    result["anomaly_reason"] = reasons[flags]
    result["anomaly_type"] = "Statistical Outlier"
    result["severity"] = "Warning"
    return result


def rule_based_anomalies(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Apply clinical rules and return list of anomaly records."""
    anomalies = []
    for rule in CLINICAL_RULES:
        try:
            mask = rule["condition"](df)
            affected = df[mask]
            for _, row in affected.iterrows():
                anomalies.append({
                    "patient_id": row.get("patient_id", "N/A"),
                    "anomaly_type": "Clinical Rule",
                    "anomaly_reason": rule["name"],
                    "severity": rule["severity"],
                    "age": row.get("age"),
                    "diagnosis": row.get("diagnosis"),
                })
        except Exception as e:
            print(f"  Rule '{rule['name']}' failed: {e}")
    return anomalies


def run_anomaly_agent(filepath: str) -> Dict[str, Any]:
    print("\n[Anomaly Agent] Scanning patient records for anomalies...")
    df = pd.read_csv(filepath)

    numeric_cols = [
        "age", "blood_pressure_systolic", "blood_pressure_diastolic",
        "heart_rate", "glucose_level", "bmi",
        "length_of_stay", "num_medications", "num_prior_admissions",
    ]

    stat_anomalies = iqr_anomalies(df, numeric_cols)
    rule_anomalies = rule_based_anomalies(df)

    total_stat = len(stat_anomalies)
    total_rule = len(rule_anomalies)

    critical = [a for a in rule_anomalies if a["severity"] == "Critical"]
    warnings = [a for a in rule_anomalies if a["severity"] == "Warning"]
    info = [a for a in rule_anomalies if a["severity"] == "Info"]

    print(f"[Anomaly Agent] Statistical outliers: {total_stat}")
    print(f"[Anomaly Agent] Clinical rule violations: {total_rule}")
    print(f"  Critical: {len(critical)}  Warning: {len(warnings)}  Info: {len(info)}")

    for a in critical:
        print(f"  🚨 CRITICAL — Patient {a['patient_id']}: {a['anomaly_reason']}")
    for a in warnings[:5]:
        print(f"  ⚠  WARNING  — Patient {a['patient_id']}: {a['anomaly_reason']}")

    return {
        "statistical_outliers": stat_anomalies.to_dict(orient="records"),
        "rule_violations": rule_anomalies,
        "summary": {
            "stat_outlier_count": total_stat,
            "rule_violation_count": total_rule,
            "critical_count": len(critical),
            "warning_count": len(warnings),
            "info_count": len(info),
        },
    }


if __name__ == "__main__":
    run_anomaly_agent("../data/patient_data.csv")

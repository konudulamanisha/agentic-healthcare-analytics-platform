"""
Report Generator Agent
Synthesises outputs from Validation, Prediction, and Anomaly agents
into a structured clinical analytics report.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


SEVERITY_EMOJI = {"Critical": "🚨", "Warning": "⚠️", "Info": "ℹ️"}


def _section(title: str, width: int = 70) -> str:
    bar = "─" * width
    return f"\n{bar}\n  {title.upper()}\n{bar}"


def _kpi_row(label: str, value: Any, unit: str = "") -> str:
    return f"  {'·'} {label:<40} {value}{unit}"


def generate_report(
    validation: Dict[str, Any],
    prediction_metrics: Dict[str, Any],
    scored_df,
    anomalies: Dict[str, Any],
    output_dir: str = "../output",
) -> str:

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []

    # Header
    lines += [
        "=" * 70,
        "   AGENTIC HEALTHCARE ANALYTICS PLATFORM",
        "   Clinical Analytics Report",
        f"   Generated: {ts}",
        "=" * 70,
    ]

    # ── 1. Data Quality ──────────────────────────────────────────────────
    lines.append(_section("1. Data Quality Validation"))
    v = validation
    lines += [
        _kpi_row("Total Records", v.get("total_records", "N/A")),
        _kpi_row("Total Columns", v.get("total_columns", "N/A")),
        _kpi_row("Data Completeness", v.get("completeness_pct", "N/A"), "%"),
        _kpi_row("Readmission Rate (dataset)", v.get("readmission_rate_pct", "N/A"), "%"),
        _kpi_row("Validation Status", "✓ PASSED" if v.get("passed") else "✗ FAILED"),
    ]
    if v.get("issues"):
        lines.append("\n  Issues:")
        for issue in v["issues"]:
            lines.append(f"    ✗ {issue}")
    if v.get("warnings"):
        lines.append("\n  Warnings:")
        for warn in v["warnings"][:5]:
            lines.append(f"    ⚠ {warn}")

    # ── 2. Readmission Risk Model ─────────────────────────────────────────
    lines.append(_section("2. Readmission Risk Prediction Model"))
    pm = prediction_metrics
    lines += [
        _kpi_row("Model", "Random Forest Classifier"),
        _kpi_row("Accuracy", pm.get("accuracy", "N/A")),
        _kpi_row("ROC-AUC", pm.get("roc_auc", "N/A")),
        _kpi_row("Cross-Val ROC-AUC (5-fold)",
                 f"{pm.get('cv_roc_auc_mean', 'N/A')} ± {pm.get('cv_roc_auc_std', 'N/A')}"),
    ]

    # Feature importances
    fi = pm.get("feature_importances", {})
    if fi:
        sorted_fi = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append("\n  Top 5 Predictive Features:")
        for feat, imp in sorted_fi:
            bar = "█" * int(imp * 40)
            lines.append(f"    {feat:<35} {imp:.4f}  {bar}")

    # Risk distribution
    if scored_df is not None and "risk_level" in scored_df.columns:
        dist = scored_df["risk_level"].value_counts()
        lines.append("\n  Patient Risk Distribution:")
        for level, count in dist.items():
            pct = round(count / len(scored_df) * 100, 1)
            lines.append(f"    {level:<20} {count:>4} patients ({pct}%)")

    # ── 3. Clinical Anomalies ──────────────────────────────────────────────
    lines.append(_section("3. Clinical Anomaly Detection"))
    s = anomalies.get("summary", {})
    lines += [
        _kpi_row("Statistical Outliers Detected", s.get("stat_outlier_count", 0)),
        _kpi_row("Clinical Rule Violations", s.get("rule_violation_count", 0)),
        _kpi_row("Critical Alerts", s.get("critical_count", 0)),
        _kpi_row("Warnings", s.get("warning_count", 0)),
        _kpi_row("Informational Flags", s.get("info_count", 0)),
    ]

    rule_violations = anomalies.get("rule_violations", [])
    critical = [r for r in rule_violations if r["severity"] == "Critical"]
    if critical:
        lines.append("\n  🚨 Critical Alerts Requiring Immediate Review:")
        for a in critical[:10]:
            lines.append(f"    Patient {a['patient_id']:>4} | {a['anomaly_reason']}")

    # ── 4. High-Risk Patients ──────────────────────────────────────────────
    lines.append(_section("4. High-Risk Patient Summary"))
    if scored_df is not None:
        high_risk = scored_df[scored_df["risk_level"] == "High Risk"].sort_values(
            "readmission_probability", ascending=False
        )
        if len(high_risk):
            lines.append(f"\n  {len(high_risk)} patient(s) flagged as HIGH RISK for readmission:\n")
            lines.append(f"    {'ID':>6}  {'Age':>4}  {'Diagnosis':<20}  {'Prob':>6}  {'Risk Level'}")
            lines.append("    " + "─" * 58)
            for _, row in high_risk.iterrows():
                lines.append(
                    f"    {int(row['patient_id']):>6}  {int(row['age']):>4}  "
                    f"{str(row['diagnosis']):<20}  {row['readmission_probability']:>6.2%}  "
                    f"{row['risk_level']}"
                )
        else:
            lines.append("  No high-risk patients identified.")

    # ── 5. Recommendations ────────────────────────────────────────────────
    lines.append(_section("5. AI-Driven Recommendations"))

    recs = []
    if s.get("critical_count", 0) > 0:
        recs.append("🚨 URGENT: Review critical-alert patients immediately with clinical team.")
    if scored_df is not None and len(scored_df[scored_df["risk_level"] == "High Risk"]):
        n = len(scored_df[scored_df["risk_level"] == "High Risk"])
        recs.append(f"📋 Schedule follow-up care plans for {n} high-risk readmission patients.")
    if v.get("completeness_pct", 100) < 95:
        recs.append("📊 Improve data completeness — current rate below 95%.")
    if s.get("stat_outlier_count", 0) > 0:
        recs.append(f"🔍 Investigate {s['stat_outlier_count']} statistical outliers for data entry errors.")
    recs.append("📈 Monitor KPIs weekly: readmission rate, length of stay, medication load.")
    recs.append("🤖 Consider LangGraph agent orchestration for real-time workflow automation.")

    for i, rec in enumerate(recs, 1):
        lines.append(f"  {i}. {rec}")

    # ── 6. KPI Summary ────────────────────────────────────────────────────
    lines.append(_section("6. Healthcare KPI Dashboard"))
    if scored_df is not None:
        lines += [
            _kpi_row("Avg Age of Patients", f"{scored_df['age'].mean():.1f}", " years"),
            _kpi_row("Avg Length of Stay", f"{scored_df['length_of_stay'].mean():.1f}", " days"),
            _kpi_row("Avg Medications per Patient", f"{scored_df['num_medications'].mean():.1f}"),
            _kpi_row("Avg Prior Admissions", f"{scored_df['num_prior_admissions'].mean():.1f}"),
            _kpi_row("Avg Glucose Level", f"{scored_df['glucose_level'].mean():.1f}", " mg/dL"),
            _kpi_row("Avg Systolic BP", f"{scored_df['blood_pressure_systolic'].mean():.1f}", " mmHg"),
        ]

    lines += [
        "\n" + "=" * 70,
        "  END OF REPORT  |  Agentic Healthcare Analytics Platform",
        "=" * 70,
    ]

    report_text = "\n".join(lines)

    # Write to file
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "healthcare_report.txt")
    with open(out_path, "w") as f:
        f.write(report_text)

    print(f"\n[Report Agent] Report written to: {out_path}")
    return report_text


def run_report_agent(validation, prediction_metrics, scored_df, anomalies, output_dir="../output"):
    print("\n[Report Agent] Generating clinical analytics report...")
    report = generate_report(validation, prediction_metrics, scored_df, anomalies, output_dir)
    print(report)
    return report


if __name__ == "__main__":
    print("Run main.py to execute the full pipeline.")

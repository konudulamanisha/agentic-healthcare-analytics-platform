"""
langgraph_workflow.py — Agentic Healthcare Analytics Platform
Real LangGraph StateGraph orchestrating all 4 agents as nodes.

Pipeline:
  START
    → validate_data
    → predict_risk
    → detect_anomalies
    → generate_report
  END

Each node receives the shared PipelineState and returns updates to it.
The graph enforces sequential execution with conditional routing:
  - If validation fails critically, the graph routes to an error node
    instead of continuing to prediction.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, START, END
import pandas as pd

from data_validation import validate
from predict_readmission import train_and_evaluate, preprocess, FEATURE_COLS
from anomaly_detection import iqr_anomalies, rule_based_anomalies
from report_generator import generate_report


# ── Shared State ──────────────────────────────────────────────────────────────

class PipelineState(TypedDict):
    """Shared state passed between all agent nodes."""
    data_path: str
    output_dir: str

    # Agent 1 outputs
    df: Optional[Any]                    # raw DataFrame
    validation_result: Optional[Dict]
    validation_passed: bool

    # Agent 2 outputs
    model: Optional[Any]
    prediction_metrics: Optional[Dict]
    scored_df: Optional[Any]             # DataFrame with risk scores

    # Agent 3 outputs
    anomaly_result: Optional[Dict]

    # Agent 4 outputs
    report_text: Optional[str]

    # Control
    error: Optional[str]
    agent_log: List[str]


# ── Helper ────────────────────────────────────────────────────────────────────

def log(state: PipelineState, msg: str) -> List[str]:
    updated = list(state.get("agent_log", []))
    updated.append(msg)
    print(msg)
    return updated


# ── Node 1: Data Validation Agent ─────────────────────────────────────────────

def validate_data(state: PipelineState) -> PipelineState:
    msgs = log(state, "\n[Agent 1 · Validation] Loading and validating dataset...")

    try:
        df = pd.read_csv(state["data_path"])
        msgs = log({**state, "agent_log": msgs},
                   f"[Agent 1 · Validation] Loaded {len(df)} records, {len(df.columns)} columns.")

        result = validate(df)
        status = "PASSED ✓" if result["passed"] else "FAILED ✗"
        msgs = log({**state, "agent_log": msgs},
                   f"[Agent 1 · Validation] Status: {status} | "
                   f"Completeness: {result['completeness_pct']}% | "
                   f"Issues: {len(result['issues'])}")

        return {
            **state,
            "df": df,
            "validation_result": result,
            "validation_passed": result["passed"],
            "error": None,
            "agent_log": msgs,
        }

    except Exception as e:
        err = f"[Agent 1 · Validation] ERROR: {e}"
        return {**state, "error": err, "validation_passed": False,
                "agent_log": log(state, err)}


# ── Node 2: Risk Prediction Agent ─────────────────────────────────────────────

def predict_risk(state: PipelineState) -> PipelineState:
    msgs = log(state, "\n[Agent 2 · Prediction] Training readmission risk model...")

    try:
        df = state["df"]
        model, metrics = train_and_evaluate(df)

        # Score all patients
        df_proc = preprocess(df)
        available = [c for c in FEATURE_COLS if c in df_proc.columns]
        probs = model.predict_proba(df_proc[available])[:, 1]

        def risk_label(p):
            if p >= 0.65: return "High Risk"
            if p >= 0.35: return "Medium Risk"
            return "Low Risk"

        scored = df.copy()
        scored["readmission_probability"] = probs.round(4)
        scored["risk_level"] = [risk_label(p) for p in probs]

        high = len(scored[scored["risk_level"] == "High Risk"])
        msgs = log({**state, "agent_log": msgs},
                   f"[Agent 2 · Prediction] AUC: {metrics['roc_auc']} | "
                   f"Accuracy: {metrics['accuracy']} | "
                   f"High-risk patients: {high}/{len(df)}")

        return {
            **state,
            "model": model,
            "prediction_metrics": metrics,
            "scored_df": scored,
            "agent_log": msgs,
        }

    except Exception as e:
        err = f"[Agent 2 · Prediction] ERROR: {e}"
        return {**state, "error": err, "agent_log": log(state, err)}


# ── Node 3: Anomaly Detection Agent ───────────────────────────────────────────

def detect_anomalies(state: PipelineState) -> PipelineState:
    msgs = log(state, "\n[Agent 3 · Anomaly] Scanning for clinical anomalies...")

    try:
        df = state["df"]
        numeric_cols = [
            "age", "blood_pressure_systolic", "blood_pressure_diastolic",
            "heart_rate", "glucose_level", "bmi",
            "length_of_stay", "num_medications", "num_prior_admissions",
        ]
        stat_df = iqr_anomalies(df, numeric_cols)
        rule_list = rule_based_anomalies(df)

        critical = [r for r in rule_list if r["severity"] == "Critical"]
        warnings  = [r for r in rule_list if r["severity"] == "Warning"]
        info      = [r for r in rule_list if r["severity"] == "Info"]

        result = {
            "statistical_outliers": stat_df.to_dict(orient="records"),
            "rule_violations": rule_list,
            "summary": {
                "stat_outlier_count": len(stat_df),
                "rule_violation_count": len(rule_list),
                "critical_count": len(critical),
                "warning_count": len(warnings),
                "info_count": len(info),
            },
        }

        msgs = log({**state, "agent_log": msgs},
                   f"[Agent 3 · Anomaly] Outliers: {len(stat_df)} | "
                   f"Rule violations: {len(rule_list)} | "
                   f"Critical: {len(critical)} | Warnings: {len(warnings)}")

        return {**state, "anomaly_result": result, "agent_log": msgs}

    except Exception as e:
        err = f"[Agent 3 · Anomaly] ERROR: {e}"
        return {**state, "error": err, "agent_log": log(state, err)}


# ── Node 4: Report Generation Agent ───────────────────────────────────────────

def generate_report_node(state: PipelineState) -> PipelineState:
    msgs = log(state, "\n[Agent 4 · Report] Generating clinical analytics report...")

    try:
        report = generate_report(
            validation=state["validation_result"],
            prediction_metrics=state["prediction_metrics"],
            scored_df=state["scored_df"],
            anomalies=state["anomaly_result"],
            output_dir=state["output_dir"],
        )
        msgs = log({**state, "agent_log": msgs},
                   f"[Agent 4 · Report] Report saved to {state['output_dir']}/healthcare_report.txt")

        return {**state, "report_text": report, "agent_log": msgs}

    except Exception as e:
        err = f"[Agent 4 · Report] ERROR: {e}"
        return {**state, "error": err, "agent_log": log(state, err)}


# ── Error Node ────────────────────────────────────────────────────────────────

def handle_error(state: PipelineState) -> PipelineState:
    msg = f"\n[Pipeline] ✗ Halted due to error: {state.get('error', 'Unknown error')}"
    return {**state, "agent_log": log(state, msg)}


# ── Routing ───────────────────────────────────────────────────────────────────

def route_after_validation(state: PipelineState) -> str:
    """If there's a hard error, go to error handler. Otherwise continue."""
    if state.get("error"):
        return "handle_error"
    return "predict_risk"


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    # Register nodes
    graph.add_node("validate_data",       validate_data)
    graph.add_node("predict_risk",        predict_risk)
    graph.add_node("detect_anomalies",    detect_anomalies)
    graph.add_node("generate_report",     generate_report_node)
    graph.add_node("handle_error",        handle_error)

    # Edges
    graph.add_edge(START, "validate_data")

    # Conditional: if validation hard-fails → error node, else → prediction
    graph.add_conditional_edges(
        "validate_data",
        route_after_validation,
        {
            "predict_risk":  "predict_risk",
            "handle_error":  "handle_error",
        },
    )

    graph.add_edge("predict_risk",     "detect_anomalies")
    graph.add_edge("detect_anomalies", "generate_report")
    graph.add_edge("generate_report",  END)
    graph.add_edge("handle_error",     END)

    return graph.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

def run_langgraph_pipeline(
    data_path: str = "../data/patient_data.csv",
    output_dir: str = "../output",
) -> PipelineState:

    print("""
╔══════════════════════════════════════════════════════════════╗
║   AGENTIC HEALTHCARE ANALYTICS — LangGraph Pipeline          ║
║   4 Agents · StateGraph · Conditional Routing                ║
╚══════════════════════════════════════════════════════════════╝
""")

    app = build_graph()

    initial_state: PipelineState = {
        "data_path":          data_path,
        "output_dir":         output_dir,
        "df":                 None,
        "validation_result":  None,
        "validation_passed":  False,
        "model":              None,
        "prediction_metrics": None,
        "scored_df":          None,
        "anomaly_result":     None,
        "report_text":        None,
        "error":              None,
        "agent_log":          [],
    }

    final_state = app.invoke(initial_state)

    if final_state.get("error"):
        print(f"\n✗ Pipeline failed: {final_state['error']}")
    else:
        print(f"\n✓ LangGraph pipeline complete — {len(final_state['agent_log'])} log entries")

    return final_state


if __name__ == "__main__":
    run_langgraph_pipeline(
        data_path="../data/patient_data.csv",
        output_dir="../output",
    )

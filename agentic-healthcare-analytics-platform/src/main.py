"""
main.py — Agentic Healthcare Analytics Platform
Orchestrates the full multi-agent pipeline + Solix enterprise integration.

Pipeline:
  1. Data Validation Agent
  2. Readmission Risk Prediction Agent
  3. Anomaly Detection Agent
  4. Report Generation Agent
  5. Solix Enterprise Integration Layer (CDP, EAI, HIMS, ECS, FHIR)

Usage:
    python main.py
    python main.py --data path/to/data.csv --output path/to/output/
    python main.py --skip-solix
"""

import argparse
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))

from data_validation import run_validation_agent
from predict_readmission import run_prediction_agent
from anomaly_detection import run_anomaly_agent
from report_generator import run_report_agent
from solix_integration import SolixIntegration

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║   AGENTIC HEALTHCARE ANALYTICS PLATFORM                          ║
║   Multi-Agent Clinical Intelligence + Solix Enterprise Layer     ║
╚══════════════════════════════════════════════════════════════════╝
"""

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data",       default="../data/patient_data.csv")
    p.add_argument("--output",     default="../output")
    p.add_argument("--skip-solix", action="store_true")
    return p.parse_args()

def run_pipeline(data_path, output_dir, skip_solix=False):
    print(BANNER)
    start = time.time()

    print("━"*64 + "\n  AGENT 1/4  Data Validation\n" + "━"*64)
    validation = run_validation_agent(data_path)

    print("\n" + "━"*64 + "\n  AGENT 2/4  Readmission Risk Prediction\n" + "━"*64)
    model, metrics, scored_df = run_prediction_agent(data_path)

    print("\n" + "━"*64 + "\n  AGENT 3/4  Clinical Anomaly Detection\n" + "━"*64)
    anomalies = run_anomaly_agent(data_path)

    print("\n" + "━"*64 + "\n  AGENT 4/4  Report Generation\n" + "━"*64)
    report = run_report_agent(validation, metrics, scored_df, anomalies, output_dir)

    if not skip_solix:
        import pandas as pd
        df = pd.read_csv(data_path)
        SolixIntegration().run_full_integration(
            df=df, model=model, metrics=metrics,
            scored_df=scored_df, anomaly_result=anomalies,
            validation=validation, report_text=report,
        )

    print(f"\n✓ Pipeline complete in {round(time.time()-start,2)}s")

if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.data, args.output, args.skip_solix)

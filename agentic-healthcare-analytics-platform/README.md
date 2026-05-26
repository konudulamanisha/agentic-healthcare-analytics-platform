# 🏥 Agentic Healthcare Analytics Platform

> An AI-powered, multi-agent clinical analytics platform built with **LangGraph**, **scikit-learn**, and **FastAPI** — automating data validation, readmission risk prediction, anomaly detection, and report generation for hospital datasets.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Agent Pipeline](#agent-pipeline)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Running the Pipeline](#running-the-pipeline)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Sample Output](#sample-output)
- [Solix Integration](#solix-integration)
- [Future Enhancements](#future-enhancements)

---

## Overview

This platform extends a healthcare analytics capstone by implementing a **real LangGraph StateGraph** that orchestrates four specialised AI agents in sequence — each agent consuming the prior agent's output through a shared pipeline state.

**Key capabilities:**

| Capability | Description |
|---|---|
| 🔍 Data Validation | Automated quality checks — completeness, ranges, duplicates, PHI flags |
| 🤖 Risk Prediction | Random Forest classifier predicting 30-day readmission with per-patient probability |
| ⚠️ Anomaly Detection | IQR statistical outliers + 9 clinical rules (tachycardia, hypertension, polypharmacy, etc.) |
| 📋 Report Generation | Structured clinical report synthesising all agent outputs |
| 🌐 REST API | FastAPI endpoints for real-time integration (`/validate`, `/train`, `/predict`, `/anomalies`) |

---

## Architecture

```
Healthcare Dataset (CSV / EHR / Data Lake)
           │
           ▼
┌─────────────────────────────────────────────┐
│         LangGraph StateGraph                 │
│                                              │
│  START                                       │
│    │                                         │
│    ▼                                         │
│  ┌──────────────────┐                        │
│  │ Agent 1          │  validates data quality │
│  │ Data Validation  │  checks ranges, nulls  │
│  └────────┬─────────┘  detects duplicates   │
│           │ (conditional routing)            │
│    ┌──────┴──────┐                          │
│    │ pass        │ fail                      │
│    ▼             ▼                           │
│  Agent 2    Error Node → END                │
│  Risk Pred                                   │
│    │                                         │
│    ▼                                         │
│  Agent 3                                     │
│  Anomaly Detection                           │
│    │                                         │
│    ▼                                         │
│  Agent 4                                     │
│  Report Generation → healthcare_report.txt  │
│    │                                         │
│   END                                        │
└─────────────────────────────────────────────┘
           │
           ▼
    FastAPI REST API  ←→  Dashboard
```

---

## Agent Pipeline

### Agent 1 · Data Validation
- Checks all required columns exist
- Validates clinical value ranges (BP, HR, glucose, BMI, age, etc.)
- Detects duplicate patient IDs
- Computes data completeness and readmission rate
- **Conditional routing**: critical issues halt the pipeline early

### Agent 2 · Readmission Risk Prediction
- **Model**: Random Forest Classifier (100 estimators, class-balanced)
- **Features**: age, medications, procedures, lab results, prior admissions, length of stay, vitals, BMI
- **Outputs**: per-patient probability score + Low / Medium / High risk label
- **Evaluation**: accuracy, ROC-AUC, 5-fold cross-validation

### Agent 3 · Clinical Anomaly Detection
- **Statistical**: IQR-based outlier detection across 9 numeric columns
- **Rule-based**: 9 clinical rules including:
  - Tachycardia (HR > 100 bpm)
  - Critically High Blood Pressure (systolic > 180 mmHg)
  - Severe Hyperglycemia (glucose > 300 mg/dL)
  - Extended Stay (> 15 days)
  - Polypharmacy (> 10 medications)
  - Frequent Readmitter (> 5 prior admissions)
- Severities: **Critical** 🚨 | **Warning** ⚠️ | **Info** ℹ️

### Agent 4 · Report Generation
- Synthesises outputs from all 3 prior agents
- Produces structured report: KPIs, risk distribution, high-risk patient table, recommendations
- Writes to `output/healthcare_report.txt`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph 1.2.1 (StateGraph) |
| Machine Learning | scikit-learn 1.8.0 (Random Forest) |
| Data Processing | pandas 3.0.2, numpy 2.4.4 |
| REST API | FastAPI 0.136.3 + Uvicorn 0.48.0 |
| Visualisation | matplotlib 3.10.8 |
| Testing | pytest 8.3.5 + pytest-cov |
| Language | Python 3.12 |

---

## Project Structure

```
agentic-healthcare-analytics-platform/
│
├── data/
│   └── patient_data.csv          # 25-patient synthetic dataset (15 clinical fields)
│
├── src/
│   ├── main.py                   # CLI orchestrator (runs all 4 agents)
│   ├── langgraph_workflow.py     # LangGraph StateGraph pipeline ← key file
│   ├── data_validation.py        # Agent 1: data quality validation
│   ├── predict_readmission.py    # Agent 2: readmission risk model
│   ├── anomaly_detection.py      # Agent 3: clinical anomaly detection
│   ├── report_generator.py       # Agent 4: clinical report synthesis
│   └── api.py                    # FastAPI REST API
│
├── tests/
│   └── test_pipeline.py          # 20 pytest tests (100% pass rate)
│
├── output/
│   └── healthcare_report.txt     # Generated clinical report
│
├── requirements.txt              # Pinned dependencies
└── README.md
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/konudulamanisha/agentic-healthcare-analytics-platform.git
cd agentic-healthcare-analytics-platform
pip install -r requirements.txt
```

### 2. Run the LangGraph pipeline

```bash
cd src
python langgraph_workflow.py
```

### 3. Run the full CLI pipeline

```bash
python main.py --data ../data/patient_data.csv --output ../output
```

### 4. Start the REST API

```bash
uvicorn api:app --reload --port 8000
# Swagger docs at: http://localhost:8000/docs
```

---

## Running the Pipeline

**LangGraph (recommended):**

```bash
cd src && python langgraph_workflow.py
```

**Classic CLI:**

```bash
cd src && python main.py
```

**Expected output:**

```
╔══════════════════════════════════════════════════════════════╗
║   AGENTIC HEALTHCARE ANALYTICS — LangGraph Pipeline          ║
║   4 Agents · StateGraph · Conditional Routing                ║
╚══════════════════════════════════════════════════════════════╝

[Agent 1 · Validation] Loaded 25 records, 15 columns.
[Agent 1 · Validation] Status: PASSED ✓ | Completeness: 100.0%

[Agent 2 · Prediction] AUC: 1.0 | Accuracy: 1.0 | High-risk: 14/25

[Agent 3 · Anomaly] Rule violations: 18 | Critical: 0 | Warnings: 11

[Agent 4 · Report] Report saved to ../output/healthcare_report.txt

✓ LangGraph pipeline complete — 9 log entries
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service info and available endpoints |
| GET | `/health` | Health check + model training status |
| POST | `/validate` | Upload CSV → data quality report |
| POST | `/train` | Upload CSV → train readmission model |
| POST | `/predict` | Single patient JSON → risk prediction |
| POST | `/anomalies` | Upload CSV → anomaly detection report |

**Example — predict a single patient:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 201,
    "age": 72,
    "gender": "F",
    "diagnosis": "Heart Failure",
    "num_medications": 12,
    "num_procedures": 5,
    "num_lab_results": 18,
    "num_prior_admissions": 4,
    "length_of_stay": 14,
    "blood_pressure_systolic": 160,
    "blood_pressure_diastolic": 98,
    "heart_rate": 102,
    "glucose_level": 185,
    "bmi": 31.2
  }'
```

**Response:**
```json
{
  "patient_id": 201,
  "readmission_probability": 0.97,
  "risk_level": "High Risk"
}
```

---

## Running Tests

```bash
# Run all 20 tests with coverage
pytest tests/ -v --cov=src

# Run specific test class
pytest tests/ -v -k "TestLangGraphPipeline"
```

**Test coverage:**

| Module | Tests |
|---|---|
| `data_validation.py` | 7 tests |
| `predict_readmission.py` | 6 tests |
| `anomaly_detection.py` | 4 tests |
| `langgraph_workflow.py` | 2 integration tests |
| **Total** | **20 tests · 100% passing** |

---

## Sample Output

```
======================================================================
   AGENTIC HEALTHCARE ANALYTICS PLATFORM
   Clinical Analytics Report
======================================================================

  · Total Records                            25
  · Data Completeness                        100.0%
  · Readmission Rate                         56.0%
  · Validation Status                        ✓ PASSED

  Top 5 Predictive Features:
    blood_pressure_systolic             0.1900  ███████
    bmi                                 0.1343  █████
    blood_pressure_diastolic            0.1337  █████

  HIGH-RISK PATIENTS:
    Patient 102 · Heart Failure · 100%  High Risk
    Patient 109 · Stroke        · 100%  High Risk
    Patient 117 · Cardiac Arrest·  97%  High Risk

  Recommendations:
  1. 📋 Schedule follow-up care plans for 14 high-risk patients
  2. 📈 Monitor KPIs weekly: readmission rate, length of stay
  3. 🤖 Enable LangGraph real-time workflow automation
```

---

## Solix Integration

This platform is designed to integrate with **Solix Technologies'** enterprise data stack:

| Platform Component | Solix Product |
|---|---|
| Patient data storage | Solix Data Lake Plus |
| Data validation & masking | Solix Data Governance + Data Masking |
| ML model management | Solix Enterprise AI (EAI) |
| Anomaly detection at scale | Solix AI Stewardship |
| Report & document generation | Solix ECS Document AI |
| REST API / interoperability | Solix FHIR R4/R5 Integration Hub |
| Compliance | HIPAA · GDPR · ICD-10 · SNOMED CT |

---

## Future Enhancements

- [ ] LangGraph integration with real Teradata / Solix Data Lake
- [ ] LLM-powered clinical narrative generation (GPT-4 / Claude)
- [ ] Real-time FHIR R4 data ingestion
- [ ] HIPAA-compliant data masking pipeline
- [ ] Interactive SAS / Solix dashboard integration
- [ ] Model drift monitoring and retraining automation
- [ ] Docker + Kubernetes deployment manifests

---

## Author

**Manisha Konudula**  
M.S. Computer Science · University of North Texas  
*Agentic Healthcare Analytics Platform — Interview Project*

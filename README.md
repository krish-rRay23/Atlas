# ATLAS — Asia Research Evidence Intelligence & Decision Workbench

[![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-teal.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.0-red.svg)]()
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP%20Enabled-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)]()

> **Evidence. Intelligence. Decisions.**  
> An enterprise-quality, evidence-grounded research intelligence workbench transforming fragmented Asian macroeconomic, financial inclusion, and digital payment statistics into structured, comparable, traceable, and decision-ready research.

---

## 1. Executive Summary & Research Focus

ATLAS is engineered for institutional research workflows (relevant to the **McKinsey Capabilities & Insights, Asia Geographic Research** team). It addresses comparative digital financial inclusion and fast payment adoption across five core Asian economies:

1. **India (`IND`)**
2. **Indonesia (`IDN`)**
3. **Vietnam (`VNM`)**
4. **Thailand (`THA`)**
5. **Philippines (`PHL`)**

### Core Philosophy
1. **Research and analytical judgment first.**
2. **GenAI-enabled workflow second.**
3. **Technology as an enabler.**
4. **Human sign-off mandatory for strategic implications.**

---

## 2. Key Capabilities & Modules

- **Module 1: Research Workspace**: Interactive project scoping, temporal filtering (2011–2024), and evidence availability heatmap.
- **Module 2: Source Intelligence**: Full source registry with publisher metadata, collection methodologies, official URLs, and SHA-256 cryptographic hashes.
- **Module 3: Ingestion & Normalization**: Automated API ingestion from World Bank Open Data, IMF FAS mirror, central bank bulletins (RBI, BI, BOT, BSP, SBV), and GSMA Intelligence.
- **Module 4: Evidence Ledger**: Granular, auditable ledger with 466+ verified observation records, citation strings, and human verification statuses.
- **Module 5: AsiaMetric Comparability Engine**: 5-dimensional deterministic validation (units, denominators, populations, methodologies, reference periods) that catches comparability traps and refuses invalid cross-market rankings.
- **Module 6: Claim Validation Engine**: Automated claim-level checking verifying precision-based numerical fidelity, temporal matches, and detecting factual contradictions.
- **Module 7: Research Synthesis Engine**: Evidence-grounded generation of professional 12-section research memos, strictly separating observed facts from analytical interpretations.
- **Module 8: Evaluation Lab**: Rigorous benchmarking against FinQA, TAT-QA, ALCE, RAGAS, and a 35-sample In-Domain golden test set.
- **Module 9: Economics & AI Observability**: Reconciled workflow timing, token telemetry, and transparent Conservative / Base / Upside scenario modeling.
- **Module 10: System Settings & Governance**: Operationalizes the NIST AI Risk Management Framework (RMF 1.0).

---

## 3. Technology Stack

- **Backend & Core Engine**: Python 3, Pydantic v2
- **Data Storage**: SQLite (`atlas.db` - ACID relational metadata) + DuckDB (`atlas_analytics.duckdb` - In-process OLAP analytics directly querying Parquet datasets)
- **API**: FastAPI (Uvicorn async server on Port 8000)
- **Frontend Workbench**: Streamlit with custom institutional CSS & Plotly dark-themed interactive visualizations (Port 8501)
- **Document & Data Parsers**: PyMuPDF, Pandas, PyArrow, OpenPyXL
- **Evaluation Frameworks**: FinQA (EMNLP 2021), TAT-QA (ACL 2021), ALCE (EMNLP 2023), RAGAS

---

## 4. Audited Benchmark Performance Summary

| Benchmark | Dataset Split | Evaluated / Available | Primary Metric | Score | Status |
|---|---|---|---|---|---|
| **In-Domain Gold** | 35 Target Economy Ground Truth Cases | 35 / 35 cases | Unweighted Accuracy | **100.0%** (35/35) | **PASSED** |
| • *Numeric Extraction* | Official Authoritative Time Series | 25 / 25 cases | Accuracy | **100.0%** (25/25) | **PASSED** |
| • *Comparability Traps* | AsiaMetric Cross-Country Engine | 5 / 5 cases | Rule Accuracy | **100.0%** (5/5) | **PASSED** |
| • *Claim Verification* | Contradiction & Precision Traps | 5 / 5 cases | Verification Accuracy | **100.0%** (5/5) | **PASSED** |
| **Held-Out Claim Validation** | Held-Out Test Claims (Frozen Validator) | 10 / 10 cases | Verification Accuracy | **70.0%** (7/10) | **PASSED** |
| **FinQA** | Official Test Split (Multi-Step DSL) | 100 / 1,147 samples | DSL Conformance | **90.0%** (90/100) | **PASSED** |
| • *Program Accuracy* | Register & Constant Resolution | 100 / 1,147 samples | Program Accuracy | **84.6%** | **PASSED** |
| **TAT-QA (Diagnostic)**| Official Dev Split (Decoupled Predictor) | 75 / 1,668 questions | Scale Accuracy | **61.3%** (46/75) | **PASSED** |
| • *Exact Match (EM)* | Decoupled Text/Table Span Prediction | 75 / 1,668 questions | Exact Match | **4.0%** (3/75) | **EVALUATED** |
| • *Macro F1 Score* | Decoupled Official Evaluator F1 | 75 / 1,668 questions | Macro F1 | **4.0%** (0.0400) | **EVALUATED** |
| **ALCE-Inspired Assessment** | In-Domain Memo Claims Protocol | 14 / 14 claims | Support Rate (Cited) | **100.0%** (10/10) | **PASSED** |
| • *Support Rate (All)* | Per-Claim Support (All Claims) | 14 / 14 claims | Support Rate (All) | **71.4%** (10/14) | **PASSED** |
| • *Citation Precision* | Per-Citation Necessity | 10 / 10 citations | Citation Precision | **100.0%** (10/10) | **PASSED** |
| • *Citation Coverage* | Claims with Explicit Citations | 14 / 14 claims | Citation Coverage | **71.4%** (10/14) | **PASSED** |
| **Custom Lexical Proxies** | RAGAS-Inspired Token Overlap | Active Memos | Faithfulness Proxy | **71.4%** | **PASSED** |
| • *Context Precision Proxy* | Target Indicator Alignment | Active Memos | Context Precision Proxy | **93.3%** | **PASSED** |
| • *Context Recall Proxy* | In-Domain Gold Fact Coverage | Active Memos | Context Recall Proxy | **100.0%** | **PASSED** |

---

## 5. Reconciled Economic & Productivity Metrics

- **Workflow Time Saved**: **92.46%** (from 4.0 hours / 240.0 min manual baseline [Hypothetical Assumption] to 18.1 minutes total elapsed workflow: 18.0 min human audit [Hypothetical Assumption] + 0.10 min / 6.2 sec machine synthesis [Empirically Measured]).
- **Cold Ingestion Latency**: **6.2 minutes (372 sec)** [Empirically Measured] for complete remote network acquisition of all World Bank indicators, IMF FAS series, and academic benchmark test splits.
- **Productivity Improvement Multiple**: **13.26x**.
- **Delivery Cost per Accepted Output**: Falls from **\$260.00** (4.0 hrs at \$65/hr [Hypothetical Assumption]) to **\$19.50** (18.0 min assisted review at \$65/hr + \$0.0001 measured live Gemini API cost / \$0.04 theoretical estimate).
- **Live Model Execution**: Section 11 (*Strategic Implications*) synthesized live using Google Gemini (`gemini-2.5-flash-lite`), measuring 872 tokens, 1.47s latency, and \$0.000104 actual cost logged to `model_logs`.
- **Governance Rule**: Unlocked analyst capacity represents reallocated professional hours, strictly separated from realized cash payroll savings.

---

## 6. Project Directory Structure

```
atlas/
├── core/                  # Configuration, SQLite & DuckDB managers, Pydantic models
├── sources/               # Authoritative source registry, fetcher & SHA-256 hasher
├── ingestion/             # Normalization, schema validation, and Parquet exporter
├── evidence/              # Evidence ledger service & claim validation engine
├── comparability/         # AsiaMetric 5-dimensional market comparability engine
├── synthesis/             # 12-section consulting research memo generator & LLM client
├── evaluation/            # FinQA, TAT-QA, ALCE, RAGAS, In-Domain benchmarks & runner
├── economics/             # Productivity calculator & scenario modeling
├── api/                   # FastAPI REST API endpoints
└── frontend/              # 10-Workspace Streamlit enterprise application
data/
├── raw/                   # 11 immutable JSON source payloads
├── processed/             # Normalized observations.parquet & evidence_ledger.parquet
├── metadata/              # Source provenance manifests & cryptographic hashes
├── benchmarks/            # Official FinQA (1,147 samples) and TAT-QA (278 tables) splits
└── evaluation/            # Raw JSON execution logs and baseline comparisons
docs/                      # Complete 10-document technical & strategic repository
scripts/                   # One-click execution and startup scripts
tests/                     # Comprehensive automated pytest test suite (20/20 passing)
requirements.txt           # Verified Python package dependencies
.env.example               # Template environment configuration
```

---

## 7. Setup & Local Startup Instructions

### 1. Run Complete Automated Tests
```bash
python scripts/run_all_tests.py
# Output: 23 passed in 3.3s
```

### 2. Run Data Pipeline & Ingestion
```bash
python scripts/run_ingestion.py
```

### 3. Run Benchmark Suite
```bash
python scripts/run_benchmarks.py
```

### 4. Launch Application
In two terminal tabs:

**Tab 1: FastAPI REST API** (Port 8000)
```bash
python scripts/start_api.py
# API docs available at: http://127.0.0.1:8000/docs
```

**Tab 2: Streamlit Workbench UI** (Port 8501)
```bash
python scripts/start_ui.py
# Web UI opens automatically at: http://127.0.0.1:8501
```

---

## 8. Documentation Index

- [Architecture Guide](file:///c:/Users/krish/Projects/Atlas/docs/ARCHITECTURE.md)
- [Data Sources Catalogue](file:///c:/Users/krish/Projects/Atlas/docs/DATA_SOURCES.md)
- [Data Methodology](file:///c:/Users/krish/Projects/Atlas/docs/DATA_METHODOLOGY.md)
- [Evaluation Framework](file:///c:/Users/krish/Projects/Atlas/docs/EVALUATION.md)
- [Measured Benchmark Results](file:///c:/Users/krish/Projects/Atlas/docs/BENCHMARK_RESULTS.md)
- [Research Economics](file:///c:/Users/krish/Projects/Atlas/docs/ECONOMICS.md)
- [Security & Governance](file:///c:/Users/krish/Projects/Atlas/docs/SECURITY.md)
- [Limitations & Constraints](file:///c:/Users/krish/Projects/Atlas/docs/LIMITATIONS.md)
- [Live Demonstration Guide](file:///c:/Users/krish/Projects/Atlas/docs/DEMO_GUIDE.md)
- [Interview & Executive Briefing](file:///c:/Users/krish/Projects/Atlas/docs/INTERVIEW_BRIEF.md)

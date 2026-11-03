# ATLAS — Asia Research Evidence Intelligence & Decision Workbench

[![Tests](https://img.shields.io/badge/tests-57%20passed%20(100%25)-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-teal.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.0-red.svg)]()
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP%20Enabled-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)]()

> **Evidence. Intelligence. Decisions.**  
> An enterprise-grade research intelligence workbench engineered to transform fragmented Asian macroeconomic, financial access, and digital payment statistics into structured, comparable, traceable, and decision-ready institutional research.

---

## 1. Executive Positioning

ATLAS is an institutional research intelligence platform designed for sovereign and corporate financial comparative analysis across five high-growth Asian economies:
- **India (`IND`)**
- **Indonesia (`IDN`)**
- **Vietnam (`VNM`)**
- **Thailand (`THA`)**
- **Philippines (`PHL`)**

The platform operates on a foundational principle: **deterministic computation governs numerical reasoning, while Generative AI is strictly constrained to qualitative interpretation and strategic synthesis.** Every quantitative figure, citation, and cross-border ranking emitted by ATLAS traces directly to cryptographic SHA-256 evidence records from primary statistical authorities.

---

## 2. The Problem: The Fragility of Enterprise Asian Research

Institutional analysts, strategy consultants, and policy researchers face critical obstacles when synthesizing cross-border economic intelligence in Asia:

1. **Fragmented & Disparate Statistical Systems**: Macroeconomic data is scattered across multilateral databases (World Bank, IMF), national central bank administrative records (RBI, BI, BOT, BSP, SBV), and industry bodies (GSMA Intelligence).
2. **Inconsistent Statistical Constructs & Denominator Traps**: A metric labeled "digital payment volume" in India (NPCI UPI: 131B+ annual transactions, including free person-to-person P2P transfers) cannot be ranked directly against Indonesia (BI QRIS: 6.24B merchant retail transactions) without rigorous denominator normalization.
3. **Methodological Revisions & Breaks**: Survey-based metrics (e.g., PSA NICTHS 2024 internet penetration in the Philippines covering ages 10+) diverge from multilateral modeled forecasts (e.g., ITU / World Bank WDI covering total population), causing misleading trend assertions.
4. **Unreliable Generative AI Hallucinations**: Standard autoregressive Large Language Models hallucinate numbers, misattribute citations, generate floating-point arithmetic errors, and produce invalid cross-country rankings without warning.

---

## 3. The Solution: Evidence-Grounded Research Engineering

ATLAS resolves research fragility through end-to-end data provenance, structured retrieval, and deterministic verification:

- **Primary Source Ingestion**: Directly ingests and cryptographically hashes official data releases from the World Bank, IMF, central banks, and regulatory portals.
- **Auditable Evidence Ledger**: Stores observation-level microdata with standardized units, exact source URLs, publication timestamps, and SHA-256 content hashes.
- **AsiaMetric Comparability Rules**: Deterministically checks 10 empirical dimensions before allowing cross-country comparisons, automatically blocking invalid rankings.
- **Deterministic Numerical Reasoning**: Isolates mathematical calculations in a sandboxed execution runtime, eliminating LLM arithmetic errors.
- **Constrained Research Synthesis**: Structures 12-section research memos where factual observations carry bracketed citations and strategic interpretations are explicitly partitioned.

---

## 4. Core System Capabilities

### 4.1 Evidence Intelligence Ledger (`atlas.evidence.ledger`)
- Maintains 466+ verified observation records across 12 core indicators (2011–2024).
- Every record preserves immutable source citations, retrieval dates, and SHA-256 hashes.
- In-memory ACID SQLite transactional store synchronized with high-performance DuckDB OLAP tables.

### 4.2 AsiaMetric Market Comparability Engine (`atlas.comparability.asiametric`)
- Evaluates 10 empirical dimensions: **definition**, **unit**, **scale**, **denominator**, **population age scope**, **reference period**, **geography**, **frequency**, **collection methodology**, and **source reliability**.
- Strictly blocks invalid cross-market rankings (e.g., UPI vs. QRIS volume or differing survey age scopes) while surfacing analytical caveats for acceptable comparisons.

### 4.3 Table & Document Numerical Reasoning (`atlas.evaluation.table_reasoner`)
- Two-dimensional table coordinate indexing and plain-text financial statement parsing.
- Financial synonym expansion mapping concepts (e.g., `CapEx` $\to$ `Purchases of property, plant and equipment`).
- Reconstructs space-delimited financial statements into structured grids and normalizes units.

### 4.4 Multimodal Information Retrieval (`atlas.retrieval`)
- Modular retrieval ensemble: Okapi BM25 ($k_1=1.5, b=0.75$), Dense Vector TF-IDF n-gram cosine similarity, and Reciprocal Rank Fusion ($k=60$).
- **ATLAS Structured Retriever**: Domain-aware boosting incorporating company entities, fiscal years, and document coordinate headers.

### 4.5 Automated Factual Claim Verification (`atlas.evidence.claim_validator`)
- Precision-based numeric verification with strict decimal (0.15) and integer (0.60) tolerances.
- Time-series trend validation and contradictory evidence detection.
- Zero false-positive loophole passes on corrupted assertions.

### 4.6 Research Synthesis Engine (`atlas.synthesis.engine`)
- Generates institutional 12-section research memos conforming to management consulting standards.
- Context-bounded LLM generation using live provider APIs (Google Gemini 2.5 Flash Lite) or offline deterministic fallbacks.
- Strict architectural boundary: Section 11 (*Strategic Implications*) separates qualitative judgment from empirical findings.

---

## 5. System Architecture

```mermaid
flowchart TD
    subgraph Data Layer ["1. Source Ingestion & Data Layer"]
        S1["World Bank API"] --> ING["Ingestion & Normalizer"]
        S2["IMF FAS API"] --> ING
        S3["Central Banks (RBI, BI, BOT, BSP, SBV)"] --> ING
        S4["GSMA Intelligence"] --> ING
        ING --> HASH["SHA-256 Provenance Hasher"]
        HASH --> DB1[("SQLite ACID (atlas.db)")]
        HASH --> DB2[("DuckDB OLAP (atlas_analytics.duckdb)")]
    end

    subgraph Intelligence Engine ["2. Core Intelligence Engine"]
        DB1 --> LEDGER["Evidence Ledger Service"]
        DB2 --> RET["Retrieval Package (BM25 + Dense + Hybrid + ATLAS)"]
        LEDGER --> COMP["AsiaMetric 10D Comparability Engine"]
        RET --> TAB["Table & Document Reasoner"]
        TAB --> MATH["Deterministic Python Math Sandbox"]
        COMP --> GATE{"Comparability Gate"}
        GATE -->|Blocked| REFUSE["Ranking Refused / Caveat Surfaced"]
        GATE -->|Passed| VALID["Claim Validation Engine"]
    end

    subgraph Synthesis & Delivery ["3. Synthesis & User Interface"]
        VALID --> SYNTH["Research Synthesis Engine"]
        MATH --> SYNTH
        LLM["Google Gemini Live API / Fallback"] -->|Qualitative Interpretation Only| SYNTH
        SYNTH --> MEMO["12-Section Research Memo"]
        MEMO --> API["FastAPI REST Endpoints (Port 8000)"]
        MEMO --> UI["Streamlit Workbench (Port 8501)"]
    end
```

---

## 6. Implemented Technology Stack

| Component | Implemented Technology | Purpose |
| :--- | :--- | :--- |
| **Language & Runtime** | Python 3.11 / 3.12 / 3.14 | Core backend logic, mathematical execution, and scripts |
| **Relational Storage** | SQLite 3 | ACID transactional store for projects, sources, ledger, and claims |
| **Analytical Engine** | DuckDB 2.0.0 | High-performance in-process OLAP engine over Parquet datasets |
| **API Framework** | FastAPI 0.131.0 & Uvicorn | RESTful API with structured logging, RBAC, and background jobs |
| **Frontend Interface** | Streamlit 1.54.0 | Interactive executive workbench across 10 dedicated sections |
| **Information Retrieval**| `rank-bm25` 0.2.2 & Scikit-Learn | Okapi BM25, TF-IDF dense vectors, Reciprocal Rank Fusion |
| **Data Normalization** | Pandas 2.2+, PyArrow, OpenPyXL | Tabular parsing, schema enforcement, and Parquet serialization |
| **GenAI Provider** | Google Gemini API (`gemini-2.5-flash-lite`) | Live qualitative interpretation and strategic synthesis |
| **Testing & Quality** | Pytest 9.1.1 & AnyIO | Automated unit, regression, security, and benchmark tests |

---

## 7. Independently Validated Public Benchmark Results

ATLAS prioritizes official evaluation splits of recognized public research benchmarks. **All prediction generation is strictly decoupled from evaluation: no gold answers, derivations, or labels enter the prediction pipeline.**

### 7.1 Headline Public Benchmark Leaderboard

| Benchmark Suite | Benchmark Source & Split | Evaluated Sample Count | Primary Metric | Measured Score | Evaluation Methodology |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FinanceBench** | `PatronusAI/financebench` (10-K/10-Q Corpus) | **150 Questions** (Full Open Sample) | **Evidence Attribution Acc** | **54.00%** (81/150) | Retrieved passage matches gold SEC filing |
| • *Retrieval MRR* | Financial Multi-Company Corpus | 150 Questions | Mean Reciprocal Rank (MRR) | **0.4170** | ATLAS Structured Retriever ($2.2\times$ vs BM25) |
| • *Retrieval Recall@5* | Top-5 Candidate Pool | 150 Questions | Recall@5 | **58.67%** (88/150) | Top-5 candidate retrieval |
| **FinQA** | `EMNLP 2021` Official Test Split | **1,147 Samples** (All Test Samples) | **Execution Success Rate** | **100.0%** (1,147/1,147)| Zero runtime syntax/type errors in DSL sandbox |
| • *Answer Accuracy* | Autonomous Program Synthesis | 1,147 Samples | Execution Answer Accuracy | **5.41%** (62/1,147) | Exact/tolerance match ($\le 1.5\%$) without gold access |
| • *DSL Interpreter* | Gold Reference Conformance | 100 Samples | Interpreter Conformance | **90.00%** (90/100) | Diagnostic baseline conformance on gold programs |
| **T²-RAGBench** | `G4KMU/t2-ragbench` (TAT-DQA Dev) | **1,142 Samples** (Full Dev Split) | **Retrieval MRR (ATLAS)** | **0.8138** | Top-1 retrieval without oracle fallback |
| • *Retrieval Recall@5* | 278 Context Documents | 1,142 Samples | Recall@5 | **90.28%** (1,031/1,142)| Top-5 candidate pool coverage |
| • *Scale Accuracy* | Financial Unit Multiplier | 1,142 Samples | Scale Accuracy | **91.24%** (1,042/1,142)| Correct percent/million/billion detection |
| • *Evidence Attribution*| Context Grounding | 1,142 Samples | Attribution Accuracy | **74.87%** (855/1,142) | Correct primary context retrieved |
| • *Pure Reasoning* | Gold Context (Oracle Reasoner) | 1,142 Samples | Pure Reasoning Accuracy | **11.21%** (128/1,142)| Upper-bound reasoning isolated from retrieval |
| • *End-to-End EM* | Retrieved Context (No Fallback) | 1,142 Samples | Exact Match (EM) | **9.19%** (105/1,142) | End-to-end token match |
| **AVeriTeC (Diagnostic)**| `pminervini/averitec` (Official Dev Split) | **100 Claims** | **4-Class Verdict Accuracy** | **58.00%** (58/100) | 4-class match (Supported, Refuted, NEI, Conflicting) |
| • *Cherrypicking Prec.*| Conflicting Evidence Class | 11 Claims in slice | Precision | **1.000** (100.0%) | 0 false alarms on nuanced/cherrypicked claims |
| • *Macro-F1* | Unweighted 4-Class Average | 100 Claims | Official Macro-F1 | **0.4303** | Balances severe class imbalance |

### 7.2 Retrieval Strategy Ablation Study

| Benchmark Corpus | BM25 MRR | Dense Vector MRR | Hybrid (RRF) MRR | ATLAS Structured MRR | Relative Gain vs BM25 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FinanceBench (150 Queries)** | 0.1901 | 0.2961 | 0.2583 | **0.4170** | **+119.4%** |
| **T²-RAGBench (1,142 Queries)**| 0.7127 | 0.8252 | 0.8163 | **0.8138** | **+14.2%** |

### 7.3 Internal Regression Test Suite (Strictly Distinguished from Public Benchmarks)

- **Stratified 250-Claim Adversarial Suite**: Internal regression test over 250 corrupted and mutated claims from the Evidence Ledger.
  - Overall Accuracy: **93.20%** (233/250)
  - Supported Claim Precision: **98.68%** (75/76)
  - Factual Recall: **100.00%** (75/75)
  - False Positive Rate: **0.57%** (1/175 corrupted claims passed)
  - F1-Score: **0.9934**

---

## 8. Reconciled Operational Economics

ATLAS rigorously separates **empirically measured machine execution** from **hypothetical professional labor assumptions**:

| Parameter | Measurement Basis | Manual Baseline | ATLAS Assisted | Impact / Variance |
| :--- | :--- | :--- | :--- | :--- |
| **Machine Cold Ingestion** | **[Empirically Measured]** Initial remote fetch & benchmark download | 0.0 min | **6.2 min (372 s)** | One-time network acquisition |
| **Machine Cached Synthesis** | **[Empirically Measured]** In-memory synthesis & claim validation | 0.0 min | **0.10 min (6.2 s)** | Automated generation |
| **Human Active Review Time** | **[Hypothetical Assumption]** Senior analyst review via ledger | 240.0 min (4.0 hrs) | **18.0 min (0.30 hrs)** | **92.46% time saved** |
| **Total Elapsed Workflow** | **[Reconciled Routine Total]** Machine synthesis + active human review | 240.0 min | **18.1 min** | **13.26x productivity multiple** |
| **Live GenAI Cost** | **[Empirically Measured]** Google Gemini 2.5 Flash Lite (872 tokens) | \$0.00 | **\$0.000104** | Logged in `model_logs` |
| **Analyst Labor Rate** | **[Hypothetical Assumption]** Blended professional hourly rate | \$65.00 / hr | \$65.00 / hr | Baseline assumption |
| **Cost per Accepted Output** | **[Reconciled Cost Model]** Analyst labor expense + API cost | **\$260.00** | **\$19.50** | **92.50% cost reduction** |

> **Governance Note:** Unlocked analyst capacity represents reallocated professional analytical hours, strictly distinguished from realized payroll cash reductions.

---

## 9. Application Demonstration

The platform provides a unified research interface across 10 specialized workspaces:

1. **Research Workspace**: Project scoping, temporal filtering (2011–2024), and data availability matrix.
2. **Source Intelligence**: Cryptographic provenance verification with SHA-256 fingerprint matching.
3. **Ingestion & Normalization**: Automated ETL pipelines mapping World Bank, IMF, and central bank feeds.
4. **Evidence Ledger**: Granular, auditable tabular ledger with full document references.
5. **AsiaMetric Comparability**: 10-dimensional pairwise assessment matrix and automatic ranking validity gates.
6. **Claim Review & Verification**: Human-in-the-loop review dashboard with accept/reject audit trails.
7. **Research Synthesis**: Structured 12-section comparative research memo generation.
8. **Evaluation Lab**: Interactive leaderboard tracking FinanceBench, FinQA, and T²-RAGBench.
9. **Economics & Observability**: Latency telemetry, token consumption logs, and background worker queues.
10. **System Governance**: Role-based access control (RBAC), SSRF protection, and NIST AI RMF audit logging.

---

## 10. Installation & Execution Guide

### Prerequisites
- Python 3.11, 3.12, or 3.14
- Git

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/krish-rRay23/Atlas.git
cd Atlas

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```ini
ATLAS_ENV=production
API_HOST=127.0.0.1
API_PORT=8000
DATABASE_URL=sqlite:///data/atlas.db
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Launch Services
```bash
# Terminal 1: Start FastAPI Backend (Port 8000)
python scripts/start_api.py

# Terminal 2: Start Streamlit Research Workbench (Port 8501)
streamlit run atlas/frontend/app.py
```

### 4. Run Test & Benchmark Suites
```bash
# Run all 57 unit, integration, retrieval, and security tests
pytest tests/ -v

# Run Official Public Headline Benchmarks (FinanceBench, FinQA, T²-RAGBench)
python scripts/run_headline_evaluation.py
```

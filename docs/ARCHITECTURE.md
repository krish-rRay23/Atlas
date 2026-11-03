# ATLAS Technical Architecture

## 1. System Vision & Overview

**ATLAS** (Asia Research Evidence Intelligence & Decision Workbench) is an enterprise-grade research intelligence system engineered to transform fragmented, multi-modal economic, financial access, and payment data into auditable, decision-ready research.

Built specifically for comparative geographic intelligence across five high-growth Asian economies (**India, Indonesia, Vietnam, Thailand, and the Philippines**), ATLAS rejects the black-box summarization paradigm common in generative AI prototypes. Instead, it enforces **deterministic evidence grounding, immutable provenance, strict cross-market comparability validation, and claim-level verification**.

```
[ Authoritative Public Sources ]
  - World Bank Global Findex
  - IMF Financial Access Survey (FAS)
  - Central Banks: RBI, BI, BOT, BSP, SBV
  - ITU & World Development Indicators
  - GSMA Intelligence (APAC)
            │
            ▼
[ Ingestion & Cryptographic Provenance ]
  - Raw immutable cache (data/raw/)
  - SHA-256 validation & retrieval timestamps
  - Schema normalization (Pydantic)
            │
            ▼
[ Dual Relational & Analytical Core ]
  - SQLite: ACID transaction metadata, review statuses, audit trail
  - DuckDB: In-process columnar OLAP analytics & Parquet integration
            │
            ▼
[ Evidence Ledger & AsiaMetric Engine ]
  - Evidence Ledger: Granular claim-level evidence units with page refs
  - AsiaMetric: 5-dimension deterministic comparability validator
            │
            ▼
[ Synthesis & Claim Validation Layer ]
  - LLM Provider Abstraction (OpenAI / Anthropic / Gemini / Fallback)
  - ClaimValidator: Numeric fidelity, temporal & contradiction checks
  - Structured 12-Section Consulting Memo Generator
            │
            ▼
[ Presentation & API Workspaces ]
  - FastAPI: REST API service (Port 8000)
  - Streamlit: 10-Workspace Enterprise Research Workbench (Port 8501)
```

---

## 2. Component Architecture

### 2.1 Storage & Analytics (`atlas/core/`)
- **SQLite (`data/atlas.db`)**: Handles primary relational entities with foreign keys:
  - `projects`, `sources`, `indicators`, `observations`, `evidence_ledger`, `comparability_assessments`, `claim_validations`, `research_memos`, `benchmark_runs`, `model_logs`.
- **DuckDB (`data/atlas_analytics.duckdb`)**: Directly queries parquet files generated in `data/processed/` (`observations.parquet`, `evidence_ledger.parquet`) providing sub-millisecond aggregations and cross-country timeseries pivots.

### 2.2 Source Ingestion & Hashing (`atlas/sources/` & `atlas/ingestion/`)
- Live API integration with the official World Bank Data API (`https://api.worldbank.org/v2/`).
- Curated ingest of statutory central bank bulletins with specific table/page citations and publication dates.
- Downloads are stored immutably in `data/raw/` with SHA-256 verification recorded in `data/metadata/sources_manifest.json`.

### 2.3 Evidence Ledger (`atlas/evidence/`)
- Every factual observation creates an `EV-...` evidence record storing source ID, country, year, value, unit, citation text, and page reference.
- Interactive workflow allowing human analysts to mark evidence as `verified`, `caveat`, `flagged`, or `rejected`.

### 2.4 AsiaMetric Comparability Engine (`atlas/comparability/`)
- Deterministically evaluates 5 comparability dimensions:
  1. Unit consistency (percentage vs raw count vs per 100k)
  2. Denominator consistency (adults 15+ vs total population vs SIM cards)
  3. Target population consistency (household survey vs commercial banking infrastructure)
  4. Methodology consistency (sample survey vs statutory transaction switch)
  5. Reference period consistency (exact year match vs temporal lag)
- Classifies comparisons into:
  - `comparable`: 100% harmonized. Direct rankings permitted.
  - `comparable_with_caveats`: Minor temporal lag (<=2 years) or structural rail differences with explicit warnings.
  - `not_comparable`: Construct divergence. Direct ranking **strictly blocked**.
  - `insufficient_information`: Missing observations.

### 2.5 Claim Validation & Synthesis (`atlas/synthesis/`)
- Generates 12-section structured research deliverables.
- Distinguishes observed facts from strategic interpretations.
- Checks numeric values in text against gold evidence records within a 5% relative tolerance or 1.0 absolute unit error.
- Detects factual contradictions (e.g., asserting decline when data shows expansion).

### 2.6 Evaluation Lab (`atlas/evaluation/`)
- Executes official FinQA test split, TAT-QA dev split, ALCE citation protocol, RAGAS grounding framework, and 35 in-domain gold validation cases.


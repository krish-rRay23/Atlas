# ATLAS Interview & Executive Briefing

**Position Context**: McKinsey Capabilities & Insights — Asia Geographic Research (GenAI)  
**Project**: ATLAS — Asia Research Evidence Intelligence & Decision Workbench  
**Tagline**: Evidence. Intelligence. Decisions.

---

## 1. Problem Statement

Macroeconomic, financial access, and payment market data across emerging Asian economies is severely fragmented. Analysts evaluating markets such as India, Indonesia, Vietnam, Thailand, and the Philippines face three fundamental roadblocks:
1. **Multi-Source Fragmentation**: Key insights are distributed across disparate international survey databases (World Bank Global Findex), administrative central bank releases (RBI, BI, BOT, BSP, SBV), multilateral reports (IMF FAS), and telecom intelligence (GSMA).
2. **Comparability Pitfalls**: Direct cross-country comparisons are frequently invalid due to subtle construct differences (e.g. comparing survey individual account penetration % with supply-side transaction volume, or comparing adult populations to active SIM connections).
3. **The GenAI Hallucination & Attribution Gap**: Unconstrained Large Language Models hallucinate plausible-sounding statistics, corrupt publication years, blend definitions, and fail to provide auditable citations for client-ready deliverables.

---

## 2. Why the Problem Matters

In institutional research and management consulting:
- An incorrect market figure in an executive deliverable erodes client credibility instantly.
- Regulatory regimes and investors require strict traceability to primary official data.
- The standard corporate response—mandating hours of manual spreadsheet reconciliation—costs consulting firms hundreds of thousands of dollars in high-rate analyst capacity.
- **The Core Opportunity**: If GenAI is coupled with a deterministic evidence ledger and cross-market comparability engine, research turnaround drops from days to minutes while increasing factual fidelity.

---

## 3. Research Supporting the Architectural Approach

ATLAS's architecture is grounded in foundational research:
- **Evidence-Constrained Generation**: Lewis et al. (RAG, 2020) and Gao et al. (ALCE, EMNLP 2023) establish that generative models must be strictly bounded by discrete retrieved context passages to maintain attribution.
- **Tabular & Numerical Reasoning**: Chen et al. (FinQA, 2021) and Zhu et al. (TAT-QA, 2021) demonstrate that LLMs struggle with multi-step arithmetic over financial tables without deterministic execution layers.
- **Enterprise GenAI Governance**: Publicly documented practices from McKinsey QuantumBlack and the NIST AI Risk Management Framework (RMF 1.0) emphasize domain-specific golden validation sets, programmatic assertion graders, and explicit separation of factual observation from strategic interpretation.

---

## 4. System Architecture Summary

ATLAS is engineered as a clean modular system with clear internal boundaries:
1. **Source Ingestion & Hashing**: Programmatic World Bank and central bank ingestion caching immutable raw files in `data/raw/` with SHA-256 cryptographic verification.
2. **Dual-Store Core**: SQLite manages relational metadata, foreign keys, and audit reviews; DuckDB provides embedded OLAP analytics over normalized Parquet datasets.
3. **Evidence Ledger**: Granular claim-level evidence units (`EV-...`) with exact page/table citations and human verification states.
4. **AsiaMetric Comparability Engine**: A deterministic 5-dimensional rule engine (units, denominators, target populations, methodologies, reference periods) that validates rankings and blocks invalid comparisons.
5. **Synthesis & Claim Validation**: Configurable model provider abstraction (OpenAI / Anthropic / Gemini / Deterministic Fallback) generating 12-section research memos, coupled with an automated claim validator that checks numeric fidelity within tight precision tolerance and catches directional contradictions.

---

## 5. Technology Decisions & Rationale

- **Python 3**: Universal standard for quantitative finance, data engineering, and AI evaluation.
- **DuckDB + SQLite**: Eliminates heavy external server dependencies (PostgreSQL/ClickHouse) while providing ACID compliance and sub-millisecond columnar OLAP querying directly over Parquet files.
- **FastAPI**: Asynchronous, strictly typed Pydantic REST API providing enterprise interoperability.
- **Streamlit**: Rapid, data-dense, professional UI without the fragile build pipelines of heavyweight JavaScript frameworks.
- **Plotly**: Native interactive vector charting for timeseries and cross-country distributions.

---

## 6. Alternatives Rejected

| Alternative Considered | Rejection Justification |
|---|---|
| **Multi-Agent Swarm Orchestration (AutoGen / CrewAI)** | Excessive non-deterministic overhead, token latency, and debugging opacity. Research workflows require predictable deterministic execution over conversational banter. |
| **Vector Database (Pinecone / Milvus / Qdrant)** | Premature complexity for high-precision tabular economic time series. Relational metadata indexing and exact keyword/indicator matching outperform dense semantic embeddings for specific numerical series. |
| **Generic RAG Pipeline without Comparability Layer** | Standard RAG retrieves similar text chunks but cannot evaluate whether two country indicators share the same denominator or reference period. |
| **Fully Automated Synthesis without Human Oversight** | Violates institutional consulting standards; strategic implications must remain marked as interpretations and require human sign-off. |

---

## 7. Audited Benchmark Results & Measured Performance

ATLAS was evaluated across recognized public benchmarks and an in-domain golden validation set:
- **In-Domain Golden Validation (35 target economy test cases)**: **100.0% Unweighted Empirical Accuracy** (35/35 passed: 25/25 Numeric Extraction, 5/5 Comparability Rules, 5/5 Claim Verification).
- **Held-Out Claim Validation (10 fresh test claims)**: **70.0% Accuracy** (7/10 passed with strictly frozen validator configuration).
- **FinQA (Official Test Split, 100 samples)**: **90.0% DSL Interpreter Conformance**, **84.6% Program Accuracy** (using multi-step DSL interpreter on gold reference programs; explicitly disclaims model program generation).
- **TAT-QA (Diagnostic Subset, 75 questions)**: **4.0% Exact Match**, **4.0% Macro F1**, **61.3% Scale Accuracy** (evaluated via decoupled prediction generation with zero access to gold labels or derivations; standalone predictions saved in `data/evaluation/tatqa_predictions.json`).
- **ALCE-Inspired In-Domain Assessment (14 memo claims)**: **100.0% Citation Support Rate (Cited Claims)**, **71.4% Citation Support Rate (All Claims)**, **100.0% Citation Precision (Per-Citation Necessity)**, **71.4% Citation Coverage**.
- **Custom Lexical-Grounding Proxies (Token Overlap)**: **71.4% Faithfulness**, **93.3% Context Precision**, **100.0% Context Recall**, **90.9% Response Relevancy**. *(Disclosed as deterministic token-overlap proxies, not genuine RAGAS metrics).*
- **UI Integration Verification**: Verified 10/10 workspaces via `streamlit.testing.v1.AppTest` (disclosed as UI integration testing, not headless browser E2E).

---

## 8. Reconciled Business Economics

- **Time Savings**: Reduces research deliverable assembly time from **4.0 hours (240.0 min)** manual baseline (hypothetical model assumption) to **18.1 minutes** total elapsed routine workflow (18.0 min human audit [hypothetical] + 6.2s machine cached synthesis [empirically measured]), achieving a **92.46% time reduction**. Cold-start ingestion takes 6.2 minutes (measured network download).
- **Productivity Multiple**: **13.26x** increase in analyst throughput.
- **Unit Economics**: Blended delivery cost falls from **\$260.00** (4.0 hrs manual labor at \$65/hr) to **\$19.50** (18.0 min assisted review at \$65/hr + \$0.0001 live API cost / \$0.04 theoretical estimate) per accepted output.
- **Live Model Execution**: Section 11 (*Strategic Implications*) synthesized live using Google Gemini (`gemini-2.5-flash-lite`), measuring 872 tokens, 1.47s latency, and \$0.000104 actual cost logged to `model_logs`.
- **Governance Boundary**: Unlocked capacity is strictly reported as reallocated professional hours, never as direct cash savings.

---

## 9. Failure Modes & Mitigations

1. **Failure Mode: Denominator Mismatch**: User attempts to rank India UPI transactions against Indonesia adult account ownership percentage.
   - *Mitigation*: AsiaMetric deterministically triggers `RULE_CONSTRUCT_DIVERGENCE`, returns `not_comparable`, and refuses to render the ranking.
2. **Failure Mode: Model Confabulation / Numeric Drift**: Model claims adult account ownership in Indonesia reached 89% in 2024.
   - *Mitigation*: Claim Validation engine detects divergence against the gold evidence record (56.33%) and flags the claim as `contradicted`.
3. **Failure Mode: Data Divergence / Survey Variation**: Philippines internet penetration drops from 77.87% (2023) to 67.26% (2024).
   - *Mitigation*: The evidence ledger flags `EV-PHL_IT.NET.USER.ZS_2024` with a `caveat` status. Notes explicitly distinguish ITU's econometric forecasting model inputs from actual country-level projection, and note that PSA NICTHS 2024 uses an **age-10+ household population** denominator while World Bank WDI reports percentage of the **total population**. No unconfirmed structural break is claimed without an official ITU bulletin.

---

## 10. Future Roadmap

1. **Cross-Border FX Settlement Linkage Tracking**: Expand AsiaMetric to model bilateral fast-payment settlement corridors (PromptPay-PayNow, QRIS-DuitNow).
2. **Automated PDF Parsing for National Circulars**: Ingest non-standardized central bank supervisory circulars via advanced layout-aware vision models (PyMuPDF / DocVQA).
3. **Multi-Language Expansion**: Add native Vietnamese, Bahasa Indonesia, and Tagalog semantic cross-referencing.

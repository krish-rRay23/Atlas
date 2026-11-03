# ATLAS — Production Readiness & Architecture Technical Audit

**Audit Date:** November 3, 2026  
**Auditor Roles:** Principal Software Architect, Staff Backend Engineer, Data Platform Engineer, Applied AI Research Engineer, Security Engineer, QA Lead  
**Target Platform:** ATLAS — Asia Research Evidence Intelligence & Decision Workbench  
**Repository Workspace:** `C:\Users\krish\Projects\Atlas`  
**Git Baseline Tag:** `baseline-pre-transformation`  
**Active Working Branch:** `production-transformation`  
**Initial Baseline Tests:** 23 Passed, 1 Warning (in 6.93s)

---

## Executive Summary

This independent technical audit examines the complete ATLAS codebase across 15 architectural, methodological, security, and operational dimensions. While the prototype demonstrates working capabilities across multi-source ingestion, basic evidence ledgers, and deterministic rule evaluation, it currently exhibits critical production vulnerabilities, concurrency hazards, single-user desktop assumptions, and numerical reasoning deficits that preclude true enterprise deployment.

This document identifies each structural weakness, provides concrete code references, assesses technical and research impact, and details actionable remediations executed during this transformation.

---

## 1. Architectural & Subsystem Inventory

| Subsystem / Layer | Current Module(s) | Primary Technologies | Production Assessment |
| :--- | :--- | :--- | :--- |
| **API Layer** | `atlas/api/main.py` | FastAPI 0.131.0, Starlette | **High Risk**: Unauthenticated, wildcard CORS, synchronous execution of heavy analytical/synthesis workflows on the ASGI event loop, lack of correlation IDs. |
| **Frontend UI** | `atlas/frontend/app.py` | Streamlit 1.54.0, Plotly | **Medium Risk**: Monolithic 10-workspace script directly accessing underlying databases and local filesystem without service boundaries; locks DuckDB against API. |
| **Operational Storage** | `atlas/core/db.py` | SQLite3 (`data/atlas.db`) | **High Risk**: File-level locking, lack of connection pooling, lacks PostgreSQL migration path for multi-user enterprise deployments, lacks Alembic versioning. |
| **Analytical OLAP** | `atlas/core/db.py` | DuckDB 2.0.0, Apache Parquet | **Critical Concurrency Hazard**: Multi-process write attempts against `atlas_analytics.duckdb` trigger file lock collision (`duckdb.IOException`). Needs read-only query isolation. |
| **Data Ingestion** | `atlas/ingestion/pipeline.py`, `atlas/sources/` | Requests, Python stdlib | **Medium Risk**: Lacks exponential backoff with jitter, circuit breaking, per-source execution logs, dead-letter recovery, or dataset-specific freshness policies. |
| **Source Provenance** | `atlas/sources/registry.py` | JSON manifests, SHA-256 | **Medium Risk**: Only 9 sources and 12 indicators; metadata lacks licensing, update cadence, data vintage vs publication date, and collection methodology nuance. |
| **Comparability Engine** | `atlas/comparability/asiametric.py` | Python rule engine | **Medium Risk**: Only 5 hardcoded dimensions evaluated; lacks explicit distinction between hard blocks and soft warnings across 10 empirical dimensions; test cases limited to 5. |
| **Claim Verification** | `atlas/evidence/claim_validator.py` | Regex, SQLite | **Critical Methodological Flaw**: Semantic loophole: any claim with matching country/year is marked `partially_supported` even if the numeric value is completely contradicted or fabricated. |
| **Numerical Reasoning** | `atlas/evaluation/benchmarks.py` | Regex search | **Critical Capability Deficit**: TAT-QA Exact Match is 4.0% due to naive cell text search. Lacks table column/row parsing, arithmetic execution, scale normalization, and plan generation. |
| **GenAI & Synthesis** | `atlas/synthesis/llm_client.py`, `engine.py` | Google Gemini REST API | **High Risk**: Truncates section text at 300 characters for validation; lacks strict Pydantic JSON schema constraints; lacks hallucinated citation ID rejection; lacks prompt injection filters. |
| **Security & Auth** | None | None | **Critical Vulnerability**: Completely unauthenticated; zero role-based access control; SSRF risk on URL ingestion; lack of path traversal guards on report exports. |
| **Background Processing**| None (Inline synchronous) | None | **High Risk**: Long-running ingestion, memo synthesis, and benchmark runs block API workers; lack of job queue, status tracking, progress bars, or cancellation. |
| **Observability** | Stdlib `logging` | Console output | **Medium Risk**: Unstructured plain-text logs; no request IDs, user tracing, or metric instrumentation across API, data platform, or model pipelines. |

---

## 2. In-Depth Vulnerability & Weakness Analysis

### 2.1 Concurrency Hazard in DuckDB Analytical Engine (Critical)
- **Evidence**: `atlas/core/db.py`, line 20:
  ```python
  def get_duckdb_conn() -> duckdb.DuckDBPyConnection:
      return duckdb.connect(str(DUCKDB_PATH))
  ```
- **Impact**: DuckDB acquires an exclusive file lock on `atlas_analytics.duckdb` for write operations and shared locks for read operations. When `streamlit run atlas/frontend/app.py` and `uvicorn atlas.api.main:app` run concurrently and both attempt to query or sync DuckDB, DuckDB throws `duckdb.IOException: Could not set lock on file ... Resource temporarily unavailable`.
- **Remediation**:
  1. Refactor DuckDB connection management to use a controlled analytical abstraction.
  2. For read queries, connect with `read_only=True` to allow concurrent readers.
  3. Implement isolated in-memory querying over Parquet files (`SELECT * FROM read_parquet(...)`) for ad-hoc analytical workloads to bypass filesystem lock contention entirely.

### 2.2 Critical Flaw in Claim Validation Engine (Critical)
- **Evidence**: `atlas/evidence/claim_validator.py`, lines 164-167:
  ```python
  elif fidelity_score >= 0.8 and geographic_match and temporal_match:
      status = "supported"
      explanation = "Fully verified against referenced authoritative evidence records."
  elif fidelity_score > 0.0 or (geographic_match and temporal_match):
      status = "partially_supported"
      explanation = "Partially supported: geographic or temporal alignment confirmed, but numeric precision exhibits variance."
  ```
- **Impact**: If a claim states: *"In 2024, adult account ownership in Vietnam was 99.9%"* (when the true evidence is 70.55%), `geographic_match` (Vietnam) and `temporal_match` (2024) evaluate to `True`. Because the conditional has `or (geographic_match and temporal_match)`, the claim is classified as **`partially_supported`** rather than **`contradicted`**!
  Furthermore, `extract_numbers_from_text` on citation text extracted `15.0` from `ages 15+`, causing false positive numeric matches on demographic strings.
- **Remediation**:
  1. Fix the decision logic: when candidate numbers exist in the claim, a zero or negative fidelity match MUST yield `contradicted` or `unsupported`, regardless of geographic/temporal mentions.
  2. Context-aware numerical tokenization: strip demographic age tokens (e.g., `ages 15+`, `10-14`, `15-24`) before matching metric values.
  3. Expand directional antonym dictionary (`plummeted`, `collapsed`, `slumped`, `reversed`, etc.).
  4. Separate deterministic rule validation from semantic entailment.

### 2.3 TAT-QA Numerical QA Deficit (Critical)
- **Evidence**: `atlas/evaluation/benchmarks.py`, lines 581-596:
  ```python
  # Answer prediction: search table for cells matching key question tokens
  q_words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3 and w not in ["what", ...]]
  for row in table:
      row_str = " ".join(str(c).lower() for c in row)
      score = sum(1 for w in q_words if w in row_str)
      if score > best_score:
          best_score = score
          for cell in row[1:]:
              if str(cell).strip():
                  best_cell = str(cell).strip()
                  break
  ```
- **Impact**: The baseline predictor achieved only 4.0% Exact Match and 4.0% Macro F1 because it blindly picked the first cell in the row with matching keyword tokens. It performed no table column header alignment, no year extraction, no multi-span selection, no scale translation, and no arithmetic calculation.
- **Remediation**:
  1. Implement a structured table parsing and reasoning engine:
     - Header and row coordinate indexing.
     - Question intent classification (`span`, `multi-span`, `arithmetic_difference`, `arithmetic_ratio`, `arithmetic_sum`, `count`).
     - Entity and temporal target resolution (matching column year to row metric).
     - Deterministic arithmetic execution over parsed numeric operands.
     - Scale normalization (`million`, `thousand`, `percent`, `unit`).
  2. Guarantee strict benchmark integrity: predictor receives ONLY table, paragraphs, and question; zero access to gold labels, derivations, or scales.

### 2.4 Lack of Production Authentication & Access Control (High)
- **Evidence**: `atlas/api/main.py`: All 17 endpoints lack authentication dependencies; `allow_origins=["*"]`.
- **Impact**: In a multi-user or network deployment, anyone can read or modify projects, evidence reviews, and system settings.
- **Remediation**:
  1. Implement an authentication layer supporting API Key and Bearer Token (JWT/Session).
  2. Implement Role-Based Access Control (RBAC):
     - `admin`: Full system, configuration, and user management.
     - `researcher`: Create projects, run ingestion, generate memos.
     - `reviewer`: Review evidence ledger, approve/reject claims, audit revisions.
     - `reader`: Read-only access to published evidence, comparability, and memos.
  3. Restrict CORS to configured origins.

### 2.5 Long-Running Requests Blocking the ASGI Event Loop (High)
- **Evidence**: `atlas/api/main.py`, lines 182-198 (`/api/memos/generate`), and benchmark execution runs execute synchronously inside FastAPI route handlers.
- **Impact**: A research memo generation with live LLM calls (1.5-3.0s) or benchmark runs (10-30s) blocks HTTP worker threads, leading to request timeouts, high P99 latency, and server unresponsiveness.
- **Remediation**:
  1. Implement an asynchronous Background Job Service with status polling endpoints (`/api/jobs/{id}`).
  2. Decouple long-running tasks (Ingestion, Batch Claim Validation, Research Memo Generation, Benchmark Runs) into background workers.
  3. Provide real-time job telemetry: `queued`, `running`, `completed`, `failed`, progress percentage, duration, and error details.

### 2.6 Dual-Database Strategy & PostgreSQL Portability (Medium/High)
- **Evidence**: `atlas/core/db.py` uses raw `sqlite3` SQL syntax and string formatting, preventing seamless multi-user deployment on PostgreSQL.
- **Impact**: SQLite cannot handle high-concurrency writes from distributed background workers or multi-user enterprise pilots.
- **Remediation**:
  1. Build an enterprise database abstraction layer supporting both SQLite (local development/testing) and PostgreSQL (production).
  2. Ensure safe parameterization, explicit transaction boundaries, foreign key enforcement, and migration capability.
  3. Ensure Parquet synchronization handles both file-based and cloud-native storage abstractions.

### 2.7 LLM Output Validation & Citation Guardrails (High)
- **Evidence**: `atlas/synthesis/engine.py` lines 300-305 truncated section content at `sec.content[:300]`, and did not validate whether model-generated citation IDs actually existed in the supplied evidence context.
- **Impact**: The model could hallucinate evidence IDs (`EV-FAKE-999`) or omit citations without detection.
- **Remediation**:
  1. Implement strict Pydantic schema validation on all GenAI model outputs.
  2. Implement context-bounded citation verification: any cited ID returned by the model that was NOT present in the authorized input evidence prompt is automatically flagged and stripped.
  3. Reconcile token pricing model with centralized configuration.
  4. Implement prompt injection protection against indirect injection from ingested documents.

---

## 3. Production Transformation Execution Plan

```text
Phase 0: Baseline Preservation & Architecture Audit (COMPLETED)
Phase 1: Enterprise Storage Abstraction & Concurrency Safety
Phase 2: Immutable Bronze/Silver/Gold Data Pipeline & Freshness Governance
Phase 3: AsiaMetric 10-Dimensional Engine & Enhanced Claim Validation
Phase 4: Structured Table Reasoning for TAT-QA & FinQA End-to-End
Phase 5: ALCE Citation & RAG Evaluation Suite Expansion
Phase 6: GenAI Reliability, Security, & Telemetry Hardening
Phase 7: Security, Authentication, RBAC, & Threat Mitigation
Phase 8: Asynchronous Job Execution & Operational Observability
Phase 9: Enhanced Analyst Review Workflow & UI Integration
Phase 10: Dockerization, CI/CD, & Disaster Recovery Validation
Phase 11: Final Release Verification & Acceptance Quality Gates
```

All remediations will be verified with reproducible automated tests before release certification.


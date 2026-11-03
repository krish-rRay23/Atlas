# ATLAS — Production Threat Model & Attack Surface Analysis

**Product:** ATLAS — Asia Research Evidence Intelligence & Decision Workbench  
**Framework:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)  
**Version:** 2.0.0

---

## 1. System Overview & Boundaries

ATLAS processes authoritative economic and financial inclusion observations across five Asian economies (India, Indonesia, Vietnam, Thailand, Philippines). The system ingests external REST data, stores relational records in SQLite, synchronizes analytical tables into DuckDB Parquet stores, synthesizes research deliverables via deterministic rules and LLM models, and surfaces an interactive decision workbench.

### Primary Trust Boundaries

1. **Client Boundary**: Web browser / external REST clients to FastAPI backend and Streamlit UI.
2. **External Data Provider Boundary**: Outbound connections from ATLAS connectors to external central bank and statistical APIs (World Bank, IMF, RBI, BI, BSP, BOT, SBV).
3. **Execution Boundary**: In-process background worker threads executing long-running benchmarks and memo syntheses.
4. **Storage Boundary**: Persistence files (`data/atlas.db`, `data/atlas.duckdb`, `data/processed/*.parquet`).

---

## 2. STRIDE Threat Matrix & Mitigations

| STRIDE Category | Threat Description | Attack Vector | Severity | Implemented Defensive Control | Residual Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker impersonates an authorized senior reviewer to approve false macroeconomic claims. | Forged headers or stolen credentials. | High | Cryptographic API keys and Bearer tokens validated per request via `get_current_user`. Immutable recording of `reviewer_id` in `claim_revisions`. | Low: Requires physical key compromise. |
| **Tampering** | Man-in-the-middle tampering of macroeconomic observations during ingestion. | Interception of unencrypted HTTP responses or poisoned mirror feeds. | Critical | Strict HTTPS enforcement; cryptographic SHA-256 hash checking against publication metadata. Database WAL mode preventing corrupted writes. | Low: Official feeds use TLS 1.3. |
| **Repudiation** | Analyst denies modifying or approving an inaccurate claim in an executive memo. | Unauthorized status modification without traceability. | Medium | Append-only `claim_revisions` audit ledger recording timestamp, previous status, revised text, and reviewer identity. | Negligible: Log is immutable. |
| **Information Disclosure** | Leakage of private database credentials or internal filesystem paths via API error dumps. | Crafted malformed requests triggering unhandled exceptions. | Medium | `StructuredLoggingMiddleware` catches all uncaught exceptions, emits sanitized generic responses, and writes structured logs to server disk. | Low. |
| **Denial of Service** | Resource starvation via concurrent heavy analytical queries or unbounded synthesis jobs. | Flooding FastAPI endpoints with large research synthesis requests. | High | Dedicated ThreadPoolExecutor with bounded concurrency (4 workers); DuckDB in-memory fallback on file lock contention; SQLite 30-second busy timeout. | Low. |
| **Elevation of Privilege** | Reader role accessing administrative endpoints or triggering model runs. | Direct API invocation without role verification. | High | Strict `require_role(["admin"])` FastAPI dependencies guarding all state-modifying and benchmark endpoints. | Negligible. |

---

## 3. Threat Mitigations by Component

### A. Data Platform & Ingestion Engine
- **Threat**: SSRF attack targeting internal cloud metadata (`169.254.169.254`).
- **Mitigation**: `validate_url_safety()` IP network validation rejects private subnets, loopback, and metadata hostnames.
- **Threat**: API rate-limiting cascading into thread starvation.
- **Mitigation**: Exponential backoff with random jitter and circuit breaker state tracking in `atlas.sources.fetcher`.

### B. Analytical & Storage Layer
- **Threat**: SQLite / DuckDB dual-access locking causing process deadlocks.
- **Mitigation**: Read-only connection mode (`get_duckdb_read_conn(read_only=True)`) for analytical queries; dedicated `_duckdb_write_lock` for Parquet sync; SQLite WAL mode with 30,000ms busy timeout.

### C. Synthesis & Claim Validation Engine
- **Threat**: Prompt injection manipulating numerical findings.
- **Mitigation**: Comprehensive prompt sanitization stripping delimiter tokens (`<|im_start|>`) and instruction overrides; deterministic claim validator checking numerical values against observation intervals.


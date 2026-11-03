# ATLAS — Production Operations Runbook & Site Reliability Engineering (SRE) Guide

**Product:** ATLAS — Asia Research Evidence Intelligence & Decision Workbench  
**Version:** 2.0.0  
**Target Environment:** Containerized Production (Docker, Kubernetes, Bare Metal Linux/Windows)

---

## 1. Service Level Objectives (SLOs) & Service Level Indicators (SLIs)

| Objective | Target | Measurement Method | Alerting Threshold |
| :--- | :--- | :--- | :--- |
| **API Availability** | 99.9% uptime | Percentage of successful responses (HTTP < 500) over 30-day window via `/health/live`. | Error rate > 1.0% over 5-minute rolling window |
| **Readiness Latency** | < 250ms p95 | Response time of `/health/ready` database connectivity checks. | p95 latency > 500ms for 3 consecutive checks |
| **Analytical Query Latency** | < 150ms p95 | DuckDB OLAP query response times over Parquet dataset caches. | p95 latency > 500ms |
| **Claim Validation Throughput** | > 100 claims/sec | Batch execution speed of `ClaimValidationEngine`. | Throughput < 50 claims/sec |
| **Zero Database Lock Drops** | 0 lock collisions | SQLite `busy_timeout` exhaustion occurrences. | Any `sqlite3.OperationalError: database is locked` event |

---

## 2. Health Check & Diagnostic Endpoints

### Liveness Probe
- **Endpoint**: `GET /health/live`
- **Expected Status**: `200 OK`
- **Payload**: `{"status": "alive", "timestamp": "2026-11-03T..."}`
- **Purpose**: Kubernetes / Docker daemon restart trigger if event loop deadlocks.

### Readiness Probe
- **Endpoint**: `GET /health/ready`
- **Expected Status**: `200 OK` (or `503 Service Unavailable` if storage uninitialized)
- **Payload**:
  ```json
  {
    "status": "ready",
    "database": {
      "sqlite": "healthy",
      "duckdb": "healthy",
      "tables": {
        "sqlite_table_count": 13,
        "duckdb_tables": ["evidence_ledger", "observations", "v_comparability", "v_evidence", "v_indicators", "v_observations"]
      }
    },
    "timestamp": "2026-11-03T..."
  }
  ```

### Operational Telemetry
- **Endpoint**: `GET /api/metrics`
- **Authentication**: Requires `admin` or `researcher` role.
- **Payload**: Emits request counts, error rate, average latency ms, status code distribution, database record counts, and GenAI token expenditure.

---

## 3. Incident Management & Remediation Procedures

### Incident 1: High Database Latency / Contention
- **Symptom**: `/health/ready` latency exceeds 500ms; log shows SQLite busy retry delays.
- **Diagnosis**:
  1. Inspect running background jobs: `GET /api/jobs`
  2. Verify WAL file size: `ls -lh data/atlas.db-wal`
- **Remediation**:
  1. Trigger SQLite WAL checkpointing: `sqlite3 data/atlas.db "PRAGMA wal_checkpoint(TRUNCATE);"`
  2. If DuckDB file is locked by a stale process, restart analytical cache:
     `python -c "from atlas.core.db import sync_duckdb; sync_duckdb()"`

### Incident 2: External Ingestion API 429 Rate Limiting
- **Symptom**: Ingestion job logs show repeated HTTP 429 responses from World Bank or IMF APIs.
- **Diagnosis**: Fetcher circuit breaker activated in `atlas/sources/fetcher.py`.
- **Remediation**:
  1. The built-in exponential backoff automatically respects `Retry-After` headers.
  2. Do not hammer endpoints manually; wait for circuit breaker to auto-reset.

### Incident 3: Background Worker Thread Pool Saturation
- **Symptom**: Newly submitted background jobs stay in `queued` state indefinitely.
- **Diagnosis**: `_job_executor` max_workers (4) occupied by hanging benchmark runs.
- **Remediation**:
  1. Inspect `background_jobs` table: `SELECT job_id, job_type, updated_at FROM background_jobs WHERE status = 'running'`
  2. Mark stale jobs as failed: `UPDATE background_jobs SET status = 'failed', error_message = 'Timed out by administrator' WHERE status = 'running'`

---

## 4. Routine Maintenance Tasks

1. **Daily Backup Verification**:
   Execute automated backup drill:
   `python scripts/backup_and_restore.py --action test-cycle`
2. **Weekly DuckDB Parquet Compaction**:
   Re-export and sync columnar stores:
   `python -c "from atlas.core.db import sync_duckdb; sync_duckdb()"`
3. **Monthly Source Freshness Governance Audit**:
   Verify data freshness across all official feeds:
   `python -c "from atlas.sources.registry import evaluate_source_freshness; print(evaluate_source_freshness())"`

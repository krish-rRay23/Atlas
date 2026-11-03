"""ATLAS Database Layer: SQLite + DuckDB.

Provides persistent relational storage and analytical OLAP engine.
"""

import sqlite3
import duckdb
from typing import List, Dict, Any, Optional, Generator
import os
import json
import threading
from contextlib import contextmanager
from atlas.core.config import SQLITE_DB_PATH, DUCKDB_PATH, PROCESSED_DATA_DIR, settings

# Thread-safe lock for DuckDB write operations
_duckdb_write_lock = threading.Lock()

def get_sqlite_conn() -> sqlite3.Connection:
    """Acquire a thread-safe connection to SQLite with row factory and foreign keys enabled."""
    conn = sqlite3.connect(str(SQLITE_DB_PATH), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for high concurrency
    conn.execute("PRAGMA busy_timeout = 5000")  # 5s busy timeout
    return conn

@contextmanager
def transaction() -> Generator[sqlite3.Cursor, None, None]:
    """Context manager for atomic database transactions with automatic rollback on error."""
    conn = get_sqlite_conn()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_duckdb_conn(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Acquire a DuckDB connection.
    For analytical queries, set read_only=True to prevent file write-lock contention.
    """
    try:
        return duckdb.connect(str(DUCKDB_PATH), read_only=read_only)
    except Exception:
        # Fallback to an in-memory instance querying parquet directly if the file is locked
        conn = duckdb.connect(":memory:")
        obs_p = PROCESSED_DATA_DIR / "observations.parquet"
        ev_p = PROCESSED_DATA_DIR / "evidence_ledger.parquet"
        if obs_p.exists():
            obs_str = str(obs_p).replace("\\", "/")
            conn.execute(f"CREATE VIEW IF NOT EXISTS observations AS SELECT * FROM read_parquet('{obs_str}')")
        if ev_p.exists():
            ev_str = str(ev_p).replace("\\", "/")
            conn.execute(f"CREATE VIEW IF NOT EXISTS evidence_ledger AS SELECT * FROM read_parquet('{ev_str}')")
        return conn

def get_duckdb_read_conn() -> duckdb.DuckDBPyConnection:
    """Safe read-only DuckDB connection for API and UI queries."""
    return get_duckdb_conn(read_only=True)

def check_db_health() -> Dict[str, Any]:
    """Health check for operational and analytical databases."""
    status = {"sqlite": "healthy", "duckdb": "healthy", "tables": {}}
    try:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        status["tables"]["sqlite_table_count"] = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        status["sqlite"] = f"unhealthy: {str(e)}"

    try:
        dconn = get_duckdb_read_conn()
        res = dconn.execute("SHOW TABLES").fetchall()
        status["tables"]["duckdb_tables"] = [r[0] for r in res]
        dconn.close()
    except Exception as e:
        status["duckdb"] = f"unhealthy: {str(e)}"

    return status

def init_database():
    """Idempotently initialize relational and analytical schemas."""
    os.makedirs(SQLITE_DB_PATH.parent, exist_ok=True)
    conn = get_sqlite_conn()
    cur = conn.cursor()
    
    # 1. Projects
    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        research_question TEXT NOT NULL,
        countries TEXT NOT NULL,
        indicators TEXT NOT NULL,
        date_start INTEGER,
        date_end INTEGER,
        created_at TEXT NOT NULL,
        status TEXT DEFAULT 'active'
    )
    """)

    # 2. Sources
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        source_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        publisher TEXT NOT NULL,
        url TEXT NOT NULL,
        source_type TEXT NOT NULL,
        methodology TEXT NOT NULL,
        coverage_geos TEXT NOT NULL,
        reference_period TEXT NOT NULL,
        publication_date TEXT NOT NULL,
        retrieval_date TEXT NOT NULL,
        file_hash_sha256 TEXT,
        data_format TEXT,
        quality_score REAL DEFAULT 1.0,
        limitations TEXT
    )
    """)

    # 3. Indicators
    cur.execute("""
    CREATE TABLE IF NOT EXISTS indicators (
        indicator_code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit TEXT NOT NULL,
        denominator TEXT,
        target_population TEXT,
        source_id TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (source_id) REFERENCES sources (source_id)
    )
    """)

    # 4. Observations
    cur.execute("""
    CREATE TABLE IF NOT EXISTS observations (
        id TEXT PRIMARY KEY,
        country_iso3 TEXT NOT NULL,
        country_name TEXT NOT NULL,
        indicator_code TEXT NOT NULL,
        indicator_name TEXT NOT NULL,
        year INTEGER NOT NULL,
        value REAL,
        unit TEXT NOT NULL,
        source_id TEXT NOT NULL,
        source_name TEXT NOT NULL,
        reference_period TEXT NOT NULL,
        extraction_date TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        status TEXT DEFAULT 'available',
        notes TEXT,
        FOREIGN KEY (source_id) REFERENCES sources (source_id),
        FOREIGN KEY (indicator_code) REFERENCES indicators (indicator_code)
    )
    """)

    # 5. Evidence Ledger
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evidence_ledger (
        evidence_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        country_iso3 TEXT NOT NULL,
        country_name TEXT NOT NULL,
        indicator_code TEXT NOT NULL,
        value REAL,
        unit TEXT NOT NULL,
        year INTEGER NOT NULL,
        citation_text TEXT NOT NULL,
        page_or_table_ref TEXT NOT NULL,
        extraction_method TEXT NOT NULL,
        validation_status TEXT NOT NULL,
        reviewer_notes TEXT,
        verified_by_human INTEGER DEFAULT 0,
        verified_at TEXT,
        FOREIGN KEY (source_id) REFERENCES sources (source_id),
        FOREIGN KEY (indicator_code) REFERENCES indicators (indicator_code)
    )
    """)

    # 6. Comparability Assessments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comparability_assessments (
        assessment_id TEXT PRIMARY KEY,
        indicator_code TEXT NOT NULL,
        country_a TEXT NOT NULL,
        country_b TEXT NOT NULL,
        classification TEXT NOT NULL,
        justification TEXT NOT NULL,
        rule_applied TEXT NOT NULL,
        unit_consistency INTEGER NOT NULL,
        denominator_consistency INTEGER NOT NULL,
        population_consistency INTEGER NOT NULL,
        methodology_consistency INTEGER NOT NULL,
        period_consistency INTEGER NOT NULL,
        FOREIGN KEY (indicator_code) REFERENCES indicators (indicator_code)
    )
    """)

    # 7. Claim Validations
    cur.execute("""
    CREATE TABLE IF NOT EXISTS claim_validations (
        claim_id TEXT PRIMARY KEY,
        claim_text TEXT NOT NULL,
        referenced_evidence_ids TEXT NOT NULL,
        status TEXT NOT NULL,
        numerical_fidelity_score REAL NOT NULL,
        temporal_match INTEGER NOT NULL,
        geographic_match INTEGER NOT NULL,
        explanation TEXT NOT NULL
    )
    """)

    # 8. Research Memos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS research_memos (
        memo_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        research_question TEXT NOT NULL,
        generated_at TEXT NOT NULL,
        model_used TEXT NOT NULL,
        sections_json TEXT NOT NULL,
        referenced_evidence_count INTEGER NOT NULL,
        validation_status TEXT NOT NULL,
        total_tokens INTEGER NOT NULL,
        inference_seconds REAL NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
    """)

    # 9. Benchmark Runs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS benchmark_runs (
        run_id TEXT PRIMARY KEY,
        benchmark_name TEXT NOT NULL,
        dataset_version TEXT NOT NULL,
        sample_count INTEGER NOT NULL,
        metrics_json TEXT NOT NULL,
        passed_threshold INTEGER NOT NULL,
        execution_time_seconds REAL NOT NULL,
        timestamp TEXT NOT NULL,
        details_json TEXT
    )
    """)

    # 10. Model Execution Logs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS model_logs (
        log_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        provider TEXT NOT NULL,
        model TEXT NOT NULL,
        task_type TEXT NOT NULL,
        input_tokens INTEGER NOT NULL,
        output_tokens INTEGER NOT NULL,
        duration_seconds REAL NOT NULL,
        estimated_cost_usd REAL NOT NULL,
        success INTEGER NOT NULL,
        error_message TEXT
    )
    """)

    # 11. Users & Roles for Production RBAC
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'researcher',
        created_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)

    # 12. Background Asynchronous Jobs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS background_jobs (
        job_id TEXT PRIMARY KEY,
        job_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        progress_pct REAL DEFAULT 0.0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        result_json TEXT,
        error_message TEXT,
        user_id TEXT
    )
    """)

    # 13. Claim Human Audit Revisions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS claim_revisions (
        revision_id TEXT PRIMARY KEY,
        claim_id TEXT NOT NULL,
        previous_status TEXT NOT NULL,
        new_status TEXT NOT NULL,
        reviewer_id TEXT NOT NULL,
        reviewer_notes TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (claim_id) REFERENCES claim_validations (claim_id)
    )
    """)

    conn.commit()
    conn.close()

    # Sync into DuckDB
    sync_duckdb()

def sync_duckdb():
    """Sync processed parquet datasets into native DuckDB tables for high-speed OLAP queries.
    Uses a thread lock to ensure safe atomic updates without concurrent lock collision.
    """
    from atlas.core.config import PROCESSED_DATA_DIR
    obs_p = PROCESSED_DATA_DIR / "observations.parquet"
    ev_p = PROCESSED_DATA_DIR / "evidence_ledger.parquet"

    with _duckdb_write_lock:
        try:
            dconn = duckdb.connect(str(DUCKDB_PATH), read_only=False)
            if obs_p.exists():
                obs_path_str = str(obs_p).replace("\\", "/")
                dconn.execute(f"CREATE OR REPLACE TABLE observations AS SELECT * FROM read_parquet('{obs_path_str}')")
                dconn.execute("CREATE OR REPLACE VIEW v_observations AS SELECT * FROM observations")
            
            if ev_p.exists():
                ev_path_str = str(ev_p).replace("\\", "/")
                dconn.execute(f"CREATE OR REPLACE TABLE evidence_ledger AS SELECT * FROM read_parquet('{ev_path_str}')")
                dconn.execute("CREATE OR REPLACE VIEW v_evidence AS SELECT * FROM evidence_ledger")

            dconn.close()
        except Exception as e:
            # Non-blocking graceful catch: if another process is holding lock, logged
            print(f"[WARN] DuckDB sync deferred due to lock or file contention: {e}")

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")

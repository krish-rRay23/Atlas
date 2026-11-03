"""ATLAS Database Layer: SQLite + DuckDB.

Provides persistent relational storage and analytical OLAP engine.
"""

import sqlite3
import duckdb
from typing import List, Dict, Any, Optional
import os
import json
from atlas.core.config import SQLITE_DB_PATH, DUCKDB_PATH

def get_sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(SQLITE_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_duckdb_conn() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DUCKDB_PATH))

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

    conn.commit()
    conn.close()

    # Sync into DuckDB
    sync_duckdb()

def sync_duckdb():
    """Sync processed parquet datasets into native DuckDB tables for high-speed OLAP queries."""
    from atlas.core.config import PROCESSED_DATA_DIR
    obs_p = PROCESSED_DATA_DIR / "observations.parquet"
    ev_p = PROCESSED_DATA_DIR / "evidence_ledger.parquet"

    dconn = get_duckdb_conn()
    if obs_p.exists():
        obs_path_str = str(obs_p).replace("\\", "/")
        dconn.execute(f"CREATE OR REPLACE TABLE observations AS SELECT * FROM read_parquet('{obs_path_str}')")
        dconn.execute("CREATE OR REPLACE VIEW v_observations AS SELECT * FROM observations")
    
    if ev_p.exists():
        ev_path_str = str(ev_p).replace("\\", "/")
        dconn.execute(f"CREATE OR REPLACE TABLE evidence_ledger AS SELECT * FROM read_parquet('{ev_path_str}')")
        dconn.execute("CREATE OR REPLACE VIEW v_evidence AS SELECT * FROM evidence_ledger")

    dconn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")

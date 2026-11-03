"""Unit tests for ATLAS Database & Storage Layer."""

import pytest
import sqlite3
from atlas.core.db import get_sqlite_conn, get_duckdb_conn, init_database

def test_database_initialization():
    init_database()
    conn = get_sqlite_conn()
    cur = conn.cursor()
    
    # Check that core tables exist
    tables = ["projects", "sources", "indicators", "observations", "evidence_ledger",
              "comparability_assessments", "claim_validations", "research_memos",
              "benchmark_runs", "model_logs"]
    for t in tables:
        cur.execute(f"SELECT count(*) FROM {t}")
        count = cur.fetchone()[0]
        assert count >= 0

    conn.close()

def test_duckdb_sync():
    dconn = get_duckdb_conn()
    res = dconn.execute("SELECT count(*) FROM v_observations").fetchone()[0]
    assert res > 0
    dconn.close()


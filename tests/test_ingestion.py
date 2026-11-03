"""Unit tests for ATLAS Ingestion & Evidence Generation Pipeline."""

import pytest
from atlas.core.db import get_sqlite_conn
from atlas.core.config import TARGET_ECONOMIES

def test_sources_and_indicators_loaded():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT count(*) FROM sources")
    s_count = cur.fetchone()[0]
    assert s_count >= 8

    cur.execute("SELECT count(*) FROM indicators")
    ind_count = cur.fetchone()[0]
    assert ind_count >= 10

    conn.close()

def test_five_countries_present():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT country_iso3 FROM observations WHERE value IS NOT NULL")
    countries = [r[0] for r in cur.fetchall()]
    for expected_c in TARGET_ECONOMIES.keys():
        assert expected_c in countries

    conn.close()

def test_evidence_ledger_populated():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT count(*) FROM evidence_ledger WHERE value IS NOT NULL")
    ev_count = cur.fetchone()[0]
    assert ev_count > 300

    conn.close()


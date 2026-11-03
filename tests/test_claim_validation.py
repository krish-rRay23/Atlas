"""Unit tests for Claim & Citation Validation Engine."""

import pytest
from atlas.evidence.claim_validator import ClaimValidationEngine
from atlas.core.db import get_sqlite_conn

def test_missing_evidence_flagged():
    val = ClaimValidationEngine()
    res = val.validate_claim("Indonesia achieved 89% financial inclusion.", [])
    assert res.status == "missing_evidence"
    assert res.numerical_fidelity_score == 0.0

def test_supported_claim_verified():
    val = ClaimValidationEngine()
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT evidence_id FROM evidence_ledger WHERE country_iso3 = 'IND' AND indicator_code = 'FX.OWN.TOTL.ZS' AND year = 2024")
    ev_id = cur.fetchone()[0]
    conn.close()

    res = val.validate_claim("In 2024, India account ownership was 89.02%.", [ev_id])
    assert res.status == "supported"
    assert res.numerical_fidelity_score >= 0.8

def test_contradiction_detected():
    val = ClaimValidationEngine()
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT evidence_id FROM evidence_ledger WHERE country_iso3 = 'IDN' AND indicator_code = 'FX.OWN.TOTL.ZS' AND year = 2024")
    ev_id = cur.fetchone()[0]
    conn.close()

    # Indonesia is 56.3%, claim states 99%
    res = val.validate_claim("In 2024, Indonesia account ownership was 99%.", [ev_id])
    assert res.status == "contradicted"


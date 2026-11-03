"""Unit tests for FastAPI REST Endpoints."""

import pytest
from fastapi.testclient import TestClient
from atlas.api.main import app

client = TestClient(app)

def test_api_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_api_health_live():
    resp = client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "alive"

def test_api_health_ready():
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"
    assert resp.json()["database"]["sqlite"] == "healthy"

def test_api_metrics():
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "api" in data
    assert "data_platform" in data

def test_api_jobs():
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_api_sources():
    resp = client.get("/api/sources")
    assert resp.status_code == 200
    assert len(resp.json()) >= 8

def test_api_evidence_summary():
    resp = client.get("/api/evidence/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_records"] > 300

def test_api_economics():
    resp = client.get("/api/economics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["time_saved_percent"] > 80.0

def test_api_memo_export():
    # Fetch existing memo list
    m_resp = client.get("/api/memos")
    assert m_resp.status_code == 200
    memos = m_resp.json()
    if memos:
        memo_id = memos[0]["memo_id"]
        exp_resp = client.get(f"/api/memos/{memo_id}/export?export_format=markdown")
        assert exp_resp.status_code == 200
        assert "text/markdown" in exp_resp.headers["content-type"]
        assert f"# {memos[0]['title']}" in exp_resp.text

def test_api_claim_review():
    review_payload = {
        "decision": "ACCEPTED",
        "reviewer_notes": "Unit test verified against central bank bulletin.",
        "revised_text": "India achieved 77.5% account ownership (WB Findex 2021).",
        "memo_id": "MEMO-TEST"
    }
    resp = client.post("/api/claims/CLM-TEST-99/review", json=review_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["decision"] == "ACCEPTED"

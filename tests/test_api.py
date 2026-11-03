"""Unit tests for FastAPI REST Endpoints."""

import pytest
from fastapi.testclient import TestClient
from atlas.api.main import app

client = TestClient(app)

def test_api_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

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


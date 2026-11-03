"""Unit tests for ATLAS system observability, health checks, and telemetry."""

import pytest
from atlas.core.db import check_db_health, init_database
from atlas.core.observability import get_system_metrics, record_request_metric, _metrics_accumulator

@pytest.fixture(autouse=True)
def setup_db():
    init_database()

def test_database_health_check():
    health = check_db_health()
    assert health["sqlite"] == "healthy"
    assert health["duckdb"] == "healthy"
    assert "tables" in health
    assert health["tables"]["sqlite_table_count"] >= 10

def test_system_metrics_structure():
    metrics = get_system_metrics()
    assert "api" in metrics
    assert "data_platform" in metrics
    assert "research_engine" in metrics
    assert "genai_telemetry" in metrics

    assert metrics["data_platform"]["total_observations"] > 0
    assert metrics["data_platform"]["total_evidence_records"] > 0
    assert metrics["research_engine"]["generated_memos"] >= 0

def test_metrics_tracker_recording():
    initial_reqs = _metrics_accumulator["total_requests"]
    record_request_metric("/api/test", 200, 15.5)
    assert _metrics_accumulator["total_requests"] == initial_reqs + 1
    assert 200 in _metrics_accumulator["status_codes"]

    initial_errs = _metrics_accumulator["error_count"]
    record_request_metric("/api/test_err", 500, 8.2)
    assert _metrics_accumulator["error_count"] == initial_errs + 1

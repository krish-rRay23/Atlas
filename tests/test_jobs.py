"""Unit and integration tests for ATLAS background asynchronous job queue."""

import time
import pytest
from atlas.core.jobs import JobService
from atlas.core.db import init_database

@pytest.fixture(autouse=True)
def setup_db():
    init_database()

def test_job_lifecycle():
    job_id = JobService.create_job("test_pipeline", user_id="TEST-USER")
    assert job_id.startswith("JOB-")

    job = JobService.get_job(job_id)
    assert job is not None
    assert job["status"] == "queued"
    assert job["job_type"] == "test_pipeline"
    assert job["progress_pct"] == 0.0

    JobService.update_job_progress(job_id, 45.0, status="running")
    job_updated = JobService.get_job(job_id)
    assert job_updated["status"] == "running"
    assert job_updated["progress_pct"] == 45.0

    JobService.complete_job(job_id, {"rows_processed": 500, "status": "success"})
    job_done = JobService.get_job(job_id)
    assert job_done["status"] == "completed"
    assert job_done["progress_pct"] == 100.0
    assert job_done["result"]["rows_processed"] == 500

def test_job_failure_logging():
    job_id = JobService.create_job("failing_task")
    JobService.fail_job(job_id, "Fatal out of memory or connection timeout")
    
    job = JobService.get_job(job_id)
    assert job["status"] == "failed"
    assert "timeout" in job["error_message"]

def test_asynchronous_worker_execution():
    job_id = JobService.create_job("async_computation")

    def _slow_add(x, y):
        time.sleep(0.05)
        return {"sum": x + y}

    JobService.submit_task(job_id, _slow_add, 15, 27)

    # Poll briefly for completion
    for _ in range(30):
        time.sleep(0.05)
        job = JobService.get_job(job_id)
        if job["status"] == "completed":
            break

    assert job["status"] == "completed"
    assert job["result"]["sum"] == 42

def test_list_jobs():
    jobs = JobService.list_jobs(limit=10)
    assert isinstance(jobs, list)
    assert len(jobs) > 0

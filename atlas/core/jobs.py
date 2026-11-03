"""ATLAS Background Job Queue & Asynchronous Processing Engine.

Executes long-running data ingestion, benchmark runs, and memo synthesis
in isolated worker threads with real-time status, progress tracking, and persistence.
"""

import time
import uuid
import datetime
import json
import threading
from typing import Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from atlas.core.db import get_sqlite_conn
from atlas.core.models import BackgroundJob

# Background thread pool
_job_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="atlas_worker")
_running_tasks: Dict[str, threading.Event] = {}

class JobService:
    @staticmethod
    def create_job(job_type: str, user_id: Optional[str] = None) -> str:
        """Create a new job record in the database."""
        job_id = f"JOB-{uuid.uuid4().hex[:10].upper()}"
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO background_jobs (
            job_id, job_type, status, progress_pct, created_at, updated_at, result_json, error_message, user_id
        ) VALUES (?, ?, 'queued', 0.0, ?, ?, NULL, NULL, ?)
        """, (job_id, job_type, now_ts, now_ts, user_id))
        conn.commit()
        conn.close()

        return job_id

    @staticmethod
    def update_job_progress(job_id: str, progress_pct: float, status: str = "running"):
        """Update job progress percentage and status."""
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
        UPDATE background_jobs
        SET progress_pct = ?, status = ?, updated_at = ?
        WHERE job_id = ?
        """, (round(progress_pct, 1), status, now_ts, job_id))
        conn.commit()
        conn.close()

    @staticmethod
    def complete_job(job_id: str, result: Dict[str, Any]):
        """Mark job as successfully completed and persist result payload."""
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
        UPDATE background_jobs
        SET status = 'completed', progress_pct = 100.0, updated_at = ?, result_json = ?
        WHERE job_id = ?
        """, (now_ts, json.dumps(result), job_id))
        conn.commit()
        conn.close()

    @staticmethod
    def fail_job(job_id: str, error_msg: str):
        """Mark job as failed and persist error message."""
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
        UPDATE background_jobs
        SET status = 'failed', updated_at = ?, error_message = ?
        WHERE job_id = ?
        """, (now_ts, error_msg, job_id))
        conn.commit()
        conn.close()

    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job details by ID."""
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM background_jobs WHERE job_id = ?", (job_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if d.get("result_json"):
            try:
                d["result"] = json.loads(d["result_json"])
            except Exception:
                d["result"] = d["result_json"]
        return d

    @classmethod
    def list_jobs(cls, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent background jobs."""
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM background_jobs ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        for r in rows:
            if r.get("result_json"):
                try:
                    r["result"] = json.loads(r["result_json"])
                except Exception:
                    pass
        return rows

    @classmethod
    def submit_task(cls, job_id: str, target_fn: Callable[..., Any], *args, **kwargs):
        """Submit a target function for asynchronous execution in background thread pool."""
        def worker_wrapper():
            try:
                cls.update_job_progress(job_id, 10.0, "running")
                res = target_fn(*args, **kwargs)
                cls.complete_job(job_id, res if isinstance(res, dict) else {"status": "ok", "output": str(res)})
            except Exception as e:
                cls.fail_job(job_id, str(e))

        _job_executor.submit(worker_wrapper)

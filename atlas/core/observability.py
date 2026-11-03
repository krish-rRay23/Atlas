"""ATLAS Operational Observability, Structured Logging, and Metrics Instrumentation.
"""

import time
import json
import logging
import uuid
import datetime
from typing import Dict, Any, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from atlas.core.db import get_sqlite_conn, get_duckdb_read_conn

# Structured Logger
logger = logging.getLogger("atlas.observability")
logger.setLevel(logging.INFO)

# Metrics collector in-memory accumulator
_metrics_accumulator = {
    "total_requests": 0,
    "status_codes": {},
    "endpoints": {},
    "total_latency_ms": 0.0,
    "error_count": 0
}

def record_request_metric(endpoint: str, status_code: int, duration_ms: float):
    """Record an API request into the in-memory telemetry accumulator."""
    _metrics_accumulator["total_requests"] += 1
    _metrics_accumulator["status_codes"][status_code] = _metrics_accumulator["status_codes"].get(status_code, 0) + 1
    _metrics_accumulator["endpoints"][endpoint] = _metrics_accumulator["endpoints"].get(endpoint, 0) + 1
    _metrics_accumulator["total_latency_ms"] += duration_ms
    if status_code >= 400:
        _metrics_accumulator["error_count"] += 1

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """ASGI Middleware: attaches correlation Request ID, measures latency, and emits structured JSON logs."""
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or f"REQ-{uuid.uuid4().hex[:10].upper()}"
        start_time = time.time()
        
        # Attach request_id to state
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Record metric
            _metrics_accumulator["total_requests"] += 1
            status_code = response.status_code
            _metrics_accumulator["status_codes"][status_code] = _metrics_accumulator["status_codes"].get(status_code, 0) + 1
            endpoint = request.url.path
            _metrics_accumulator["endpoints"][endpoint] = _metrics_accumulator["endpoints"].get(endpoint, 0) + 1
            _metrics_accumulator["total_latency_ms"] += duration_ms

            if status_code >= 400:
                _metrics_accumulator["error_count"] += 1

            # Append Request ID header to response
            response.headers["X-Request-ID"] = request_id

            # Structured Log
            log_entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "severity": "INFO" if status_code < 400 else ("WARNING" if status_code < 500 else "ERROR"),
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else "unknown"
            }
            if status_code >= 400:
                logger.warning(json.dumps(log_entry))
            else:
                logger.info(json.dumps(log_entry))

            return response
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            _metrics_accumulator["total_requests"] += 1
            _metrics_accumulator["error_count"] += 1
            log_entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "severity": "CRITICAL",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
                "error": str(e)
            }
            logger.error(json.dumps(log_entry))
            raise

def get_system_metrics() -> Dict[str, Any]:
    """Compile application, operational database, and model metrics for operational dashboard."""
    tot_reqs = _metrics_accumulator["total_requests"]
    avg_latency = (_metrics_accumulator["total_latency_ms"] / tot_reqs) if tot_reqs > 0 else 0.0
    err_rate = (_metrics_accumulator["error_count"] / tot_reqs * 100.0) if tot_reqs > 0 else 0.0

    # Query operational counts from DB
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM observations")
    total_observations = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM evidence_ledger")
    total_evidence = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM research_memos")
    total_memos = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM background_jobs WHERE status = 'running'")
    active_jobs = cur.fetchone()[0]
    cur.execute("SELECT coalesce(sum(estimated_cost_usd), 0.0), coalesce(sum(input_tokens), 0), coalesce(sum(output_tokens), 0) FROM model_logs")
    model_stats = cur.fetchone()
    total_model_cost = float(model_stats[0])
    total_in_tok = int(model_stats[1])
    total_out_tok = int(model_stats[2])
    conn.close()

    return {
        "api": {
            "total_requests": tot_reqs,
            "error_rate_pct": round(err_rate, 2),
            "average_latency_ms": round(avg_latency, 2),
            "status_code_distribution": _metrics_accumulator["status_codes"],
            "top_endpoints": _metrics_accumulator["endpoints"]
        },
        "data_platform": {
            "total_observations": total_observations,
            "total_evidence_records": total_evidence,
            "active_background_jobs": active_jobs
        },
        "research_engine": {
            "generated_memos": total_memos
        },
        "genai_telemetry": {
            "total_estimated_cost_usd": round(total_model_cost, 6),
            "input_tokens_consumed": total_in_tok,
            "output_tokens_consumed": total_out_tok,
            "total_tokens_consumed": total_in_tok + total_out_tok
        }
    }


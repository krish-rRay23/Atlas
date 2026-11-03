"""ATLAS FastAPI REST API.

Provides endpoints for projects, source intelligence, evidence ledger,
AsiaMetric comparability engine, research memo synthesis, evaluation, background jobs,
claim review governance, observability metrics, and health checks.
"""

from fastapi import FastAPI, HTTPException, Query, Body, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import json
import uuid
import datetime
from pathlib import Path

from atlas.core.config import settings
from atlas.core.db import get_sqlite_conn, sync_duckdb, check_db_health
from atlas.core.models import ProjectCreate, Project, SourceMetadata, IndicatorDefinition, EvidenceRecord
from atlas.evidence.ledger import EvidenceLedgerService
from atlas.comparability.asiametric import AsiaMetricEngine
from atlas.synthesis.engine import ResearchSynthesisEngine
from atlas.evaluation.runner import run_all_benchmarks
from atlas.evaluation.headline_benchmarks import HeadlineBenchmarkSuite
from atlas.economics.calculator import EconomicsCalculator
from atlas.sources.registry import OFFICIAL_SOURCES, OFFICIAL_INDICATORS
from atlas.core.security import get_current_user, require_role, safe_path_join
from atlas.core.jobs import JobService
from atlas.core.observability import StructuredLoggingMiddleware, get_system_metrics

app = FastAPI(
    title="ATLAS — Asia Research Evidence Intelligence API",
    description="Enterprise API for evidence-grounded comparative research across Asian economies.",
    version="2.0.0"
)

# 1. Observability & Structured Logging
app.add_middleware(StructuredLoggingMiddleware)

# 2. CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins if "*" not in settings.allowed_cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HEALTH & OBSERVABILITY ---
@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "ATLAS Backend",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

@app.get("/health/live")
def liveness_check():
    """Liveness probe: returns 200 immediately if process is responsive."""
    return {"status": "alive", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}

@app.get("/health/ready")
def readiness_check():
    """Readiness probe: validates database connectivity and storage health."""
    db_health = check_db_health()
    is_ready = db_health.get("sqlite") == "healthy" and db_health.get("duckdb") == "healthy"
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if is_ready else "not_ready",
        "database": db_health,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

@app.get("/api/metrics")
def get_metrics(current_user: Dict[str, Any] = Depends(require_role(["admin", "researcher", "reviewer"]))):
    """Retrieve operational system telemetry, memory usage, request counts, and error rates."""
    return get_system_metrics()

# --- BACKGROUND JOBS ---
@app.get("/api/jobs")
def list_background_jobs(
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """List recent background jobs and their execution statuses."""
    return JobService.list_jobs(limit=limit)

@app.get("/api/jobs/{job_id}")
def get_background_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve status, progress, and results of a specific background job."""
    job = JobService.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job

@app.post("/api/jobs")
def submit_background_job(
    job_type: str = Body(..., embed=True),
    parameters: Dict[str, Any] = Body(default={}, embed=True),
    current_user: Dict[str, Any] = Depends(require_role(["admin", "researcher"]))
):
    """Enqueue an asynchronous background task (e.g. memo synthesis, benchmark suite, data sync)."""
    user_id = current_user.get("user_id", "ANONYMOUS")
    job_id = JobService.create_job(job_type, user_id=user_id)

    if job_type == "generate_memo":
        project_id = parameters.get("project_id", "PROJ-DEFAULT")
        question = parameters.get("research_question")
        def _task():
            engine = ResearchSynthesisEngine()
            memo = engine.generate_comparative_memo(
                project_id=project_id,
                research_question=question or "Comparative digital financial inclusion across Asian economies"
            )
            return {"memo_id": memo.memo_id, "claims_count": len(memo.claims_ledger)}
        JobService.submit_task(job_id, _task)

    elif job_type == "run_benchmarks":
        def _bench_task():
            return run_all_benchmarks()
        JobService.submit_task(job_id, _bench_task)

    elif job_type == "sync_duckdb":
        def _sync_task():
            sync_duckdb()
            return {"synced": True}
        JobService.submit_task(job_id, _sync_task)

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported job_type: '{job_type}'. Valid: generate_memo, run_benchmarks, sync_duckdb")

    return {"job_id": job_id, "status": "queued", "job_type": job_type}

# --- PROJECTS ---
@app.get("/api/projects")
def list_projects():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.post("/api/projects")
def create_project(payload: ProjectCreate, current_user: Dict[str, Any] = Depends(require_role(["admin", "researcher"]))):
    conn = get_sqlite_conn()
    cur = conn.cursor()
    proj_id = f"PROJ-{uuid.uuid4().hex[:8].upper()}"
    now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cur.execute("""
    INSERT INTO projects (id, title, research_question, countries, indicators, date_start, date_end, created_at, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        proj_id, payload.title, payload.research_question,
        json.dumps(payload.countries), json.dumps(payload.indicators),
        payload.date_start, payload.date_end, now_ts, "active"
    ))
    conn.commit()
    conn.close()
    return {"id": proj_id, "title": payload.title, "created_at": now_ts, "status": "active"}

# --- SOURCES ---
@app.get("/api/sources")
def list_sources():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sources ORDER BY quality_score DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# --- INDICATORS ---
@app.get("/api/indicators")
def list_indicators():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM indicators ORDER BY category, name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# --- OBSERVATIONS ---
@app.get("/api/observations")
def get_observations(
    country: Optional[str] = None,
    indicator: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None
):
    conn = get_sqlite_conn()
    cur = conn.cursor()
    query = ["SELECT * FROM observations WHERE value IS NOT NULL"]
    params = []
    if country:
        query.append("AND country_iso3 = ?")
        params.append(country)
    if indicator:
        query.append("AND indicator_code = ?")
        params.append(indicator)
    if year_min:
        query.append("AND year >= ?")
        params.append(year_min)
    if year_max:
        query.append("AND year <= ?")
        params.append(year_max)
    query.append("ORDER BY year DESC, country_name ASC")

    cur.execute(" ".join(query), params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# --- EVIDENCE LEDGER ---
@app.get("/api/evidence")
def list_evidence(
    country: Optional[str] = None,
    indicator: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    return EvidenceLedgerService.list_evidence(
        country_iso3=country,
        indicator_code=indicator,
        validation_status=status,
        search_query=search,
        limit=limit,
        offset=offset
    )

@app.get("/api/evidence/summary")
def get_evidence_summary():
    return EvidenceLedgerService.get_ledger_summary_stats()

@app.post("/api/evidence/{evidence_id}/review")
def review_evidence(
    evidence_id: str,
    status: str = Body(..., embed=True),
    reviewer_notes: str = Body("", embed=True),
    current_user: Dict[str, Any] = Depends(require_role(["admin", "reviewer"]))
):
    success = EvidenceLedgerService.update_review_status(evidence_id, status, reviewer_notes, True)
    if not success:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    return {"status": "success", "evidence_id": evidence_id, "updated_status": status}

# --- COMPARABILITY (ASIAMETRIC) ---
@app.get("/api/comparability")
def get_comparability_assessments(indicator: Optional[str] = None):
    conn = get_sqlite_conn()
    cur = conn.cursor()
    if indicator:
        cur.execute("SELECT * FROM comparability_assessments WHERE indicator_code = ?", (indicator,))
    else:
        cur.execute("SELECT * FROM comparability_assessments")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.post("/api/comparability/evaluate")
def evaluate_comparability(
    indicator_a: str = Body(...),
    country_a: str = Body(...),
    year_a: int = Body(...),
    indicator_b: str = Body(...),
    country_b: str = Body(...),
    year_b: int = Body(...)
):
    engine = AsiaMetricEngine()
    result = engine.evaluate_pair(indicator_a, country_a, year_a, indicator_b, country_b, year_b)
    return result.model_dump()

# --- RESEARCH SYNTHESIS & CLAIM AUDIT REVISION ---
@app.get("/api/memos")
def list_memos():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT memo_id, project_id, title, research_question, generated_at, model_used, validation_status FROM research_memos ORDER BY generated_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.get("/api/memos/{memo_id}")
def get_memo(memo_id: str):
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM research_memos WHERE memo_id = ?", (memo_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Memo not found")
    data = dict(row)
    data["sections"] = json.loads(data["sections_json"])
    return data

@app.get("/api/memos/{memo_id}/export")
def export_memo(
    memo_id: str,
    export_format: str = Query(default="markdown", pattern="^(markdown|json)$")
):
    """Safely export research memo as formatted Markdown report or JSON artifact."""
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM research_memos WHERE memo_id = ?", (memo_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Memo not found")
    
    data = dict(row)
    if export_format == "json":
        data["sections"] = json.loads(data["sections_json"])
        return data

    # Markdown serialization
    sections = json.loads(data["sections_json"])
    lines = [
        f"# {data['title']}",
        f"**Memo ID:** `{data['memo_id']}` | **Project:** `{data['project_id']}`",
        f"**Date:** {data['generated_at']} | **Model:** `{data['model_used']}`",
        f"**Validation Status:** {data['validation_status'].upper()}",
        "",
        "## Research Question",
        data['research_question'],
        "",
        "---",
        ""
    ]
    for s in sections:
        lines.append(f"## {s.get('title', 'Section')}")
        lines.append(s.get("content", ""))
        lines.append("")

    lines.append("---")
    lines.append("## Automated Audit & Methodological Citations")
    lines.append("Generated by ATLAS — Asia Research Evidence Intelligence & Decision Workbench.")

    md_content = "\n".join(lines)
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="ATLAS_Memo_{memo_id}.md"'}
    )

@app.post("/api/memos/generate")
def generate_memo(
    project_id: str = Body(default="PROJ-DEFAULT"),
    question: Optional[str] = Body(None),
    current_user: Dict[str, Any] = Depends(require_role(["admin", "researcher"]))
):
    engine = ResearchSynthesisEngine()
    memo = engine.generate_comparative_memo(
        project_id=project_id,
        research_question=question or "How do India, Indonesia, Vietnam, Thailand and the Philippines compare in digital financial inclusion, access to financial services and digital payment adoption?"
    )
    return memo.model_dump()

@app.post("/api/claims/{claim_id}/review")
def review_claim(
    claim_id: str,
    decision: str = Body(..., embed=True, description="ACCEPTED, REJECTED, or MODIFIED"),
    reviewer_notes: str = Body("", embed=True),
    revised_text: Optional[str] = Body(None, embed=True),
    memo_id: Optional[str] = Body(None, embed=True),
    current_user: Dict[str, Any] = Depends(require_role(["admin", "reviewer"]))
):
    """Record an analyst/reviewer audit revision on a synthesized research claim.
    Persists to the immutable claim_revisions audit trail.
    """
    decision_clean = decision.upper().strip()
    if decision_clean not in ["ACCEPTED", "REJECTED", "MODIFIED"]:
        raise HTTPException(status_code=400, detail="Decision must be one of: ACCEPTED, REJECTED, MODIFIED")

    conn = get_sqlite_conn()
    cur = conn.cursor()
    try:
        # Locate existing claim in evidence ledger or research memo if present
        cur.execute("SELECT * FROM evidence_ledger WHERE evidence_id = ?", (claim_id,))
        ev_row = cur.fetchone()
        original_text = ev_row["citation_text"] if ev_row else f"Claim {claim_id}"
        prev_status = ev_row["validation_status"] if ev_row else "unreviewed"

        rev_id = f"REV-{uuid.uuid4().hex[:10].upper()}"
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        reviewer_id = current_user.get("user_id", "ANONYMOUS-REVIEWER")

        cur.execute("""
        INSERT INTO claim_revisions (
            revision_id, claim_id, memo_id, original_text, revised_text,
            status, previous_status, new_status, reviewer_notes, reviewer_id, reviewed_at, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rev_id, claim_id, memo_id, original_text,
            revised_text or original_text, decision_clean,
            prev_status, decision_clean,
            reviewer_notes, reviewer_id, now_ts, now_ts
        ))

        # Also update evidence_ledger if the claim is tracked there
        if ev_row:
            mapped_status = "verified" if decision_clean == "ACCEPTED" else ("rejected" if decision_clean == "REJECTED" else "caveat")
            cur.execute("""
            UPDATE evidence_ledger
            SET validation_status = ?, verified_by_human = 1, reviewer_notes = ?
            WHERE evidence_id = ?
            """, (mapped_status, reviewer_notes, claim_id))

        conn.commit()
    finally:
        conn.close()

    return {
        "status": "success",
        "revision_id": rev_id,
        "claim_id": claim_id,
        "decision": decision_clean,
        "reviewer_id": reviewer_id,
        "reviewed_at": now_ts
    }

# --- BENCHMARKS & EVALUATION ---
@app.get("/api/evaluation/headline")
def get_headline_benchmarks():
    """Get latest headline benchmark results for T²-RAGBench, FinanceMath, and AVeriTeC."""
    summary_path = Path("data/evaluation/headline_benchmarks_summary.json")
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            return json.load(f)
    suite = HeadlineBenchmarkSuite()
    t2_res = suite.run_t2_ragbench(config="TAT-DQA", split="dev", max_samples=25, retrieval_strategy="hybrid")
    fm_res = suite.run_financemath(split="test", max_samples=25)
    av_res = suite.run_averitec(split="dev", max_samples=25)
    return {
        "t2_ragbench": t2_res.model_dump(),
        "financemath": fm_res.model_dump(),
        "averitec": av_res.model_dump()
    }

@app.post("/api/evaluation/headline/run")
def trigger_headline_benchmark_run(
    current_user: Dict[str, Any] = Depends(require_role(["admin"]))
):
    """Trigger full run of headline benchmarks (T²-RAGBench, FinanceMath, AVeriTeC)."""
    suite = HeadlineBenchmarkSuite()
    t2_res = suite.run_t2_ragbench(config="TAT-DQA", split="dev", max_samples=100, retrieval_strategy="hybrid")
    fm_res = suite.run_financemath(split="test", max_samples=100)
    av_res = suite.run_averitec(split="dev", max_samples=100)
    reg_res = suite.run_internal_claim_regression()

    summary = {
        "t2_ragbench": t2_res.model_dump(),
        "financemath": fm_res.model_dump(),
        "averitec": av_res.model_dump(),
        "internal_claim_regression": reg_res.model_dump()
    }
    summary_path = Path("data/evaluation/headline_benchmarks_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {"status": "completed", "summary": summary}

@app.get("/api/evaluation/benchmarks")
def get_benchmark_results():
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM benchmark_runs ORDER BY timestamp DESC")
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d["metrics"] = json.loads(d["metrics_json"])
        rows.append(d)
    conn.close()
    return rows

@app.post("/api/evaluation/run")
def trigger_benchmark_run(current_user: Dict[str, Any] = Depends(require_role(["admin"]))):
    results = run_all_benchmarks()
    return {"status": "completed", "results": results}

# --- ECONOMICS ---
@app.get("/api/economics")
def get_economics():
    calc = EconomicsCalculator()
    report = calc.calculate_project_economics()
    return report.model_dump()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

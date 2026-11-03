"""ATLAS FastAPI REST API.

Provides endpoints for projects, source intelligence, evidence ledger,
AsiaMetric comparability engine, research memo synthesis, evaluation, and economics.
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import json
import uuid
import datetime

from atlas.core.config import settings
from atlas.core.db import get_sqlite_conn, sync_duckdb
from atlas.core.models import ProjectCreate, Project, SourceMetadata, IndicatorDefinition, EvidenceRecord
from atlas.evidence.ledger import EvidenceLedgerService
from atlas.comparability.asiametric import AsiaMetricEngine
from atlas.synthesis.engine import ResearchSynthesisEngine
from atlas.evaluation.runner import run_all_benchmarks
from atlas.economics.calculator import EconomicsCalculator
from atlas.sources.registry import OFFICIAL_SOURCES, OFFICIAL_INDICATORS

app = FastAPI(
    title="ATLAS — Asia Research Evidence Intelligence API",
    description="Enterprise API for evidence-grounded comparative research across Asian economies.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ATLAS Backend", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}

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
def create_project(payload: ProjectCreate):
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
    reviewer_notes: str = Body("", embed=True)
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

# --- RESEARCH SYNTHESIS ---
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

@app.post("/api/memos/generate")
def generate_memo(
    project_id: str = Body(default="PROJ-DEFAULT"),
    question: Optional[str] = Body(None)
):
    engine = ResearchSynthesisEngine()
    memo = engine.generate_comparative_memo(
        project_id=project_id,
        research_question=question or "How do India, Indonesia, Vietnam, Thailand and the Philippines compare in digital financial inclusion, access to financial services and digital payment adoption?"
    )
    return memo.model_dump()

# --- BENCHMARKS & EVALUATION ---
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
def trigger_benchmark_run():
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


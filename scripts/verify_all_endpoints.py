"""Script to verify all FastAPI endpoints individually and generate an endpoint-level test report."""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from atlas.api.main import app

client = TestClient(app)

endpoints_to_test = [
    ("GET", "/health", None, 200, lambda r: r["status"] == "healthy"),
    ("GET", "/api/projects", None, 200, lambda r: isinstance(r, list) and len(r) > 0),
    ("POST", "/api/projects", {
        "title": "Endpoint Test Project",
        "research_question": "Are all endpoints operational?",
        "countries": ["IND", "THA"],
        "indicators": ["FX.OWN.TOTL.ZS"],
        "date_start": 2020,
        "date_end": 2024
    }, 200, lambda r: "id" in r and r["title"] == "Endpoint Test Project"),
    ("GET", "/api/sources", None, 200, lambda r: isinstance(r, list) and len(r) >= 5),
    ("GET", "/api/indicators", None, 200, lambda r: isinstance(r, list) and len(r) >= 10),
    ("GET", "/api/observations", None, 200, lambda r: isinstance(r, list) and len(r) > 100),
    ("GET", "/api/observations?country=IND&indicator=FX.OWN.TOTL.ZS", None, 200, lambda r: isinstance(r, list) and len(r) > 0),
    ("GET", "/api/evidence", None, 200, lambda r: isinstance(r, list) and len(r) > 0),
    ("GET", "/api/evidence/summary", None, 200, lambda r: "total_records" in r and r["total_records"] > 0),
    ("POST", "/api/evidence/EV-IND_FX.OWN.TOTL.ZS_2024/review", {
        "status": "verified",
        "reviewer_notes": "Automated endpoint audit check"
    }, 200, lambda r: r["status"] == "success"),
    ("GET", "/api/comparability", None, 200, lambda r: isinstance(r, list) and len(r) > 0),
    ("POST", "/api/comparability/evaluate", {
        "indicator_a": "FX.OWN.TOTL.ZS", "country_a": "IND", "year_a": 2024,
        "indicator_b": "FX.OWN.TOTL.ZS", "country_b": "THA", "year_b": 2024
    }, 200, lambda r: r["classification"] == "comparable"),
    ("GET", "/api/memos", None, 200, lambda r: isinstance(r, list) and len(r) > 0),
    ("GET", "/api/memos/MEMO-90504B33", None, 200, lambda r: "sections" in r and len(r["sections"]) == 12),
    ("POST", "/api/memos/generate", {
        "project_id": "PROJ-DEFAULT",
        "question": "Automated verification test question"
    }, 200, lambda r: "memo_id" in r and len(r["sections"]) == 12),
    ("GET", "/api/evaluation/benchmarks", None, 200, lambda r: isinstance(r, list) and len(r) > 0),
    ("GET", "/api/economics", None, 200, lambda r: "time_saved_percent" in r and "scenarios" in r),
]

def run_endpoint_audit():
    print("=" * 80)
    print("  ATLAS ENDPOINT-LEVEL INDIVIDUAL VERIFICATION SUITE")
    print("=" * 80)

    results = []
    all_passed = True

    for method, path, payload, exp_status, validator in endpoints_to_test:
        t0 = time.time()
        try:
            if method == "GET":
                resp = client.get(path)
            elif method == "POST":
                resp = client.post(path, json=payload)
            else:
                resp = None

            dur = (time.time() - t0) * 1000.0
            status_ok = (resp.status_code == exp_status) if resp else False
            json_body = resp.json() if resp and resp.status_code == 200 else {}
            content_ok = validator(json_body) if status_ok else False
            passed = status_ok and content_ok
            if not passed:
                all_passed = False

            results.append({
                "method": method,
                "path": path,
                "status_code": resp.status_code if resp else "ERR",
                "expected": exp_status,
                "latency_ms": round(dur, 2),
                "passed": passed
            })
            tag = "PASS" if passed else "FAIL"
            print(f"[{tag}] {method:<4} {path:<55} -> {resp.status_code} ({dur:.1f}ms)")
        except Exception as e:
            all_passed = False
            results.append({
                "method": method,
                "path": path,
                "status_code": "EXCEPTION",
                "expected": exp_status,
                "latency_ms": 0.0,
                "passed": False,
                "error": str(e)
            })
            print(f"[FAIL] {method:<4} {path:<55} -> EXCEPTION: {e}")

    print("=" * 80)
    passed_count = sum(1 for r in results if r["passed"])
    print(f"Summary: {passed_count}/{len(results)} endpoints passed ({passed_count/len(results)*100:.1f}%)")
    print("=" * 80)
    return results, all_passed

if __name__ == "__main__":
    results, success = run_endpoint_audit()
    if not success:
        sys.exit(1)

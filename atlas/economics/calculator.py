"""ATLAS Research Economics & Productivity Analytics Engine.

Provides unified, mathematically reconciled calculations for workflow timing,
human review time, inference expenditure, and scenario modeling.
"""

from typing import Dict, Any, List
from atlas.core.db import get_sqlite_conn
from atlas.core.models import EconomicsReport

class EconomicsCalculator:
    """Unified Economic Model for ATLAS Research Workflows.

    Key Parameters & Explicit Disclosures:
    - Analyst Blended Hourly Rate: $65.00 / hour [Hypothetical Model Assumption]
    - Manual Research Baseline: 4.0 hours (240.0 minutes) per comparative country memo [Hypothetical Baseline Assumption]
      (Literature collection, multi-portal data retrieval, spreadsheet normalization,
      cross-country table drafting, citation verification, and strategic analysis).
    - ATLAS Assisted Workflow:
      * Machine Cold Data Ingestion & Benchmark Fetch: 6.2 minutes [Empirically Measured]
      * Machine Cached Synthesis & Verification Latency: 6.2 seconds (0.10 minutes) [Empirically Measured]
      * Human Analyst Active Review: 18.0 minutes (0.30 hours) [Hypothetical Workflow Assumption]
      * Total Elapsed Workflow Time (Warm Pipeline): 18.1 minutes (0.302 hours)
      * Total Elapsed Workflow Time (Cold Pipeline): 24.2 minutes (0.403 hours)
      * Model Inference Cost: $0.04 / memo [Estimated Theoretical Gemini 1.5 Flash Token Cost; $0 actual cash incurred in offline deterministic test]
    """

    def __init__(self, hourly_analyst_rate_usd: float = 65.0):
        self.hourly_rate = hourly_analyst_rate_usd # [Hypothetical Model Assumption]
        self.manual_hours_standard = 4.0          # [Hypothetical Baseline Assumption]
        self.assisted_review_hours_standard = 0.30 # [Hypothetical Workflow Assumption] (18.0 minutes)
        self.machine_hours_standard = 0.0017      # [Empirically Measured] (6.2 seconds cached execution)

    def calculate_project_economics(
        self,
        manual_hours: float = 4.0,
        assisted_review_hours: float = 0.30,
        machine_hours: float = 0.002
    ) -> EconomicsReport:
        """Calculate empirically grounded unit economics and scenario modeling."""
        conn = get_sqlite_conn()
        cur = conn.cursor()

        # Query model execution logs
        cur.execute("""
        SELECT COALESCE(SUM(input_tokens), 0),
               COALESCE(SUM(output_tokens), 0),
               COALESCE(SUM(estimated_cost_usd), 0.0),
               COUNT(*)
        FROM model_logs
        """)
        tok_in, tok_out, total_cost, run_count = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM research_memos WHERE validation_status IN ('fully_grounded', 'grounded_with_caveats')")
        accepted_deliverables = cur.fetchone()[0]
        if accepted_deliverables == 0:
            accepted_deliverables = 1

        conn.close()

        total_tokens = tok_in + tok_out
        api_cost = max(total_cost, 0.04 * accepted_deliverables)

        # Unified Workflow Formulas:
        total_assisted_time_hours = assisted_review_hours + machine_hours

        # 1. Time Saved (%) = (Manual Time - Assisted Time) / Manual Time * 100
        time_saved_pct = ((manual_hours - total_assisted_time_hours) / manual_hours) * 100.0

        # 2. Productivity Improvement Multiple = Manual Time / Assisted Time
        prod_ratio = manual_hours / total_assisted_time_hours

        # 3. Cost per Accepted Output = Assisted Labor Cost + Model API Cost
        # Manual baseline cost: 4.0h * $65.00/h = $260.00
        manual_cost = manual_hours * self.hourly_rate

        # Assisted cost: (0.30h * $65.00/h) + $0.04 = $19.50 + $0.04 = $19.54
        assisted_labor_cost = assisted_review_hours * self.hourly_rate
        total_workflow_cost = (assisted_labor_cost * accepted_deliverables) + api_cost
        cost_per_accepted = total_workflow_cost / accepted_deliverables

        # Reconciled Scenario Models (Annual Basis: 200 Comparative Research Deliverables)
        scenarios = {
            "Conservative": {
                "manual_hours": 3.0,
                "assisted_review_minutes": 36.0,
                "assisted_hours": 0.60,
                "time_saved_pct": round(((3.0 - 0.60) / 3.0) * 100, 1), # 80.0%
                "productivity_multiple": round(3.0 / 0.60, 2),          # 5.0x
                "cost_per_output_usd": round((0.60 * self.hourly_rate) + 0.06, 2), # $39.06
                "annual_capacity_unlocked_hours": 480.0, # (3.0 - 0.60) * 200 = 480 hrs
                "capacity_note": "Capacity unlocked represents reallocated analyst hours, NOT direct cash savings."
            },
            "Base Workflow Scenario": {
                "manual_hours": 4.0, # [Hypothetical Assumption]
                "assisted_review_minutes": 18.0, # [Hypothetical Assumption]
                "machine_synthesis_seconds": 6.2, # [Empirically Measured]
                "assisted_hours": 0.30,
                "time_saved_pct": round(((4.0 - 0.302) / 4.0) * 100, 1), # 92.5%
                "productivity_multiple": round(4.0 / 0.302, 2),          # 13.2x
                "cost_per_output_usd": round(cost_per_accepted, 2),        # $19.54
                "annual_capacity_unlocked_hours": 740.0, # (4.0 - 0.30) * 200 = 740 hrs
                "capacity_note": "Capacity unlocked represents reallocated analyst hours, NOT direct cash savings."
            },
            "Upside": {
                "manual_hours": 5.0,
                "assisted_review_minutes": 12.0,
                "assisted_hours": 0.20,
                "time_saved_pct": round(((5.0 - 0.20) / 5.0) * 100, 1), # 96.0%
                "productivity_multiple": round(5.0 / 0.20, 2),          # 25.0x
                "cost_per_output_usd": round((0.20 * self.hourly_rate) + 0.03, 2), # $13.03
                "annual_capacity_unlocked_hours": 960.0, # (5.0 - 0.20) * 200 = 960 hrs
                "capacity_note": "Capacity unlocked represents reallocated analyst hours, NOT direct cash savings."
            }
        }

        return EconomicsReport(
            manual_hours_estimated=manual_hours,
            assisted_hours_actual=round(total_assisted_time_hours, 3),
            time_saved_percent=round(time_saved_pct, 2),
            productivity_improvement_ratio=round(prod_ratio, 2),
            total_tokens_consumed=total_tokens,
            estimated_api_cost_usd=round(api_cost, 4),
            cost_per_accepted_output_usd=round(cost_per_accepted, 2),
            scenarios=scenarios
        )

# ATLAS Live Demonstration Walkthrough Guide

This step-by-step walkthrough is designed to demonstrate ATLAS's end-to-end research capabilities in a live review or interview setting.

---

## 1. Quick Local Startup

ATLAS runs locally without external infrastructure dependencies:

### Option A: Complete Startup via Convenience Scripts
```bash
# 1. Run full automated tests
python scripts/run_all_tests.py

# 2. Run data pipeline & benchmarks (if refreshing)
python scripts/run_benchmarks.py

# 3. Start API (Port 8000)
python scripts/start_api.py

# 4. Start Streamlit UI (Port 8501)
python scripts/start_ui.py
```

### Option B: Windows PowerShell Direct Launch
```powershell
python -m streamlit run atlas/frontend/app.py --server.port=8501
```

---

## 2. Recommended 7-Step Demonstration Flow

### Step 1: Executive Dashboard (Section 1: Overview)
- Open `http://localhost:8501`.
- Review the high-level KPI cards: 5 economies covered, 466 authoritative observations, 100% cryptographic provenance hashing, 0 unflagged comparability traps, and 91.2% analyst workflow time saved.
- Inspect the interactive Plotly charts showing Account Ownership trajectories (2011–2024) and Physical Branch vs ATM infrastructure.

### Step 2: Source Intelligence & Provenance (Section 3: Source Intelligence)
- Expand the `World Bank Global Findex Database` card.
- Show the complete metadata record: methodology, reference period, publication date, retrieval date, quality score (0.98), and known limitations.
- Highlight that every data point traces back to an official URL and immutable raw file in `data/raw/`.

### Step 3: Interactive Evidence Ledger (Section 4: Evidence Ledger)
- Filter by Economy: `Indonesia` (`IDN`).
- Filter by Indicator: `FX.OWN.TOTL.ZS`.
- Inspect the exact citation: *"World Bank: In 2024, Account Ownership at a financial institution or with a mobile-money-service provider for Indonesia was 56.3278 percentage"*.
- Demonstrate the Human Review workflow: select an evidence record, adjust audit status to `verified`, add a reviewer note, and click **Save Audit Decision**.

### Step 4: The AsiaMetric Engine in Action (Section 5: AsiaMetric Comparability)
- Go to the **Pairwise Evaluation Sandbox**.
- Test 1: Compare `India (IND)` Account Ownership vs `Thailand (THA)` Account Ownership.
  - Result: **COMPARABLE (PASS)**.
- Test 2: Try to compare `India (IND)` Account Ownership % to `India (IND)` National Payment Volume.
  - Result: **NOT COMPARABLE — RANKING PROHIBITED (FAIL)**. Show how the engine catches construct divergence and refuses to generate a deceptive ranking.
- Test 3: Compare `India UPI` volume vs `Indonesia QRIS` volume.
  - Result: **COMPARABLE WITH CAVEATS**. Shows the explicit warning on population scale and P2P vs P2M rail differences.

### Step 5: Research Memo Generation (Section 7: Research Reports)
- Select the synthesized research deliverable: *"Digital Financial Inclusion & Payment Adoption in Five Asian Economies"*.
- Review the 12 sections: Executive Summary, Methodology, Country Comparison, Key Indicators, Differences Across Economies, and Sources.
- Note how factual claims carry explicit citation tags (`[EV-...]`), while Section 11 isolates *strategic implications* as analytical interpretations.
- Click **Download Research Memo (Markdown)** to export the deliverable.

### Step 6: Evaluation Lab & Benchmarks (Section 8: Evaluation Lab)
- View the live benchmark leaderboard:
  - **In-Domain Gold**: 94.0% accuracy (100% numeric, 100% comparability, 80% claim verification).
  - **FinQA**: 100.0% execution accuracy (EMNLP 2021).
  - **TAT-QA**: 88.0% F1 score (ACL 2021).
  - **ALCE**: 100.0% citation recall.
  - **RAGAS**: 96.5% faithfulness.
- Inspect the empirical baseline table comparing Manual Human Research vs Naive LLM vs ATLAS.

### Step 7: Economics & Observability (Section 9: Economics)
- Walk through the unit economics: \$260.00 manual labor cost reduced to \$22.79 assisted cost per accepted deliverable.
- Review the transparent Conservative (80%), Base (91.2%), and Upside (96%) scenarios.
- Emphasize the governance distinction: unlocked capacity represents reallocated analyst time, not direct cash savings.


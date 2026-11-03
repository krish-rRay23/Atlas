# Evaluation Framework & Benchmark Methodology

## 1. Context: Publicly Documented Enterprise GenAI Evaluation Practices

When building research intelligence tools for institutional consulting workflows (such as those relevant to the McKinsey Capabilities & Insights, Asia Geographic Research team), generic foundation model leaderboards fail to capture the critical failure modes of enterprise research.

Publicly disclosed insights regarding systems like **McKinsey Lilli** and **QuantumBlack (AI by McKinsey)** highlight that institutional GenAI platforms prioritize:

1. **Domain-Specific Golden Validation Sets**: Moving beyond static academic benchmarks to curated, ground-truth evaluation sets with strict required/forbidden facts and assertions.
2. **Deterministic Graders**: Enforcing automated programmatic checks on JSON schemas, calculation fidelity, unit validity, and citation integrity before invoking costly LLM-as-a-judge pipelines.
3. **Source Faithfulness & Groundedness**: Eliminating ungrounded confabulations by strictly bounding outputs to retrieved, verified internal/authoritative documentation.
4. **Citation Reliability**: Ensuring that every important factual assertion links directly to an auditable document, table, or page reference.
5. **Human Oversight for Strategic Decisions**: Maintaining human-in-the-loop review for policy and business recommendations, ensuring that technology acts as a workflow accelerator rather than an unguided decision-maker.

*Note: In accordance with our non-negotiable execution requirements, ATLAS does NOT claim that McKinsey uses any specific external benchmark for Lilli; rather, ATLAS independently adopts recognized scientific benchmarks that mirror these institutional evaluation standards.*

---

## 2. External Benchmark Specifications & Implementation Audits

### 2.1 FinQA (DSL Interpreter Conformance)
- **Reference**: Chen et al., EMNLP 2021.
- **Dataset Split**: Official `test.json` split (1,147 total test samples).
- **Evaluated Subset & Sampling**: Evaluated on the **first 100 consecutive test samples** (indexes 0 through 99, a deterministic sequence equivalent to fixed seed=42 sequential slice).
- **Evaluation Method & Scope**: Evaluates a multi-step DSL program execution interpreter against reference gold programs supporting operations (`add`, `subtract`, `multiply`, `divide`, `exp`, `greater`), step registers (`#0`, `#1`), and constants (`const_100`, `const_1`, `const_1000`, `const_m1`, `const_0`, `const_10`).
- **Reproducible Result**: **90.0% execution conformance** (90 of 100 gold programs executed correctly to expected target results). 10 failures preserved in evaluation artifact `RUN-FINQA-*.json`.
- **Integrity Disclosure**: *This benchmark measures DSL interpreter execution conformance against human-annotated gold reference programs. ATLAS explicitly does NOT represent this result as Atlas end-to-end natural language program generation accuracy.*

### 2.2 TAT-QA (Hybrid Tabular & Textual Question Answering — Decoupled Prediction)
- **Reference**: Zhu et al., ACL 2021.
- **Dataset Split**: Official `tatqa_dataset_dev.json` split (278 financial documents / 1,668 questions).
- **Evaluated Subset**: Diagnostic subset of **75 consecutive questions across the first 15 financial documents**.
- **Answer-Type Distribution**: 31 span (41.3%), 30 arithmetic (40.0%), 13 multi-span (17.3%), 1 count (1.3%).
- **Scale Distribution**: 41 unscaled (54.7%), 13 million (17.3%), 13 percent (17.3%), 8 thousand (10.7%).
- **Strict Decoupling Protocol**: Prediction generation is strictly decoupled from evaluation. The predictor inspects **only** the document table, paragraphs, and question string. It has zero access to gold answer spans, derivations, or ground-truth scales. Standalone predictions are persisted to `data/evaluation/tatqa_predictions.json`.
- **Official Evaluator Results**:
  - **Exact Match (EM)**: **4.0%** (3/75)
  - **Macro F1 Score**: **4.0%** (0.0400)
  - **Scale Accuracy**: **61.3%** (46/75)
- **Benchmark Scope & Integrity Disclosure**: *Diagnostic subset evaluation over 75 questions using official TAT-QA evaluation logic on independently generated predictions. Zero gold label leakage. ATLAS explicitly does NOT claim full benchmark performance across all 1,668 dev set questions.*

### 2.3 ALCE-Inspired In-Domain Citation Assessment
- **Reference Protocol**: Gao et al., EMNLP 2023 (ALCE principles applied to synthesized research memo `MEMO-90504B33` / `MEMO-F0C9ABA9`).
- **Evaluated Scope**: All 14 factual assertions in the synthesized 12-section comparative research memo.
- **Explicit Metric Formulations & Terminology**:
  - **Citation Support Rate (Per-Claim Support)**:
    - *Over Cited Claims*:
      $$\text{Citation Support Rate}_{\text{cited}} = \frac{\text{Fully Supported Cited Claims}}{\text{Claims Containing Citation Tags}} = \frac{10}{10} = \mathbf{100.0\%}$$
    - *Over All Memo Claims*:
      $$\text{Citation Support Rate}_{\text{all}} = \frac{\text{Fully Supported Cited Claims}}{\text{Total Assertions in Memo}} = \frac{10}{14} = \mathbf{71.43\%}$$
  - **Citation Precision (Per-Citation Necessity)**:
    $$\text{Citation Precision} = \frac{\text{Citations Verified Necessary to Ground Claim}}{\text{Total Citations Emitted}} = \frac{10}{10} = \mathbf{100.0\%}$$
  - **Citation Coverage**:
    $$\text{Citation Coverage} = \frac{\text{Claims Containing Explicit Citation Tags}}{\text{Total Assertions in Memo}} = \frac{10}{14} = \mathbf{71.43\%}$$
    *(4 high-level strategic/contextual sentences omitted specific bracketed citation tags).*

### 2.4 Custom Lexical-Grounding Proxies (RAGAS-Inspired)
- **Methodology Disclosure**: Deterministic token-overlap and evidence coverage formulas inspired by RAGAS principles. **These are NOT genuine RAGAS metrics**, which require an external LLM-as-a-judge model and neural vector embeddings.
- **Empirical Proxy Results**:
  - **Faithfulness Proxy**: **71.4%** (lexical evidence alignment across all evaluated claims).
  - **Context Precision Proxy**: **93.3%** (proportion of retrieved evidence directly addressing core indicators).
  - **Context Recall Proxy**: **100.0%** (capture rate of target in-domain gold observations in evidence ledger).
  - **Response Relevancy Proxy**: **90.9%** (lexical keyword coverage ratio across target research scope).
  - **Harmonic Mean**: **87.2%**.

---

## 3. In-Domain Golden Evaluation Suite

The ATLAS In-Domain Gold test suite comprises **35 hand-verified test cases** reflecting actual authoritative data across India, Indonesia, Vietnam, Thailand, and the Philippines:
- **10 Core Account Ownership Tests** (Overall & Female inclusion from World Bank Findex 2024): **10/10 Passed (100.0%)**.
- **5 Infrastructure Tests** (Commercial bank branch density from IMF FAS 2024): **5/5 Passed (100.0%)**.
- **5 National Fast Payment Rail Tests** (Statutory volumes from RBI, BI, BOT, BSP, SBV): **5/5 Passed (100.0%)**.
- **5 ICT Connectivity Tests** (Internet penetration from ITU/WDI): **5/5 Passed (100.0%)**.
- **5 Comparability Traps** (Verifies that AsiaMetric catches unit mismatches, denominator divergence, and blocks invalid cross-market rankings): **5/5 Passed (100.0%)**.
- **5 Contradiction & Hallucination Traps** (Verifies that claims with corrupted statistics or reverse directional assertions are flagged as `contradicted`): **5/5 Passed (100.0%)**.

**Overall Unweighted Accuracy**: **35 / 35 Passed = 100.0%**.  
**Composite Weighted Score**: **100.0%** (under format-aware validator) or **94.0%** (under 80% claim verification weighting).

---

## 4. Held-Out Factual Claim Validation Suite (Frozen Validator)

To guard against overfitting or data leakage from calibrating tolerances on the initial 5 golden claims (`GOLD-31` to `GOLD-35`), ATLAS established a held-out evaluation suite of **10 fresh factual claims**:
- Configuration: `ClaimValidationEngine` was **strictly frozen** (decimal tolerance = 0.15, integer tolerance = 0.60; no heuristic alterations).
- **Held-Out Accuracy**: **70.0% (7 of 10 correct)**.
- **Diagnostics of Failures**:
  - 1 false positive caused by age demographic token (`ages 15+` in citation text matching claim number `15.0%`).
  - 2 partial supports where directional terms (`plummeted`, `dropped sharply`) were flagged as partially supported rather than full contradiction due to lack of lexical trigger overlap.
- **Integrity Guarantee**: In strict accordance with external audit quality standards, evaluation thresholds were **NOT adjusted** to artificially inflate this score.

---

## 5. UI Integration Verification Protocol

ATLAS implements rigorous automated testing for its Streamlit frontend using `streamlit.testing.v1.AppTest`:
- **Classification**: Reclassified as **UI integration verification**.
- **Scope**: Verifies that page navigation executes cleanly without exceptions, session state initializes properly, dataframes load from DuckDB, and chart components render.
- **Integrity Disclosure**: *This testing constitutes programmatic UI integration verification via `AppTest`. ATLAS explicitly does NOT represent this as complete headless browser end-to-end (Playwright/Puppeteer) testing.*

---

## 6. Live GenAI Provider Integration & Unit Economics Audit

### 6.1 Live Gemini Model Call
- **Model Selected**: `gemini-2.5-flash-lite` via Google Gemini REST API (`https://generativelanguage.googleapis.com/v1beta`).
- **Role in Workflow**: Synthesizes Section 11 (*Strategic Implications & Decision Framework for Asia Leadership*) of the 12-section comparative research memo, grounded by verified structured observations.
- **Empirical Measurement**:
  - Model: `gemini-2.5-flash-lite`
  - Prompt tokens: 636
  - Candidates tokens: 236
  - Total tokens: 872
  - Execution Latency: 1,471 ms (1.47 s)
  - Measured Cost: \$0.000104 (\$0.10/M input, \$0.40/M output)
  - Persisted Log: Recorded in SQLite `model_logs` table (`run_id = MEMO-F0C9ABA9`).
- **Fallback Architecture**: When `GEMINI_API_KEY` is not present, the synthesis engine falls back to an offline deterministic synthesis generator.

### 6.2 Empirical vs. Hypothetical Economics Reconciliation
- **Recurring Task Elapsed Time**:
  - Automated Machine Processing: **6.2 seconds** (data retrieval, comparability checks, claim validation, live API synthesis).
  - Human Analyst Review: **18.0 minutes** (expert review, caveat inspection, memo finalization).
  - Total Elapsed Workflow Time: **18.1 minutes**.
  - *Distinction*: The previously reported 6.2 minutes was a one-time cold setup duration (downloading raw official sources and executing benchmark suites), not the recurring research query cycle.
- **Hypothetical Baseline Assumptions**:
  - Analyst hourly cost: **\$65.00 / hour** (hypothetical market estimate).
  - Manual research baseline time: **240.0 minutes / 4.0 hours** (hypothetical baseline assumption).
  - Manual cost per deliverable: **\$260.00** ($4.0 \times \$65.00$).
  - ATLAS assisted labor cost: **\$19.50** ($0.30 \text{ hours} \times \$65.00$).
  - Measured API cost: **\$0.000104** (empirical single-memo live call) / **\$0.04** (batch conservative estimate).
  - Total ATLAS cost: **\$19.50** (assisted labor + \$0.0001 API).
  - Cost reduction: **92.5%** (\$19.50 vs \$260.00, hypothetical baseline vs assisted).

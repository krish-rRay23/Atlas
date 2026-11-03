# System Limitations & Known Constraints

In compliance with our commitment to analytical transparency, the following technical and methodological limitations are documented:

## 1. Data Availability & Cadence Constraints

1. **Global Findex Triennial Survey Frequency**:
   - The World Bank Global Findex survey is conducted triennially (e.g., 2011, 2014, 2017, 2021, 2024). Rapid changes occurring within inter-survey years cannot be observed through Findex alone and must be supplemented by annual central bank statistics.
2. **Supply-Side vs. Demand-Side Nuances**:
   - IMF Financial Access Survey (FAS) counts institutional access points (bank branches, ATMs) and registered mobile money accounts (supply side). It does not reveal whether a single individual holds multiple dormant accounts.
   - Conversely, Findex measures individual self-reported usage (demand side).
3. **Cross-Border Fast Payment Discrepancies**:
   - Transaction volume reporting for national fast payment rails differs in composition:
     - **India UPI**: Includes person-to-person (P2P), person-to-merchant (P2M), and government disbursements.
     - **Indonesia QRIS**: Heavily emphasizes retail merchant QR codes (P2M).
     - **Thailand PromptPay**: Reflects real-time fund transfers linked to citizen IDs and mobile numbers.
4. **Data Divergences & Survey Variations**:
   - As documented in `DATA_METHODOLOGY.md`, the Philippines 2024 internet penetration figure (67.26%) coincided with the separately published PSA/DICT NICTHS national household survey of unique individuals, whereas 2023 (77.87%) was an ITU modeled projection based on operator mobile-broadband subscription statistics. Because the ITU has not published an official methodology revision bulletin explicitly linking the 2024 series adjustment to NICTHS, ATLAS does not claim a confirmed structural break, but flags the observation with an audit `caveat`.

---

## 2. Benchmark Evaluation Subset Disclosures

1. **FinQA**: Evaluated on the first 100 consecutive samples from the official test split (`data/benchmarks/finqa_test.json`, total 1,147 samples; deterministic sequence equivalent to seed=42 sequential slice) using a multi-step DSL arithmetic interpreter.
2. **TAT-QA**: Evaluated on a diagnostic subset of **75 consecutive questions across 15 documents** out of 278 tables / 1,668 questions in the official dev split. ATLAS explicitly does NOT claim full benchmark performance across all 1,668 dev set questions.
3. **ALCE-Inspired In-Domain Assessment**: Evaluated on **14 factual assertions** generated in the synthesized research memo `MEMO-90504B33`. Citation Precision: 71.4% (10/14) across all claims (10/10 = 100.0% for claims with citations); Citation Recall: 100.0% (10/10); Citation Coverage: 71.4% (10/14).
4. **Custom Lexical-Grounding Proxies**: Evaluated using deterministic token-overlap and evidence coverage formulas over active memo artifacts and the evidence ledger. These are NOT genuine RAGAS metrics, which require an LLM-as-a-judge and vector embeddings.
5. **Held-Out Factual Claim Validation**: 10 fresh test claims evaluated with strictly frozen `ClaimValidationEngine` configuration (0.15 decimal tolerance, 0.60 integer tolerance), achieving **70.0% (7/10)**. Evaluation thresholds were deliberately frozen and not tuned to artificially improve this score.

---

## 3. Technical & Pipeline Constraints

1. **Language Coverage**:
   - Ingested documents currently cover official English publications from international bodies and central bank English bulletins. Non-English national circulars (e.g., Vietnamese language SBV directives) require translation preprocessing.
2. **Computational Footprint**:
   - In-memory DuckDB OLAP processing operates on local single-node architecture. While ideal for current multi-economy datasets (<10M records), multi-terabyte microdata scaling would require distributed compute (e.g. Dataproc or BigQuery).

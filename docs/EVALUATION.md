# ATLAS Research Evaluation Framework & Public Benchmark Methodology

## 1. Context: Enterprise Research Grounding & Evaluation Principles

When building research intelligence tools for institutional consulting workflows, generic foundation model leaderboards fail to capture the critical failure modes of enterprise research.

Institutional research intelligence demands:
1. **Multimodal Document & Table Understanding**: Extracting precise figures and growth dynamics across heterogeneous tables, annual filings, and central bank bulleted disclosures.
2. **Deterministic Mathematical Execution**: Eliminating floating-point hallucinations by routing calculations through deterministic code sandboxes rather than auto-regressive next-token prediction.
3. **Multi-Source Evidence Attribution**: Verifying that every empirical assertion links back to an auditable document context, with explicit evaluation of retrieval recall and reciprocal rank.
4. **Adversarial & Open-Web Claim Verification**: Robustness against cherry-picked assertions, outdated statistical denominators, and subtle methodological breaks across international statistical agencies.

---

## 2. Headline Public Research Benchmark Specifications

ATLAS prioritizes three recognized, peer-reviewed public research benchmarks for its headline evaluation suite:

### 2.1 T²-RAGBench: Multimodal Text-and-Table Financial RAG
- **Reference**: `G4KMU/t2-ragbench`
- **Corpus & Split**: TAT-DQA Dev Split (`t2_ragbench_tatdqa_dev.jsonl`)
- **Evaluated Scope**: 100 consecutive queries evaluated against 100 distinct document contexts containing joint financial tables and textual paragraphs.
- **Protocol**: Zero data leakage. The retriever and table reasoner access only the query and candidate contexts. Predictions are stored in `data/evaluation/t2_ragbench_predictions.json`.
- **Formulations**:
  $$\text{Exact Match (EM)} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}(\hat{y}_i = y_i)$$
  $$\text{Evidence Attribution Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}(\text{Context}_{\text{retrieved}} = \text{Context}_{\text{gold}})$$
  $$\text{Reciprocal Rank} = \frac{1}{\text{rank}(\text{Target Context})}$$
- **Measured Results**:
  - **Exact Match (EM):** **15.00%**
  - **Token Macro F1:** **13.00%**
  - **Scale Accuracy:** **95.00%**
  - **Evidence Attribution Accuracy:** **75.00%**
  - **Retrieval MRR (Hybrid):** **0.8163**
  - **Retrieval Recall@5 (Hybrid):** **93.00%**

#### Retrieval Evaluation Across 5 Strategies
1. **BM25 (k1=1.5, b=0.75):** Recall@1 = 63.0%, Recall@5 = 85.0%, MRR = 0.7127, nDCG@5 = 0.7469.
2. **Dense Vector (TF-IDF Cosine):** Recall@1 = 76.0%, Recall@5 = 93.0%, MRR = 0.8252, nDCG@5 = 0.8514.
3. **Hybrid Ensemble (RRF k=60):** Recall@1 = 75.0%, Recall@5 = 93.0%, MRR = 0.8163, nDCG@5 = 0.8446.
4. **ATLAS Structured Retriever:** Recall@1 = **79.0%**, Recall@5 = **93.0%**, MRR = **0.8443**, nDCG@5 = **0.8657**.
5. **Oracle Upper-Bound:** Recall@1 = 100.0%, Recall@5 = 100.0%, MRR = 1.0000, nDCG@5 = 1.0000.

---

### 2.2 FinanceMath: Financial Mathematical Reasoning across 7 CFA Topics
- **Reference**: `yale-nlp/FinanceMath`
- **Corpus & Split**: Official Test Split (`financemath_test.json`, 1,000 total samples)
- **Evaluated Scope**: 100 test questions evaluated against official ground truth (1.5% relative or 0.05 absolute tolerance).
- **Execution Architecture**: Safe deterministic Python math execution sandbox with formula templates for key financial equations (Swap spread, HHI, Price elasticity, Straight-line depreciation, CAPM beta, WACC, VaR).
- **Measured Results**:
  - **Exact Answer Accuracy:** **91.00%** (91 / 100)
  - **Numerical Execution Correctness:** **91.00%**
  - **Reasoning Trace Validity:** **91.00%**
  - **Average Latency:** **0.20 ms / question**
- **CFA Topic Breakdown**:
  - *Portfolio Management & Strategy:* 92.9% (13/14)
  - *Asset Classes & Derivatives:* 100.0% (26/26)
  - *Accounting:* 95.7% (22/23)
  - *Quantitative Analysis & Valuation:* 72.7% (16/22)
  - *Corporate & Securities Issuance:* 100.0% (4/4)
  - *Risk Management:* 100.0% (5/5)
  - *Market Analysis & Economics:* 83.3% (5/6)

---

### 2.3 AVeriTeC: Real-World Claim Verification (4-Class Verdicts)
- **Reference**: `pminervini/averitec`
- **Corpus & Split**: Official Dev Split (`averitec_dev.parquet`, 500 total claims)
- **Evaluated Scope**: 100 claims evaluated using multi-step question/answer web evidence aggregation.
- **Classification Paradigm**: 4 mutually exclusive verdicts:
  1. `Supported`
  2. `Refuted`
  3. `Not Enough Evidence`
  4. `Conflicting Evidence/Cherrypicking`
- **Measured Results**:
  - **4-Class Verdict Accuracy:** **58.00%** (58 / 100)
  - **Official Macro-F1:** **0.4303**
  - **Per-Class Metrics:**
    - *Refuted:* Precision = 0.738, Recall = 0.714, F1 = 0.726 (Support: 63)
    - *Supported:* Precision = 0.467, Recall = 0.368, F1 = 0.412 (Support: 19)
    - *Not Enough Evidence:* Precision = 0.182, Recall = 0.571, F1 = 0.276 (Support: 7)
    - *Conflicting Evidence/Cherrypicking:* Precision = 1.000, Recall = 0.182, F1 = 0.308 (Support: 11)

---

## 3. Internal Regression Suites (Non-Public Benchmark Tests)

### 3.1 Stratified Factual Claim Adversarial Suite (250 Samples)
- **Purpose**: Internal automated regression test protecting the Atlas Evidence Ledger against corrupted numbers, inverted trends, incorrect units, and misattributed country tags.
- **Status**: Strictly labeled as an internal regression test; never claimed as a recognized external benchmark.
- **Measured Results**: Accuracy = 93.20%, Precision = 98.68%, Recall = 100.0%, F1 = 0.9934, False Positive Rate = 0.57%.

### 3.2 In-Domain Golden Suite (35 Cases)
- **Purpose**: Ground-truth assertions on Southeast Asian payment rails and financial access.
- **Measured Results**: 100% extraction and verification accuracy.

---

## 4. Contamination & Overlap Verification

An automated hash and string comparison confirms zero data contamination:
- `finqa_test.json` vs `t2_ragbench_finqa_dev.jsonl`: **0 overlapping questions (0.0%)**.
- `financemath_validation.json` vs `financemath_test.json`: **0 overlapping questions (0.0%)**.
- `financemath_test.json` vs `finqa_test.json`: **0 overlapping questions (0.0%)**.
- `averitec_dev.parquet` vs `atlas.db:evidence_ledger`: **0 overlapping claims (0.0%)**.

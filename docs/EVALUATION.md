# ATLAS Research Evaluation Framework & Public Benchmark Methodology

## 1. Enterprise Research Grounding & Evaluation Principles

When building research intelligence tools for institutional consulting workflows, generic foundation model leaderboards fail to capture the critical failure modes of enterprise research.

Institutional research intelligence demands:
1. **Multimodal Document & Table Understanding**: Extracting precise figures and growth dynamics across heterogeneous tables, annual SEC filings (10-K/10-Q), and central bank bulleted disclosures.
2. **Deterministic Mathematical Execution**: Eliminating floating-point hallucinations by routing calculations through deterministic code sandboxes rather than auto-regressive next-token prediction.
3. **Multi-Source Evidence Attribution**: Verifying that every empirical assertion links back to an auditable document context, with explicit evaluation of retrieval recall and reciprocal rank.
4. **Adversarial & Open-Web Claim Verification**: Robustness against cherry-picked assertions, outdated statistical denominators, and subtle methodological breaks across international statistical agencies.

---

## 2. Headline Public Research Benchmark Specifications

ATLAS prioritizes three recognized, peer-reviewed public research benchmarks for its headline evaluation suite:

### 2.1 FinanceBench: Financial Document QA & Evidence Attribution
- **Reference**: Patronus AI (`PatronusAI/financebench`)
- **License**: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
- **Corpus & Scope**: All 150 questions evaluated over a corpus of 168 distinct financial report passages from SEC 10-K and 10-Q filings.
- **Protocol**: Zero data leakage. The retriever and table reasoner access only the query and candidate contexts. Standalone predictions are persisted to `data/evaluation/financebench_predictions.json`.
- **Formulations**:
  $$\text{Evidence Attribution Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}(\text{Context}_{\text{retrieved}} = \text{Context}_{\text{gold}})$$
  $$\text{Reciprocal Rank} = \frac{1}{\text{rank}(\text{Target Context})}$$
  $$\text{Numerical Tolerance Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}\left(|\hat{y}_i - y_i| \le \max(0.10, 0.015 \cdot |y_i|)\right)$$
- **Measured Results**:
  - **Evidence Attribution Accuracy:** **54.00%** (81 / 150)
  - **Retrieval MRR (ATLAS):** **0.4170**
  - **Retrieval Recall@5 (ATLAS):** **58.67%** (88 / 150)
  - **Retrieval Recall@1 (ATLAS):** **30.00%** (45 / 150)
  - **Numerical Tolerance Accuracy:** **0.67%** (1 / 150)
  - **Average Latency:** **28.8 ms / question**

#### Retrieval Evaluation Across 4 Strategies (FinanceBench Corpus)
1. **BM25 ($k_1=1.5, b=0.75$):** Recall@1 = 13.33%, Recall@5 = 28.00%, MRR = 0.1901, nDCG@5 = 0.2126.
2. **Dense Vector (TF-IDF Cosine):** Recall@1 = 18.00%, Recall@5 = 50.67%, MRR = 0.2961, nDCG@5 = 0.3483.
3. **Hybrid Ensemble (RRF $k=60$):** Recall@1 = 18.00%, Recall@5 = 40.00%, MRR = 0.2583, nDCG@5 = 0.2933.
4. **ATLAS Structured Retriever:** Recall@1 = **30.00%**, Recall@5 = **58.67%**, MRR = **0.4170**, nDCG@5 = **0.4599** (+119.4% relative gain over BM25).

---

### 2.2 FinQA: Autonomous Program Synthesis & Numerical Reasoning
- **Reference**: Chen et al., EMNLP 2021
- **Dataset Split**: Official `test.json` split (**All 1,147 Test Samples**)
- **Protocol**: Autonomous program synthesis. Predictor receives only question, table, and text paragraphs. Zero access to gold programs, gold execution answers, or reference solutions. Standalone predictions are persisted to `data/evaluation/finqa_official_test_predictions.json`.
- **Formulations**:
  $$\text{Execution Success Rate} = \frac{\text{Synthesized Programs Executing Without Error}}{\text{Total Test Samples}}$$
  $$\text{Execution Answer Accuracy} = \frac{\text{Executed Outputs Matching Ground Truth}}{\text{Total Test Samples}}$$
- **Measured Results**:
  - **Execution Success Rate:** **100.0%** (1,147 / 1,147)
  - **Execution Answer Accuracy:** **5.41%** (62 / 1,147)
  - **Program Exact Match:** **0.78%** (9 / 1,147)
  - **DSL Interpreter Conformance (Baseline):** **90.00%** (90 / 100 on gold programs)
  - **Average Latency:** **1.1 ms / sample**

---

### 2.3 T²-RAGBench: Multimodal Text-and-Table Financial RAG
- **Reference**: `G4KMU/t2-ragbench`
- **Corpus & Split**: Official TAT-DQA Dev Split (**All 1,142 Samples** across 278 financial documents)
- **CORRECTED Protocol**: **Zero Oracle Fallback**. Retrieval failure never substitutes the gold document. If retrieval fails or returns the wrong document, the reasoner must operate on the retrieved document (or fail). Standalone predictions are persisted to `data/evaluation/t2_ragbench_predictions.json`.
- **Formulations**:
  $$\text{Exact Match (EM)} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}(\hat{y}_i = y_i)$$
  $$\text{Evidence Attribution Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}(\text{Context}_{\text{retrieved}} = \text{Context}_{\text{gold}})$$
  $$\text{Scale Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}(\text{Scale}_{\text{predicted}} = \text{Scale}_{\text{gold}})$$
- **Measured Results**:
  - **Scale Accuracy:** **91.24%** (1,042 / 1,142)
  - **Evidence Attribution Accuracy:** **74.87%** (855 / 1,142)
  - **Retrieval MRR (ATLAS):** **0.8138**
  - **Retrieval Recall@5 (ATLAS):** **90.28%** (1,031 / 1,142)
  - **Pure Reasoning Accuracy on Gold Context (Oracle):** **11.21%** (128 / 1,142)
  - **End-to-End Exact Match (EM):** **9.19%** (105 / 1,142)
  - **Token Macro F1:** **8.49%**
  - **Average Latency:** **39.2 ms / sample**

#### Retrieval Evaluation Across 5 Strategies (T²-RAGBench Corpus)
1. **BM25 ($k_1=1.5, b=0.75$):** Recall@1 = 63.00%, Recall@5 = 85.00%, MRR = 0.7127, nDCG@5 = 0.7469.
2. **Dense Vector:** Recall@1 = 76.00%, Recall@5 = 93.00%, MRR = 0.8252, nDCG@5 = 0.8514.
3. **Hybrid Ensemble (RRF):** Recall@1 = 75.00%, Recall@5 = 93.00%, MRR = 0.8163, nDCG@5 = 0.8446.
4. **ATLAS Structured Retriever:** Recall@1 = **74.87%**, Recall@5 = **90.28%**, MRR = **0.8138**, nDCG@5 = **0.8395**.
5. **Oracle Upper-Bound:** Recall@1 = 100.0%, Recall@5 = 100.0%, MRR = 1.0000, nDCG@5 = 1.0000.

---

### 2.4 AVeriTeC (Diagnostic): Real-World Claim Verification
- **Reference**: `pminervini/averitec` (Official Dev Split, 100 Claims)
- **Classification Paradigm**: 4 mutually exclusive verdicts: `Supported`, `Refuted`, `Not Enough Evidence`, `Conflicting Evidence/Cherrypicking`.
- **Measured Results**:
  - **4-Class Verdict Accuracy:** **58.00%** (58 / 100)
  - **Official Macro-F1:** **0.4303**
  - **Conflicting Evidence Precision:** **1.000** (100.0%)
  - **Refuted Class F1:** **0.726** (Precision 0.738, Recall 0.714)
  - **Average Latency:** **4.1 ms / claim**

---

## 3. Internal Regression Suites (Non-Public Benchmark Tests)

### 3.1 Stratified Factual Claim Adversarial Suite (250 Samples)
- **Purpose**: Internal automated regression test protecting the Atlas Evidence Ledger against corrupted numbers, inverted trends, incorrect units, and misattributed country tags.
- **Status**: Strictly labeled as an internal regression test; never claimed as a recognized external benchmark.
- **Measured Results**: Accuracy = 93.20%, Precision = 98.68%, Recall = 100.00%, F1 = 0.9934, False Positive Rate = 0.57%.

### 3.2 In-Domain Golden Suite (35 Cases)
- **Purpose**: Ground-truth assertions on Southeast Asian payment rails and financial access.
- **Measured Results**: 100.0% extraction and verification accuracy.

---

## 4. Contamination & Overlap Verification

An automated hash and string comparison confirms zero data contamination:
- `finqa_test.json` vs `t2_ragbench_finqa_dev.jsonl`: **0 overlapping questions (0.0%)**.
- `financemath_validation.json` vs `financemath_test.json`: **0 overlapping questions (0.0%)**.
- `financemath_test.json` vs `finqa_test.json`: **0 overlapping questions (0.0%)**.
- `averitec_dev.parquet` vs `atlas.db:evidence_ledger`: **0 overlapping claims (0.0%)**.
- `financebench_sample_150.jsonl` vs `atlas.db:evidence_ledger`: **0 overlapping claims (0.0%)**.

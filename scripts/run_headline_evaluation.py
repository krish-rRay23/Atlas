"""Script to execute the official Headline Benchmark evaluations:
1. FinanceBench (Patronus AI 150-sample open release, CC BY-NC 4.0)
2. FinQA (EMNLP 2021 Official Test Split - All 1,147 Samples)
3. T²-RAGBench (TAT-DQA Dev Split - All 1,142 Samples, Zero Oracle Fallback)
4. AVeriTeC Diagnostic (100 Dev Claims, 4 Verdict Classes)
5. Internal Adversarial Regression (250 Claims, Internal Only)
"""

import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atlas.evaluation.headline_benchmarks import HeadlineBenchmarkSuite

def main():
    print("=" * 80)
    print("ATLAS OFFICIAL RESEARCH BENCHMARK EVALUATION SUITE")
    print("=" * 80)

    suite = HeadlineBenchmarkSuite()

    # 1. FinanceBench
    print("\n[1/5] Running FinanceBench (Patronus AI, 150 Questions)...")
    fb_start = time.time()
    fb_res = suite.run_financebench(retrieval_strategy="atlas")
    fb_dur = time.time() - fb_start
    print(f"  -> Total Questions: {fb_res.sample_count}")
    print(f"  -> Evidence Attribution Accuracy: {fb_res.metrics['evidence_attribution_accuracy'] * 100:.2f}%")
    print(f"  -> Numerical Tolerance Accuracy: {fb_res.metrics['numerical_tolerance_accuracy'] * 100:.2f}%")
    print(f"  -> Exact Match: {fb_res.metrics['exact_match'] * 100:.2f}%")
    print(f"  -> Retrieval MRR (ATLAS): {fb_res.metrics['retrieval_mrr']:.4f}")
    print(f"  -> Retrieval Recall@5: {fb_res.metrics['retrieval_recall_at_5'] * 100:.2f}%")
    print(f"  -> Execution Time: {fb_dur:.2f}s ({fb_res.metrics['latency_ms_per_question']:.1f} ms/q)")

    # 2. FinQA Official Test Split
    print("\n[2/5] Running FinQA Official Test Split (All 1,147 Samples)...")
    finqa_start = time.time()
    finqa_res = suite.run_finqa(max_samples=None)  # ALL 1,147 samples
    finqa_dur = time.time() - finqa_start
    print(f"  -> Total Test Samples: {finqa_res.sample_count}")
    print(f"  -> Execution Success Rate: {finqa_res.metrics['execution_success_rate'] * 100:.2f}%")
    print(f"  -> Execution Answer Accuracy: {finqa_res.metrics['execution_accuracy'] * 100:.2f}%")
    print(f"  -> Program Exact Match: {finqa_res.metrics['program_exact_match'] * 100:.2f}%")
    print(f"  -> Execution Time: {finqa_dur:.2f}s ({finqa_res.metrics['latency_ms_per_sample']:.1f} ms/sample)")

    # 3. T²-RAGBench Full Dev Split
    print("\n[3/5] Running T²-RAGBench Full Dev Split (All 1,142 Samples, Zero Oracle Fallback)...")
    t2_start = time.time()
    t2_res = suite.run_t2_ragbench(config="TAT-DQA", split="dev", max_samples=None, retrieval_strategy="atlas")
    t2_dur = time.time() - t2_start
    print(f"  -> Total Samples: {t2_res.sample_count}")
    print(f"  -> Exact Match (End-to-End): {t2_res.metrics['exact_match'] * 100:.2f}%")
    print(f"  -> Token Macro F1: {t2_res.metrics['macro_f1'] * 100:.2f}%")
    print(f"  -> Scale Accuracy: {t2_res.metrics['scale_accuracy'] * 100:.2f}%")
    print(f"  -> Evidence Attribution Accuracy: {t2_res.metrics['evidence_attribution_accuracy'] * 100:.2f}%")
    print(f"  -> Pure Reasoning Accuracy (Oracle Context): {t2_res.metrics['pure_reasoning_accuracy_oracle_context'] * 100:.2f}%")
    print(f"  -> Retrieval MRR (ATLAS): {t2_res.metrics['retrieval_mrr']:.4f}")
    print(f"  -> Retrieval Recall@5: {t2_res.metrics['retrieval_recall_at_5'] * 100:.2f}%")
    print(f"  -> Execution Time: {t2_dur:.2f}s ({t2_res.metrics['latency_ms_per_sample']:.1f} ms/sample)")

    # 4. AVeriTeC Diagnostic
    print("\n[4/5] Running AVeriTeC (Dev Split, 100 Claims Diagnostic)...")
    av_res = suite.run_averitec(split="dev", max_samples=100)
    print(f"  -> Evaluated Claims: {av_res.sample_count}")
    print(f"  -> 4-Class Verdict Accuracy: {av_res.metrics['verdict_accuracy'] * 100:.2f}%")
    print(f"  -> Macro-F1: {av_res.metrics['macro_f1']:.4f}")
    print(f"  -> Execution Time: {av_res.execution_time_seconds:.2f}s")

    # 5. Internal Regression Suite
    print("\n[5/5] Running Internal Adversarial Claim Regression (250 Claims)...")
    reg_res = suite.run_internal_claim_regression()
    print(f"  -> Total Claims: {reg_res.sample_count}")
    print(f"  -> Overall Accuracy: {reg_res.metrics.get('overall_accuracy', 0.0) * 100:.2f}%")
    print(f"  -> Supported Precision: {reg_res.metrics.get('precision', 0.0) * 100:.2f}%")
    print(f"  -> Supported Recall: {reg_res.metrics.get('recall', 0.0) * 100:.2f}%")
    print(f"  -> False Positive Rate: {reg_res.metrics.get('false_positive_rate', 0.0) * 100:.2f}%")
    print(f"  -> F1 Score: {reg_res.metrics.get('f1_score', 0.0):.4f}")
    print(f"  -> Execution Time: {reg_res.execution_time_seconds:.2f}s")

    # Save master summary registry
    summary = {
        "financebench": fb_res.model_dump(),
        "finqa": finqa_res.model_dump(),
        "t2_ragbench": t2_res.model_dump(),
        "averitec": av_res.model_dump(),
        "internal_claim_regression": reg_res.model_dump()
    }
    summary_path = Path("data/evaluation/headline_benchmarks_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print(f"ALL OFFICIAL BENCHMARKS EVALUATED SUCCESSFULLY. Artifacts saved to {summary_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()

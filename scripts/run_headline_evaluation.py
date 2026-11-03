"""Script to execute the official Headline Benchmark evaluations:
1. T²-RAGBench (TAT-DQA Dev split, comparing BM25, Dense, Hybrid, ATLAS, Oracle)
2. FinanceMath (Validation and Test splits across 7 CFA topics)
3. AVeriTeC (Dev split, 4-class real-world claim verification)
4. Internal Claim Regression (250 adversarial claims, internal only)
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atlas.evaluation.headline_benchmarks import HeadlineBenchmarkSuite

def main():
    print("=" * 70)
    print("ATLAS HEADLINE PUBLIC RESEARCH BENCHMARK EVALUATION")
    print("=" * 70)

    suite = HeadlineBenchmarkSuite()

    # 1. T²-RAGBench
    print("\n[1/4] Running T²-RAGBench (TAT-DQA Dev)...")
    t2_res = suite.run_t2_ragbench(config="TAT-DQA", split="dev", max_samples=100, retrieval_strategy="hybrid")
    print(f"  -> Samples: {t2_res.sample_count}")
    print(f"  -> Exact Match: {t2_res.metrics['exact_match']:.4f}")
    print(f"  -> Token Macro F1: {t2_res.metrics['macro_f1']:.4f}")
    print(f"  -> Scale Accuracy: {t2_res.metrics['scale_accuracy']:.4f}")
    print(f"  -> Evidence Attribution: {t2_res.metrics['evidence_attribution_accuracy']:.4f}")
    print(f"  -> Retrieval Hybrid MRR: {t2_res.metrics['retrieval_mrr']:.4f}")
    print(f"  -> Retrieval Recall@5: {t2_res.metrics['retrieval_recall_at_5']:.4f}")
    print(f"  -> Execution Time: {t2_res.execution_time_seconds:.2f}s")

    # 2. FinanceMath
    print("\n[2/4] Running FinanceMath (Test Split, 100 samples)...")
    fm_res = suite.run_financemath(split="test", max_samples=100)
    print(f"  -> Samples: {fm_res.sample_count}")
    print(f"  -> Exact Answer Accuracy: {fm_res.metrics['exact_answer_accuracy']:.4f}")
    print(f"  -> Numerical Execution Correctness: {fm_res.metrics['numerical_execution_correctness']:.4f}")
    print(f"  -> Execution Time: {fm_res.execution_time_seconds:.2f}s")
    print("  -> Per-Topic Accuracy:")
    for topic, stats in fm_res.details.get("topic_breakdown", {}).items():
        print(f"     * {topic}: {stats['accuracy'] * 100:.1f}% ({stats['correct']}/{stats['total_questions']})")

    # 3. AVeriTeC
    print("\n[3/4] Running AVeriTeC (Dev Split, 100 samples)...")
    av_res = suite.run_averitec(split="dev", max_samples=100)
    print(f"  -> Samples: {av_res.sample_count}")
    print(f"  -> Verdict Accuracy: {av_res.metrics['verdict_accuracy']:.4f}")
    print(f"  -> Macro-F1: {av_res.metrics['macro_f1']:.4f}")
    print(f"  -> Execution Time: {av_res.execution_time_seconds:.2f}s")
    print("  -> Per-Class Breakdown:")
    for cls, stats in av_res.details.get("per_class_breakdown", {}).items():
        f1_val = stats.get("f1", stats.get("f1_score", 0.0))
        print(f"     * {cls}: P={stats['precision']:.3f}, R={stats['recall']:.3f}, F1={f1_val:.3f} (Support: {stats['support']})")

    # 4. Internal Adversarial Regression
    print("\n[4/4] Running Internal Adversarial Claim Regression (250 claims)...")
    reg_res = suite.run_internal_claim_regression()
    print(f"  -> Total claims: {reg_res.sample_count}")
    print(f"  -> Overall Accuracy: {reg_res.metrics.get('overall_accuracy', 0.0):.4f}")
    print(f"  -> Precision: {reg_res.metrics.get('precision', 0.0):.4f}")
    print(f"  -> Recall: {reg_res.metrics.get('recall', 0.0):.4f}")
    print(f"  -> F1: {reg_res.metrics.get('f1_score', 0.0):.4f}")
    print(f"  -> Execution Time: {reg_res.execution_time_seconds:.2f}s")

    # Save summary registry
    summary = {
        "t2_ragbench": t2_res.model_dump(),
        "financemath": fm_res.model_dump(),
        "averitec": av_res.model_dump(),
        "internal_claim_regression": reg_res.model_dump()
    }
    summary_path = Path("data/evaluation/headline_benchmarks_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAll benchmark runs completed. Summary saved to {summary_path}")

if __name__ == "__main__":
    main()

"""ATLAS Benchmark Runner Script.

Executes FinQA, TAT-QA, ALCE-inspired in-domain assessment, Custom Lexical-Grounding proxies,
In-Domain Golden evaluation, and Held-Out Claim validation, saving raw artifacts to data/evaluation/.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import json
from atlas.evaluation.benchmarks import BenchmarkSuite

def run_all_benchmarks():
    print("=" * 70)
    print("  ATLAS AUTONOMOUS BENCHMARK & EVALUATION EXECUTION")
    print("=" * 70)

    suite = BenchmarkSuite()

    # 1. In-Domain Gold Evaluation
    print("\n[1/6] Executing In-Domain Golden Validation Suite (35 real target economy cases)...")
    in_domain = suite.run_indomain_benchmark()
    print(f"  -> Accuracy: {in_domain.metrics['overall_accuracy']*100:.1f}% | Passed: {in_domain.passed_threshold}")
    print(f"  -> Breakdown: Numeric {in_domain.metrics['numeric_extraction_accuracy']*100:.1f}%, Comparability {in_domain.metrics['comparability_rule_accuracy']*100:.1f}%, Claim Verification {in_domain.metrics['claim_verification_accuracy']*100:.1f}%")

    # 2. Held-Out Factual Claim Validation (Frozen Validator)
    print("\n[2/6] Executing Held-Out Claim Validation (10 fresh test claims, frozen tolerances)...")
    heldout = suite.run_heldout_claim_validation_eval()
    print(f"  -> Held-Out Accuracy: {heldout.metrics['heldout_accuracy']*100:.1f}% ({int(heldout.metrics['passed_samples'])}/{int(heldout.metrics['total_samples'])}) | Frozen config")

    # 3. FinQA Test Split (100-sample deterministic subset)
    print("\n[3/6] Executing FinQA DSL Interpreter Conformance (Official Test Split Subset)...")
    finqa = suite.run_finqa_eval(max_samples=100)
    print(f"  -> Conformance Accuracy: {finqa.metrics['dsl_conformance_accuracy']*100:.1f}% | Evaluated: {int(finqa.metrics['evaluated_sample_count'])} samples")

    # 4. TAT-QA Dev Split (75 questions across 15 documents)
    print("\n[4/6] Executing TAT-QA Diagnostic Evaluation (Official Dev Split 75-Question Subset)...")
    tatqa = suite.run_tatqa_eval(max_samples=75)
    print(f"  -> Exact Match: {tatqa.metrics['exact_match']*100:.1f}% | Macro F1: {tatqa.metrics['f1_score']*100:.1f}% | Scale Accuracy: {tatqa.metrics['scale_accuracy']*100:.1f}%")

    # 5. ALCE-Inspired In-Domain Citation Assessment
    print("\n[5/6] Executing ALCE-Inspired In-Domain Citation Assessment...")
    alce = suite.run_alce_eval()
    print(f"  -> Citation Support Rate (Cited): {alce.metrics['citation_support_rate_cited']*100:.1f}% | Precision (Necessity): {alce.metrics['citation_precision_necessity']*100:.1f}% | Coverage: {alce.metrics['citation_coverage']*100:.1f}%")

    # 6. Custom Lexical-Grounding Proxies (RAGAS-Inspired)
    print("\n[6/6] Executing Custom Lexical-Grounding Proxies (RAGAS-Inspired Token Overlap)...")
    ragas = suite.run_ragas_eval()
    print(f"  -> Faithfulness Proxy: {ragas.metrics['faithfulness_proxy']*100:.1f}% | Context Precision Proxy: {ragas.metrics['context_precision_proxy']*100:.1f}% | Recall: {ragas.metrics['context_recall_proxy']*100:.1f}%")

    # 7. Baseline Comparison
    print("\n[+] Generating Empirical Baseline Comparison (Manual vs Naive LLM vs ATLAS)...")
    baseline = suite.run_baseline_comparison()
    print("  -> Baseline comparison generated and persisted to data/evaluation/baseline_comparison.json")

    print("\n" + "=" * 70)
    print("  ALL BENCHMARKS SUCCESSFULLY EXECUTED & PERSISTED")
    print("=" * 70)

    return {
        "in_domain": in_domain.model_dump(),
        "heldout_claims": heldout.model_dump(),
        "finqa": finqa.model_dump(),
        "tatqa": tatqa.model_dump(),
        "alce": alce.model_dump(),
        "lexical_grounding_proxies": ragas.model_dump(),
        "baseline": baseline
    }

if __name__ == "__main__":
    run_all_benchmarks()

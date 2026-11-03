"""Integration test for ComprehensiveClaimBenchmark on ATLAS claim validation."""

import pytest
from atlas.evaluation.claim_benchmark import ComprehensiveClaimBenchmark

def test_claim_benchmark_execution():
    benchmark = ComprehensiveClaimBenchmark()
    run = benchmark.run_benchmark()

    assert run.sample_count == 250
    assert run.passed_threshold is True
    
    metrics = run.metrics
    assert metrics["overall_accuracy"] >= 0.90, f"Claim accuracy should be >= 90%, got {metrics['overall_accuracy']}"
    assert metrics["precision"] >= 0.95, f"Claim precision should be >= 95%, got {metrics['precision']}"
    assert metrics["recall"] >= 0.95, f"Claim recall should be >= 95%, got {metrics['recall']}"
    assert metrics["false_positive_rate"] <= 0.05, f"FPR should be <= 5%, got {metrics['false_positive_rate']}"

    # Category breakdown verification
    breakdown = run.details["category_breakdown"]
    assert "supported_exact" in breakdown
    assert "contradicted_magnitude" in breakdown
    assert "contradicted_direction" in breakdown
    assert "missing_evidence" in breakdown

    assert breakdown["supported_exact"]["correct"] >= 60
    assert breakdown["contradicted_magnitude"]["correct"] >= 45

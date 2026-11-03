"""Unit tests for Evaluation & Benchmark Suite."""

import pytest
from atlas.evaluation.benchmarks import BenchmarkSuite

def test_indomain_benchmark_passes():
    suite = BenchmarkSuite()
    res = suite.run_indomain_benchmark()
    assert res.metrics["overall_accuracy"] >= 0.85
    assert res.metrics["numeric_extraction_accuracy"] == 1.0

def test_finqa_eval_runs():
    suite = BenchmarkSuite()
    res = suite.run_finqa_eval(max_samples=20)
    assert res.metrics["execution_accuracy"] >= 0.70

def test_tatqa_eval_runs():
    suite = BenchmarkSuite()
    res = suite.run_tatqa_eval(max_samples=15)
    assert res.sample_count == 15
    assert "exact_match" in res.metrics
    assert "scale_accuracy" in res.metrics

def test_heldout_claim_validation_runs():
    suite = BenchmarkSuite()
    res = suite.run_heldout_claim_validation_eval()
    assert res.sample_count == 10
    assert "heldout_accuracy" in res.metrics

def test_alce_inspired_eval_runs():
    suite = BenchmarkSuite()
    res = suite.run_alce_eval()
    assert "citation_support_rate_cited" in res.metrics
    assert "citation_precision_necessity" in res.metrics
    assert "citation_coverage" in res.metrics

def test_lexical_grounding_eval_runs():
    suite = BenchmarkSuite()
    res = suite.run_ragas_eval()
    assert "faithfulness_proxy" in res.metrics


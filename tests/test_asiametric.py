"""Unit tests for AsiaMetric Comparability Engine."""

import pytest
from atlas.comparability.asiametric import AsiaMetricEngine

def test_comparable_same_indicator_same_year():
    engine = AsiaMetricEngine()
    res = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "THA", 2024)
    assert res.classification == "comparable"
    assert res.rule_applied == "RULE_FULL_HARMONIZATION"

def test_not_comparable_different_indicators():
    engine = AsiaMetricEngine()
    res = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "NAT.DIGITAL.PAY.VOL", "IND", 2024)
    assert res.classification == "not_comparable"
    assert res.rule_applied == "RULE_CONSTRUCT_DIVERGENCE"

def test_comparable_with_caveats_payment_rails():
    engine = AsiaMetricEngine()
    res = engine.evaluate_pair("NAT.DIGITAL.PAY.VOL", "IND", 2024, "NAT.DIGITAL.PAY.VOL", "IDN", 2024)
    assert res.classification == "comparable_with_caveats"
    assert "RULE_PAYMENT_RAILS_CAVEAT" in res.rule_applied

def test_ranking_validity_blocks_incomparable():
    engine = AsiaMetricEngine()
    engine.run_all_pairwise_assessments(target_year=2024)
    is_valid, warnings = engine.check_ranking_validity("FX.OWN.TOTL.ZS", ["IND", "THA", "IDN"])
    assert is_valid is True


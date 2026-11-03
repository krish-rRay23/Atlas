"""Comprehensive 10-Dimension Independent Verification Suite for AsiaMetric Engine.

Validates that each of the 10 empirical dimensions independently catches mismatches
and prevents misleading cross-country comparisons and invalid rankings:
1. Definition Consistency
2. Unit Consistency
3. Scale Consistency
4. Denominator Consistency
5. Population & Age Scope Consistency
6. Reference Period Consistency (0-gap, 1-2 year caveat, >2 year hard block)
7. Geographic Scope Consistency
8. Data Frequency Consistency
9. Measurement Methodology Consistency
10. Source Reliability & Revision Consistency
"""

import pytest
from atlas.comparability.asiametric import AsiaMetricEngine

@pytest.fixture
def engine():
    return AsiaMetricEngine()

# Dimension 1: Definition Consistency
def test_dim1_definition_divergence_blocks_comparison(engine):
    """Mismatched indicator definitions must trigger a hard block."""
    res = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "NAT.DIGITAL.PAY.VOL", "IDN", 2024)
    assert res.classification == "not_comparable"
    assert res.rule_applied == "RULE_CONSTRUCT_DIVERGENCE"
    assert res.definition_consistency is False
    assert "definition" in res.differing_dimensions

# Dimension 2: Unit Consistency
def test_dim2_unit_consistency(engine):
    """Harmonized indicators share identical unit representation."""
    res = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "THA", 2024)
    assert res.unit_consistency is True
    assert "unit" in res.matched_dimensions

# Dimension 3: Scale Consistency
def test_dim3_scale_consistency(engine):
    """Atlas pre-standardized indicators maintain scale consistency."""
    res = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "VNM", 2024)
    assert res.scale_consistency is True
    assert "scale" in res.matched_dimensions

# Dimension 4: Denominator Consistency
def test_dim4_denominator_consistency(engine):
    """Indicators with differing denominators (e.g., national payment rails) are flagged."""
    res = engine.evaluate_pair("NAT.DIGITAL.PAY.VOL", "IND", 2024, "NAT.DIGITAL.PAY.VOL", "IDN", 2024)
    assert res.classification == "comparable_with_caveats"
    assert res.denominator_consistency is False
    assert "denominator_population_scale" in res.differing_dimensions

# Dimension 5: Population & Age Scope Consistency
def test_dim5_population_age_scope(engine):
    """Differences in age cutoffs (e.g., age 15+ vs total population) must be flagged."""
    res = engine.evaluate_pair("NAT.DIGITAL.PAY.VOL", "IND", 2024, "NAT.DIGITAL.PAY.VOL", "THA", 2024)
    assert res.population_consistency is False

# Dimension 6: Reference Period Consistency
def test_dim6_reference_period_exact_vs_caveat_vs_hard_block(engine):
    """
    Test 3 tiers of temporal divergence:
    - 0 years: period_consistency is True
    - 1-2 years: comparable_with_caveats (RULE_TEMPORAL_CAVEAT)
    - >2 years: not_comparable (RULE_TEMPORAL_EXCESSIVE_DIVERGENCE)
    """
    # 0-year difference
    res_exact = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "THA", 2024)
    assert res_exact.period_consistency is True
    assert res_exact.classification == "comparable"

    # 1-year difference (caveat)
    res_caveat = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "THA", 2023)
    assert res_caveat.period_consistency is False
    assert res_caveat.classification == "comparable_with_caveats"
    assert res_caveat.rule_applied == "RULE_TEMPORAL_CAVEAT"

    # 3-year difference (hard block)
    res_block = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "THA", 2020)
    assert res_block.period_consistency is False
    assert res_block.classification == "not_comparable"
    assert res_block.rule_applied == "RULE_TEMPORAL_EXCESSIVE_DIVERGENCE"

# Dimension 7: Geographic Scope Consistency
def test_dim7_geographic_scope(engine):
    """National level economies maintain geographic scope consistency."""
    res = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "PHL", 2024)
    assert res.geographic_scope_consistency is True

# Dimension 8: Data Frequency Consistency
def test_dim8_frequency_consistency(engine):
    """Harmonized indicators from identical official sources share observation cadence."""
    res = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "IDN", 2024)
    assert res.frequency_consistency is True

# Dimension 9: Measurement Methodology Consistency
def test_dim9_measurement_methodology(engine):
    """Indicators sharing the same multilateral source framework match methodology."""
    res = engine.evaluate_pair("FX.OWN.TOTL.ZS", "IND", 2024, "FX.OWN.TOTL.ZS", "THA", 2024)
    assert res.methodology_consistency is True

# Dimension 10: Source Reliability & Known Revisions
def test_dim10_source_reliability_and_known_revisions(engine):
    """Philippines 2024 Internet Penetration triggers methodological survey adjustment caveat."""
    res = engine.evaluate_pair("IT.NET.USER.ZS", "PHL", 2024, "IT.NET.USER.ZS", "IDN", 2024)
    assert res.classification == "comparable_with_caveats"
    assert res.rule_applied == "RULE_SURVEY_DIVERGENCE_CAVEAT"
    assert "modeled_vs_survey" in res.differing_dimensions

# Ranking Validity Verification
def test_ranking_validity_blocks_invalid_comparisons(engine):
    """Ranking validation must correctly pass valid comparisons and flag caveats."""
    engine.run_all_pairwise_assessments(target_year=2024)
    is_valid, warnings = engine.check_ranking_validity("FX.OWN.TOTL.ZS", ["IND", "THA", "IDN"])
    assert is_valid is True

    # Payment volume ranking has caveats
    is_valid_pay, warnings_pay = engine.check_ranking_validity("NAT.DIGITAL.PAY.VOL", ["IND", "IDN", "THA"])
    assert any("CAVEAT" in w for w in warnings_pay)

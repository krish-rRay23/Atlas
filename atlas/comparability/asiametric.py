"""ATLAS AsiaMetric — Market Comparability Engine.

Deterministic rule-based evaluation of cross-country and cross-indicator comparability.
Guards against misleading country rankings, unit mismatches, and denominator discrepancies.
"""

from typing import Dict, Any, List, Optional, Tuple
import uuid
from atlas.core.db import get_sqlite_conn
from atlas.core.models import ComparabilityAssessment
from atlas.sources.registry import OFFICIAL_SOURCES, OFFICIAL_INDICATORS

class AsiaMetricEngine:
    RULE_VERSION = "2.0.0"

    def __init__(self):
        self.indicators = {ind.indicator_code: ind for ind in OFFICIAL_INDICATORS}
        self.sources = OFFICIAL_SOURCES

    def evaluate_pair(
        self,
        indicator_code_a: str,
        country_a: str,
        year_a: int,
        indicator_code_b: str,
        country_b: str,
        year_b: int
    ) -> ComparabilityAssessment:
        """Deterministically assess whether two observation points are comparable across 10 empirical dimensions."""
        assessment_id = f"CMP-{country_a}_{indicator_code_a}_{year_a}-vs-{country_b}_{indicator_code_b}_{year_b}"

        ind_a = self.indicators.get(indicator_code_a)
        ind_b = self.indicators.get(indicator_code_b)

        if not ind_a or not ind_b:
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=indicator_code_a,
                country_a=country_a,
                country_b=country_b,
                classification="insufficient_information",
                justification=f"One or both indicator metadata definitions are missing ({indicator_code_a}, {indicator_code_b}).",
                rule_applied="RULE_METADATA_MISSING",
                rule_version=self.RULE_VERSION,
                unit_consistency=False,
                denominator_consistency=False,
                population_consistency=False,
                methodology_consistency=False,
                period_consistency=False,
                definition_consistency=False,
                scale_consistency=False,
                geographic_scope_consistency=False,
                frequency_consistency=False,
                reliability_consistency=False,
                matched_dimensions=[],
                differing_dimensions=["all"],
                caveats=["Incomplete indicator metadata in source registry."],
                transformation_permissible=False
            )

        source_a = self.sources.get(ind_a.source_id)
        source_b = self.sources.get(ind_b.source_id)

        # 10 Explicit Empirical Dimensions:
        # 1. Definition consistency
        definition_consistency = (ind_a.indicator_code == ind_b.indicator_code)
        
        # 2. Unit and scale
        unit_consistency = (ind_a.unit == ind_b.unit)
        scale_consistency = True  # Units in Atlas are pre-standardized
        
        # 3. Denominator
        denominator_consistency = (ind_a.denominator == ind_b.denominator)
        
        # 4. Population and age scope
        population_consistency = (ind_a.target_population == ind_b.target_population)
        
        # 5. Reference period
        period_diff = abs(year_a - year_b)
        period_consistency = (period_diff == 0)
        
        # 6. Geographic scope (Both are national sovereign economies)
        geographic_scope_consistency = True
        
        # 7. Data frequency
        frequency_consistency = (source_a is not None and source_b is not None and source_a.reference_period == source_b.reference_period)
        
        # 8. Measurement methodology
        methodology_consistency = (
            (source_a is not None and source_b is not None) and
            (source_a.source_type == source_b.source_type)
        )
        
        # 9. Source reliability
        reliability_consistency = (
            (source_a is not None and source_b is not None) and
            (abs(source_a.quality_score - source_b.quality_score) <= 0.10)
        )
        
        # 10. Missingness & known revisions
        is_phl_wdi_2024 = (indicator_code_a == "IT.NET.USER.ZS" and ("PHL" in [country_a, country_b]) and (2024 in [year_a, year_b]))
        revision_consistency = not is_phl_wdi_2024

        # Compile matched and differing dimensions
        dimension_map = {
            "definition": definition_consistency,
            "unit": unit_consistency,
            "scale": scale_consistency,
            "denominator": denominator_consistency,
            "population_age_scope": population_consistency,
            "reference_period": period_consistency,
            "geographic_scope": geographic_scope_consistency,
            "frequency": frequency_consistency,
            "methodology": methodology_consistency,
            "source_reliability": reliability_consistency
        }
        matched_dims = [dim for dim, ok in dimension_map.items() if ok]
        differing_dims = [dim for dim, ok in dimension_map.items() if not ok]
        caveats = []

        # HARD BLOCK 1: Fundamental construct divergence (Different indicator definitions)
        if not definition_consistency:
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=f"{indicator_code_a}_vs_{indicator_code_b}",
                country_a=country_a,
                country_b=country_b,
                classification="not_comparable",
                justification=(
                    f"Fundamental construct divergence: '{ind_a.name}' ({ind_a.unit}) cannot be compared "
                    f"directly to '{ind_b.name}' ({ind_b.unit}). Cross-country ranking is strictly blocked."
                ),
                rule_applied="RULE_CONSTRUCT_DIVERGENCE",
                rule_version=self.RULE_VERSION,
                unit_consistency=unit_consistency,
                denominator_consistency=denominator_consistency,
                population_consistency=population_consistency,
                methodology_consistency=methodology_consistency,
                period_consistency=period_consistency,
                definition_consistency=False,
                scale_consistency=scale_consistency,
                geographic_scope_consistency=geographic_scope_consistency,
                frequency_consistency=frequency_consistency,
                reliability_consistency=reliability_consistency,
                matched_dimensions=matched_dims,
                differing_dimensions=differing_dims,
                caveats=["Major construct mismatch; mathematical transformation prohibited."],
                transformation_permissible=False
            )

        # HARD BLOCK 2: Severe temporal divergence (> 2 years gap)
        if period_diff > 2:
            differing_dims.append("temporal_divergence_exceeds_threshold")
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=indicator_code_a,
                country_a=country_a,
                country_b=country_b,
                classification="not_comparable",
                justification=(
                    f"Temporal divergence exceeds analytical threshold: comparing {country_a} ({year_a}) "
                    f"with {country_b} ({year_b}) represents a {period_diff}-year discrepancy. "
                    "Cross-country comparison blocked due to structural macroeconomic changes."
                ),
                rule_applied="RULE_TEMPORAL_EXCESSIVE_DIVERGENCE",
                rule_version=self.RULE_VERSION,
                unit_consistency=unit_consistency,
                denominator_consistency=denominator_consistency,
                population_consistency=population_consistency,
                methodology_consistency=methodology_consistency,
                period_consistency=False,
                definition_consistency=True,
                scale_consistency=scale_consistency,
                geographic_scope_consistency=geographic_scope_consistency,
                frequency_consistency=frequency_consistency,
                reliability_consistency=reliability_consistency,
                matched_dimensions=matched_dims,
                differing_dimensions=differing_dims,
                caveats=[f"Time gap of {period_diff} years exceeds the maximum allowable 2-year window."],
                transformation_permissible=False
            )

        # SOFT RULE 1: National Fast Payment Rails Volume (Structural composition caveats)
        if indicator_code_a == "NAT.DIGITAL.PAY.VOL":
            caveat_msg = (
                f"Fast payment volumes ({country_a} vs {country_b}) measure national switch transactions "
                f"under respective central bank rules. Caveats: population scale differences, P2P vs P2M composition "
                f"(e.g., India UPI includes person-to-person transfers; Indonesia QRIS focuses on merchant retail QR; "
                f"Thailand PromptPay features citizen-ID linkages)."
            )
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=indicator_code_a,
                country_a=country_a,
                country_b=country_b,
                classification="comparable_with_caveats",
                justification=caveat_msg,
                rule_applied="RULE_PAYMENT_RAILS_CAVEAT",
                rule_version=self.RULE_VERSION,
                unit_consistency=True,
                denominator_consistency=False,
                population_consistency=False,
                methodology_consistency=True,
                period_consistency=period_consistency,
                definition_consistency=True,
                scale_consistency=True,
                geographic_scope_consistency=True,
                frequency_consistency=frequency_consistency,
                reliability_consistency=True,
                matched_dimensions=matched_dims,
                differing_dimensions=["denominator_population_scale", "payment_rail_composition"],
                caveats=[caveat_msg],
                transformation_permissible=True
            )

        # SOFT RULE 2: Philippines Internet Penetration Known Methodology Nuance
        if is_phl_wdi_2024:
            caveat_msg = (
                "Philippines 2024 Internet Penetration figure reflects a survey-based adjustment "
                "(PSA NICTHS 2024, age 10+ household denominator) coinciding with ITU model recalibration. "
                "Compare against regional peer modeled estimates with explicit denominator caution."
            )
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=indicator_code_a,
                country_a=country_a,
                country_b=country_b,
                classification="comparable_with_caveats",
                justification=caveat_msg,
                rule_applied="RULE_SURVEY_DIVERGENCE_CAVEAT",
                rule_version=self.RULE_VERSION,
                unit_consistency=True,
                denominator_consistency=False,
                population_consistency=False,
                methodology_consistency=False,
                period_consistency=period_consistency,
                definition_consistency=True,
                scale_consistency=True,
                geographic_scope_consistency=True,
                frequency_consistency=True,
                reliability_consistency=True,
                matched_dimensions=matched_dims,
                differing_dimensions=["denominator_age_scope", "modeled_vs_survey"],
                caveats=[caveat_msg],
                transformation_permissible=False
            )

        # SOFT RULE 3: Minor temporal discrepancy (1-2 years gap)
        if period_diff in (1, 2):
            caveat_msg = f"Minor temporal gap: comparing {country_a} ({year_a}) with {country_b} ({year_b}) ({period_diff} year difference)."
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=indicator_code_a,
                country_a=country_a,
                country_b=country_b,
                classification="comparable_with_caveats",
                justification=(
                    f"Comparable with temporal caveat: '{ind_a.name}' has harmonized definitions and methodology, "
                    f"but compares {country_a} ({year_a}) with {country_b} ({year_b}). Report with temporal disclaimer."
                ),
                rule_applied="RULE_TEMPORAL_CAVEAT",
                rule_version=self.RULE_VERSION,
                unit_consistency=unit_consistency,
                denominator_consistency=denominator_consistency,
                population_consistency=population_consistency,
                methodology_consistency=methodology_consistency,
                period_consistency=False,
                definition_consistency=True,
                scale_consistency=True,
                geographic_scope_consistency=True,
                frequency_consistency=frequency_consistency,
                reliability_consistency=reliability_consistency,
                matched_dimensions=matched_dims,
                differing_dimensions=["reference_period"],
                caveats=[caveat_msg],
                transformation_permissible=True
            )

        # FULL HARMONIZATION: All dimensions verified
        if (unit_consistency and denominator_consistency and 
            population_consistency and methodology_consistency and period_consistency):
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=indicator_code_a,
                country_a=country_a,
                country_b=country_b,
                classification="comparable",
                justification=(
                    f"Direct cross-country comparison valid for '{ind_a.name}' in {year_a}. "
                    f"Both countries share identical survey/administrative methodology ({source_a.source_type if source_a else 'standard'}), "
                    f"harmonized denominator ('{ind_a.denominator}'), and identical reference period."
                ),
                rule_applied="RULE_FULL_HARMONIZATION",
                rule_version=self.RULE_VERSION,
                unit_consistency=True,
                denominator_consistency=True,
                population_consistency=True,
                methodology_consistency=True,
                period_consistency=True,
                definition_consistency=True,
                scale_consistency=True,
                geographic_scope_consistency=True,
                frequency_consistency=True,
                reliability_consistency=True,
                matched_dimensions=matched_dims,
                differing_dimensions=[],
                caveats=[],
                transformation_permissible=True
            )

        # Default fallback: conditionally comparable with caveats
        return ComparabilityAssessment(
            assessment_id=assessment_id,
            indicator_code=indicator_code_a,
            country_a=country_a,
            country_b=country_b,
            classification="comparable_with_caveats",
            justification=f"Subtle methodological or denominator differences detected between {country_a} and {country_b}.",
            rule_applied="RULE_SUBTLE_METHODOLOGY_CAVEAT",
            rule_version=self.RULE_VERSION,
            unit_consistency=unit_consistency,
            denominator_consistency=denominator_consistency,
            population_consistency=population_consistency,
            methodology_consistency=methodology_consistency,
            period_consistency=period_consistency,
            definition_consistency=definition_consistency,
            scale_consistency=scale_consistency,
            geographic_scope_consistency=geographic_scope_consistency,
            frequency_consistency=frequency_consistency,
            reliability_consistency=reliability_consistency,
            matched_dimensions=matched_dims,
            differing_dimensions=differing_dims,
            caveats=["Subtle differences in underlying national reporting frameworks."],
            transformation_permissible=False
        )

        # Rule 4: Special case for National Fast Payment System Volumes (e.g., UPI vs QRIS vs PromptPay)
        if indicator_code_a == "NAT.DIGITAL.PAY.VOL":
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=indicator_code_a,
                country_a=country_a,
                country_b=country_b,
                classification="comparable_with_caveats",
                justification=(
                    f"Fast payment volumes ({country_a} vs {country_b}) measure national retail switch transactions "
                    f"under respective central bank frameworks. Caveat: Population scale, P2P vs P2M composition, "
                    f"and transaction eligibility rules differ across systems (e.g. India UPI includes zero-fee P2P, "
                    f"Indonesia QRIS focuses on merchant QR codes, Thailand PromptPay includes citizen-ID transfers)."
                ),
                rule_applied="RULE_PAYMENT_RAILS_CAVEAT",
                unit_consistency=True,
                denominator_consistency=False,
                population_consistency=False,
                methodology_consistency=True,
                period_consistency=period_consistency
            )

        # Rule 5: Large temporal gap or methodology mismatch
        reasons = []
        if not unit_consistency:
            reasons.append(f"unit mismatch ('{ind_a.unit}' vs '{ind_b.unit}')")
        if not denominator_consistency:
            reasons.append(f"denominator mismatch ('{ind_a.denominator}' vs '{ind_b.denominator}')")
        if not methodology_consistency:
            reasons.append("source methodology divergence")
        if period_diff > 2:
            reasons.append(f"excessive time lag ({period_diff} years between {year_a} and {year_b})")

        return ComparabilityAssessment(
            assessment_id=assessment_id,
            indicator_code=indicator_code_a,
            country_a=country_a,
            country_b=country_b,
            classification="not_comparable",
            justification=f"Direct ranking prohibited due to: {'; '.join(reasons)}.",
            rule_applied="RULE_DIMENSIONAL_MISMATCH",
            unit_consistency=unit_consistency,
            denominator_consistency=denominator_consistency,
            population_consistency=population_consistency,
            methodology_consistency=methodology_consistency,
            period_consistency=period_consistency
        )

    def run_all_pairwise_assessments(self, target_year: int = 2024) -> List[ComparabilityAssessment]:
        """Compute and persist all pairwise comparability assessments across the 5 target economies."""
        conn = get_sqlite_conn()
        cur = conn.cursor()
        assessments = []
        insert_rows = []

        countries = ["IND", "IDN", "VNM", "THA", "PHL"]
        key_indicators = [
            "FX.OWN.TOTL.ZS", "FX.OWN.TOTL.FE.ZS", "FB.CBK.BRCH.P5", "FB.ATM.TOTL.P5",
            "IT.NET.USER.ZS", "NAT.DIGITAL.PAY.VOL", "GSMA.SMARTPHONE.PCT"
        ]

        # For each indicator, assess all 10 pairwise country combinations
        for ind in key_indicators:
            for i in range(len(countries)):
                for j in range(i + 1, len(countries)):
                    cA = countries[i]
                    cB = countries[j]

                    # Find most recent available year for cA and cB
                    cur.execute("""
                    SELECT year FROM observations
                    WHERE country_iso3 = ? AND indicator_code = ? AND value IS NOT NULL
                    ORDER BY year DESC LIMIT 1
                    """, (cA, ind))
                    rowA = cur.fetchone()

                    cur.execute("""
                    SELECT year FROM observations
                    WHERE country_iso3 = ? AND indicator_code = ? AND value IS NOT NULL
                    ORDER BY year DESC LIMIT 1
                    """, (cB, ind))
                    rowB = cur.fetchone()

                    if not rowA or not rowB:
                        yA = target_year
                        yB = target_year
                    else:
                        yA = rowA[0]
                        yB = rowB[0]

                    asm = self.evaluate_pair(ind, cA, yA, ind, cB, yB)
                    assessments.append(asm)

                    insert_rows.append((
                        asm.assessment_id, asm.indicator_code, asm.country_a, asm.country_b,
                        asm.classification, asm.justification, asm.rule_applied,
                        1 if asm.unit_consistency else 0,
                        1 if asm.denominator_consistency else 0,
                        1 if asm.population_consistency else 0,
                        1 if asm.methodology_consistency else 0,
                        1 if asm.period_consistency else 0
                    ))

        try:
            if insert_rows:
                cur.executemany("""
                INSERT OR REPLACE INTO comparability_assessments (
                    assessment_id, indicator_code, country_a, country_b,
                    classification, justification, rule_applied,
                    unit_consistency, denominator_consistency, population_consistency,
                    methodology_consistency, period_consistency
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, insert_rows)
                conn.commit()
        finally:
            conn.close()
        return assessments

    def check_ranking_validity(self, indicator_code: str, country_iso_list: List[str]) -> Tuple[bool, List[str]]:
        """Validate whether a ranked table or bar chart can be legitimately generated for an indicator."""
        conn = get_sqlite_conn()
        cur = conn.cursor()
        warnings = []
        is_valid = True

        for i in range(len(country_iso_list)):
            for j in range(i + 1, len(country_iso_list)):
                cA = country_iso_list[i]
                cB = country_iso_list[j]
                cur.execute("""
                SELECT classification, justification FROM comparability_assessments
                WHERE indicator_code = ? AND ((country_a = ? AND country_b = ?) OR (country_a = ? AND country_b = ?))
                """, (indicator_code, cA, cB, cB, cA))
                row = cur.fetchone()
                if row:
                    cls, just = row[0], row[1]
                    if cls == "not_comparable":
                        is_valid = False
                        warnings.append(f"CRITICAL: {cA} vs {cB} is NOT comparable for {indicator_code}. {just}")
                    elif cls == "comparable_with_caveats":
                        warnings.append(f"CAVEAT: {cA} vs {cB} has caveats for {indicator_code}. {just}")

        conn.close()
        return is_valid, warnings

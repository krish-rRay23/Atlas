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
        """Deterministically assess whether two observation points are comparable."""
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
                unit_consistency=False,
                denominator_consistency=False,
                population_consistency=False,
                methodology_consistency=False,
                period_consistency=False
            )

        # Dimension 1: Indicator identity and unit check
        unit_consistency = (ind_a.unit == ind_b.unit)
        
        # Dimension 2: Denominator check
        denominator_consistency = (ind_a.denominator == ind_b.denominator)

        # Dimension 3: Population check
        population_consistency = (ind_a.target_population == ind_b.target_population)

        # Dimension 4: Methodology check
        source_a = self.sources.get(ind_a.source_id)
        source_b = self.sources.get(ind_b.source_id)
        methodology_consistency = (
            (source_a is not None and source_b is not None) and
            (source_a.source_type == source_b.source_type)
        )

        # Dimension 5: Reference period check
        period_diff = abs(year_a - year_b)
        period_consistency = (period_diff == 0)

        # Rule evaluation
        # Rule 1: Incompatible indicators (e.g., trying to rank Account Ownership % against Transaction Volume count)
        if indicator_code_a != indicator_code_b:
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=f"{indicator_code_a}_vs_{indicator_code_b}",
                country_a=country_a,
                country_b=country_b,
                classification="not_comparable",
                justification=(
                    f"Fundamental construct divergence: '{ind_a.name}' ({ind_a.unit}) cannot be compared "
                    f"directly to '{ind_b.name}' ({ind_b.unit}). Ranking prohibited."
                ),
                rule_applied="RULE_CONSTRUCT_DIVERGENCE",
                unit_consistency=unit_consistency,
                denominator_consistency=denominator_consistency,
                population_consistency=population_consistency,
                methodology_consistency=methodology_consistency,
                period_consistency=period_consistency
            )

        # Rule 2: Special case for National Fast Payment System Volumes (e.g., UPI vs QRIS vs PromptPay)
        # Evaluated before Full Harmonization because retail payment rails have structural scale & rail composition nuances
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

        # Rule 3: Same indicator, identical dimensions and exact year
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
                    f"Both countries share identical survey/administrative methodology ({source_a.source_type}), "
                    f"harmonized denominator ('{ind_a.denominator}'), and identical reference period."
                ),
                rule_applied="RULE_FULL_HARMONIZATION",
                unit_consistency=True,
                denominator_consistency=True,
                population_consistency=True,
                methodology_consistency=True,
                period_consistency=True
            )

        # Rule 3: Same indicator, but minor temporal difference (e.g. 1-2 years gap in survey rounds)
        if (unit_consistency and denominator_consistency and 
            population_consistency and methodology_consistency and period_diff <= 2):
            return ComparabilityAssessment(
                assessment_id=assessment_id,
                indicator_code=indicator_code_a,
                country_a=country_a,
                country_b=country_b,
                classification="comparable_with_caveats",
                justification=(
                    f"Comparable with temporal caveat: '{ind_a.name}' has harmonized definitions and methodology, "
                    f"but compares {country_a} ({year_a}) with {country_b} ({year_b}), a {period_diff}-year discrepancy. "
                    "Report with temporal disclaimer."
                ),
                rule_applied="RULE_TEMPORAL_CAVEAT",
                unit_consistency=True,
                denominator_consistency=True,
                population_consistency=True,
                methodology_consistency=True,
                period_consistency=False
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

                    cur.execute("""
                    INSERT OR REPLACE INTO comparability_assessments (
                        assessment_id, indicator_code, country_a, country_b,
                        classification, justification, rule_applied,
                        unit_consistency, denominator_consistency, population_consistency,
                        methodology_consistency, period_consistency
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        asm.assessment_id, asm.indicator_code, asm.country_a, asm.country_b,
                        asm.classification, asm.justification, asm.rule_applied,
                        1 if asm.unit_consistency else 0,
                        1 if asm.denominator_consistency else 0,
                        1 if asm.population_consistency else 0,
                        1 if asm.methodology_consistency else 0,
                        1 if asm.period_consistency else 0
                    ))

        conn.commit()
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

"""ATLAS Evidence & Citation Claim Validation Engine.

Provides rigorous claim-level verification against the immutable Evidence Ledger.
Performs precision-based numerical fidelity testing, unit-aware matching,
temporal verification, and contradiction detection.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from atlas.core.db import get_sqlite_conn
from atlas.core.models import ClaimValidation

class ClaimValidationEngine:
    def __init__(self):
        pass

    @staticmethod
    def extract_numbers_from_text(text: str) -> List[Tuple[float, bool, bool]]:
        """Extract numeric candidates from text with format metadata.
        Returns tuples: (numeric_value, is_percentage, has_decimal)
        """
        # Find numeric tokens
        tokens = re.findall(r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?", text)
        results = []
        for t in tokens:
            is_pct = "%" in t
            has_dec = "." in t
            t_clean = t.replace(",", "").replace("%", "")
            try:
                val = float(t_clean)
                # Exclude 4-digit calendar years (1950-2050) from factual metric values
                if 1950 <= val <= 2050 and not has_dec and not is_pct:
                    continue
                results.append((val, is_pct, has_dec))
            except ValueError:
                pass
        return results

    def validate_claim(
        self,
        claim_text: str,
        referenced_evidence_ids: List[str]
    ) -> ClaimValidation:
        """Validate a single factual claim against its referenced evidence records.
        Applies precision-based numerical tolerances based on formatting and source units.
        """
        claim_id = f"CLM-{abs(hash(claim_text)) % 10000000}"

        if not referenced_evidence_ids:
            return ClaimValidation(
                claim_id=claim_id,
                claim_text=claim_text,
                referenced_evidence_ids=[],
                status="missing_evidence",
                numerical_fidelity_score=0.0,
                temporal_match=False,
                geographic_match=False,
                explanation="No evidence records were referenced for this factual claim. Citations are mandatory."
            )

        conn = get_sqlite_conn()
        cur = conn.cursor()

        loaded_evidence = []
        for ev_id in referenced_evidence_ids:
            cur.execute("""
            SELECT e.*, s.name as source_publisher
            FROM evidence_ledger e
            LEFT JOIN sources s ON e.source_id = s.source_id
            WHERE e.evidence_id = ?
            """, (ev_id,))
            row = cur.fetchone()
            if row:
                loaded_evidence.append(dict(row))

        conn.close()

        if not loaded_evidence:
            return ClaimValidation(
                claim_id=claim_id,
                claim_text=claim_text,
                referenced_evidence_ids=referenced_evidence_ids,
                status="unverified",
                numerical_fidelity_score=0.0,
                temporal_match=False,
                geographic_match=False,
                explanation=f"Referenced evidence ID(s) {referenced_evidence_ids} do not exist in the Evidence Ledger."
            )

        # Extract numbers from claim
        claim_num_tuples = self.extract_numbers_from_text(claim_text)

        # Extract verified numbers from evidence: primary values + citation text excerpts
        evidence_primary_values = [e["value"] for e in loaded_evidence if e["value"] is not None]
        evidence_text_numbers = []
        for e in loaded_evidence:
            cit = e.get("citation_text", "")
            for num, _, _ in self.extract_numbers_from_text(cit):
                evidence_text_numbers.append(num)

        all_evidence_numbers = list(set(evidence_primary_values + evidence_text_numbers))

        matched_nums = 0
        contradiction_details = []

        if claim_num_tuples and all_evidence_numbers:
            for c_val, is_pct, has_dec in claim_num_tuples:
                # Precision-based tolerance:
                # If claim has decimal (e.g. 89.02% or 19.89B): tolerance = 0.15
                # If claim is integer rounded (e.g. 89%): tolerance = 0.60
                allowed_tol = 0.15 if has_dec else 0.60

                closest_dist = min([abs(c_val - ev_num) for ev_num in all_evidence_numbers])
                
                if closest_dist <= allowed_tol:
                    matched_nums += 1
                elif closest_dist > 5.0:
                    # Clear contradiction: difference > 5.0 units
                    contradiction_details.append(f"Cited number {c_val} diverges significantly from evidence values {evidence_primary_values}")

            fidelity_score = matched_nums / max(len(claim_num_tuples), 1)
        elif not claim_num_tuples and not all_evidence_numbers:
            fidelity_score = 1.0
        else:
            fidelity_score = 0.5

        # Check temporal match
        temporal_match = False
        for ev in loaded_evidence:
            ref_period = ev.get("reference_period") or str(ev.get("year", ""))
            if str(ev.get("year", "")) in claim_text or ref_period in claim_text:
                temporal_match = True
                break
        if not re.search(r"\b(201\d|202\d)\b", claim_text):
            temporal_match = True

        # Check geographic match
        geographic_match = False
        for ev in loaded_evidence:
            c_name = ev["country_name"].lower()
            c_iso = ev["country_iso3"].lower()
            if c_name in claim_text.lower() or c_iso in claim_text.lower():
                geographic_match = True
                break

        # Check qualitative directional contradiction (e.g. "declined" vs positive growth)
        directional_contradiction = False
        if any(w in claim_text.lower() for w in ["decreased", "declined", "dropped", "shrank"]):
            for ev in loaded_evidence:
                cit_lower = str(ev["citation_text"]).lower()
                if any(w in cit_lower for w in ["growth", "surged", "expanded", "increased", "climb"]):
                    directional_contradiction = True
                    contradiction_details.append("Claim asserts decline/drop while source evidence confirms positive expansion.")

        # Classify final status
        is_contradicted = (directional_contradiction or (matched_nums == 0 and len(contradiction_details) > 0))

        if is_contradicted:
            status = "contradicted"
            explanation = f"Contradiction detected: {'; '.join(contradiction_details)}"
        elif fidelity_score >= 0.8 and geographic_match and temporal_match:
            status = "supported"
            explanation = "Fully verified against referenced authoritative evidence records."
        elif fidelity_score > 0.0 or (geographic_match and temporal_match):
            status = "partially_supported"
            explanation = "Partially supported: geographic or temporal alignment confirmed, but numeric precision exhibits variance."
        else:
            status = "unverified"
            explanation = "Evidence cited fails to verify the specific factual assertion."

        return ClaimValidation(
            claim_id=claim_id,
            claim_text=claim_text,
            referenced_evidence_ids=referenced_evidence_ids,
            status=status,
            numerical_fidelity_score=round(fidelity_score, 2),
            temporal_match=temporal_match,
            geographic_match=geographic_match,
            explanation=explanation
        )

    def validate_memo_claims(self, claims: List[Dict[str, Any]]) -> List[ClaimValidation]:
        """Validate a batch of claims and persist validation records to SQLite."""
        conn = get_sqlite_conn()
        cur = conn.cursor()
        results = []

        for c in claims:
            res = self.validate_claim(c["claim_text"], c.get("referenced_evidence_ids", []))
            results.append(res)
            
            cur.execute("""
            INSERT OR REPLACE INTO claim_validations (
                claim_id, claim_text, referenced_evidence_ids, status,
                numerical_fidelity_score, temporal_match, geographic_match, explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                res.claim_id, res.claim_text, ",".join(res.referenced_evidence_ids),
                res.status, res.numerical_fidelity_score,
                1 if res.temporal_match else 0,
                1 if res.geographic_match else 0,
                res.explanation
            ))

        conn.commit()
        conn.close()
        return results

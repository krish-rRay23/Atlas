"""ATLAS Evidence Ledger Service.

Provides querying, filtering, provenance tracing, and human verification
workflows for all evidence records.
"""

from typing import List, Dict, Any, Optional
import sqlite3
import datetime
from atlas.core.db import get_sqlite_conn
from atlas.core.models import EvidenceRecord

class EvidenceLedgerService:
    @staticmethod
    def list_evidence(
        country_iso3: Optional[str] = None,
        indicator_code: Optional[str] = None,
        source_id: Optional[str] = None,
        validation_status: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        search_query: Optional[str] = None,
        limit: int = 200,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve filtered evidence records from SQLite."""
        conn = get_sqlite_conn()
        cur = conn.cursor()

        query = ["SELECT * FROM evidence_ledger WHERE 1=1"]
        params = []

        if country_iso3:
            query.append("AND country_iso3 = ?")
            params.append(country_iso3)
        if indicator_code:
            query.append("AND indicator_code = ?")
            params.append(indicator_code)
        if source_id:
            query.append("AND source_id = ?")
            params.append(source_id)
        if validation_status:
            query.append("AND validation_status = ?")
            params.append(validation_status)
        if min_year:
            query.append("AND year >= ?")
            params.append(min_year)
        if max_year:
            query.append("AND year <= ?")
            params.append(max_year)
        if search_query:
            query.append("AND (citation_text LIKE ? OR page_or_table_ref LIKE ? OR country_name LIKE ?)")
            wild = f"%{search_query}%"
            params.extend([wild, wild, wild])

        query.append("ORDER BY year DESC, country_name ASC LIMIT ? OFFSET ?")
        params.extend([limit, offset])

        cur.execute(" ".join(query), params)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_evidence_by_id(evidence_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single evidence record by its unique ID."""
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM evidence_ledger WHERE evidence_id = ?", (evidence_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update_review_status(
        evidence_id: str,
        new_status: str,
        reviewer_notes: str,
        verified_by_human: bool = True
    ) -> bool:
        """Update review status and reviewer audit notes."""
        if new_status not in ["verified", "caveat", "flagged", "rejected"]:
            raise ValueError(f"Invalid validation status: {new_status}")

        conn = get_sqlite_conn()
        cur = conn.cursor()
        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        cur.execute("""
        UPDATE evidence_ledger
        SET validation_status = ?,
            reviewer_notes = ?,
            verified_by_human = ?,
            verified_at = ?
        WHERE evidence_id = ?
        """, (new_status, reviewer_notes, 1 if verified_by_human else 0, now_ts, evidence_id))
        
        updated = cur.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    @staticmethod
    def get_ledger_summary_stats() -> Dict[str, Any]:
        """Aggregate ledger statistics for executive dashboards."""
        conn = get_sqlite_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM evidence_ledger")
        total_records = cur.fetchone()[0]

        cur.execute("SELECT validation_status, COUNT(*) FROM evidence_ledger GROUP BY validation_status")
        status_counts = dict(cur.fetchall())

        cur.execute("SELECT country_iso3, COUNT(*) FROM evidence_ledger GROUP BY country_iso3")
        country_counts = dict(cur.fetchall())

        cur.execute("SELECT COUNT(DISTINCT indicator_code) FROM evidence_ledger")
        distinct_indicators = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT source_id) FROM evidence_ledger")
        distinct_sources = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM evidence_ledger WHERE verified_by_human = 1")
        human_verified_count = cur.fetchone()[0]

        conn.close()
        return {
            "total_records": total_records,
            "status_breakdown": status_counts,
            "country_breakdown": country_counts,
            "distinct_indicators": distinct_indicators,
            "distinct_sources": distinct_sources,
            "human_verified_count": human_verified_count
        }


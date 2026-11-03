"""ATLAS Structured Entity-Proximity Retriever and Oracle Retriever Upper Bound.

ATLAS Retriever leverages entity recognition (company/country), temporal year matches,
and tabular structural markers to weight candidate documents.
Oracle Retriever always guarantees that the target ground truth document is rank 1,
establishing the theoretical ceiling to isolate retrieval from reasoning errors.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from atlas.retrieval.hybrid import HybridRetriever

class AtlasStructuredRetriever:
    """Domain-specific structured retriever weighting financial entities, years, and tables."""
    def __init__(self, corpus: Dict[str, str], metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        self.corpus = corpus
        self.doc_ids = list(corpus.keys())
        self.metadata = metadata or {}
        self.hybrid = HybridRetriever(corpus)

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        # 1. Base hybrid candidates
        candidates = self.hybrid.retrieve(query, top_k=min(30, len(self.doc_ids)), mode="rrf")

        # 2. Extract query features
        q_lower = query.lower()
        years = re.findall(r"\b(20\d\d)\b", q_lower)
        has_table_intent = any(w in q_lower for w in ["table", "rate", "percent", "%", "increase", "decrease", "million", "total", "ratio"])

        rescored = []
        for doc_id, base_score in candidates:
            text = self.corpus.get(doc_id, "").lower()
            bonus = 0.0

            # Year overlap bonus
            for y in years:
                if y in text:
                    bonus += 0.05

            # Table structure bonus
            if has_table_intent and "|" in text:
                bonus += 0.04

            # Metadata matching (company name or ticker if available)
            doc_meta = self.metadata.get(doc_id, {})
            c_name = str(doc_meta.get("company_name", "")).lower()
            if c_name and c_name in q_lower:
                bonus += 0.10

            final_score = base_score + bonus
            rescored.append((doc_id, final_score))

        rescored.sort(key=lambda x: x[1], reverse=True)
        return rescored[:top_k]

class OracleRetriever:
    """Oracle retriever that places the ground-truth document at Rank 1.
    Used exclusively as an experimental upper bound to isolate retrieval errors from reasoning errors.
    """
    def __init__(self, corpus: Dict[str, str]):
        self.corpus = corpus
        self.doc_ids = list(corpus.keys())

    def retrieve(self, query: str, target_doc_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Return target_doc_id as rank 1 with 1.0 confidence, followed by other documents."""
        results = [(target_doc_id, 1.0)]
        for doc_id in self.doc_ids:
            if doc_id != target_doc_id and len(results) < top_k:
                results.append((doc_id, 0.5))
        return results

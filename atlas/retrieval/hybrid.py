"""Hybrid Retrieval Engine combining Lexical (BM25) and Dense Vector Retrieval.

Implements Reciprocal Rank Fusion (RRF) and convex alpha-score normalization
to achieve superior recall and ranking on mixed text-table contexts.
"""

from typing import List, Dict, Any, Tuple
from atlas.retrieval.bm25 import BM25Retriever
from atlas.retrieval.dense import DenseRetriever

class HybridRetriever:
    """Ensemble hybrid retriever combining BM25 and Dense vector similarity."""
    def __init__(self, corpus: Dict[str, str], rrf_k: int = 60, alpha: float = 0.5):
        self.doc_ids = list(corpus.keys())
        self.rrf_k = rrf_k
        self.alpha = alpha  # weight on BM25 vs (1-alpha) on Dense
        self.bm25 = BM25Retriever(corpus)
        self.dense = DenseRetriever(corpus)

    def retrieve(self, query: str, top_k: int = 5, mode: str = "rrf") -> List[Tuple[str, float]]:
        """Retrieve top-K documents using Reciprocal Rank Fusion (RRF) or convex scoring."""
        bm25_results = self.bm25.retrieve(query, top_k=min(50, len(self.doc_ids)))
        dense_results = self.dense.retrieve(query, top_k=min(50, len(self.doc_ids)))

        if mode == "rrf":
            # Reciprocal Rank Fusion: score(d) = sum(1 / (k + rank))
            rrf_scores: Dict[str, float] = {}
            for rank, (doc_id, _) in enumerate(bm25_results, 1):
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank))
            for rank, (doc_id, _) in enumerate(dense_results, 1):
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank))

            ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
            return ranked[:top_k]

        # Convex combination with min-max normalization
        b_max = max([s for _, s in bm25_results]) if bm25_results else 1.0
        d_max = max([s for _, s in dense_results]) if dense_results else 1.0
        b_max = b_max if b_max > 0 else 1.0
        d_max = d_max if d_max > 0 else 1.0

        scores: Dict[str, float] = {}
        for doc_id, s in bm25_results:
            scores[doc_id] = scores.get(doc_id, 0.0) + self.alpha * (s / b_max)
        for doc_id, s in dense_results:
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 - self.alpha) * (s / d_max)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

"""Retrieval Evaluation Module.

Computes standard Information Retrieval metrics:
- Recall@K (K=1, 3, 5)
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (nDCG@K)
"""

import math
from typing import List, Dict, Any, Tuple

class RetrievalEvaluator:
    @staticmethod
    def compute_recall_at_k(ranked_doc_ids: List[str], target_doc_id: str, k: int) -> float:
        """Binary recall: 1.0 if target_doc_id in top-K, else 0.0."""
        return 1.0 if target_doc_id in ranked_doc_ids[:k] else 0.0

    @staticmethod
    def compute_reciprocal_rank(ranked_doc_ids: List[str], target_doc_id: str) -> float:
        """1.0 / rank (1-indexed) if target found, else 0.0."""
        for rank, doc_id in enumerate(ranked_doc_ids, 1):
            if doc_id == target_doc_id:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def compute_ndcg_at_k(ranked_doc_ids: List[str], target_doc_id: str, k: int) -> float:
        """Binary relevance nDCG@K: DCG@K / IDCG@K."""
        dcg = 0.0
        for rank, doc_id in enumerate(ranked_doc_ids[:k], 1):
            if doc_id == target_doc_id:
                dcg = 1.0 / math.log2(rank + 1)
                break
        idcg = 1.0 / math.log2(1 + 1)  # Ideal rank is 1
        return dcg / idcg

    @classmethod
    def evaluate_retrieval_batch(
        cls,
        queries_with_targets: List[Tuple[str, str]],
        retrieve_fn: Any,
        top_k: int = 5
    ) -> Dict[str, float]:
        """Evaluate a batch of queries against target documents."""
        recalls_1 = []
        recalls_3 = []
        recalls_5 = []
        mrrs = []
        ndcgs_5 = []

        for query, target_id in queries_with_targets:
            ranked_pairs = retrieve_fn(query, top_k=top_k)
            ranked_ids = [doc_id for doc_id, _ in ranked_pairs]

            recalls_1.append(cls.compute_recall_at_k(ranked_ids, target_id, 1))
            recalls_3.append(cls.compute_recall_at_k(ranked_ids, target_id, 3))
            recalls_5.append(cls.compute_recall_at_k(ranked_ids, target_id, 5))
            mrrs.append(cls.compute_reciprocal_rank(ranked_ids, target_id))
            ndcgs_5.append(cls.compute_ndcg_at_k(ranked_ids, target_id, 5))

        n = max(1, len(queries_with_targets))
        return {
            "recall_at_1": round(sum(recalls_1) / n, 4),
            "recall_at_3": round(sum(recalls_3) / n, 4),
            "recall_at_5": round(sum(recalls_5) / n, 4),
            "mrr": round(sum(mrrs) / n, 4),
            "ndcg_at_5": round(sum(ndcgs_5) / n, 4),
            "total_queries": len(queries_with_targets)
        }

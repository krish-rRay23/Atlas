"""ATLAS Information Retrieval & Grounding Package.

Provides BM25, Dense Vector, Hybrid (RRF), ATLAS Structured, and Oracle retrievers,
alongside standardized Recall@K, MRR, and nDCG metrics.
"""

from atlas.retrieval.bm25 import BM25Retriever
from atlas.retrieval.dense import DenseRetriever
from atlas.retrieval.hybrid import HybridRetriever
from atlas.retrieval.atlas_retriever import AtlasStructuredRetriever, OracleRetriever
from atlas.retrieval.evaluator import RetrievalEvaluator

__all__ = [
    "BM25Retriever",
    "DenseRetriever",
    "HybridRetriever",
    "AtlasStructuredRetriever",
    "OracleRetriever",
    "RetrievalEvaluator",
]

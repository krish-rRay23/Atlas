"""BM25 Lexical Retrieval Engine for Document and Tabular Contexts.

Implements Okapi BM25 scoring with configurable k1 (term saturation) and b (length normalization),
text preprocessing, and tokenization.
"""

import re
import math
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi

class BM25Retriever:
    """Okapi BM25 retriever for structured documents and table context strings."""
    def __init__(self, corpus: Dict[str, str], k1: float = 1.5, b: float = 0.75):
        """Initialize with a corpus dictionary mapping doc_id -> text content."""
        self.doc_ids = list(corpus.keys())
        self.corpus_texts = list(corpus.values())
        self.k1 = k1
        self.b = b

        self.tokenized_corpus = [self._tokenize(doc) for doc in self.corpus_texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus, k1=self.k1, b=self.b)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Normalize and tokenize text, preserving alphanumeric and monetary tokens."""
        clean = re.sub(r"[^\w\s\$\%\.\-]", " ", text.lower())
        tokens = [t.strip() for t in clean.split() if len(t.strip()) > 1]
        return tokens

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Retrieve top-K document IDs with their BM25 relevance scores."""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return [(self.doc_ids[i], 0.0) for i in range(min(top_k, len(self.doc_ids)))]

        scores = self.bm25.get_scores(query_tokens)
        scored_pairs = list(zip(self.doc_ids, [float(s) for s in scores]))
        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:top_k]

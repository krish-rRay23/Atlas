"""Dense / Vector Semantic Retrieval Engine.

Implements vector space retrieval using sublinear TF-IDF character and word n-gram embeddings
with cosine similarity scoring over documents and tabular contexts.
"""

import re
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DenseRetriever:
    """Vector similarity retriever over documents and tables."""
    def __init__(self, corpus: Dict[str, str], max_features: int = 15000):
        self.doc_ids = list(corpus.keys())
        self.corpus_texts = list(corpus.values())

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=max_features,
            sublinear_tf=True,
            stop_words="english"
        )
        if self.corpus_texts:
            self.doc_embeddings = self.vectorizer.fit_transform(self.corpus_texts)
        else:
            self.doc_embeddings = None

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Retrieve top-K document IDs with vector cosine similarity scores."""
        if not self.corpus_texts or self.doc_embeddings is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.doc_embeddings).flatten()

        scored_pairs = list(zip(self.doc_ids, [float(s) for s in similarities]))
        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:top_k]


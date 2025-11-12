import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple, Dict, Any


class HybridLoadRetriever:
    """Load retriever BM25 and semantic embeddings for neural load search."""

    def __init__(
        self,
        loads: List[Any],
        text_fields: List[str] = None,
        embed_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.loads = loads
        self.text_fields = text_fields or [
            "origin",
            "destination",
            "equipment_type",
            "commodity_type",
            "notes",
        ]

        corpus = [
            " ".join(str(getattr(x, f) or "") for f in self.text_fields) for x in loads
        ]
        tokenized_corpus = [doc.lower().split() for doc in corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)

        self.model = SentenceTransformer(embed_model)
        self.embeddings = self.model.encode(corpus, normalize_embeddings=True)

    def search(
        self,
        query_dict: Dict[str, Any],
        top_k: int = 5,
        bm25_weight: float = 0.5,
        embed_weight: float = 0.5,
    ) -> List[Tuple[Any, float]]:
        """
        Search for loads using hybrid BM25 + embedding retrieval.

        Args:
            query_dict: Dictionary of search parameters (e.g., {"origin": "Los Angeles", "destination": "New York"})
            top_k: Number of top results to return
            bm25_weight: Weight for BM25 scores (default 0.5)
            embed_weight: Weight for embedding similarity scores (default 0.5)

        Returns:
            List of tuples (load, score) sorted by relevance
        """
        query_text = " ".join(str(v) for v in query_dict.values() if v)

        if not query_text.strip():
            return []

        tokenized_query = query_text.lower().split()

        bm25_scores = np.array(self.bm25.get_scores(tokenized_query))

        query_emb = self.model.encode([query_text], normalize_embeddings=True)
        embed_scores = util.cos_sim(query_emb, self.embeddings)[0].cpu().numpy()

        if bm25_scores.max() > 0:
            bm25_scores = bm25_scores / bm25_scores.max()

        scores = bm25_weight * bm25_scores + embed_weight * embed_scores
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [(self.loads[i], float(scores[i])) for i in top_indices]

# from sentence_transformers import SentenceTransformer
# import numpy as np
# import faiss
# from typing import List, Dict

# """
# FAISS-based article storage and retrieval using SentenceTransformers for embeddings.
# This module provides an ArticleStore class that allows adding articles and searching them
# based on their titles and descriptions.
# It uses the all-MiniLM-L6-v2 model for embeddings, which is a
# 384-dimensional model suitable for semantic similarity tasks.
# The articles are stored in a FAISS index, which allows efficient similarity search.
# The search function returns articles ranked by their similarity to the query.
# """

# EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim
# _embedder = None
# # Lazy loading of the SentenceTransformer model


# def _get_embedder():
#     global _embedder
#     if _embedder is None:
#         _embedder = SentenceTransformer(EMB_MODEL)
#     return _embedder


# # The ArticleStore class for managing articles with FAISS
# # This class provides methods to add articles and search them based on their titles and descriptions.
# # It uses FAISS for efficient similarity search and SentenceTransformers for embeddings.
# class ArticleStore:
#     # Initializes the FAISS index and prepares for article storage.
#     # The index uses inner product for similarity, which is suitable for normalized vectors.
#     def __init__(self, dim: int = 384):
#         self.index = faiss.IndexFlatIP(
#             dim
#         )  # inner product with normalized vecs ≈ cosine
#         self.meta: List[Dict] = []
#         self._count = 0

#     def _embed(self, texts: List[str]):
#         emb = _get_embedder().encode(texts, normalize_embeddings=True)
#         return np.asarray(emb, dtype="float32")

#     # The _embed method encodes a list of texts into embeddings using the SentenceTransformer model.
#     # It normalizes the embeddings to ensure they are unit vectors for cosine similarity.
#     def add(self, articles: List[Dict]):
#         texts = [
#             (
#                 a.get("title", "")
#                 + " "
#                 + (a.get("summary") or a.get("description") or "")
#             )
#             for a in articles
#         ]
#         vecs = self._embed(texts)
#         self.index.add(vecs)
#         self.meta.extend(articles)
#         self._count += len(articles)

#     # The add method takes a list of articles, extracts their titles and descriptions,
#     # computes their embeddings, and adds them to the FAISS index.

#     def search(self, query: str, k: int = 5) -> List[Dict]:
#         if self._count == 0:
#             return []
#         qv = self._embed([query])
#         D, I = self.index.search(qv, min(k, self._count))
#         out = []
#         for rank, idx in enumerate(I[0]):
#             art = self.meta[idx]
#             out.append(
#                 {
#                     "rank": rank + 1,
#                     "similarity": float(D[0][rank]),
#                     "title": art.get("title"),
#                     "url": art.get("url"),
#                     "source": art.get("source"),
#                     "sentiment_label": art.get("sentiment_label"),
#                     "sentiment_conf": art.get("sentiment_conf"),
#                 }
#             )
#         return out

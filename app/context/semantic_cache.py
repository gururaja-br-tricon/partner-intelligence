# -----------------------------------------------------------------------------
# SEMANTIC CACHE — SIMPLIFIED TO STRING-KEY MODE FOR POC SIMPLICITY.
# We are NOT using embeddings / RAG yet, so caching matches on a normalized
# query string instead of cosine similarity. Identical (rephrased-away) repeat
# questions still hit the cache; paraphrases do not.
# The previous embedding-based implementation is kept below as a comment block
# for future re-enable alongside the RAG pipeline.
# -----------------------------------------------------------------------------

import os
import re


def _normalize(query: str) -> str:
    """Lowercase, strip punctuation, and collapse whitespace."""
    text = query.lower().strip()
    text = re.sub(r"[\W_]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class SemanticCache:
    def __init__(self, path: str | None = None):
        self.path = path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "cache",
            "semantic_cache.json",
        )
        self.entries: dict[str, str] = {}
        self.hits: int = 0
        self.misses: int = 0
        self._load()

    def _load(self):
        import json

        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                stored = json.load(f)

            if isinstance(stored, list):
                self.entries = {}
            else:
                self.entries = stored

    def _persist(self):
        import json

        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        with open(self.path, "w") as f:
            json.dump(self.entries, f, indent=2)

    def get(self, query: str) -> str | None:
        key = _normalize(query)

        if key in self.entries:
            self.hits += 1
            return self.entries[key]

        self.misses += 1
        return None

    def put(self, query: str, answer: str) -> None:
        self.entries[_normalize(query)] = answer
        self._persist()

    def stats(self) -> dict:
        return {
            "entries": len(self.entries),
            "hits": self.hits,
            "misses": self.misses,
        }


# -----------------------------------------------------------------------------
# PREVIOUS EMBEDDING-BASED IMPLEMENTATION (disabled, RAG not used).
# Requires an embedder + cosine_similarity from app.rag.vector_store.
# -----------------------------------------------------------------------------
# import os
#
# import numpy as np
#
# from app.rag.vector_store import cosine_similarity
#
#
# class SemanticCache:
#     def __init__(self, threshold: float = 0.95, path: str | None = None):
#         self.threshold = threshold
#         self.path = path or os.path.join(
#             os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
#             "data",
#             "cache",
#             "semantic_cache.json",
#         )
#         self.entries: list[dict] = []
#         self.hits: int = 0
#         self.misses: int = 0
#         self._load()
#
#     def _load(self):
#         import json
#
#         if os.path.exists(self.path):
#             with open(self.path, "r") as f:
#                 self.entries = json.load(f)
#
#     def _persist(self):
#         import json
#
#         os.makedirs(os.path.dirname(self.path), exist_ok=True)
#
#         with open(self.path, "w") as f:
#             json.dump(self.entries, f, indent=2)
#
#     def _find(self, query_embedding):
#         if not self.entries:
#             return None
#
#         embedded = [e["embedding"] for e in self.entries]
#
#         scores = cosine_similarity(query_embedding, embedded)
#
#         best_index = int(np.argmax(scores))
#
#         if scores[best_index] >= self.threshold:
#             return self.entries[best_index]
#
#         return None
#
#     def get(self, query_embedding):
#         entry = self._find(query_embedding)
#
#         if entry is not None:
#             self.hits += 1
#             return entry
#
#         self.misses += 1
#         return None
#
#     def put(self, query: str, query_embedding, answer: str) -> None:
#         self.entries.append(
#             {
#                 "query": query,
#                 "embedding": query_embedding,
#                 "answer": answer,
#             }
#         )
#         self._persist()
#
#     def stats(self) -> dict:
#         return {
#             "entries": len(self.entries),
#             "hits": self.hits,
#             "misses": self.misses,
#         }
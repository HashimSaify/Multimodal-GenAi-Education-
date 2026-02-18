"""Lightweight vector store using sentence-transformers + NumPy.

Replaces ChromaDB to avoid Python 3.14 / Pydantic-v1 incompatibility.
Data is persisted as a JSON file in the configured persist path.
"""

import json
import os
from pathlib import Path
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class VectorDB:
    def __init__(self, persist_path: str = "./vector_store"):
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self._store_file = self.persist_path / "store.json"
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self._documents: list[dict] = []
        self._embeddings: list[list[float]] = []
        self._load()

    # ---- persistence ----

    def _load(self):
        if self._store_file.exists():
            data = json.loads(self._store_file.read_text(encoding="utf-8"))
            self._documents = data.get("documents", [])
            self._embeddings = data.get("embeddings", [])

    def _save(self):
        self._store_file.write_text(
            json.dumps(
                {"documents": self._documents, "embeddings": self._embeddings}
            ),
            encoding="utf-8",
        )

    # ---- public API (same interface as before) ----

    def add_document(self, prompt: str, explanation: str):
        embedding = self.embedder.encode(explanation).tolist()
        self._documents.append({"prompt": prompt, "explanation": explanation})
        self._embeddings.append(embedding)
        self._save()

    def search(self, query: str, top_k: int = 3):
        if not self._embeddings:
            return []
        q_embed = np.array(self.embedder.encode(query))
        db_embeds = np.array(self._embeddings)

        # cosine similarity
        norms = np.linalg.norm(db_embeds, axis=1) * np.linalg.norm(q_embed)
        norms = np.where(norms == 0, 1, norms)  # avoid division by zero
        similarities = db_embeds @ q_embed / norms

        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [
            {
                "explanation": self._documents[i]["explanation"],
                "prompt": self._documents[i]["prompt"],
            }
            for i in top_indices
        ]

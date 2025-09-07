"""Embedding + FAISS vector store utilities."""
from __future__ import annotations
import os
import pickle
from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np

try:
    import faiss  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError("faiss not installed. Add to requirements.txt (cpu version).") from e

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class VectorStore:
    index: any
    embeddings: np.ndarray
    texts: List[str]
    model_name: str

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "meta.pkl"), "wb") as f:
            pickle.dump({
                "texts": self.texts,
                "embeddings_shape": self.embeddings.shape,
                "model_name": self.model_name
            }, f)

    @classmethod
    def load(cls, path: str) -> "VectorStore":
        index = faiss.read_index(os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "meta.pkl"), "rb") as f:
            meta = pickle.load(f)
        # embeddings not stored (could store optional). We'll lazily reconstruct if needed.
        return cls(index=index, embeddings=np.empty(meta["embeddings_shape"]), texts=meta["texts"], model_name=meta["model_name"])

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[int, float, str]]:
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        distances, indices = self.index.search(query_embedding.astype("float32"), top_k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            results.append((int(idx), float(dist), self.texts[idx]))
        return results


def load_embedding_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def chunk_text(text: str, max_chars: int = 600, overlap: int = 120) -> List[str]:
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + max_chars)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def build_faiss_index(embeddings: np.ndarray):
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings.astype('float32'))
    return index


def create_vector_store(text: str, model_name: str = DEFAULT_MODEL_NAME, chunk_size: int = 600, overlap: int = 120) -> VectorStore:
    model = load_embedding_model(model_name)
    chunks = chunk_text(text, chunk_size, overlap)
    embeddings = model.encode(chunks, batch_size=16, show_progress_bar=False, convert_to_numpy=True)
    index = build_faiss_index(embeddings)
    return VectorStore(index=index, embeddings=embeddings, texts=chunks, model_name=model_name)


def embed_query(query: str, model: SentenceTransformer) -> np.ndarray:
    return model.encode([query], convert_to_numpy=True)[0]

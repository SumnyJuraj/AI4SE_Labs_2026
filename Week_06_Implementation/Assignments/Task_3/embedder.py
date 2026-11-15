#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "fastembed>=0.2.0",
#     "numpy>=1.20.0",
# ]
# ///
"""
Chunk Embedder & Vector Storage Engine (Task 3)

Generates dense numerical vector representations for code chunks produced in Task 2
and provides a persistent vector storage mechanism for downstream semantic retrieval.

Assignment: Week 06 Implementation - Task 3
Course: AI for Software Engineering (AI4SE)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


class CodeEmbedder:
    """
    Transforms code chunks into dense numerical embedding vectors.
    Uses ONNX-accelerated BAAI/bge-small-en-v1.5 (384 dimensions) by default,
    with an automatic fallback to LSA/TF-IDF dense vectors if fastembed is unavailable.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None
        self.dimension = 384
        self._init_model()

    def _init_model(self):
        try:
            from fastembed import TextEmbedding
            print(f"[*] Initializing FastEmbed dense transformer model: {self.model_name}")
            self._model = TextEmbedding(model_name=self.model_name)
            self.dimension = 384
            self.backend = "fastembed"
        except ImportError:
            print("[!] fastembed not found. Falling back to SVD/TF-IDF dense semantic embedder.")
            self.backend = "lsa_fallback"
            self.dimension = 300

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Computes L2-normalized embeddings for a list of text strings."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        if self.backend == "fastembed":
            raw_embeddings = list(self._model.embed(texts))
            matrix = np.array(raw_embeddings, dtype=np.float32)
        else:
            matrix = self._lsa_embed(texts)

        # L2-normalize vectors so dot product is exact cosine similarity
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1e-12
        normalized_matrix = matrix / norms
        return normalized_matrix

    def embed_text(self, text: str) -> np.ndarray:
        """Computes L2-normalized embedding for a single text query."""
        return self.embed_texts([text])[0]

    def _lsa_embed(self, texts: List[str]) -> np.ndarray:
        """Fallback dense vectorizer using TF-IDF and Truncated SVD."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import TruncatedSVD

            vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", max_features=2000)
            tfidf = vectorizer.fit_transform(texts)
            n_components = min(self.dimension, max(2, tfidf.shape[1] - 1))
            svd = TruncatedSVD(n_components=n_components, random_state=42)
            dense = svd.fit_transform(tfidf)
            if dense.shape[1] < self.dimension:
                padded = np.zeros((dense.shape[0], self.dimension), dtype=np.float32)
                padded[:, : dense.shape[1]] = dense
                return padded
            return dense.astype(np.float32)
        except Exception:
            # Deterministic pseudo-semantic token hash projection
            vocab_dim = self.dimension
            vectors = np.zeros((len(texts), vocab_dim), dtype=np.float32)
            for i, txt in enumerate(texts):
                for word in txt.split():
                    h = hash(word) % vocab_dim
                    vectors[i, h] += 1.0
            return vectors


class EmbeddingStore:
    """
    Manages persistent storage and retrieval of chunk-embedding pairs.
    Saves dual representations:
      1. embeddings.json - portable, human-readable structured archive.
      2. embeddings.npz  - high-throughput binary NumPy array for sub-millisecond retrieval.
    """

    def __init__(self, embedder: Optional[CodeEmbedder] = None):
        self.embedder = embedder or CodeEmbedder()
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.chunk_ids: List[str] = []

    @staticmethod
    def construct_chunk_representation(chunk: Dict[str, Any]) -> str:
        """
        Creates the optimal text representation for embedding:
        Combines structural identifiers (file, class, methods) with the context-enriched code.
        """
        file_path = chunk.get("file", "")
        class_name = chunk.get("class_name") or ""
        methods = " ".join(chunk.get("methods", []))
        component = chunk.get("component", "source")

        # Explicit header boosts retrieval accuracy for class/method name queries
        header = f"# Target File: {file_path}\n# Class: {class_name}\n# Methods: {methods}\n# Type: {component}"
        content = chunk.get("content", chunk.get("code", ""))

        return f"{header}\n\n{content}"

    def build_store(self, chunks: List[Dict[str, Any]], batch_size: int = 64) -> None:
        """Generates embeddings for all chunks and indexes them in memory."""
        self.chunks = chunks
        self.chunk_ids = [c["id"] for c in chunks]

        print(f"[*] Preparing text representations for {len(chunks)} chunks...")
        representations = [self.construct_chunk_representation(c) for c in chunks]

        print(f"[*] Generating {self.embedder.dimension}-dimensional embeddings...")
        all_embeddings = []
        for i in range(0, len(representations), batch_size):
            batch = representations[i : i + batch_size]
            emb_batch = self.embedder.embed_texts(batch)
            all_embeddings.append(emb_batch)

        self.embeddings = np.vstack(all_embeddings)
        print(f"[+] Embeddings successfully generated with matrix shape: {self.embeddings.shape}")

    def save(self, json_path: str, npz_path: Optional[str] = None) -> None:
        """Persists the chunk-embedding store to disk."""
        if self.embeddings is None:
            raise ValueError("No embeddings to save. Run build_store() or load() first.")

        os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)

        if npz_path is None:
            npz_path = str(Path(json_path).with_suffix(".npz"))

        # 1. Save optimized binary NumPy archive
        np.savez_compressed(
            npz_path,
            embeddings=self.embeddings,
            chunk_ids=np.array(self.chunk_ids),
        )

        # 2. Save portable JSON storage with chunk-embedding pairs
        records = []
        for i, chunk in enumerate(self.chunks):
            record = dict(chunk)
            record["embedding"] = self.embeddings[i].tolist()
            record["embedding_repr"] = self.construct_chunk_representation(chunk)
            records.append(record)

        payload = {
            "metadata": {
                "model_name": self.embedder.model_name,
                "embedding_dimension": int(self.embeddings.shape[1]),
                "total_chunks": len(self.chunks),
                "similarity_metric": "cosine",
                "binary_archive": os.path.basename(npz_path),
            },
            "records": records,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"[+] Storage saved successfully:")
        print(f"    - JSON Archive: {json_path}")
        print(f"    - Binary Array: {npz_path}")

    def load(self, json_path: str, npz_path: Optional[str] = None) -> None:
        """Loads chunks and embeddings from disk."""
        if npz_path is None:
            npz_path = str(Path(json_path).with_suffix(".npz"))

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.chunks = []
        for record in data["records"]:
            c = dict(record)
            c.pop("embedding", None)
            c.pop("embedding_repr", None)
            self.chunks.append(c)
        self.chunk_ids = [c["id"] for c in self.chunks]

        if os.path.exists(npz_path):
            with np.load(npz_path) as npz:
                self.embeddings = npz["embeddings"]
        else:
            # Reconstruct from JSON embeddings
            self.embeddings = np.array([r["embedding"] for r in data["records"]], dtype=np.float32)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieves the top-k most relevant chunks for a textual query using cosine similarity.
        """
        if self.embeddings is None:
            raise ValueError("Store is empty. Please load or build embeddings first.")

        query_vec = self.embedder.embed_text(query)
        # Cosine similarity via dot product of L2-normalized vectors
        scores = np.dot(self.embeddings, query_vec)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(scores[idx])))

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Compute embeddings for code chunks and manage vector storage."
    )
    parser.add_argument(
        "--chunks-path",
        type=str,
        default=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../Task_2/chunks.json",
            )
        ),
        help="Path to chunks.json produced by Task 2.",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "embeddings.json")
        ),
        help="Destination path for embeddings.json.",
    )
    parser.add_argument(
        "--output-npz",
        type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "embeddings.npz")
        ),
        help="Destination path for binary embeddings.npz.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Optional test query to run against the indexed vector store.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of chunks to retrieve for test query.",
    )

    args = parser.parse_args()

    if not os.path.exists(args.chunks_path):
        print(f"Error: Chunks file not found at {args.chunks_path}", file=sys.stderr)
        sys.exit(1)

    with open(args.chunks_path, "r", encoding="utf-8") as f:
        chunks_file_data = json.load(f)
        chunks = chunks_file_data.get("chunks", [])

    print(f"[*] Loaded {len(chunks)} chunks from {args.chunks_path}")

    embedder = CodeEmbedder()
    store = EmbeddingStore(embedder=embedder)
    store.build_store(chunks)
    store.save(args.output_json, args.output_npz)

    if args.query:
        print(f"\n[*] Executing sample query: '{args.query}' (top {args.top_k})")
        results = store.search(args.query, top_k=args.top_k)
        for rank, (chunk, score) in enumerate(results, 1):
            methods = ", ".join(chunk.get("methods", []))
            print(
                f"  {rank}. [Score: {score:.4f}] {chunk['id']} -> {chunk['file']} "
                f"(Class: {chunk.get('class_name')}, Methods: [{methods}])"
            )


if __name__ == "__main__":
    main()

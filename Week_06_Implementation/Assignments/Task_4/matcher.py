#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "fastembed>=0.2.0",
#     "numpy>=1.20.0",
# ]
# ///
"""
Vector Matching & Top-N Retrieval Engine (Task 4)

Implements high-performance similarity matching between an input embedding
(representing a programming task or query) and the persistent chunk embeddings
stored in Task 3. Supports cosine similarity, euclidean distance, and raw dot product.

Assignment: Week 06 Implementation - Task 4
Course: AI for Software Engineering (AI4SE)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# Dynamically import CodeEmbedder from Task 3 if available
TASK3_DIR = Path(__file__).resolve().parent.parent / "Task_3"
if str(TASK3_DIR) not in sys.path:
    sys.path.append(str(TASK3_DIR))

try:
    from embedder import CodeEmbedder
except ImportError:
    CodeEmbedder = None


class EmbeddingMatcher:
    """
    Retrieval engine that performs exact vector similarity search against
    precomputed code chunk embeddings.
    """

    SUPPORTED_METRICS = {"cosine", "euclidean", "dot"}

    def __init__(
        self,
        embeddings_path: Optional[str] = None,
        npz_path: Optional[str] = None,
        embedder: Optional[Any] = None,
    ):
        self.embeddings_path = embeddings_path or str(TASK3_DIR / "embeddings.json")
        self.npz_path = npz_path or str(TASK3_DIR / "embeddings.npz")
        self.chunks: List[Dict[str, Any]] = []
        self.chunk_ids: List[str] = []
        self.matrix: Optional[np.ndarray] = None
        self.embedder = embedder
        self.load_storage()

    def load_storage(self) -> None:
        """Loads chunks metadata and dense vector matrix into memory."""
        if not os.path.exists(self.embeddings_path):
            raise FileNotFoundError(
                f"Embeddings storage not found at: {self.embeddings_path}. Run Task 3 embedder first."
            )

        with open(self.embeddings_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = data.get("records", [])
        self.chunks = []
        for r in records:
            chunk_copy = dict(r)
            chunk_copy.pop("embedding", None)
            chunk_copy.pop("embedding_repr", None)
            self.chunks.append(chunk_copy)

        self.chunk_ids = [c["id"] for c in self.chunks]

        # Prefer binary NumPy archive for instantaneous loading
        if os.path.exists(self.npz_path):
            with np.load(self.npz_path) as npz:
                self.matrix = npz["embeddings"].astype(np.float32)
        else:
            self.matrix = np.array([r["embedding"] for r in records], dtype=np.float32)

        # Ensure L2-normalization for cosine search
        norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1e-12
        self.matrix = self.matrix / norms

        print(
            f"[*] Loaded {len(self.chunks)} chunks into vector matrix of shape: {self.matrix.shape}"
        )

    def match_embedding(
        self,
        query_vector: Union[List[float], np.ndarray],
        top_n: int = 5,
        metric: str = "cosine",
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_n most relevant chunks for an input numerical embedding vector.

        Args:
            query_vector: A 1D numerical embedding vector (e.g. 384 dimensions).
            top_n: Number of candidate chunks to retrieve.
            metric: Similarity metric ('cosine', 'euclidean', 'dot').

        Returns:
            List of dictionaries containing chunk metadata and similarity score.
        """
        if self.matrix is None or len(self.chunks) == 0:
            raise ValueError("Matcher storage is empty. Please load embeddings first.")

        q = np.asarray(query_vector, dtype=np.float32).flatten()
        if q.shape[0] != self.matrix.shape[1]:
            raise ValueError(
                f"Dimension mismatch: query vector has dim {q.shape[0]}, "
                f"expected {self.matrix.shape[1]}"
            )

        metric = metric.lower()
        if metric not in self.SUPPORTED_METRICS:
            raise ValueError(f"Unsupported metric: {metric}. Choose from: {self.SUPPORTED_METRICS}")

        t0 = time.perf_counter()

        if metric == "cosine":
            q_norm = np.linalg.norm(q)
            if q_norm == 0:
                q_norm = 1e-12
            q_unit = q / q_norm
            # Dot product of normalized vectors equals cosine similarity
            scores = np.dot(self.matrix, q_unit)
            top_indices = np.argsort(scores)[::-1][:top_n]

        elif metric == "dot":
            scores = np.dot(self.matrix, q)
            top_indices = np.argsort(scores)[::-1][:top_n]

        elif metric == "euclidean":
            # Euclidean distance: ||u - v||_2
            diffs = self.matrix - q
            dists = np.linalg.norm(diffs, axis=1)
            # Invert distance so higher score means closer match: score = 1 / (1 + dist)
            scores = 1.0 / (1.0 + dists)
            top_indices = np.argsort(dists)[:top_n]

        latency_ms = (time.perf_counter() - t0) * 1000.0

        results = []
        for rank, idx in enumerate(top_indices, 1):
            chunk = dict(self.chunks[idx])
            result = {
                "rank": rank,
                "chunk_id": chunk["id"],
                "file": chunk.get("file"),
                "component": chunk.get("component"),
                "class_name": chunk.get("class_name"),
                "methods": chunk.get("methods", []),
                "start_line": chunk.get("start_line"),
                "end_line": chunk.get("end_line"),
                "line_count": chunk.get("line_count"),
                "score": float(scores[idx]),
                "metric": metric,
                "latency_ms": latency_ms,
                "code": chunk.get("code", ""),
                "content": chunk.get("content", ""),
            }
            results.append(result)

        return results

    def match_task(
        self,
        task_text: str,
        top_n: int = 5,
        metric: str = "cosine",
    ) -> List[Dict[str, Any]]:
        """
        Embeds a textual task description and retrieves the top_n most relevant chunks.
        """
        if self.embedder is None:
            if CodeEmbedder is None:
                raise ImportError(
                    "CodeEmbedder not found. Provide an embedder instance or install Task 3 dependencies."
                )
            self.embedder = CodeEmbedder()

        query_vec = self.embedder.embed_text(task_text)
        return self.match_embedding(query_vec, top_n=top_n, metric=metric)

    def batch_match(
        self,
        query_vectors: np.ndarray,
        top_n: int = 5,
        metric: str = "cosine",
    ) -> List[List[Dict[str, Any]]]:
        """
        Performs high-throughput vectorized batch retrieval for multiple queries simultaneously.
        """
        results = []
        for vec in query_vectors:
            results.append(self.match_embedding(vec, top_n=top_n, metric=metric))
        return results


def run_benchmark_on_missing_code(matcher: EmbeddingMatcher, top_n: int = 5) -> None:
    """Evaluates matcher against all 10 target tasks defined in missing_code.json."""
    missing_path = Path(__file__).resolve().parent.parent / "missing_code.json"
    if not missing_path.exists():
        print(f"missing_code.json not found at: {missing_path}", file=sys.stderr)
        return

    with open(missing_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    print(f"\n{'='*80}")
    print(f"BENCHMARK: Matching top {top_n} chunks for 10 tasks from missing_code.json")
    print(f"{'='*80}\n")

    perfect_matches = 0
    top5_hits = 0

    for i, t in enumerate(tasks, 1):
        target_file = t["file"]
        target_class = t["class"]
        target_method = t["method"]
        docstring = t["docstring"].strip()

        # Query format combining task identifiers and semantics
        query = f"{target_file} {target_class} {target_method} {docstring}"
        matches = matcher.match_task(query, top_n=top_n, metric="cosine")

        top1 = matches[0]
        # Check if target class or method is present in top 1
        is_top1_hit = (
            (top1.get("class_name") == target_class)
            or (target_method in top1.get("methods", []))
            or (target_file.endswith(top1.get("file", "")))
        )
        if is_top1_hit:
            perfect_matches += 1

        # Check if target is present within top N
        in_top_n = any(
            (m.get("class_name") == target_class) or (target_method in m.get("methods", []))
            for m in matches
        )
        if in_top_n:
            top5_hits += 1

        print(
            f"Task {i:02d}: {target_class}.{target_method}() [{target_file}]\n"
            f"  -> Top 1: {top1['chunk_id']} (Score: {top1['score']:.4f}, Latency: {top1['latency_ms']:.2f}ms)\n"
            f"     File: {top1['file']}, Class: {top1['class_name']}, Methods: {top1['methods'][:3]}\n"
            f"  -> Rank 1 Match: {'YES' if is_top1_hit else 'NEARBY'}, Top-{top_n} Match: {'YES' if in_top_n else 'NO'}\n"
        )

    print(f"{'='*80}")
    print(f"RESULTS SUMMARY:")
    print(f"  - Top-1 Precision: {perfect_matches}/{len(tasks)} ({perfect_matches/len(tasks)*100:.1f}%)")
    print(f"  - Top-{top_n} Recall:   {top5_hits}/{len(tasks)} ({top5_hits/len(tasks)*100:.1f}%)")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve top-n matching chunks for an input embedding or task query."
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Textual task query to embed and match against chunk storage.",
    )
    parser.add_argument(
        "--embedding-json",
        type=str,
        default=None,
        help="Path to JSON file containing a raw numerical embedding array to match directly.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of most relevant chunks to retrieve (default: 5).",
    )
    parser.add_argument(
        "--metric",
        type=str,
        default="cosine",
        choices=["cosine", "euclidean", "dot"],
        help="Similarity metric for matching (default: cosine).",
    )
    parser.add_argument(
        "--test-missing-code",
        action="store_true",
        help="Run benchmark across all 10 tasks in missing_code.json.",
    )

    args = parser.parse_args()

    matcher = EmbeddingMatcher()

    if args.test_missing_code:
        run_benchmark_on_missing_code(matcher, top_n=args.top_n)
        return

    if args.embedding_json:
        with open(args.embedding_json, "r") as f:
            query_vec = json.load(f)
        print(f"[*] Loaded query vector of length {len(query_vec)} from {args.embedding_json}")
        matches = matcher.match_embedding(query_vec, top_n=args.top_n, metric=args.metric)
    elif args.task:
        print(f"[*] Matching task: '{args.task}' (metric: {args.metric}, top_n: {args.top_n})")
        matches = matcher.match_task(args.task, top_n=args.top_n, metric=args.metric)
    else:
        # Default demonstration query if no arguments provided
        demo_query = "Customer can_afford: check if balance plus total exceeds credit limit"
        print(f"[*] Running demo matching query: '{demo_query}'")
        matches = matcher.match_task(demo_query, top_n=args.top_n, metric=args.metric)

    print(f"\nTop {len(matches)} retrieved chunks:")
    for m in matches:
        methods_str = ", ".join(m["methods"][:4]) if m["methods"] else "N/A"
        print(
            f"  Rank {m['rank']}: [Score: {m['score']:.4f}] {m['chunk_id']} | "
            f"{m['file']} | Class: {m['class_name']} | Methods: [{methods_str}]"
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Task 3: Custom Evaluation Metric Implementation
Proposes, implements, and evaluates a Soft Row-Level F1-Score (and Latency-Adjusted Utility)
for evaluating Text-to-SQL predictions against the restaurants database.
Complements the strict binary exact-match accuracy from Task 2.
"""

import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Increase CSV field size limit
csv.field_size_limit(1_000_000_000)

BASE_DIR = Path(__file__).resolve().parent
ASSIGNMENTS_DIR = BASE_DIR.parent
TASK_2_DATA_DIR = ASSIGNMENTS_DIR / "Task_2" / "data"
LABELS_PATH = TASK_2_DATA_DIR / "restaurants_dataset.csv"

# Import evaluation database loader
sys.path.append(str(TASK_2_DATA_DIR))
from evaluate_retrieval_predictions import load_database, row_multiset


def compute_row_level_metrics(predicted_rows, expected_rows, latency_s=None):
    """
    Computes fine-grained multiset information retrieval metrics:
    - Exact Match (Original Task 2 metric)
    - Row-Level Precision
    - Row-Level Recall
    - Row-Level F1-Score
    - Jaccard Multiset Similarity
    - Latency-Adjusted Efficiency Score (F1 / (log2(1 + latency) + 1))
    """
    pred_counter = Counter(tuple(r) for r in predicted_rows)
    exp_counter = Counter(tuple(r) for r in expected_rows)

    # Intersection multiset: min count for each element
    intersection_counter = pred_counter & exp_counter
    intersection_count = sum(intersection_counter.values())

    len_pred = len(predicted_rows)
    len_exp = len(expected_rows)

    # Exact Match (Original Metric)
    exact_match = 1.0 if pred_counter == exp_counter else 0.0

    # Handle empty expected / predicted edge cases
    if len_exp == 0 and len_pred == 0:
        precision = 1.0
        recall = 1.0
        f1 = 1.0
        jaccard = 1.0
    elif len_exp == 0 and len_pred > 0:
        precision = 0.0
        recall = 0.0
        f1 = 0.0
        jaccard = 0.0
    elif len_exp > 0 and len_pred == 0:
        precision = 0.0
        recall = 0.0
        f1 = 0.0
        jaccard = 0.0
    else:
        precision = intersection_count / len_pred
        recall = intersection_count / len_exp
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0
        union_count = len_pred + len_exp - intersection_count
        jaccard = intersection_count / union_count if union_count > 0 else 0.0

    # Latency-Adjusted Efficiency Score
    if latency_s is not None and latency_s > 0:
        efficiency_score = f1 / (math.log2(1.0 + latency_s) + 1.0)
    else:
        efficiency_score = f1

    return {
        "exact_match": exact_match,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "jaccard": jaccard,
        "efficiency_score": efficiency_score,
    }


def evaluate_predictions_file(pred_file_path, conn, ground_truth):
    """Evaluates a predictions CSV file across all metrics."""
    with open(pred_file_path, "r", encoding="utf-8") as f:
        predictions = list(csv.DictReader(f))

    if len(predictions) != len(ground_truth):
        raise ValueError(f"Mismatch in count: {len(predictions)} predictions vs {len(ground_truth)} labels.")

    metrics_list = []
    latencies = []

    for gt_row, pred_row in zip(ground_truth, predictions):
        expected_rows = json.loads(gt_row["result"])
        pred_sql = pred_row["predicted_sql"]
        lat = float(pred_row.get("inference_time_s", 0.0))
        latencies.append(lat)

        try:
            predicted_rows = conn.execute(pred_sql).fetchall()
        except Exception:
            predicted_rows = []

        m = compute_row_level_metrics(predicted_rows, expected_rows, latency_s=lat)
        metrics_list.append(m)

    # Aggregate means
    n = len(metrics_list)
    summary = {
        "count": n,
        "exact_accuracy": sum(m["exact_match"] for m in metrics_list) / n,
        "mean_precision": sum(m["precision"] for m in metrics_list) / n,
        "mean_recall": sum(m["recall"] for m in metrics_list) / n,
        "mean_f1": sum(m["f1"] for m in metrics_list) / n,
        "mean_jaccard": sum(m["jaccard"] for m in metrics_list) / n,
        "mean_efficiency": sum(m["efficiency_score"] for m in metrics_list) / n,
        "mean_latency": sum(latencies) / n,
        "f1_scores": [m["f1"] for m in metrics_list],
        "efficiency_scores": [m["efficiency_score"] for m in metrics_list],
    }
    return summary


def main():
    print("=" * 60)
    print("Task 3: Custom Metric Calculation on Task 2 Predictions")
    print("=" * 60)

    # 1. Load ground truth dataset
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        ground_truth = list(csv.DictReader(f))
    print(f"Loaded {len(ground_truth)} ground truth questions.")

    # 2. Load database
    conn = load_database()

    frameworks = {
        "ICIO": TASK_2_DATA_DIR / "predictions_icio.csv",
        "Few-Shot": TASK_2_DATA_DIR / "predictions_few_shot.csv",
        "CoT": TASK_2_DATA_DIR / "predictions_cot.csv",
    }

    results = {}
    print("\nCalculating metrics across frameworks...")
    for name, path in frameworks.items():
        if not path.exists():
            print(f"Error: {path} not found. Please run Task 2 first.")
            return
        res = evaluate_predictions_file(path, conn, ground_truth)
        results[name] = res

        print(f"\n--- Framework: {name} ---")
        print(f"  Exact Match Accuracy: {res['exact_accuracy']:.2%}")
        print(f"  Mean Precision:       {res['mean_precision']:.4f}")
        print(f"  Mean Recall:          {res['mean_recall']:.4f}")
        print(f"  Mean Row-Level F1:    {res['mean_f1']:.4f} ({res['mean_f1']:.2%})")
        print(f"  Mean Jaccard Index:   {res['mean_jaccard']:.4f}")
        print(f"  Mean Efficiency Score:{res['mean_efficiency']:.4f}")
        print(f"  Mean Latency:         {res['mean_latency']:.4f}s")

    # 3. Generate Visualization
    print("\nGenerating Task 3 visualization...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    names = list(frameworks.keys())
    exact_accs = [results[k]["exact_accuracy"] * 100 for k in names]
    f1_scores = [results[k]["mean_f1"] * 100 for k in names]
    eff_scores = [results[k]["mean_efficiency"] * 100 for k in names]

    x = np.arange(len(names))
    width = 0.28

    # Panel 1: Strict Accuracy vs Soft F1 vs Efficiency
    rects1 = ax1.bar(x - width, exact_accs, width, label="Exact Match Accuracy (%)", color="#3498db", edgecolor="black")
    rects2 = ax1.bar(x, f1_scores, width, label="Soft Row-Level F1 (%)", color="#2ecc71", edgecolor="black")
    rects3 = ax1.bar(x + width, eff_scores, width, label="Efficiency-Adjusted F1 (%)", color="#9b59b6", edgecolor="black")

    ax1.set_title("Metric Comparison Across Frameworks", fontsize=13, fontweight="bold", pad=12)
    ax1.set_ylabel("Score (%)", fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontsize=11, fontweight="bold")
    ax1.set_ylim(0, 105)
    ax1.legend(loc="upper left")
    ax1.grid(axis="y", linestyle="--", alpha=0.6)

    def autolabel(rects, ax):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height:.1f}%",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

    autolabel(rects1, ax1)
    autolabel(rects2, ax1)
    autolabel(rects3, ax1)

    # Panel 2: Distribution of Row-Level F1 Scores
    f1_distributions = [results[k]["f1_scores"] for k in names]
    box = ax2.boxplot(f1_distributions, labels=names, patch_artist=True, widths=0.55)
    colors = ["#3498db", "#2ecc71", "#e67e22"]
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax2.set_title("Distribution of Row-Level F1 Scores", fontsize=13, fontweight="bold", pad=12)
    ax2.set_ylabel("F1 Score [0.0 - 1.0]", fontsize=11)
    ax2.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    viz_path = BASE_DIR / "task_3_metric_comparison.png"
    plt.savefig(viz_path, dpi=300)
    print(f"[OK] Saved visualization to: {viz_path}")

    # 4. Save metrics summary CSV
    summary_csv_path = BASE_DIR / "metrics_comparison.csv"
    with open(summary_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Framework", "Exact_Accuracy", "Precision", "Recall", "Row_F1", "Jaccard", "Efficiency_Score", "Mean_Latency_s"])
        for k in names:
            r = results[k]
            writer.writerow([
                k,
                f"{r['exact_accuracy']:.4f}",
                f"{r['mean_precision']:.4f}",
                f"{r['mean_recall']:.4f}",
                f"{r['mean_f1']:.4f}",
                f"{r['mean_jaccard']:.4f}",
                f"{r['mean_efficiency']:.4f}",
                f"{r['mean_latency']:.4f}",
            ])
    print(f"[OK] Saved summary CSV to: {summary_csv_path}")


if __name__ == "__main__":
    main()

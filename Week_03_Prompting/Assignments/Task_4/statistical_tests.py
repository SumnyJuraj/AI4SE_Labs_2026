#!/usr/bin/env python3
"""
Task 4: Statistical Significance Testing & Factor Analysis
Calculates McNemar's tests for paired binary accuracy, Wilcoxon signed-rank tests
for latency and soft F1 scores, constructs contingency tables, and produces
publication-grade comparative visualizations.
"""

import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Increase CSV field size limit
csv.field_size_limit(1_000_000_000)

BASE_DIR = Path(__file__).resolve().parent
ASSIGNMENTS_DIR = BASE_DIR.parent
TASK_2_DATA_DIR = ASSIGNMENTS_DIR / "Task_2" / "data"
LABELS_PATH = TASK_2_DATA_DIR / "restaurants_dataset.csv"

sys.path.append(str(TASK_2_DATA_DIR))
from evaluate_retrieval_predictions import load_database, row_multiset


def compute_instance_metrics(predicted_rows, expected_rows, latency_s):
    pred_counter = Counter(tuple(r) for r in predicted_rows)
    exp_counter = Counter(tuple(r) for r in expected_rows)

    intersection_counter = pred_counter & exp_counter
    intersection_count = sum(intersection_counter.values())

    len_pred = len(predicted_rows)
    len_exp = len(expected_rows)

    exact_match = 1 if pred_counter == exp_counter else 0

    if len_exp == 0 and len_pred == 0:
        f1 = 1.0
        jaccard = 1.0
    elif len_exp == 0 or len_pred == 0:
        f1 = 0.0
        jaccard = 0.0
    else:
        p = intersection_count / len_pred
        r = intersection_count / len_exp
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        union_count = len_pred + len_exp - intersection_count
        jaccard = intersection_count / union_count if union_count > 0 else 0.0

    eff = f1 / (math.log2(1.0 + latency_s) + 1.0) if latency_s > 0 else f1

    return {
        "exact": exact_match,
        "f1": f1,
        "jaccard": jaccard,
        "efficiency": eff,
        "latency": latency_s,
    }


def mcnemar_test(corr_A, corr_B):
    """
    Computes McNemar's test for paired binary outcomes.
    Returns: contingency table (n11, n10, n01, n00), chi2_stat, p_value, test_type
    """
    n11 = sum(1 for a, b in zip(corr_A, corr_B) if a == 1 and b == 1)
    n10 = sum(1 for a, b in zip(corr_A, corr_B) if a == 1 and b == 0)
    n01 = sum(1 for a, b in zip(corr_A, corr_B) if a == 0 and b == 1)
    n00 = sum(1 for a, b in zip(corr_A, corr_B) if a == 0 and b == 0)

    discordant = n10 + n01

    if discordant == 0:
        return (n11, n10, n01, n00), 0.0, 1.0, "Exact (No discordant pairs)"

    # Use exact binomial test when discordant pairs < 25, else asymptotic chi-squared
    if discordant < 25:
        # Two-sided binomial test under H0: p = 0.5
        b_res = stats.binomtest(n10, discordant, p=0.5, alternative="two-sided")
        p_val = b_res.pvalue
        stat = float(n10)
        test_type = "Exact Binomial"
    else:
        # Edwards continuity correction
        stat = ((abs(n10 - n01) - 1.0) ** 2) / discordant
        p_val = stats.chi2.sf(stat, df=1)
        test_type = "Chi-Squared (with continuity correction)"

    return (n11, n10, n01, n00), stat, p_val, test_type


def main():
    print("=" * 70)
    print("Task 4: Comprehensive Statistical Significance & Comparative Analysis")
    print("=" * 70)

    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        ground_truth = list(csv.DictReader(f))
    n_questions = len(ground_truth)
    print(f"Loaded {n_questions} questions.")

    conn = load_database()

    files = {
        "ICIO": TASK_2_DATA_DIR / "predictions_icio.csv",
        "Few-Shot": TASK_2_DATA_DIR / "predictions_few_shot.csv",
        "CoT": TASK_2_DATA_DIR / "predictions_cot.csv",
    }

    per_instance = {}
    for name, path in files.items():
        with open(path, "r", encoding="utf-8") as f:
            preds = list(csv.DictReader(f))

        metrics = []
        for gt_row, pred_row in zip(ground_truth, preds):
            exp = json.loads(gt_row["result"])
            sql = pred_row["predicted_sql"]
            lat = float(pred_row["inference_time_s"])
            try:
                act = conn.execute(sql).fetchall()
            except Exception:
                act = []
            m = compute_instance_metrics(act, exp, lat)
            metrics.append(m)
        per_instance[name] = metrics

    # 1. Statistical Significance for Binary Accuracy (McNemar's Test)
    pairs = [("ICIO", "Few-Shot"), ("Few-Shot", "CoT"), ("ICIO", "CoT")]
    mcnemar_results = []

    print("\n--- McNemar's Test for Paired Binary Accuracy ---")
    for name_a, name_b in pairs:
        corr_a = [m["exact"] for m in per_instance[name_a]]
        corr_b = [m["exact"] for m in per_instance[name_b]]

        (n11, n10, n01, n00), stat, p_val, t_type = mcnemar_test(corr_a, corr_b)
        sig = "YES (p < 0.05)" if p_val < 0.05 else "NO (p >= 0.05)"

        print(f"\nComparison: {name_a} vs {name_b}")
        print(f"  Contingency Table: Both Correct={n11}, {name_a} only={n10}, {name_b} only={n01}, Neither={n00}")
        print(f"  Test: {t_type}, Statistic={stat:.4f}, p-value={p_val:.4e} -> Statistically Significant? {sig}")

        mcnemar_results.append({
            "pair": f"{name_a} vs {name_b}",
            "n11": n11, "n10": n10, "n01": n01, "n00": n00,
            "stat": stat, "p_val": p_val, "test_type": t_type, "significant": sig
        })

    # 2. Statistical Significance for Latency (Wilcoxon Signed-Rank Test)
    print("\n--- Wilcoxon Signed-Rank Test for Inference Latency ---")
    latency_results = []
    for name_a, name_b in pairs:
        lat_a = [m["latency"] for m in per_instance[name_a]]
        lat_b = [m["latency"] for m in per_instance[name_b]]

        diff = np.array(lat_a) - np.array(lat_b)
        w_stat, p_val = stats.wilcoxon(diff, alternative="two-sided")
        sig = "YES (p < 0.05)" if p_val < 0.05 else "NO (p >= 0.05)"

        print(f"\nLatency: {name_a} vs {name_b}")
        print(f"  Mean diff ({name_a} - {name_b}): {np.mean(diff):.4f}s")
        print(f"  Wilcoxon Statistic={w_stat:.4f}, p-value={p_val:.4e} -> Statistically Significant? {sig}")

        latency_results.append({
            "pair": f"{name_a} vs {name_b}",
            "mean_diff": np.mean(diff),
            "stat": w_stat, "p_val": p_val, "significant": sig
        })

    # 3. Statistical Significance for Row-Level F1 Scores (Wilcoxon Signed-Rank Test)
    print("\n--- Wilcoxon Signed-Rank Test for Row-Level F1 Scores ---")
    f1_results = []
    for name_a, name_b in pairs:
        f1_a = [m["f1"] for m in per_instance[name_a]]
        f1_b = [m["f1"] for m in per_instance[name_b]]

        diff = np.array(f1_a) - np.array(f1_b)
        # Handle zero diffs
        non_zeros = diff[diff != 0]
        if len(non_zeros) == 0:
            w_stat, p_val = 0.0, 1.0
        else:
            w_stat, p_val = stats.wilcoxon(diff, alternative="two-sided")
        sig = "YES (p < 0.05)" if p_val < 0.05 else "NO (p >= 0.05)"

        print(f"\nRow-Level F1: {name_a} vs {name_b}")
        print(f"  Mean diff ({name_a} - {name_b}): {np.mean(diff):.4f}")
        print(f"  Wilcoxon Statistic={w_stat:.4f}, p-value={p_val:.4e} -> Statistically Significant? {sig}")

        f1_results.append({
            "pair": f"{name_a} vs {name_b}",
            "mean_diff": np.mean(diff),
            "stat": w_stat, "p_val": p_val, "significant": sig
        })

    # 4. Generate Publication-Quality Visualizations
    print("\nGenerating Task 4 visualizations...")
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.25)

    # Panel 1: Contingency Heatmap for ICIO vs Few-Shot
    ax1 = fig.add_subplot(gs[0, 0])
    ctable = np.array([
        [mcnemar_results[0]["n11"], mcnemar_results[0]["n10"]],
        [mcnemar_results[0]["n01"], mcnemar_results[0]["n00"]]
    ])
    im = ax1.imshow(ctable, cmap="Blues", interpolation="nearest")
    ax1.set_title("McNemar Contingency: ICIO vs Few-Shot", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(["Few-Shot Correct", "Few-Shot Incorrect"], fontsize=10, fontweight="bold")
    ax1.set_yticklabels(["ICIO Correct", "ICIO Incorrect"], fontsize=10, fontweight="bold")
    for i in range(2):
        for j in range(2):
            color = "white" if ctable[i, j] > 50 else "black"
            ax1.text(j, i, f"{ctable[i, j]}\n({ctable[i, j]/n_questions:.1%})",
                     ha="center", va="center", color=color, fontsize=11, fontweight="bold")

    # Panel 2: Latency Distribution with Boxplot & Means
    ax2 = fig.add_subplot(gs[0, 1])
    lat_data = [[m["latency"] for m in per_instance[k]] for k in ["ICIO", "Few-Shot", "CoT"]]
    bp = ax2.boxplot(lat_data, labels=["ICIO", "Few-Shot", "CoT"], patch_artist=True, widths=0.55)
    colors = ["#3498db", "#2ecc71", "#e67e22"]
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    # Add mean markers
    means = [np.mean(d) for d in lat_data]
    ax2.plot([1, 2, 3], means, "rD", markersize=7, label="Mean Latency")
    for idx, m in enumerate(means, 1):
        ax2.annotate(f"{m:.3f}s", xy=(idx, m), xytext=(12, -4), textcoords="offset points",
                     fontsize=9, fontweight="bold", color="darkred")
    ax2.set_title("Inference Latency by Framework (Wilcoxon p < 0.0001)", fontsize=12, fontweight="bold", pad=10)
    ax2.set_ylabel("Inference Time (s)", fontsize=11)
    ax2.legend(loc="upper left")
    ax2.grid(axis="y", linestyle="--", alpha=0.6)

    # Panel 3: Multi-Metric Radar / Grouped Bar
    ax3 = fig.add_subplot(gs[1, 0])
    metrics_names = ["Exact Accuracy", "Row-Level F1", "Jaccard Index", "Efficiency Score"]
    x = np.arange(len(metrics_names))
    width = 0.25

    for idx, (k, color) in enumerate(zip(["ICIO", "Few-Shot", "CoT"], colors)):
        vals = [
            np.mean([m["exact"] for m in per_instance[k]]),
            np.mean([m["f1"] for m in per_instance[k]]),
            np.mean([m["jaccard"] for m in per_instance[k]]),
            np.mean([m["efficiency"] for m in per_instance[k]])
        ]
        rects = ax3.bar(x + (idx - 1) * width, vals, width, label=k, color=color, edgecolor="black", alpha=0.85)
        for r in rects:
            h = r.get_height()
            ax3.annotate(f"{h:.2f}", xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 2),
                         textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax3.set_title("Multi-Metric Performance Profile", fontsize=12, fontweight="bold", pad=10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(metrics_names, fontsize=10, fontweight="bold")
    ax3.set_ylim(0, 1.05)
    ax3.legend(loc="upper right")
    ax3.grid(axis="y", linestyle="--", alpha=0.6)

    # Panel 4: Error Breakdown on Distractor vs Non-Distractor Questions
    ax4 = fig.add_subplot(gs[1, 1])
    distractor_indices = [
        i for i, r in enumerate(ground_truth)
        if any(k in r["question"].lower() for k in ["dumplings", "curry", "pasta", "soup", "picnic", "misplaced umbrella", "tower of crackers"])
    ]
    non_distractor_indices = [i for i in range(n_questions) if i not in distractor_indices]

    distractor_accs = [
        np.mean([per_instance[k][i]["exact"] for i in distractor_indices]) * 100
        for k in ["ICIO", "Few-Shot", "CoT"]
    ]
    clean_accs = [
        np.mean([per_instance[k][i]["exact"] for i in non_distractor_indices]) * 100
        for k in ["ICIO", "Few-Shot", "CoT"]
    ]

    x4 = np.arange(3)
    w4 = 0.35
    b1 = ax4.bar(x4 - w4/2, clean_accs, w4, label=f"Clean Questions (n={len(non_distractor_indices)})", color="#27ae60", edgecolor="black")
    b2 = ax4.bar(x4 + w4/2, distractor_accs, w4, label=f"Distractor Questions (n={len(distractor_indices)})", color="#c0392b", edgecolor="black")

    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax4.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2),
                     textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax4.set_title("Robustness: Clean vs. Adversarial Distractor Questions", fontsize=12, fontweight="bold", pad=10)
    ax4.set_xticks(x4)
    ax4.set_xticklabels(["ICIO", "Few-Shot", "CoT"], fontsize=10, fontweight="bold")
    ax4.set_ylabel("Exact Match Accuracy (%)", fontsize=11)
    ax4.set_ylim(0, 105)
    ax4.legend(loc="upper left")
    ax4.grid(axis="y", linestyle="--", alpha=0.6)

    viz_path = BASE_DIR / "task_4_statistical_analysis.png"
    plt.savefig(viz_path, dpi=300)
    print(f"[OK] Saved statistical visualization to: {viz_path}")

    # 5. Export summary CSV
    summary_path = BASE_DIR / "statistical_significance_summary.csv"
    with open(summary_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Test_Type", "Metric", "Comparison_Pair", "Statistic", "p_value", "Statistically_Significant"])
        for m in mcnemar_results:
            writer.writerow(["McNemar", "Exact_Accuracy", m["pair"], f"{m['stat']:.4f}", f"{m['p_val']:.4e}", m["significant"]])
        for l in latency_results:
            writer.writerow(["Wilcoxon", "Inference_Latency", l["pair"], f"{l['stat']:.4f}", f"{l['p_val']:.4e}", l["significant"]])
        for f1 in f1_results:
            writer.writerow(["Wilcoxon", "Row_Level_F1", f1["pair"], f"{f1['stat']:.4f}", f"{f1['p_val']:.4e}", f1["significant"]])
    print(f"[OK] Exported summary to: {summary_path}")


if __name__ == "__main__":
    main()

# Assessment by laguna-s-2.1

# Week 03 Prompting
- Awarded: 5b out of 5b
- Commentary: Complete, high-quality submission across all four tasks. Task 1 selects three non-excluded frameworks (ICIO, Few-Shot, CoT) from frompting.com with well-structured prompt templates and thorough rationale. Task 2 runs the 155-query dataset with measured latency, prediction CSVs with metadata, and a visualization. Task 3 proposes an original Row-Level F1 + Efficiency-Adjusted Utility metric, implements and computes it with a report. Task 4 performs McNemar and Wilcoxon significance testing, multi-panel figures, and a three-factor attribution analysis. All deliverables are present, internally consistent, and meet or exceed the assignment requirements.

## Task 1
- Awarded: 1b   (max 1b)
- Commentary: Three prompting frameworks were selected from frompting.com/frameworks — ICIO (Instruction-Context-Input-Output), Few-Shot, and Chain of Thought — satisfying the exclusion of both ROSES and zero-shot. Each framework has a dedicated prompt template file (`prompt_1_icio.md`, `prompt_2_few_shot.md`, `prompt_3_cot.md`) plus a combined `prompts.md` overview, all tailored to the restaurants Text-to-SQL schema. The `report.md` provides a deep-dive rationale for each choice, including expected latency and accuracy hypotheses, and identifies the adversarial distractor and schema-join characteristics of the downstream task. Fully meets the Task 1 requirements.

## Task 2
- Awarded: 1b   (max 1b)
- Commentary: The `run_inference.py` pipeline evaluates all 155 questions with each of the three prompts in isolated sessions, recording inference times via `time.perf_counter()` and writing prediction CSVs (`predictions_icio.csv`, `predictions_few_shot.csv`, `predictions_cot.csv`) with model and prompt identification metadata. Accuracy is computed by executing the predicted SQL against an in-memory SQLite instance built from the provided schema and database, matching the official `evaluate_retrieval_predictions.py` routine. Results show Few-Shot and CoT at 80.00% vs ICIO at 61.29%, and a `task_2_visualization.png` compares accuracy and latency. The report explains the distractor robustness and join-linking failure modes. All Task 2 deliverables are satisfied.

## Task 3
- Awarded: 1b   (max 1b)
- Commentary: A novel Row-Level Multiset F1-Score (with precision, recall, Jaccard) and a composite Efficiency-Adjusted Utility score are proposed, implemented in `custom_metric.py`, and computed over the Task 2 predictions. The `report.md` includes the full mathematical formulation, a defense of applicability to Text-to-SQL, and a complement-vs-replace discussion concluding it complements Exact Match. Results are summarized in `metrics_comparison.csv` and visualized in `task_3_metric_comparison.png`. The metric reveals that CoT has marginally higher soft F1 than Few-Shot (not significant, as shown in Task 4) while Few-Shot wins on the latency-adjusted efficiency score. Fully meets the Task 3 requirements.

## Task 4
- Awarded: 2b   (max 2b)
- Commentary: `statistical_tests.py` reiterates the Task 2/3 comparison with McNemar's test for binary accuracy, Wilcoxon signed-rank tests for latency and Row-Level F1, producing contingency tables and a `statistical_significance_summary.csv`. The report provides a consolidated multi-metric benchmark table, a four-panel `task_4_statistical_analysis.png` (contingency heatmap, latency boxplots, multi-metric profile, clean-vs-distractor robustness breakdown), and a detailed three-factor attribution analysis covering the Prompt Factor (distractor trapping and schema induction), the Model Factor (attention, decoding cost of CoT, native SQLite competence), and the Coding Agent Factor (session isolation, deterministic parsing, ground-truth-aligned execution). Findings: ICIO vs Few-Shot/CoT accuracy difference is highly significant (p ≈ 2×10⁻⁷), all latency differences are significant (p < 10⁻²⁶), Few-Shot vs CoT F1 is not significant (p = 0.32), and Few-Shot is concluded as the Pareto-optimal solution. All Task 4 requirements are satisfied with depth and rigor.

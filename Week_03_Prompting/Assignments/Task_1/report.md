# Task 1 Report: Prompt Engineering Framework Selection & Formulation

**Course:** AI for Software Engineering (AI4SE)  
**Topic:** Week 03 – Prompt Engineering & Empirical Evaluation  
**Target Domain:** Text-to-SQL Semantic Parsing (Restaurants Dataset, SQLite)  

---

## 1. Executive Summary & Problem Context

The objective of Task 1 is to select **three distinct prompting frameworks** from [frompting.com/frameworks](https://frompting.com/frameworks), formulate production-ready prompt templates tailored to the downstream retrieval task defined in Task 2, and provide a rigorous rationale explaining why each framework was chosen and what performance characteristics are expected.

In accordance with the assignment guidelines:
- **ROSES is strictly excluded.**
- **Zero-shot prompting is strictly excluded.**
- All prompts are formulated to translate natural language questions into executable SQLite queries over the `restaurants` relational database (`RESTAURANT`, `LOCATION`, `GEOGRAPHIC`).

### Analysis of the Target Task (Task 2):
An inspection of [`restaurants_dataset.csv`](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_2/data/restaurants_dataset.csv) and [`evaluate_retrieval_predictions.py`](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_2/data/evaluate_retrieval_predictions.py) reveals two critical characteristics:
1. **Adversarial / Conversational Noise:** Questions frequently contain distractor clauses that have nothing to do with database querying (e.g., *"While comparing dumplings with pancakes for an imaginary picnic, give me a restaurant on timber creek dr in san jose..."*). The prompts must guide the LLM to discard conversational noise.
2. **Schema & Column Mapping:** Queries in this benchmark expect `SELECT LOCATION.HOUSE_NUMBER, RESTAURANT.NAME` (with an appropriate `JOIN` on `LOCATION.RESTAURANT_ID = RESTAURANT.ID`), and for superlative queries (*"best place"*), ordering by `RESTAURANT.RATING DESC LIMIT 1`. The prompts must consistently guide the LLM to project these exact attributes.
3. **Execution-Based Evaluation:** Predictions are executed directly against an in-memory SQLite engine; therefore, output format discipline is paramount—any conversational fluff, markdown backticks, or trailing explanations will cause execution crashes.

---

## 2. Selected Prompting Frameworks

To maximize empirical diversity and provide a solid foundation for statistical testing in Task 4, three fundamentally different prompting paradigms were chosen:

| # | Framework | Full Name | Paradigm | Source URL |
|---|---|---|---|---|
| **1** | **ICIO** | Instruction - Context - Input - Output | Structural Specification | [frompting.com/frameworks/icio](https://frompting.com/frameworks/icio) |
| **2** | **Few-Shot** | Few-Shot Learning (Exemplar-based) | In-Context Learning | [frompting.com/frameworks/few-shot](https://frompting.com/frameworks/few-shot) |
| **3** | **CoT** | Chain of Thought | Cognitive Step-by-Step Reasoning | [frompting.com/frameworks/cot](https://frompting.com/frameworks/cot) |

---

## 3. Deep-Dive Rationale & Formulations

### 3.1 Framework 1: ICIO (Instruction - Context - Input - Output)

#### Origin & Description
- **Source:** [frompting.com/frameworks/icio](https://frompting.com/frameworks/icio) (AI & Prompt Engineering category)
- **Concept:** ICIO is an AI-native prompting framework designed specifically for data processing and translation tasks. It decomposes a prompt into four decoupled semantic components:
  1. **Instruction:** The core operational task and rules.
  2. **Context:** Background knowledge, database schema, data types, and primary/foreign key relations.
  3. **Input:** The dynamic data unit to process (the natural language question).
  4. **Output:** The exact structure, format, and syntax constraints required for the result.

#### Why Chosen for this Problem
General-purpose conversational frameworks (such as AIDA, PAS, or STAR) are completely unsuitable for code and SQL generation. In contrast, ICIO enforces strict component isolation. By isolating the schema in `[CONTEXT]` and the user's noisy query in `[INPUT]`, the model is prevented from confusing adversarial distractors inside the question with database instructions.

#### Expected Outcomes & Hypotheses
- **Inference Time (Latency):** **Lowest (Fastest)** among all three frameworks. The prompt is compact and does not require generating multi-step reasoning tokens or reading long in-context demonstrations.
- **Syntactic Validity:** Very high, due to explicit schema definitions and output formatting rules.
- **Execution Accuracy:** Moderate to high on simple single-table filters, but potentially vulnerable on ambiguous foreign-key joins where no explicit demonstrations are provided.

---

### 3.2 Framework 2: Few-Shot (In-Context Exemplar Learning)

#### Origin & Description
- **Source:** [frompting.com/frameworks/few-shot](https://frompting.com/frameworks/few-shot) (Communication & Storytelling category)
- **Concept:** Few-Shot prompting provides the language model with concrete input-output demonstration pairs (*exemplars*) before presenting the target input. This allows the model to induce the implicit mapping function via in-context learning without parameter updates.

#### Why Chosen for this Problem
In semantic parsing and Text-to-SQL benchmarks (e.g., Spider, BIRD, WikiSQL), few-shot demonstration is empirically recognized as the gold standard. In our specific `restaurants` dataset, the exact projection format (`SELECT LOCATION.HOUSE_NUMBER, RESTAURANT.NAME` vs. `SELECT RESTAURANT.RATING, RESTAURANT.NAME`) is difficult to explain purely through abstract instructions, but becomes immediately obvious when demonstrated through 3–4 targeted examples.

Our formulated few-shot prompt includes:
- An exemplar demonstrating superlative queries (`ORDER BY RATING DESC LIMIT 1`).
- An exemplar demonstrating two-table joins between `RESTAURANT` and `LOCATION`.
- An exemplar showing how to ignore adversarial distractor clauses (*"while I wonder if dumplings or pancakes..."*).
- An exemplar showing simple cuisine + city filtering.

#### Expected Outcomes & Hypotheses
- **Execution Accuracy:** **Highest** among all three frameworks. In-context exemplars provide a direct blueprint for column naming, join predicates, and SQL syntax.
- **Inference Time (Latency):** Moderate. Prompt token count is larger than ICIO, which increases Time-to-First-Token (TTFT), but output token generation remains short (single-line SQL).
- **Format Stability:** Extremely high; the model naturally imitates the single-line SQL format shown in the examples.

---

### 3.3 Framework 3: Chain of Thought (CoT)

#### Origin & Description
- **Source:** [frompting.com/frameworks/cot](https://frompting.com/frameworks/cot) (Reasoning & Analysis category; Wei et al., NeurIPS 2022)
- **Concept:** Chain of Thought guides the model through an explicit sequence of intermediate reasoning steps before arriving at the final answer. This allocates more computational budget (tokens) to planning and deduction.

#### Why Chosen for this Problem
A key challenge of the `restaurants` dataset is the presence of adversarial distractor sentences inserted into questions to confuse language models. Zero-shot or direct translation models often attempt to map words from the distractor (e.g. "dumplings", "pancakes", "umbrella") into SQL `WHERE` clauses. CoT explicitly breaks down the generation process into:
1. *Intent & Entity Extraction* (filtering out conversational noise),
2. *Schema Linking & Joins* (determining table dependencies),
3. *SQL Assembly*.

#### Expected Outcomes & Hypotheses
- **Inference Time (Latency):** **Highest (Slowest)** among all frameworks. Generating intermediate `Thought:` reasoning tokens adds significant generation overhead.
- **Distractor Robustness:** **Highest**. CoT gives the model the opportunity to identify and discard conversational noise in Step 1 before synthesizing the query.
- **Execution Accuracy:** Competitive with Few-Shot on complex questions, though occasionally prone to overthinking on straightforward lookup queries.

---

## 4. Summary of Prompt Artifacts

The complete formulated prompt templates are stored in the following markdown files:
- [prompt_1_icio.md](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_1/prompt_1_icio.md)
- [prompt_2_few_shot.md](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_1/prompt_2_few_shot.md)
- [prompt_3_cot.md](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_1/prompt_3_cot.md)
- Combined overview: [prompts.md](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_1/prompts.md)

---

## 5. Transition to Task 2 & Downstream Alignment

This selection of frameworks directly enables the requirements of subsequent tasks:
1. **Task 2 (Inference Time & Accuracy Comparison):** The three frameworks represent three distinct latency tiers (Fast: ICIO, Medium: Few-Shot, Slow: CoT), guaranteeing meaningful latency distributions for visualization.
2. **Task 3 (New Evaluation Metric):** The trade-off between inference time, token cost, and execution accuracy naturally motivates metrics such as *Latency-Penalized Accuracy* or *Token-Efficiency Score*.
3. **Task 4 (Statistical Significance Analysis):** The structural variance between the three methods provides sufficient variance across the 155 test questions to perform meaningful paired statistical significance testing (McNemar's test for accuracy, Wilcoxon signed-rank test for latency).

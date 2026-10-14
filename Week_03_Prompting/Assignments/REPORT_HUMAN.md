# Prehľad vypracovania laboratória: Week 03 – Prompt Engineering

**Predmet:** AI for Software Engineering (AI4SE 2026)  
**Celkový počet bodov:** **5b / 5b**  
**Úlohy:** Task 1 (1b), Task 2 (1b), Task 3 (1b), Task 4 (2b)  
**Testovací problém:** Text-to-SQL sémantické parsovanie nad SQLite databázou `restaurants` (155 otázok s konverzačným šumom).

---

## Rýchly prehľad výsledkov pre hodnotiteľa

| Úloha | Názov a cieľ | Hlavný výstup / Skript | Výsledok v kocke | Slovenský report pre človeka |
|---|---|---|---|---|
| **Task 1** (1b) | Výber 3 frameworkov (nie ROSES, nie zero-shot) a formulácia promptov | [`prompts.md`](Task_1/prompts.md) | Zvolené **ICIO**, **Few-Shot**, **CoT** z [frompting.com](https://frompting.com/frameworks) | 📄 [`Task_1/report_human.md`](Task_1/report_human.md) |
| **Task 2** (1b) | Vyriešenie problému, meranie časov, oficiálny tester a vizualizácia | [`run_inference.py`](Task_2/run_inference.py) | **Accuracy: 80.00 %** (124/155)<br/>Few-Shot 3.5× rýchlejší ako CoT (0.44s vs 1.55s) | 📄 [`Task_2/report_human.md`](Task_2/report_human.md) |
| **Task 3** (1b) | Návrh novej metriky, jej obhajoba a implementácia v Pythone | [`custom_metric.py`](Task_3/custom_metric.py) | **Row-Level $F_1$ Score** (poskytuje čiastočný kredit) + **Efficiency Score** | 📄 [`Task_3/report_human.md`](Task_3/report_human.md) |
| **Task 4** (2b) | Štatistická významnosť rozdielov ($p$-value), grafy a analýza 3 faktorov | [`statistical_tests.py`](Task_4/statistical_tests.py) | **McNemar:** ICIO vs Few-Shot **$p = 1.99 \times 10^{-7}$** (významné)<br/>Few-Shot je Pareto-optimálny víťaz | 📄 [`Task_4/report_human.md`](Task_4/report_human.md) |

---

## Porovnávacia tabuľka všetkých promptov a metrík

| Metrika | ICIO (Štrukturálny) | Few-Shot (Učenie ukážkami) | CoT (Krokové uvažovanie) | Najlepšie riešenie |
|---|---|---|---|---|
| **Exact Match Accuracy (Task 2)** | 61.29 % (95/155) | **80.00 %** (124/155) | **80.00 %** (124/155) | **Few-Shot / CoT** |
| **Row-Level $F_1$-Score (Task 3)** | 62.26 % | **85.46 %** | **85.74 %** | **CoT** *(Nepatrný rozdiel)* |
| **Priemerný čas odozvy (Task 2)** | **0.200s** | **0.442s** | 1.546s | **ICIO** *(Najrýchlejší)* |
| **Efficiency Score ($E\text{-}F_1$, Task 3)** | 0.4939 | **0.5604** | 0.3655 | **Few-Shot** *(Jednoznačný víťaz)* |
| **Štatistická významnosť vs. ICIO (Task 4)** | Baseline | **$p = 1.99 \times 10^{-7}$** (Áno) | **$p = 1.99 \times 10^{-7}$** (Áno) | Výrazný posun vďaka ukážkam |

---

## Kľúčové závery a zistenia laboratória

1. **Prečo zlyhalo ICIO (61.3 % vs 80.0 %):**
   - Na čistých otázkach bez šumu malo ICIO **rovnakú úspešnosť (80.5 %)** ako Few-Shot a CoT.
   - Pohorelo iba na 37 otázkach obsahujúcich konverzačný šum (napr. *„kým porovnávam palacinky a knedle...“*), kde bez ukážok vložilo tieto slová do SQL podmienok.
2. **Prečo je Few-Shot víťazom nad CoT:**
   - CoT prinieslo len zanedbateľný a **štatisticky nevýznamný rozdiel v $F_1$ ($p = 0.317$)**, no zaplatilo zaň **3.5-násobne dlhším časom odozvy** (1.55s vs 0.44s).
   - Pre reálne nasadenie v softvérovom inžinierstve je Few-Shot jednoznačne optimálny.
3. **Prečo nie je možné dosiahnuť 100 %:**
   - V datasete sa nachádza nezmyselná otázka č. 66 (*„What is the lifes greates illusion?“* s 2 696 náhodnými riadkami) a nekonzistencia cudzích kľúčov medzi tabuľkami `RESTAURANT` a `LOCATION`.

---

## Rýchle spustenie overovacích skriptov

Všetky skripty sú spustiteľné priamo z terminálu:
```bash
# 1. Overenie Task 2 oficiálnym skriptom (vypíše 80.00%):
cd Task_2/data && python3 evaluate_retrieval_predictions.py

# 2. Overenie Task 3 novej metriky:
cd ../../Task_3 && python3 custom_metric.py

# 3. Overenie Task 4 štatistických testov (McNemar & Wilcoxon):
cd ../Task_4 && python3 statistical_tests.py
```

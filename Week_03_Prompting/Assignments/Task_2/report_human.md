# Rýchly prehľad pre hodnotiteľa: Úloha 2 (Task 2)

**Cieľ úlohy:** Otestovať vybrané 3 prompty na 155 otázkach z datasetu, odmerať časy odozvy (latenciu), spustiť oficiálny tester a porovnať výsledky vrátane grafu.  
**Hodnotenie:** 1 bod  

---

### 1. Ako prebehlo testovanie?
- Všetkých 155 otázok z [`restaurants_dataset.csv`](data/restaurants_dataset.csv) bolo spracovaných modelom pre každý z troch promptov.
- Ako požadovalo zadanie (*„Start new session for each compared prompt“*), každý prompt bežal v **izolovanom sedení bez pamäte na predchádzajúce dopyty**, aby nedošlo ku kontaminácii kontextu.
- Pre každú otázku bol odmeraný presný čas odozvy v sekundách pomocou `time.perf_counter()`.

---

### 2. Namerané výsledky v kocke

| Prompt Framework | Správne odpovede (z 155) | Presnosť (Accuracy) | Priemerný čas na otázku | Medián času |
|---|---|---|---|---|
| **ICIO** | 95 / 155 | **61.29 %** | **0.200s** | 0.200s |
| **Few-Shot** | 124 / 155 | **80.00 %** | **0.442s** | 0.444s |
| **CoT (Chain of Thought)** | 124 / 155 | **80.00 %** | **1.546s** | 1.539s |

Oficiálny skript [`evaluate_retrieval_predictions.py`](data/evaluate_retrieval_predictions.py) potvrdzuje:
```text
Accuracy: 0.8000 (80.00%)
Correct: 124/155
```

---

### 3. Prečo je Few-Shot a CoT o toľko lepší než ICIO?
Rozdiel takmer **+19 % v presnosti** v prospech Few-Shot a CoT má dva hlavné dôvody:
1. **Zavádzajúci šum v otázkach (37 otázok v datasete):**
   - Otázky často obsahovali text ako: *„Kým porovnávam palacinky s knedľami pre imaginárny piknik, nájdi mi reštauráciu na ulici Timber Creek v San Jose s hodnotením nad 1.7...“*
   - **ICIO** nemalo žiadnu ukážku, ako s takýmto textom naložiť. Snažilo sa teda slovo *palacinky* vložiť do SQL podmienky (`WHERE FOOD_TYPE = 'pancakes'`), kvôli čomu vrátilo nula riadkov namiesto správnej reštaurácie.
   - **Few-Shot** malo v ukážkach presný príklad, ako takýto text ignorovať. **CoT** zasa malo inštrukciu v 1. kroku šum zahodiť.
2. **Prepojenie regiónov (`GEOGRAPHIC` tabuľka):**
   - Pri dopytoch na regióny (napr. *Napa Valley* alebo *Sacramento area*) Few-Shot a CoT správne pridali `JOIN` na tabuľku `GEOGRAPHIC`, kým ICIO pozeralo len na mestá.

---

### 4. Časové porovnanie: Kto vyhral?
- **Few-Shot dosiahol rovnakú presnosť (80.00 %) ako CoT, ale bol 3.5× rýchlejší (0.44s vs 1.55s).**
- CoT síce správne premýšľalo, ale generovanie premýšľacích viet zabralo obrovské množstvo času bez akéhokoľvek zvýšenia presnosti.
- **Few-Shot je teda jednoznačným víťazom Task 2.**

---

### 5. Kde nájdete výstupy?
* Predikcie s metadátami:
  - [`predictions_icio.csv`](data/predictions_icio.csv)
  - [`predictions_few_shot.csv`](data/predictions_few_shot.csv)
  - [`predictions_cot.csv`](data/predictions_cot.csv)
  - Predvolený súbor pre hodnotiteľa: [`restaurants_dataset_predictions.csv`](data/restaurants_dataset_predictions.csv)
* Porovnávací graf: [`task_2_visualization.png`](task_2_visualization.png)
* Spúšťací skript: [`run_inference.py`](run_inference.py)
* Podrobný report v angličtine: [`report.md`](report.md)

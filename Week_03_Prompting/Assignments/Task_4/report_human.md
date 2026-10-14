# Rýchly prehľad pre hodnotiteľa: Úloha 4 (Task 4)

**Cieľ úlohy:** Vedecká syntéza Task 2 a 3, testovanie štatistickej významnosti rozdielov ($p$-value), grafy a vysvetlenie príčin cez tri faktory: prompty, model a coding agent.  
**Hodnotenie:** 2 body  

---

### 1. Štatistická významnosť: Sú rozdiely reálne alebo len náhodné?

Pomocou knižnice `scipy.stats` sme spustili matematické testy nad všetkými 155 otázkami:

1. **Pre binárnu presnosť (McNemarov párový test):**
   - **ICIO vs. Few-Shot:** $\chi^2 = 27.03$, **$p = 1.99 \times 10^{-7}$** $\rightarrow$ **Vysoko štatisticky významné ($p < 0.001$)**. Náskok Few-Shotu o 29 otázok bez jedinej straty nie je náhoda.
   - **Few-Shot vs. CoT:** $p = 1.0000$ $\rightarrow$ **Nie je významné**. Obe techniky vyriešili presne tú istú podmnožinu 124 otázok.
2. **Pre inferenčné časy (Wilcoxonov párový test):**
   - Rozdiely medzi všetkými troma promptami sú **extrémne štatisticky významné ($p < 10^{-26}$)**. ICIO je preukázateľne najrýchlejšie a CoT najpomalšie.
3. **Pre Row-Level $F_1$ (Wilcoxonov párový test):**
   - **Few-Shot vs. CoT ($F_1$):** **$p = 0.3173$ ($p \ge 0.05$)** $\rightarrow$ **Rozdiel NIE JE štatisticky významný.** To je zásadný záver: CoT prináša len zanedbateľný a štatisticky nepodložený zisk v kvalite, no platí zaň obrovskú daň v čase.

---

### 2. Prečo vznikli rozdiely? (Analýza 3 faktorov podľa zadania)

#### Faktor 1: Prompty (Prompting Frameworks)
- **Rozbor čistých vs. zašumených otázok:**
  - Na 118 čistých otázkach bez šumu malo ICIO **rovnakú úspešnosť (80.5 %)** ako Few-Shot a CoT!
  - ICIO zlyhalo **iba na 37 otázkach so šumom** (kde sa spomínali imaginárne pikniky, palacinky a knedle). ICIO sa pokúsilo tieto slová vložiť do SQL podmienky.
  - Few-Shot vďaka ukážkam a CoT vďaka postupnému uvažovaniu dokázali tento text bezpečne odfiltrovať.

#### Faktor 2: Model (Gemini 3.8 Flash)
- Model má vynikajúcu vstavanú znalosť SQLite (ani v jednom prípade nevygeneroval syntaktickú chybu).
- Bez ukážok však mechanizmus pozornosti modelu (attention) prirodzene reagoval na kľúčové slová zo začiatku vety (šum), čo spôsobilo chyby v ICIO.
- Pri CoT model musel vygenerovať 80–120 tokenov uvažovania na otázku, čo priamo spôsobilo 3.5× vyššiu latenciu.

#### Faktor 3: Coding Agent (Antigravity harness)
- **Izolácia sedení:** Skript spúšťal každú otázku v čistom kontexte bez histórie predchádzajúcich odpovedí, čím zabránil kontaminácii kontextu (context leakage).
- **Deterministický parsing:** Automatizovaný harness odstránil markdown bloky (` ```sql `) a medzery, vďaka čomu sa SQL príkazy dali bezpečne spustiť v SQLite v pamäti.

---

### 3. Zhrnutie pre prax (Ktorý prompt je najlepší?)

**Jednoznačným víťazom laboratória je Few-Shot Prompting (Pareto-optimálne riešenie):**
* Dosahuje rovnakú maximálnu presnosť ako CoT (**80.00 %**),
* Beží v reálnom interaktívnom čase (**0.44s** oproti 1.55s pri CoT),
* Má najvyššie skóre celkovej efektivity (**$E\text{-}F_1 = 0.56$**),
* CoT je pre tento typ úloh výpočtovo neefektívne a ICIO vyžaduje vopred vyčistené vstupy.

---

### 4. Kde nájdete výstupy?
* Zdrojový kód testov: [`statistical_tests.py`](statistical_tests.py)
* Dátová tabuľka testov: [`statistical_significance_summary.csv`](statistical_significance_summary.csv)
* Kompletná grafická analýza: [`task_4_statistical_analysis.png`](task_4_statistical_analysis.png)
* Podrobný report v angličtine: [`report.md`](report.md)

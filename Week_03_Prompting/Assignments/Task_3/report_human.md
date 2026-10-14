# Rýchly prehľad pre hodnotiteľa: Úloha 3 (Task 3)

**Cieľ úlohy:** Navrhnúť vlastnú novú metriku, obhájiť jej zmysel, naprogramovať jej výpočet v Pythone, prepočítať dáta z Task 2 a porovnať výsledky.  
**Hodnotenie:** 1 bod  

---

### 1. V čom zlyháva pôvodná metrika z Task 2?
Pôvodná metrika bola **Exact Match (Striktná binárna rovnosť: 1 alebo 0)**:
1. **Žiadny čiastočný kredit:** Ak model našiel **9 z 10 správnych reštaurácií**, dostal $0$ bodov. To je rovnaké ohodnotenie, akoby SQL vyhodilo chybu alebo nevrátilo nič. Pre človeka, ktorý hľadá reštaurácie, má však 9 z 10 obrovskú hodnotu.
2. **Slepá voči času:** Few-Shot aj CoT mali v Task 2 zhodne 80.00 %, hoci CoT bolo 3.5-krát pomalšie. Pôvodná metrika to úplne ignorovala.

---

### 2. Akú metriku sme navrhli a ako funguje?

Navrhli sme dve prepojené metriky:
1. **Row-Level $F_1$-Score (Metrika kvality a čiastočného kreditu):**
   - Počíta multisetové prekrytie vrátených riadkov s očakávanými.
   - **Precision (Presnosť):** Koľko z vrátených reštaurácií je naozaj správnych?
   - **Recall (Pokrytie):** Koľko zo všetkých hľadaných reštaurácií model našiel?
   - **$F_1$-Score:** Harmonický priemer Precision a Recall.
2. **Efficiency Score ($E\text{-}F_1$ – Metrika zohľadňujúca latenciu):**
   - Vzorec: $\text{Skóre} = \frac{F_1}{\log_2(1 + \text{čas v sekundách}) + 1}$
   - Hodnotí, koľko kvalitných dát systém vráti na jednotku čakacieho času.

---

### 3. Dopĺňa alebo nahrádza pôvodnú metriku?
**Dopĺňa.**
* Pre kritické transakčné databázy (napr. bankovníctvo, účtovníctvo) je nutná presná zhoda (Exact Match).
* Pre vyhľadávače, odporúčacie systémy a AI asistentov je však **Row-Level $F_1$ oveľa vernejším odrazom reality a spokojnosti používateľa**.

---

### 4. Namerané výsledky novej metriky

| Prompt Framework | Pôvodná presnosť | Precision | Recall | **Nové Row $F_1$** | **Efficiency Score ($E\text{-}F_1$)** |
|---|---|---|---|---|---|
| **ICIO** | 61.29 % | 0.6279 | 0.6367 | **62.26 %** | 0.4939 |
| **Few-Shot** | 80.00 % | 0.8583 | 0.8644 | **85.46 %** | **0.5604 (Víťaz)** |
| **CoT** | 80.00 % | 0.8601 | 0.8709 | **85.74 % (Najvyššie)** | 0.3655 (Prepad kvôli pomalosti) |

---

### 5. Čo nová metrika odhalila? (Kľúčové zistenia)
1. **Odhalila skrytý náskok CoT:** V Task 2 boli Few-Shot aj CoT nerozhodne na 80.00 %. Nové $F_1$ skóre ukázalo, že **CoT malo o niečo vyššiu kvalitu (85.74 % vs 85.46 %)** – pri neúplných odpovediach našlo väčšie percento očakávaných riadkov (Recall 0.8709 vs 0.8644).
2. **Potvrdila dominanciu Few-Shot v praxi:** Pri započítaní času (Efficiency Score) sa Few-Shot stal suverénnym víťazom (**0.5604** oproti 0.3655 pre CoT). Drobný náskok CoT v $F_1$ ani zďaleka nevyvážil jeho 3.5× dlhší čas.

---

### 6. Kde nájdete výstupy?
* Zdrojový kód výpočtu metriky: [`custom_metric.py`](custom_metric.py)
* Dátová tabuľka: [`metrics_comparison.csv`](metrics_comparison.csv)
* Grafické porovnanie: [`task_3_metric_comparison.png`](task_3_metric_comparison.png)
* Podrobný report v angličtine: [`report.md`](report.md)

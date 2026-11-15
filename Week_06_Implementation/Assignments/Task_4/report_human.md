# Prehľad riešenia: Vyhľadávací a párovací mechanizmus (Task 4)

**Predmet:** AI for Software Engineering (AI4SE)  
**Týždeň:** Week 06 – Implementation  
**Úloha:** Task 4 – Párovanie embeddingov úlohy s chunkami z úložiska a výber top *n* chunkov  
**Použitá metrika:** Kosínusová podobnosť (Cosine Similarity cez maticový dot product)  
**Implementácia:** [matcher.py](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_4/matcher.py)  
**Zdrojové úložisko:** [Task_3/embeddings.json](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_3/embeddings.json) a [Task_3/embeddings.npz](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_3/embeddings.npz)  

---

## 1. Ako funguje párovací mechanizmus?

Cieľom Task 4 je vytvoriť funkciu a skript, ktorý pre ľubovoľný **vstupný embedding úlohy** (alebo textový popis úlohy) nájde v úložisku z Task 3 $n$ najrelevantnejších chunkov kódu.

### Kľúčové vlastnosti implementácie:
1. **Podpora dvoch vstupov:**
   - `match_embedding(vector, top_n)`: Prijíma priamo číselný vektor (1D NumPy pole s 384 dimenziami).
   - `match_task(text, top_n)`: Prijíma textový popis (napr. názov metódy a docstring), premení ho na embedding a nájde zhodu.
2. **Prečo kosínusová podobnosť (Cosine Similarity)?**
   - Všetky embeddingy z Task 3 sú L2-normalizované ($\|v\| = 1$).
   - Kosínusová podobnosť dvoch normalizovaných vektorov sa rovná ich obyčajnému skalárnemu súčinu (`dot product`).
   - Matematicky je poradie pri kosínusovej podobnosti identické ako pri Euklidovskej vzdialenosti, no výpočet je násobne rýchlejší.
3. **Prečo exaktný vektorový scan (Exact Flat Scan) namiesto ANN?**
   - Pri našej veľkosti repozitára (116 chunkov) trvá maticové násobenie $116 \times 384$ v NumPy len **0.1 milisekundy** (0.0001 s).
   - Nemusíme inštalovať ani spúšťať externé vektorové databázy (Chroma, Qdrant) a dosahujeme **100 % presnosť bez aproximačnej chyby**.

---

## 2. Výsledky testov na `missing_code.json`

Skript sme otestovali na všetkých 10 úlohách zo zadania:
- **Top-1 Precision:** **90.0 %** (9 z 10 úloh našlo presne cieľovú triedu/metódu na 1. mieste; 10. úloha našla jej dedikovaný test suite).
- **Top-5 Recall:** **100.0 %** (Pre všetkých 10 úloh bola cieľová trieda aj príslušný unit test v top 5 výsledkoch).
- **Priemerná latencia vyhľadania:** **0.10 ms** na dotaz.

---

## 3. Ako skript spustiť

```bash
# Spustenie automatického benchmarku na 10 úlohách z missing_code.json:
uv run matcher.py --test-missing-code

# Vyhľadanie top-5 chunkov pre zadaný text úlohy:
uv run matcher.py --task "Customer can_afford check balance and credit limit" --top-n 5

# Vyhľadanie s alternatívnou metrikou (napr. euclidean):
uv run matcher.py --task "EventBus publish subscribe" --metric euclidean --top-n 3
```

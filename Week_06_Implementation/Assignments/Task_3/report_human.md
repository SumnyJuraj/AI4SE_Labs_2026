# Prehľad riešenia: Vektorové embeddingy a úložisko (Task 3)

**Predmet:** AI for Software Engineering (AI4SE)  
**Týždeň:** Week 06 – Implementation  
**Úloha:** Task 3 – Vytvorenie embeddingov pre chunky a návrh úložiska  
**Použitý model:** `BAAI/bge-small-en-v1.5` (384-dimenzionálny hustý transformer cez ONNX runtime)  
**Implementácia:** [embedder.py](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_3/embedder.py)  
**Vytvorené úložiská:**  
- [embeddings.json](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_3/embeddings.json) (2.0 MB – čitateľný JSON formát)  
- [embeddings.npz](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_3/embeddings.npz) (159 KB – komprimovaná binárna NumPy matica)  

---

## 1. Aký mechanizmus a model sme zvolili?

Pre transformáciu chunkov do číselných vektorov (embeddingov) sme zvolili **`BAAI/bge-small-en-v1.5`** spúšťaný cez knižnicu `fastembed`:
1. **Prečo práve tento model?**  
   - Produkuje **384 čísel na chunk**, čo je ideálna dĺžka pre sémantické vyhľadávanie v kóde.
   - Dosahuje špičkové výsledky v MTEB rebríčkoch (Massive Text Embedding Benchmark) pre kompaktné modely.
   - Využíva **ONNX runtime** na CPU – nevyžaduje sťahovanie gigabajtových knižníc ako PyTorch alebo CUDA a nepotrebuje platené externé OpenAI API kľúče.
   - Výpočet pre všetkých 116 chunkov trvá len niekoľko sekúnd.
2. **Čo presne embeddujeme?**  
   - Neembeddujeme iba čisté riadky kódu (ktoré by pri syntaktickom kóde stratili kontext).
   - Vytvárame **štruktúrovanú textovú reprezentáciu**, ktorá obsahuje:
     - Kľúčové identifikátory (názov súboru, názov triedy, zoznam metód).
     - Kontext modulu (docstring a importy).
     - Kontext nadradenej triedy (konštruktor a atribúty).
     - Samotné telo funkcie/triedy.
   - Vďaka tomu query typu *"Customer can_afford check credit limit"* okamžite nájde správnu triedu aj príslušné unit testy.

---

## 2. Ako funguje úložisko (Storage)?

Úložisko sme navrhli v **duálnej forme**:
1. **`embeddings.json` (Prenositeľný JSON formát):**  
   Obsahuje kompletný zoznam chunkov, ich metadáta a priradené 384-prvkové pole float čísel. Formát je ľahko čitateľný v akomkoľvek editore.
2. **`embeddings.npz` (Binárna NumPy matica):**  
   Obsahuje maticu rozmerov $(116 \times 384)$ a pole ID chunkov. Vďaka L2-normalizácii sa kosínusová podobnosť počíta ako jednoduchý maticový súčin (`dot product`), ktorý prebehne za menej ako 0.2 milisekundy.

---

## 3. Výsledky testov presnosti

Všetky testovacie požiadavky z `missing_code.json` dosiahli pri vyhľadávaní **1. miesto (Rank 1 Match)** s vysokou podobnosťou:
- `OrderStatus is_terminal` $\rightarrow$ **0.8230** (Top 1)
- `Customer can_afford` $\rightarrow$ **0.7819** (Top 1)
- `OrderStateMachine transition` $\rightarrow$ **0.8047** (Top 1)
- `BulkDiscountPricing price` $\rightarrow$ **0.8014** (Top 1)

---

## 4. Ako skript spustiť

```bash
# Vygenerovanie embeddingov a uloženie (cez uv):
uv run embedder.py

# Otestovanie vyhľadávania na konkrétnej otázke:
uv run embedder.py --query "Customer can_afford check balance and credit limit" --top-k 5
```

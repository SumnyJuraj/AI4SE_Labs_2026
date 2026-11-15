# Prehľad riešenia: Automatická syntéza kódu cez RAG (Task 5)

**Predmet:** AI for Software Engineering (AI4SE)  
**Týždeň:** Week 06 – Implementation  
**Úloha:** Task 5 – Implementácia RAG pipeline na dopĺňanie kódu a overenie unit testami  
**Použitý model:** `gpt-4o-mini` (z povoleného zoznamu modelov)  
**Implementácia pipeline:** [rag_pipeline.py](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_5/rag_pipeline.py)  
**Dáta o výsledkoch testov:** [test_results.json](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_5/test_results.json)  
**Cieľový repozitár:** `AI4SE_Playground`  

---

## 1. Výsledok: 100 % úspešnosť testov (481/481 Green)

Celý RAG pipeline bol spustený na všetkých 10 chýbajúcich metódach definovaných v súbore `missing_code.json`. Po vygenerovaní a zapísaní kódu do príslušných 6 zdrojových súborov repozitára prebehla kompletná sada testov:

- **Celkový počet unit testov:** **481**
- **Úspešné testy:** **481 (100.0 % Pass Rate)**
- **Zlyhania (Failures):** **0**
- **Chyby (Errors):** **0**
- **Trvanie behu testov:** **0.158 sekundy**

Pred spustením Task 5 v repozitári zlyhávalo 52 testov (kvôli prázdnym `pass` v daných 10 metódach). Po aplikácii RAG sú **všetky testy repozitára zelené**.

---

## 2. Ako funguje funkcia `solve_task`?

V skripte [rag_pipeline.py](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_5/rag_pipeline.py) sme vytvorili funkciu `solve_task`, ktorá presne spĺňa štyri body zadania:
1. **Prijme textovú úlohu:** Na vstupe dostane špecifikáciu (cieľový súbor, triedu, metódu a docstring).
2. **Nájde top 5 chunkov cez vektorové úložisko:** Pomocou matcher nástroja z Task 4 načíta 5 najrelevantnejších chunkov z Task 3 (vrátane definícií tried, typov a príslušných unit testov).
3. **Zostaví prompt a odošle požiadavku do LLM:** Prompt obsahuje presnú špecifikáciu metódy spolu s 5 nájdenými chunkami kódu a testov. Ako model sme použili povolený model `gpt-4o-mini`.
4. **Bezpečne zapíše vygenerovaný kód do zdrojového súboru:** Pomocou modulu `ast` nájde v cieľovom súbore presné riadky pôvodnej metódy, nahradí ich novým kódom so správnym odsadením (4 medzery) a pred uložením na disk overí syntaktickú správnosť celého súboru cez `ast.parse`.

---

## 3. Prehľad implementovaných metód z `missing_code.json`

| Úloha | Trieda a metóda | Súbor | Vygenerovaná logika |
|---|---|---|---|
| **1** | `OrderStatus.is_terminal` | `enums.py` | `@property` vracajúci `self in (OrderStatus.SHIPPED, OrderStatus.CANCELLED)` |
| **2** | `InventoryLedger.__contains__` | `inventory.py` | Bezpečné ošetrenie `normalize_sku` v `try/except` a overenie `normalized in self._on_hand` |
| **3** | `Warehouse.stock_report` | `inventory.py` | Dict comprehension `{sku: available for sku in self._ledger if available > 0}` |
| **4** | `OrderStateMachine.transition` | `orders.py` | Kontrola `can_transition`; pri neplatnom stave vyvolanie `InvalidTransitionError` |
| **5** | `OrderLog.by_status` | `orders.py` | Generátor `yield order for order in self if order.status == status` |
| **6** | `Customer.can_afford` | `models.py` | Typová kontrola a overenie `(self.balance + total) <= self.credit_limit` |
| **7** | `Order.__len__` | `orders.py` | Vrátenie počtu položiek `len(self.items)` |
| **8** | `BulkDiscountPricing.price` | `pricing.py` | Získanie `base_total` z `self._base.price(items)` a zľava v centoch |
| **9** | `EventBus.__contains__` | `events.py` | Kontrola registrácie handlerov pre daný `EventType` |
| **10** | `Money.__bool__` | `models.py` | Logická pravdivosť: `self._cents != 0` |

---

## 4. Ako skript spustiť

```bash
# Spustenie celej RAG pipeline a overenie unit testami:
uv run rag_pipeline.py

# Iba spustenie testovacej sady (bez opätovného volania LLM):
uv run rag_pipeline.py --run-tests-only
```

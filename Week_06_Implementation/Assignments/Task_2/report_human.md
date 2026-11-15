# Prehľad riešenia: Rozdelenie repozitára na chunky (Task 2)

**Predmet:** AI for Software Engineering (AI4SE)  
**Týždeň:** Week 06 – Implementation  
**Úloha:** Task 2 – Rozdelenie kontextu repozitára (Chunking) a odôvodnenie návrhu  
**Zvolená metóda:** Metóda 4 – Obohatený AST Chunking (Context-Enriched AST)  
**Zvolená veľkosť:** Stredné chunky (~30–70 riadkov / ~250–500 tokenov)  

---

## 1. Prečo práve Metóda 4 a stredné chunky?

Pri programovom kóde bežné rozdelenie podľa fixného počtu znakov alebo riadkov zlyháva, pretože **kód má prísnu syntaktickú štruktúru**. Useknutie v strede cyklu `for` alebo vytrhnutie metódy bez toho, aby model poznal atribúty triedy a importy, vedie k chybám pri následnom generovaní kódu.

### Výhody zvoleného prístupu:
1. **Syntaktická čistota (cez AST):** Každý chunk je platným uzlom v syntaktickom strome Pythonu. Žiadna funkcia nie je useknutá na polovicu.
2. **Kontextové obohatenie (Context Enrichment):** Každý chunk automaticky obsahuje:
   - Hlavičku súboru a importy modulu (aby model vedel, aké typy má k dispozícii).
   - Kontext nadradenej triedy (názov triedy, docstring a signatúru konštruktora `__init__`).
3. **Ideálna veľkosť (priemerne 32.9 riadkov):**
   - Menšie triedy ako `Customer`, `OrderStateMachine` alebo `Warehouse` tvoria jeden ucelený chunk.
   - Väčšie triedy (napr. `Money` s 80 riadkami) sú logicky rozdelené do skupín metód, pričom každá skupina má plný kontext triedy.
   - V Task 5 bude RAG vyberať **top 5 chunkov**. Vďaka strednej veľkosti pošleme do LLM promptu ~1 500 až 2 500 tokenov, čo je rýchle, lacné a bez zbytočného šumu.

---

## 2. Vygenerované výstupy

Všetky výstupy sú pripravené v priečinku `Week_06_Implementation/Assignments/Task_2`:

1. **Python skript pre chunking:** [chunker.py](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_2/chunker.py)
   - Využíva štandardný modul `ast`.
   - Podporuje CLI parametre (`--repo-path`, `--output-file`, `--min-lines`, `--max-lines`, `--exclude-tests`).
2. **Dátová štruktúra s chunkami:** [chunks.json](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_2/chunks.json)
   - Obsahuje **116 chunkov** (38 zo zdrojových súborov `playground/`, 78 z testov `tests/`).
   - Každý záznam má unikátne ID, relatívnu cestu, rozsah riadkov, zoznam metód, samotný kód aj obohatený text (`content`) pripravený pre embedding v Task 3.
3. **Detailný technický report:** [report.md](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_2/report.md)
   - Obsahuje porovnávaciu maticu alternatív, Mermaid diagram architektúry a mapovanie na 10 chýbajúcich úloh z `missing_code.json`.

---

## 3. Ako skript spustiť

```bash
# Štandardné spustenie (vygeneruje chunks.json v aktuálnom priečinku):
python3 chunker.py

# Voliteľné nastavenie vlastných parametrov:
python3 chunker.py --repo-path ../Task_1/AI4SE_Playground/playground --output-file chunks.json --min-lines 15 --max-lines 70
```

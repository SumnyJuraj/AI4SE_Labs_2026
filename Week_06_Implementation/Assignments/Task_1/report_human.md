# Správa o riešení: Klonovanie repozitára pomocou AI Agenta (Task 1)

**Predmet:** AI for Software Engineering (AI4SE)  
**Týždeň:** Week 06 – Implementation  
**Úloha:** Task 1 – Naklonovanie repozitára a analýza mechanizmu agenta  
**Cieľový repozitár:** [https://github.com/Neltharion59/AI4SE_Playground](https://github.com/Neltharion59/AI4SE_Playground)  

---

## 1. Zhrnutie vykonaných krokov

1. **Naklonovanie repozitára:**  
   Pomocou nástroja na spúšťanie príkazov (`run_command`) agent spustil príkaz:
   ```bash
   git clone https://github.com/Neltharion59/AI4SE_Playground.git AI4SE_Playground
   ```
   Tým sa stiahol repozitár do priečinka `Week_06_Implementation/Assignments/Task_1/AI4SE_Playground`.

2. **Odstránenie priečinka `.git`:**  
   Aby vnorený repozitár nevytváral konflikt submodulov (gitlink) a neznečisťoval históriu hlavného študentského repozitára, agent odstránil vnútorný `.git` priečinok:
   ```bash
   rm -rf AI4SE_Playground/.git
   ```
   Všetky súbory repozitára sú teraz sledované priamo v hlavnom git repozitári.

3. **Overenie integrity súborov:**  
   V repozitári sa nachádza celkovo 27 zdrojových a testovacích Python súborov v balíku `playground`.

---

## 2. Aký mechanizmus umožnil agentovi repozitár naklonovať?

Samotný jazykový model (LLM) je len generátor textu – nemá priamy prístup k operačnému systému, sieti ani k súborovému systému.

Klonovanie umožnila **agentná architektúra s podporou volania nástrojov (Tool Use / Function Calling)**:

1. **Definícia nástroja (Tool Schema):** Agent má v promptovom kontexte zaregistrovaný nástroj `run_command`, ktorý definuje rozhranie pre spúšťanie príkazov v hostiteľskom shelli (Linux bash).
2. **Kognitívne rozhodnutie (LLM Reasoning):** Po prečítaní zadania v `Task_1.md` model usúdil, že na získanie kódu je potrebné spustiť `git clone`. Vygeneroval štruktúrovanú požiadavku (JSON) na zavolanie nástroja `run_command`.
3. **Vykonanie na hostiteľovi (Subprocess Dispatch):** Výkonné prostredie (agent runtime) požiadavku zachytilo a spustilo príkaz v skutočnom linuxovom shelli hostiteľského počítača.
4. **Využitie sieťovej a systémovej infraštruktúry:** Hostiteľský systém mal nainštalovaný nástroj `git` a povolenú odchádzajúcu HTTPS komunikáciu so servermi `github.com`.
5. **Návrat výsledku do kontextu:** Štandardný výstup a chybový kód procesu (`0`) sa vrátili späť do kontextu modelu, ktorý potvrdil úspešnosť operácie a následne vykonal vyčistenie `.git` priečinka.

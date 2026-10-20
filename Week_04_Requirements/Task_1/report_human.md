# Stručný prehľad riešenia (Human-Friendly Report)

Tento dokument stručne a ľudsky vysvetľuje, ako funguje naša agentná sieť na spresňovanie softvérových požiadaviek a ako si ju môžeš vyskúšať.

---

## 1. O čo v projekte ide?
Máme 20 rôznych neštruktúrovaných súborov (emaily, prepisy rozhovorov, zápisnice z porád) o knižničnom systéme **Evergreen ILS**.  
Naša autonómna sieť v **LangGraph** tieto texty prečíta, extrahuje z nich požiadavky, zlúči duplicity, priradí priority, vyradí nezmysly do Blacklistu a vygeneruje čistý finálny dokument špecifikácie požiadaviek (**SRS**).

---

## 2. Ako funguje agentná sieť?

Sieť sa skladá z **5 uzlov** zapojených v grafe:

1. **Ingestor (Deterministický uzol - bez AI)**:
   - Nájde a prečíta všetky `.txt` a `.eml` súbory zo zadaného priečinka (cesta nie je natvrdo zakódovaná).
2. **Extractor (LLM 1 – `gpt-4o-mini`)**:
   - Paralelne prebehne všetkých 20 dokumentov a vyťahuje jednotlivé kandidátne požiadavky (vyťažil 252 surových požiadaviek).
3. **Consolidator (LLM 2 – `gpt-5.6-luna`)**:
   - Zlúči rovnaké nápady, priradí unikátne ID (`REQ-CAT-001`, `REQ-CIR-001`...), nastaví prioritu (**MoSCoW**) a prepojí každú požiadavku s jej pôvodnými súbormi (trasovateľnosť).
   - Nápady, ktoré nie sú softvérové požiadavky (organizačné meetingy, chýbajúce prílohy), presunie do **Blacklistu**.
4. **Quality Critic & Feedback Loop (LLM 3 – `gpt-6-luna`)**:
   - Prísny audítor, ktorý skontroluje výstup voči zadaniu (OS1–OS9).
   - **Feedback Loop**: V 1. iterácii našiel 2 nedostatky a vrátil prácu späť Consolidatorovi na prepracovanie. V 2. iterácii po úpravách dosiahol dokument skóre **94/100** a bol schválený!
5. **Document Builder (Deterministický uzol - bez AI)**:
   - Vygeneruje finálny Markdown dokument `requirements.md` a JSON dáta pre vizuálny graf `requirements_graph.json`.

---

## 3. Splnenie požiadaviek zadania

- **ANS1–ANS5**:
  - 3 agentné LLM uzly (Extractor, Consolidator, Critic).
  - 2 deterministické uzly (Ingestor, Builder).
  - Skutočný feedback loop (Critic vrátil Consolidatora v cykle na opravu).
  - 3 rôzne OpenAI modely (`gpt-4o-mini`, `gpt-5.6-luna`, `gpt-6-luna`).
  - Implementované v `LangGraph`.
- **OS1–OS9**:
  - 1 ucelený dokument `requirements.md`.
  - Každá požiadavka má unikátne ID, názov, odsek popisu, prioritu a zoznam zdrojových dokumentov.
  - V úvode dokumentu je podrobne vysvetlená stupnica priorít (Must, Should, Could, Won't Have).
  - Na konci je samostatná sekcia **Blacklist** (`BLK-001` až `BLK-004`) s vysvetlením dôvodov vyradenia.

---

## 4. Ako spustiť webové UI (Streamlit)?

Pre vizualizáciu prepojení sme pripravili interaktívne webové rozhranie s legendou farieb:

```bash
# 1. Aktivuj virtuálne prostredie
source .venv/bin/activate

# 2. Spusť aplikáciu
streamlit run app.py
```

### Vizuálna legenda v UI:
- 🟪 **Fialový šesťuholník**: **AI Agent / Systémový uzol** (zobrazuje jednotlivé uzly siete: `gpt-4o-mini`, `gpt-5.6-luna`, `gpt-6-luna`, `Python`).
- 🟦 **Modrý obdĺžnik**: Vstupný zdrojový dokument z korpusu (napr. `email_financial_reports.eml`).
- 🟥 **Červený kruh**: Požiadavka typu **Must Have** (Kritická priorita).
- 🟧 **Oranžový kruh**: Požiadavka typu **Should Have** (Dôležitá prevádzková funkcia).
- 🟩 **Zelený kruh**: Požiadavka typu **Could Have / Won't Have** (Rozšírenie / odložená funkcia).
- ⬛ **Tmavosivý trojuholník**: **Blacklistovaná požiadavka** (Vyradená s odôvodnením).
- ➖ **Plná čiara**: Prepojenie (tok dát alebo trasovateľnosť).
- ╌ **Červená prerušovaná čiara**: **Feedback Loop (ANS3)** (Critic vracia Consolidatorovi pripomienky na opravu).

V UI si môžeš kliknúť na ktorýkoľvek uzol, filtrovať požiadavky v tabuľke, čítať detailné popisy alebo priamo stiahnuť finálny `requirements.md`.

---

## 5. Ako spustiť pipeline cez terminál?
```bash
source .venv/bin/activate
python main.py --input data/corpus --output requirements.md
```
Pipeline automaticky prejde celý priečinok a prepíše výstupné súbory.

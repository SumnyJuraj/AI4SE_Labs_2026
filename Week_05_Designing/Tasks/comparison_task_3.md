# Porovnávacia správa (Comparison Report) – Task 3

Táto správa porovnáva proces a výstupy architektonického návrhu pre systém **EventTicket** vytvorené:
1. **Pred zavedením skillu (`ADR_before.md` / Task 1 & Task 2)** – ad-hoc konverzácia a manuálne iterácie bez formalizovaného pracovného postupu.
2. **S použitím skillu `/architecture` (`tickets_using_skill.md`)** – štruktúrovaný proces riadený fázami 1 až 6 metodiky softvérového architekta.

---

## 1. Prehľadné zhrnutie porovnania (Executive Summary)

| Kritérium | Pred zavedením skillu (`ADR_before.md`) | S použitím skillu `/architecture` (`tickets_using_skill.md`) | Hodnotenie prínosu skillu |
|---|---|---|---|
| **Riešenie konkurencie a inventára** | *First-to-Pay-Wins* (bez predbežnej rezervácie, riešenie prepredaja cez automatické refundácie na Stripe). | *Soft-Lock s TTL (10–15 min)* podložený atomickým SQL odpočtom kapacity a Redis zámkom. | **Kritické zlepšenie:** Skill odhalil a eliminoval finančnú stratu zo Stripe poplatkov (2.9% + 30¢), ktoré sa pri refunde nevracajú. |
| **Hĺbka implementačných detailov** | Konceptuálny SQL fragment a pseudokód v Pythone. | Kompletná DDL schéma PostgreSQL (tabuľky, indexy, stavy), transakčné bloky a čistiaci SQL worker. | **Vysoký prínos:** Vývojár má pripravenú presnú databázovú schému pripravenú na nasadenie. |
| **Metodika NFR (Nefunkčné požiadavky)** | Pomenovanie zvolených hodnôt v odrážkach bez explicitného porovnania alternatív. | Štruktúrovaná tabuľková matica Tier A / Tier B / Tier C pre 5 dimenzií bez pýtania sa na sumy v eurách. | **Vysoký prínos:** Prehľadné zladenie rozpočtu, dostupnosti, škálovania a personálnych kapacít. |
| **Kvalita a validita Mermaid diagramov** | Diagramy obsahovali cylindrické uzly `[("...")]`, ktoré zlyhávajú na starších rendereroch. | Prísne dodržanie *Mermaid Quality Gate* (bezpečné hranaté uzly, texty v úvodzovkách, žiadne zátvorky v šípkach). Navyše pridaný sekvenčný diagram životného cyklu rezervácie. | **Vysoký prínos:** Bezchybná vizualizácia v ľubovoľnom Markdown prehliadači (GitHub, VS Code, GitLab). |
| **Rýchlosť a proces (Time-to-Value)** | Vyžadoval viacero kôl otázok, usmerňovania a manuálnych opráv počas dvoch fáz. | Okamžité vygenerovanie kompletného end-to-end riešenia v jedinom kroku. | **Radikálne zrýchlenie:** Eliminácia komunikačného šumu a opakovaného vysvetľovania kontextu. |

---

## 2. Detailné kvalitatívne porovnanie

### 2.1 Architektonické paradigmy a výber víťaza
V oboch prípadoch bol ako optimálna voľba vyhodnotený **Multi-Process Modular Monolith s oddelenými worker procesmi**.
- **Pred skillom:** Voľba bola vysvetlená pragmaticky s dôrazom na malý tím a SSR rendering.
- **So skillom:** Analýza ide hlbšie do prevádzkových detailov. Identifikuje PgBouncer ako kritickú podmienku pre zamedzenie connection exhaustion, presne definuje doménové hranice modulov a rieši oddelenie workerov na úrovni Redis front (BullMQ).

### 2.2 Zásadný rozdiel: Inventár, platby a ochrana pred poplatkami
Najvýraznejší kvalitatívny rozdiel nastal pri návrhu nákupného toku a ochrany proti prepredaju:
- **Prístup v `ADR_before.md` (First-to-Pay-Wins):**
  Systém nechával používateľov zaplatiť na Stripe bez držania rezervácie. Ak 500 používateľov súťažilo o 50 lístkov, 450 zákazníkov bolo úspešne naúčtovaných a následne refundovaných cez Stripe API.
  *Kritická slabina:* Stripe si ponecháva transakčný poplatok (cca 2.9% + 30¢ za transakciu). Pri 450 neúspešných nákupoch po 50 € platforma okamžite stratí približne **787,50 €** na nevratných poplatkoch brány!
- **Prístup v `tickets_using_skill.md` (Soft-Lock s TTL):**
  Skill `/architecture` obsahuje vo svojej vedomostnej báze (Fáza 4) explicitné varovanie pred týmto rizikom. Namiesto First-to-Pay-Wins implementuje **atomický Soft-Lock s TTL (15 min)**:
  1. Zákazník klikne na nákup -> v databáze sa atomicky odpočíta počet miest (`remaining_tickets = remaining_tickets - qty WHERE remaining_tickets >= qty`).
  2. Vytvorí sa rezervácia so stavom `PENDING` a platnosťou 15 minút.
  3. Karta sa na Stripe autorizuje a zúčtuje iba pre garantované lístky.
  4. Ak zákazník nákup nedokončí, worker uvoľní lístky späť do predaja.
  *Výsledok:* Nulový prepredaj a nulové straty na transakčných poplatkoch.

### 2.3 Implementačné protokoly a DDL schémy
- **V pôvodnom `ADR_before.md`:** Uvedený iba jeden atomický `UPDATE` dopyt a Python pseudokód pre refundáciu.
- **V `tickets_using_skill.md`:**
  - Plnohodnotná PostgreSQL DDL schéma s tabuľkami `events`, `reservations`, `tickets`, `payments`.
  - Enum typy (`reservation_status`) a `CHECK` integritné obmedzenia.
  - SQL dotaz s CTE (`WITH expired AS ...`) pre hromadné uvoľňovanie expirovaných rezervácií workerom v jedinej transakcii.
  - Ochrana webhookov pred duplicitným spracovaním (idempotencia cez `payment_intent_id UNIQUE`).

### 2.4 Dodržanie štandardov vizualizácie (Mermaid Quality Gate)
- V `ADR_before.md` boli v Option 2 použité cylindrické uzly typu `CatDB[("Catalog DB")]`. Tieto konštrukcie spôsobujú v určitých verziách Mermaidu parsovacie chyby (`lexer error`).
- V `tickets_using_skill.md` sú všetky diagramy syntakticky čisté, uzly používajú bezpečné hranaté zátvorky `["..."]`, popisy spojení sú zbavené zátvoriek a znakov `<` / `>`, a navyše je priložený prehľadný sekvenčný diagram (`sequenceDiagram`) zachytávajúci celý end-to-end tok medzi používateľom, webovým serverom, Redisom, databázou, platobnou bránou a e-mailovým workerom.

---

## 3. Efektivita procesu: Pred vs. Po vytvorení skillu

### Priebeh pred vytvorením skillu (Task 1 & Task 2)
- Vývojár musel postupne viesť asistenta otázkami:
  1. Vyžiadať si návrh troch rôznych architektúr.
  2. Manuálne upozorňovať na riziká a pýtať sa na trade-offy.
  3. Samostatne zadať požiadavku na vygenerovanie ADR.
  4. Opakovane žiadať o úpravu štruktúry, doplnenie porovnávacích tabuliek a kontrolu diagramov.
- Riziko, že asistent zabudne na kľúčové edge cases (napr. poplatky Stripe, connection pooling, rate limity e-mailov).

### Priebeh po aktivácii skillu `/architecture` (Task 3)
- Jediný príkaz `/architecture` spustil ucelený workflow:
  1. Automatická extrakcia entít a rolí z požiadaviek.
  2. Generovanie 3 kvalitatívne odlišných architektonických štýlov.
  3. Špecifikácia NFR vo forme troch rozpočtových balíkov (Tier A / B / C).
  4. Hĺbková analýza nízkoúrovňových rizík (inventory locking, idempotencia, SMTP fan-out).
  5. Finálne vygenerovanie formálneho MADR dokumentu s overenými diagramami.
- **Výsledok:** Cieľ bol dosiahnutý násobne rýchlejšie, v konzistentnom formáte a bez vynechania dôležitých inžinierskych detailov.

---

## 4. Záver

Zavedenie skillu `/architecture` preukázalo výrazné zvýšenie kvality výstupov aj efektivity práce. Výsledný architektonický návrh v `tickets_using_skill.md` je:
1. **Biznisovo bezpečnejší** (odstraňuje finančné riziká pri zlyhaní platieb).
2. **Technicky konkrétnejší** (poskytuje priame SQL protokoly a DDL schému).
3. **Vizuálne spoľahlivejší** (rešpektuje Mermaid Quality Gate).
4. **Okamžite reprodukovateľný** pre akýkoľvek ďalší softvérový systém v priečinku `data/`.

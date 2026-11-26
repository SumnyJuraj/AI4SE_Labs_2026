# Task 6 – Záznam konverzácie so subagentmi (Claude Code)

Nástroj: **Claude Code** (orchestrátor Opus 5.5, subagenti Sonnet cez nástroj `Agent`). Žiadna zmena konfigurácie nebola potrebná – spawnovanie subagentov je vstavaná funkcia.

## Obsah

- [1. Zadanie od používateľa](#1-zadanie-od-používateľa)
- [2. Upresňujúce otázky](#2-upresňujúce-otázky)
- [3. Fáza 1 – 10 subagentov na poznámky](#3-fáza-1--10-subagentov-na-poznámky)

---

## 1. Zadanie od používateľa

> Ukladaj tuto konverzaciu do .md suboru. Precitaj si zadanie najprv ktore je v tomto priecinku. Moj napad je vytvarat subagentov kde kazdy subagent prejde jednu prezentaciu ulozia sa ich zapisy z prezentacie do md suboru jedneho potom iny subagent vygeneruje json file z tych poznamok s otazkami a odpovedami. potom iny subagent vytvori interaktivnu mini web apku s kartickami kde sa mozem dynamicky posuvat bude karticka jedna otazka otocim odpoved potom sa presuniem na druhu karticku. Takto chcem aby bolo aspon 10 otazok z kazdej prezentacie. Ak chces rady a mas neistoty opytaj sa ma na bud strukturu alebo styl aby mi to co najviac vyhovovalo. Funkcionalitu tohto tasku otestujeme z prednasok, ktore sa nachadzaju v /home/juraj/skola/zimny1/animacia/prezentacie_teoria/prednasky. Interaktivnu apku nemusis ukladat do tohto repa uloz mi ju to toho /prednasky.

**Claude:** Prečítal `Task_6.md` (úloha: nechať asistenta spawnovať subagentov, odovzdať záznam) a vypísal priečinok `prednasky/` – 10 PDF (`Ca15_lesson01.pdf` … `Ca16_lesson10.pdf`).

---

## 2. Upresňujúce otázky

| Otázka | Odpoveď |
|---|---|
| Jazyk kartičiek | **Slovensky** |
| Funkcie appky navyše | **Filter podľa prednášky** |
| Vizuálny štýl | **Tmavý minimalistický** (3D flip) |
| Model subagentov | **Sonnet** (lacnejší; orchestráciu robí Opus) |

---

## 3. Fáza 1 – 10 subagentov na poznámky

**Claude:** Spustil paralelne **10 subagentov (Sonnet, na pozadí)**, každý na jednu prednášku. Každý zapisuje do vlastného súboru `flashcards/notes/lessonNN.md` (aby sa súbežné zápisy neprepisovali); orchestrátor ich potom zlúči do jedného `poznamky.md`.

Prompt (rovnaký pre všetky, mení sa číslo):

> Read the PDF …/Ca15_lessonNN.pdf (Read tool with `pages`, max 20 pages per call). Write study notes IN SLOVAK to …/flashcards/notes/lessonNN.md. Start with `## Prednáška NN: <topic>`, then `###` subsections with bullets (concepts, definitions, formulas, algorithms). ~80–150 lines, enough for 10+ exam questions. Reply only with one line: topic title and line count.

Obmedzenia (podľa varovania v zadaní): pevný počet agentov (10 + 1 + 1), lacnejší model, krátka odpoveď späť orchestrátorovi, aby sa nezahlcoval jeho kontext.

Výsledky subagentov:

- Prednáška 08: Dynamika tuhých telies (Rigid Body Dynamics) – 179 riadkov
- Prednáška 04: Látka, vlasy a mäkké telesá (mass-spring, PBD) – 175 riadkov
- Prednáška 01: Úvod do počítačovej animácie – 174 riadkov (agent uviedol odhad 151, overené cez wc)
- Prednáška 09: Kolízie tuhých telies a väzby (joints) – 163 riadkov
- Prednáška 05: Broad Phase Collision Detection (grids, spatial hashing, sweep and prune) – 125 riadkov
- Prednáška 06: Mid-phase detekcia kolízií (BVH, ohraničujúce objemy, ACD) – 150 riadkov
- Prednáška 02: Základné metódy počítačovej animácie – 187 riadkov
- Prednáška 03: Časticové systémy (Particle Systems) – 229 riadkov
- Prednáška 10: Simulácia tekutín (Navier-Stokes, MAC, SPH) – 132 riadkov
- Prednáška 07: Detekcia kolízií – Narrow Phase (GJK, V-Clip, SDM) – 189 riadkov

**Claude (orchestrátor):** Všetkých 10 hotových. Zlúčil poznámky príkazom `cat notes/lesson*.md > poznamky.md` (1735 riadkov).

---

## 4. Fáza 2 – subagent generuje JSON

**Claude:** Spustil 1 subagenta (Sonnet), ktorý prečíta `poznamky.md` a vytvorí `flashcards.json` (min. 10 otázok na prednášku).

**Subagent JSON:** `[12, 12, 12, 12, 12, 12, 12, 12, 12, 12]` – 120 kartičiek; orchestrátor overil nezávisle cez `python3 json.load`.

---

## 5. Fáza 3 – subagent vytvára web appku

**Claude:** Spustil 1 subagenta (Sonnet) na `prednasky/flashcards/index.html`: tmavý minimalistický štýl, 3D flip, šípky + filter podľa prednášky, KaTeX pre vzorce, dáta vložené inline (funguje aj cez `file://`).

**Subagent appka:** Vytvoril `index.html` (JSON vložený inline) a generátor `build.py`. Overenie: 120 kartičiek po spätnom parsovaní, `node --check` bez chýb. V prehliadači netestoval; KaTeX ide z CDN (vzorce potrebujú internet).

**Claude (orchestrátor):** Nezávisle overil cez grep, že appka obsahuje flip (`rotateY`), šípky, filter a KaTeX render.

---

## 6. Výsledok

Výstupy v `/home/juraj/skola/zimny1/animacia/prezentacie_teoria/prednasky/flashcards/`:

- `notes/lesson01..10.md` – poznámky od 10 subagentov,
- `poznamky.md` – zlúčené poznámky,
- `flashcards.json` – 120 otázok (12 × 10),
- `index.html` + `build.py` – interaktívna appka.

**Spolu 12 subagentov** (10 + 1 + 1, všetky Sonnet), orchestrácia Opus. Každý subagent vracal len 1–3 riadky, takže kontext orchestrátora ostal malý; subagenti na poznámky a JSON spotrebovali 77–146 tis. tokenov a bežali 50–130 s, subagent na appku 42 tis. tokenov a 23 s.

# Rýchly prehľad pre hodnotiteľa: Úloha 1 (Task 1)

**Cieľ úlohy:** Vybrať 3 prompting frameworky (nie ROSES a nie Zero-Shot), vytvoriť z nich prompty pre Text-to-SQL databázovú úlohu a vysvetliť ich výber.  
**Hodnotenie:** 1 bod  

---

### 1. Ktoré 3 frameworky boli vybrané a odkiaľ sú?
Všetky 3 frameworky pochádzajú z knižnice na [frompting.com/frameworks](https://frompting.com/frameworks):
1. **ICIO** (*Instruction - Context - Input - Output*) – kategória *AI & Prompt Engineering*
2. **Few-Shot** (*Few-Shot Learning*) – kategória *Communication & Storytelling*
3. **CoT** (*Chain of Thought*) – kategória *Reasoning & Analysis*

*(Podmienka zadania splnená: Ani jeden z nich nie je ROSES a ani jeden nie je Zero-Shot).*

---

### 2. Prečo práve tieto tri a prečo sú lepšie než iné?
Bežné frameworky na trhu (ako AIDA, STAR, PAS, BAB) sú stavané na copywriting, marketing alebo pracovné pohovory a pre generovanie SQL kódu sú nepoužiteľné. 

Zvolili sme preto **tri odlišné paradigmy AI inžinierstva**, aby sme ich v ďalších úlohách mohli reálne a zmysluplne porovnať:
- **ICIO (Štrukturálna špecifikácia):** Presne oddeľuje databázovú schému (`Context`), pravidlá (`Instruction`), otázku používateľa (`Input`) a formát kódu (`Output`). Zabraňuje tomu, aby si model pomýlil zadanie s otázkou.
- **Few-Shot (Učenie na príkladoch):** Zlatý štandard pre Text-to-SQL. Namiesto abstraktných poučiek dáva modelu 4 konkrétne ukážky dvojíc (Otázka $\rightarrow$ Správny SQL kód). Ukazuje mu, ako spájať tabuľky (`JOIN`) a ako ignorovať zavádzajúci text.
- **CoT (Krokové uvažovanie):** Núti model pred napísaním SQL najprv spraviť 3 myšlienkové kroky: 1. odfiltrovať šum, 2. identifikovať stĺpce a tabuľky, 3. poskladať SQL.

---

### 3. Čo od nich očakávame (Hypotézy pre Task 2 až 4)?
* **Rýchlosť (latencia):** ICIO bude najrýchlejšie (krátky text), Few-Shot bude stredný, CoT bude najpomalší (musí generovať desiatky slov uvažovania navyše).
* **Presnosť (Accuracy):** Few-Shot a CoT dosiahnu podstatne vyššiu úspešnosť než ICIO, pretože otázky v datasete obsahujú schválne vložený šum (reči o koláčoch a počasí), s ktorým si ICIO bez ukážok neporadí.

---

### 4. Kde nájdete výstupy?
* Šablóna ICIO: [`prompt_1_icio.md`](prompt_1_icio.md)
* Šablóna Few-Shot: [`prompt_2_few_shot.md`](prompt_2_few_shot.md)
* Šablóna CoT: [`prompt_3_cot.md`](prompt_3_cot.md)
* Všetky prompty spolu: [`prompts.md`](prompts.md)
* Podrobný akademický report v angličtine: [`report.md`](report.md)

---
name: notes
description: Spoznámkuje všetky prezentácie (PDF/PPTX) v aktuálnom priečinku do .md súborov a preskočí tie, ktoré už majú poznámky.
disable-model-invocation: true
---

Spoznámkuj prezentácie v aktuálnom pracovnom priečinku.

## Postup

1. **Nájdi prezentácie** v aktuálnom priečinku (nie rekurzívne): `*.pdf`, `*.pptx`, `*.ppt`, `*.odp`.
2. **Zisti, čo už je spoznámkované.** Prejdi všetky `.md` súbory v aktuálnom priečinku (tam, kde sú prezentácie; nie v nadradených priečinkoch).
   Prezentácia je spoznámkovaná, ak niektorý `.md` súbor:
   - má rovnaký základný názov (napr. `Ca16_lesson03.pdf` → `Ca16_lesson03.md`), alebo
   - spomína názov súboru prezentácie či jej identifikátor (napr. `lesson03`, `Lesson 03`) v nadpise alebo v obsahu ako spracovanú prednášku.
   Pri neistote si súbor prečítaj a over, že prezentáciu naozaj pokrýva.
3. **Vypíš zoznam** prezentácií: ktoré preskočíš (a v ktorom `.md` súbore sú) a ktoré spoznámkuješ.
4. **Spoznámkuj každú zvyšnú prezentáciu** do `<názov_prezentácie>.md` v aktuálnom priečinku:
   - prečítaj celú prezentáciu (PDF po častiach, najviac 20 strán naraz),
   - zachyť všetky pojmy, definície, algoritmy, vzorce a príklady,
   - pri veľkom počte prezentácií spracuj každú v samostatnom subagentovi.
5. Na záver vypíš, ktoré súbory vznikli a čo sa preskočilo.

## Formát poznámok

Dodržuj formát z `/home/juraj/skola/zimny1/animacia/prezentacie_teoria/prednasky/vsetky_vzorce.md`:
- `#` nadpis, krátky úvod, `## Obsah` s odkazmi, sekcie oddelené `---`,
- kapitoly `## N. Názov`, podkapitoly `### N.M Názov`,
- inline matematika `$...$`, blokové vzorce:
  ```
  $$
  vzorec
  $$
  ```
  (`$$` na samostatných riadkoch, prázdny riadok pred blokom aj za ním; nepoužívaj `\(...\)` ani `\[...\]`),
- pod každým vzorcom odrážky **Kedy:**, **Premenné:**, **Pravidlá:**, prípadne **Očakávaný výsledok** a **⚠ Pozn.** pri preklepe na slajde,
- kľúčové pojmy **tučne**, po slovensky s diakritikou.

Ďalšie pokyny od používateľa: $ARGUMENTS

---
name: test
description: Z prednášok v aktuálnom priečinku (alebo len z vybraných) vytvorí test s 20 otázkami s voľnou odpoveďou a so všetkými odpoveďami na konci. Použi pri /test alebo keď si používateľ pýta otázky na precvičenie z prednášok.
argument-hint: "[voliteľne: názvy prednášok, napr. prednaska3.pdf prednaska5]"
---

# Test z prednášok

Argumenty: $ARGUMENTS

## 1. Výber prednášok
- **Bez argumentov (default):** použi všetky prednášky v aktuálnom priečinku (`.pdf`, `.pptx`, `.md`, `.txt`, `.docx`).
- **S argumentmi:** použi len prednášky, ktoré zodpovedajú zadaným názvom alebo číslam (stačí čiastočná zhoda, napr. `3` → `prednaska_03.pdf`). Ak sa nič nenájde, vypíš dostupné súbory a skonči.
- Na začiatku vypíš, z ktorých súborov test vzniká.

## 2. Otázky
- Vytvor **presne 20 otázok** s **voľnou odpoveďou**. Nepoužívaj výber z možností ani áno/nie.
- Otázky rozlož rovnomerne medzi vybrané prednášky.
- Mix obtiažnosti: definície, vysvetlenie princípov, porovnanie pojmov, aplikácia na príklad, výpočet (ak prednáška obsahuje vzorce).
- Pri každej otázke uveď v zátvorke zdrojovú prednášku.
- Píš po slovensky s diakritikou. Matematiku zapisuj ako `$...$` a blokové vzorce ako `$$` na samostatných riadkoch.

## 3. Formát výstupu
Výsledok ulož do `test_otazky.md` v aktuálnom priečinku. Ak súbor existuje, ulož do `test_otazky_2.md` atď. Štruktúra:

```
# Test z prednášok
Zdroje: ...

## Otázky
1. ...
...
20. ...

---

## Odpovede
1. ...
...
20. ...
```

- Pod otázkami **nesmú byť žiadne odpovede ani nápovedy**. Všetky odpovede sú spolu až v sekcii **Odpovede** úplne na konci.
- Odpoveď má 1 – 4 vety s kľúčovými pojmami zvýraznenými **tučne**, aby sa dala porovnať s vlastnou odpoveďou.

Na záver v chate vypíš len cestu k súboru a zoznam použitých prednášok.

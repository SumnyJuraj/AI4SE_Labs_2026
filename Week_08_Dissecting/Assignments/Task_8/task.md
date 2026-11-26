Na tuto konverzaciu bol pouzity novy agent aby nevedel o vytvorenom rule z pamati. 
Rule bol dodrzany ale vsimol som si napriklad chybu ze na miesto root mal dat toor ale realne napisal tooc. Nejedna sa vsak o chybu o nedodrzanom rule.



# Task 8 – Konverzácia

Záznam konverzácie s Claude Code pri tvorbe jednoduchej šachovnice v Pythone.

## Obsah

- [1. Zadanie používateľa](#1-zadanie-používateľa)
- [2. Odpoveď a postup](#2-odpoveď-a-postup)

---

## 1. Zadanie používateľa

> Vytvor v tomto priecinku .md subor s nazvom task. Tam nahras tuto nasu konverzaciu.
> Vytvor v pythone velmi jednoduchy program ktory bude robit nasledovne. Ked sa spusti tak sa vytvori nakreslena sachovnica. Pridaj tam aj figurky ale nedavaj ich tam ako favicony ale vytvor ich z roznych geometrickych tvarov ktore ty uznas za vhodne. Kludne to mozu byt kruzky, trojuholniky take jednoduche tvary. Figurky sa nemusia hybat chcem len aby staticky stali.

---

## 2. Odpoveď a postup

1. Vytvoril som súbor **`sachovnica.py`** s knižnicou **tkinter** (súčasť štandardnej knižnice Pythonu).
2. Šachovnica má 8×8 políčok (svetlé a tmavé hnedé), okolo je tmavý rám.
3. Figúrky sú zložené len z geometrických tvarov (podstavec je pri každej obdĺžnik):
   - **Pešiak** – trojuholník + krúžok (hlava),
   - **Veža** – obdĺžnik + tri malé obdĺžniky (cimburie),
   - **Jazdec** – mnohouholník v tvare konskej hlavy + bodka (oko),
   - **Strelec** – trojuholník + ovál + malý krúžok na vrchu,
   - **Dáma** – mnohouholník v tvare koruny + tri krúžky,
   - **Kráľ** – lichobežník + kríž z dvoch obdĺžnikov.
4. Kód dodržiava pravidlá repozitára: premenné cyklov sú `x`, `y` a ostatné názvy premenných sú písané **odzadu** (napr. `savnac`, `roloc`, `ezis`).
5. Overenie: syntax je v poriadku. Python z Homebrew nemá modul `_tkinter`, preto treba spúšťať systémovým Pythonom:

```bash
/usr/bin/python3 sachovnica.py
```

Figúrky sú statické, nedajú sa hýbať.

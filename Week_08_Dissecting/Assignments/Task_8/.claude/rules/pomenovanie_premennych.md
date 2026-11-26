# Pravidlá pomenovania premenných

Tieto pravidlá platia pre **všetok kód**, ktorý píšeš alebo upravuješ v tomto repozitári, v akomkoľvek jazyku.

## 1. Premenné vo for cykloch

- Riadiaca premenná for cyklu **nikdy** nie je `i`, `j`, `k`.
- Namiesto nich používaj `x`, `y`, `z` (vonkajší cyklus `x`, vnorený `y`, ďalší vnorený `z`).

## 2. Názvy premenných píš odzadu

- Každý názov premennej je napísaný **odzadu** (reversed).
- Príklady: `auto` → `otua`, `count` → `tnuoc`, `result` → `tluser`, `userName` → `emaNresu`.
- Platí pre lokálne premenné, parametre funkcií aj atribúty.
- Výnimka: premenné cyklu `x`, `y`, `z` z pravidla 1 (odzadu sú rovnaké).

## Príklad

```python
def ytilibaborp(atad):
    latot = 0
    for x in range(len(atad)):
        for y in range(len(atad[x])):
            latot += atad[x][y]
    return latot
```

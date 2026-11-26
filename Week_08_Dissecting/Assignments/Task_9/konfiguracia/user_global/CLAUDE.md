## Workflow Orchestration

### 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One tack per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests - then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Formát Markdown súborov s matematikou

Pri písaní `.md` súborov dodržuj štýl súboru `prednasky/vsetky_vzorce.md`:

- **Inline matematika:** `$...$`, napr. `$t_i$`, `$-10$`. Nepoužívaj `\(...\)`.
- **Blokové vzorce:** `$$` na samostatnom riadku, vzorec na ďalšom riadku a uzatváracie `$$` znova na samostatnom riadku. Pred blokom aj za ním nechaj prázdny riadok. Nepoužívaj `\[...\]` a nepíš blok na jeden riadok (`$$x$$`).
  $$
  p = I(t,\ F_i,\ F_{i+1}), \qquad t_i < t < t_{i+1}
  $$
- **Medzery v LaTeX-u:** `\ ` za čiarkou v n-ticiach, `\qquad` medzi vzorcom a podmienkou, `\dots` pre výpustky.S
- **Štruktúra:** `#` nadpis, krátky úvod, `## Obsah` s odkazmi na sekcie a sekcie oddelené `---`. Kapitoly píš ako `## N. Názov`, podkapitoly ako `### N.M Názov`.
- **Pod každým vzorcom** daj odrážky:
- **Kedy:** kedy sa vzorec používa,
- **Premenné:** význam každej premennej (v `$...$`),
- **Pravidlá:** čo nesmie byť záporné či nulové a aký tvar musí mať,
- podľa potreby **Očakávaný výsledok** (zmysluplné hodnoty) a **⚠ Pozn.** (preklep na slajde a správny tvar).
- Kľúčové pojmy zvýrazni **tučne**. Píš po slovensky s diakritikou.


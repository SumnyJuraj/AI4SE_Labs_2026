# Task 9 – Konfiguračné súbory Claude Code

Claude Code neukladá konfiguráciu do jedného súboru. Rozdeľuje ju na **globálnu** (`~/.claude/`) a **projektovú** (`.claude/` v repozitári, `.mcp.json`). Kópie všetkých súborov so zmenami z Taskov 1 – 8 sú v priečinku `konfiguracia/`. Originály som nemenil.

## Obsah

- [1. Mapovanie taskov na súbory](#1-mapovanie-taskov-na-súbory)
- [2. Cenzúra](#2-cenzúra)

---

## 1. Mapovanie taskov na súbory

| Task | Funkcia | Originál | Kópia |
|---|---|---|---|
| 1 | **System prompt** (sekcia „Formát Markdown súborov s matematikou“) | `~/.claude/CLAUDE.md` | `konfiguracia/user_global/CLAUDE.md` |
| 2 | **Slash command** `/notes` | `~/.claude/skills/notes/SKILL.md` | `konfiguracia/user_global/skills/notes/SKILL.md` |
| 3 | **CLAUDE.md** namiesto AGENTS.md | – (pozri `Task_3/odpoved.md`) | – |
| 4 | **Profil** = subagent `unit-tester` | `Task_4/.claude/agents/unit-tester.md` | `konfiguracia/repo/.claude/agents/unit-tester.md` |
| 5 | **Skill** `test` | `Task_5/.claude/skills/test/SKILL.md` | `konfiguracia/repo/.claude/skills/test/SKILL.md` |
| 6 | **Subagenty** (vstavaná funkcia, bez zmeny konfigurácie) | `settings.json` → `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `konfiguracia/user_global/settings.json` |
| 7 | **MCP server** `latex-checker` | `Task_7/.mcp.json` a `/.claude/settings.local.json` (`enabledMcpjsonServers`) | `konfiguracia/repo/.mcp.json`, `konfiguracia/repo/.claude/settings.local.json` |
| 8 | **Rule** na pomenovanie premenných | `Task_8/.claude/rules/pomenovanie_premennych.md` | `konfiguracia/repo/.claude/rules/pomenovanie_premennych.md` |

Hlavný konfiguračný súbor je **`~/.claude/settings.json`** (oprávnenia, premenné prostredia, hooky, pluginy, effort level).

---

## 2. Cenzúra

- V `settings.json` som cenzuroval **`ANTHROPIC_API_BASE_URL`** a **`CLAUDE_AGENT_API_BASE_URL`** (adresa lokálneho proxy) a používateľské meno v cestách `/Users/***/`.
- API kľúč sa v súboroch nenachádza. Claude Code ho drží v prihlasovacích údajoch (`~/.claude/.credentials.json`), ktoré som neodovzdal.

# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2,<2"]
# ///
"""Jednoduchý lokálny MCP server s jedným nástrojom: check_latex.

Skontroluje LaTeX matematiku v Markdown texte (alebo v .md súbore)
a vráti zoznam nájdených problémov s číslom riadku.
"""

import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("latex-checker")

BRACKETS = {"{": "}", "(": ")", "[": "]"}


def _check_braces(expr: str, line_no: int, issues: list[str]) -> None:
    """Skontroluje párovanie {} () [] vo vzorci (ignoruje \\{ \\} a \\left/\\right)."""
    stack: list[str] = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == "\\":  # escapovaný znak, napr. \{ alebo \,
            i += 2
            continue
        if ch in BRACKETS:
            stack.append(ch)
        elif ch in BRACKETS.values():
            if ch == "}":
                if not stack or stack[-1] != "{":
                    issues.append(f"riadok {line_no}: nadbytočná '}}'")
                else:
                    stack.pop()
            elif stack and BRACKETS.get(stack[-1]) == ch:
                stack.pop()
        i += 1
    if "{" in stack:
        issues.append(f"riadok {line_no}: neuzavretá '{{' ({stack.count('{')}x)")


def _check_envs(expr: str, line_no: int, issues: list[str]) -> None:
    stack: list[str] = []
    for kind, name in re.findall(r"\\(begin|end)\{([^}]*)\}", expr):
        if kind == "begin":
            stack.append(name)
        elif not stack or stack.pop() != name:
            issues.append(f"riadok {line_no}: \\end{{{name}}} bez zodpovedajúceho \\begin")
    for name in stack:
        issues.append(f"riadok {line_no}: \\begin{{{name}}} bez \\end")


def _check_text(text: str) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    in_block = False
    block_start = 0
    block_lines: list[str] = []
    in_code = False

    for n, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        if in_block:
            if stripped == "$$":
                expr = "\n".join(block_lines)
                if not expr.strip():
                    issues.append(f"riadok {block_start}: prázdny blokový vzorec")
                _check_braces(expr, block_start, issues)
                _check_envs(expr, block_start, issues)
                if n < len(lines) and lines[n].strip():
                    issues.append(f"riadok {n}: za blokom $$ chýba prázdny riadok")
                in_block = False
            elif "$$" in stripped:
                issues.append(f"riadok {n}: uzatváracie $$ nie je na samostatnom riadku")
            else:
                block_lines.append(line)
            continue

        if stripped == "$$":
            in_block, block_start, block_lines = True, n, []
            if n > 1 and lines[n - 2].strip():
                issues.append(f"riadok {n}: pred blokom $$ chýba prázdny riadok")
            continue

        if "$$" in stripped:
            issues.append(f"riadok {n}: blokový vzorec na jednom riadku ($$x$$) – rozdeľ na 3 riadky")
        if "\\(" in line or "\\)" in line:
            issues.append(f"riadok {n}: použité \\(...\\) – použi $...$")
        if "\\[" in line or "\\]" in line:
            issues.append(f"riadok {n}: použité \\[...\\] – použi blok $$")

        # inline $...$ (bez $$ a bez escapovaného \$)
        no_code = re.sub(r"`[^`]*`", "", line).replace("$$", "")
        dollars = [m.start() for m in re.finditer(r"(?<!\\)\$", no_code)]
        if len(dollars) % 2:
            issues.append(f"riadok {n}: nepárny počet '$' – neuzavretý inline vzorec")
        for a, b in zip(dollars[::2], dollars[1::2]):
            expr = no_code[a + 1 : b]
            if not expr.strip():
                issues.append(f"riadok {n}: prázdny inline vzorec $$")
            _check_braces(expr, n, issues)
            _check_envs(expr, n, issues)

    if in_block:
        issues.append(f"riadok {block_start}: blok $$ nie je nikdy uzavretý")
    if in_code:
        issues.append("neuzavretý ``` blok kódu")
    return issues


@mcp.tool()
def check_latex(text: str = "", file_path: str = "") -> str:
    """Skontroluje LaTeX matematiku v Markdowne.

    Zadaj buď `text` (obsah na kontrolu), alebo `file_path` (cesta k .md súboru).
    Kontroluje: párovanie $ a $$, $$ na samostatnom riadku, prázdne riadky okolo
    blokov, zakázané \\(..\\) a \\[..\\], párovanie zátvoriek {} a \\begin/\\end.
    """
    if file_path:
        p = Path(file_path).expanduser()
        if not p.is_file():
            return f"Chyba: súbor '{file_path}' neexistuje."
        text = p.read_text(encoding="utf-8")
    if not text:
        return "Chyba: zadaj 'text' alebo 'file_path'."
    issues = _check_text(text)
    if not issues:
        return "OK – žiadne problémy s LaTeX-om nenájdené."
    return f"Nájdených problémov: {len(issues)}\n" + "\n".join(f"- {i}" for i in issues)


if __name__ == "__main__":
    mcp.run()  # stdio transport

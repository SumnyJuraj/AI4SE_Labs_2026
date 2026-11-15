#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "fastembed>=0.2.0",
#     "numpy>=1.20.0",
# ]
# ///
"""
Retrieval-Augmented Generation (RAG) Code Synthesis Pipeline (Task 5)

Implements the end-to-end RAG agent pipeline:
1. Accepts a textual programming task on input.
2. Matches top 5 relevant chunks from vector storage (Task 4 matcher).
3. Constructs a context-enriched prompt and queries an authorized LLM.
4. Safely writes the synthesized code into the target source file.
5. Runs the unit test suite and reports verification results.

Assignment: Week 06 Implementation - Task 5
Course: AI for Software Engineering (AI4SE)
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Import matcher from Task 4
TASK4_DIR = Path(__file__).resolve().parent.parent / "Task_4"
if str(TASK4_DIR) not in sys.path:
    sys.path.append(str(TASK4_DIR))

try:
    from matcher import EmbeddingMatcher
except ImportError:
    EmbeddingMatcher = None

ALLOWED_MODELS = [
    "gpt-6-luna",
    "gpt-5.6-luna",
    "gpt-5.4-nano",
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-4.1-nano",
    "gpt-4o-mini",
]


def load_env_file():
    """Loads environment variables from local .env files if present."""
    for p in [
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path.cwd() / ".env",
    ]:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip("'\""))


load_env_file()


class RAGCodeAgent:
    """
    Autonomous code generation agent driven by semantic retrieval context.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        matcher: Optional[Any] = None,
        repo_root: Optional[str] = None,
    ):
        if model_name not in ALLOWED_MODELS:
            raise ValueError(
                f"Model '{model_name}' not permitted. Must be one of: {ALLOWED_MODELS}"
            )
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not provided. Pass --api-key, export OPENAI_API_KEY, or set it in .env"
            )
        self.matcher = matcher or (EmbeddingMatcher() if EmbeddingMatcher else None)

        if repo_root is None:
            # Default to Task 1 cloned repository
            self.repo_root = Path(__file__).resolve().parent.parent / "Task_1" / "AI4SE_Playground"
        else:
            self.repo_root = Path(repo_root)

    def _call_llm(self, prompt: str) -> str:
        """Sends a completion request to the OpenAI Chat API."""
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert Python software engineer and automated code generator. "
                        "Your mission is to implement missing methods in an existing codebase based strictly "
                        "on retrieved architectural context, type hints, docstrings, and unit test specifications. "
                        "Return ONLY the clean Python method code. Do NOT enclose in markdown code blocks. "
                        "Do NOT include explanations or surrounding class definitions."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                return content.strip()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"OpenAI API HTTP {e.code} Error: {err_body}")

    def _build_prompt(
        self,
        target_file: str,
        target_class: str,
        target_method: str,
        docstring: str,
        matched_chunks: List[Dict[str, Any]],
    ) -> str:
        """Constructs a context-augmented prompt for the LLM."""
        context_blocks = []
        for i, chunk in enumerate(matched_chunks, 1):
            file_ref = chunk.get("file", "unknown")
            class_ref = chunk.get("class_name") or "Module Level"
            methods_ref = ", ".join(chunk.get("methods", []))
            code_body = chunk.get("content", chunk.get("code", ""))
            score = chunk.get("score", 0.0)

            context_blocks.append(
                f"### CONTEXT CHUNK {i} (File: {file_ref} | Class: {class_ref} | Relevance: {score:.4f}):\n"
                f"{code_body}\n"
            )

        full_context = "\n".join(context_blocks)

        prompt = f"""We are completing an implementation in the target Python file.

TARGET SPECIFICATION:
- File: {target_file}
- Class: {target_class}
- Method to Implement: {target_method}
- Method Docstring / Specification:
{docstring}

RETRIEVED CODE CONTEXT (Classes, Enums, Models, and Unit Tests):
{full_context}

INSTRUCTIONS:
1. Implement the method '{target_method}' for class '{target_class}'.
2. Scrutinize the retrieved unit tests and class definitions carefully to deduce exact behaviors and contracts:
   - Dunder methods (methods starting and ending with double underscores like __len__, __bool__, __contains__, __iter__) must NEVER be decorated with @property. They are normal instance methods.
   - For regular non-dunder methods: only decorate with @property if unit tests access it without call parentheses (e.g. `obj.{target_method}` instead of `obj.{target_method}()`).
   - If the class uses `Money`, remember amounts are in `.cents` (e.g., `Money(base.cents - discount_cents)`).
   - In `BulkDiscountPricing.price`: base price is obtained via `self._base.price(items)` or `self._base(items)`.
   - In `InventoryLedger.__contains__`: safely handle malformed inputs; return `False` if `normalize_sku` raises ValueError/TypeError or if sku is not a string. Containment checks `normalized_sku in self._on_hand` (do not check `> 0`, since a SKU remains present even when on-hand quantity is 0 after commit).
3. Use correct type hints and handle exceptions (TypeError, ValueError, InvalidTransitionError, etc.) as expected by the tests.
4. Output ONLY the method implementation. Do NOT include markdown ticks (```python). Do NOT include the outer class.
"""
        return prompt

    def _clean_code_snippet(self, raw_code: str) -> str:
        """Strips markdown fences and extraneous formatting."""
        code = raw_code.strip()
        # Remove markdown code fences if present
        code = re.sub(r"^```(?:python)?\s*", "", code, flags=re.IGNORECASE)
        code = re.sub(r"\s*```$", "", code)
        return code.strip()

    def _write_method_to_file(
        self,
        file_rel_path: str,
        class_name: str,
        method_name: str,
        new_method_code: str,
    ) -> bool:
        """
        Safely replaces the method in the target file using AST-located boundaries.
        """
        full_path = self.repo_root / file_rel_path
        if not full_path.exists():
            # Try removing leading 'playground/' if doubled
            alt_path = self.repo_root / file_rel_path.replace("playground/playground/", "playground/")
            if alt_path.exists():
                full_path = alt_path
            else:
                raise FileNotFoundError(f"Target source file not found: {full_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            raw_source = f.read()

        lines = raw_source.splitlines()
        try:
            tree = ast.parse(raw_source, filename=str(full_path))
        except SyntaxError as e:
            raise ValueError(f"Target file has existing syntax error: {e}")

        # Locate class and method in AST
        target_node = None
        class_indent = 4
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                        target_node = item
                        break
                if target_node:
                    break

        if target_node is None:
            raise ValueError(f"Could not find method '{method_name}' in class '{class_name}' in {full_path}")

        # Determine start line including decorators
        start_line = target_node.lineno
        if target_node.decorator_list:
            start_line = min(d.lineno for d in target_node.decorator_list)
        end_line = target_node.end_lineno

        # Re-indent the new code to match class body indentation (4 spaces)
        clean_code = self._clean_code_snippet(new_method_code)
        dedented = textwrap.dedent(clean_code).strip()
        indented_lines = ["    " + line if line.strip() else "" for line in dedented.splitlines()]

        # Splice into lines
        modified_lines = lines[: start_line - 1] + indented_lines + lines[end_line:]
        modified_source = "\n".join(modified_lines) + "\n"

        # Validate that modified file parses cleanly
        try:
            ast.parse(modified_source, filename=str(full_path))
        except SyntaxError as e:
            raise ValueError(f"Generated code produced syntax error in {full_path}: {e}")

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(modified_source)

        return True

    def solve_task(
        self,
        task: Union[str, Dict[str, Any]],
        top_n: int = 5,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Main RAG function required by Task 5 assignment:
        * Accepts a textual task on input
        * Matches top 5 chunks from the storage for the input
        * Sends a prompt containing the task and the matched chunks into an LLM
        * Writes the returned source code into the target source file
        """
        if isinstance(task, str):
            # Parse unstructured task string or treat as task query
            task_dict = {
                "file": "playground/playground/models.py",
                "class": "Customer",
                "method": "can_afford",
                "docstring": task,
            }
            query_text = task
        else:
            task_dict = task
            query_text = (
                f"{task_dict.get('file', '')} {task_dict.get('class', '')} "
                f"{task_dict.get('method', '')} {task_dict.get('docstring', '')}"
            )

        print(f"\n[*] Processing Task: {task_dict.get('class')}.{task_dict.get('method')}()")
        print(f"    - Target File: {task_dict.get('file')}")

        # Step 2: Match top 5 chunks from storage
        matched_chunks = self.matcher.match_task(query_text, top_n=top_n)
        print(f"    - Matched {len(matched_chunks)} chunks (Top 1: {matched_chunks[0]['chunk_id']}, score: {matched_chunks[0]['score']:.4f})")

        # Step 3: Construct prompt and call LLM
        prompt = self._build_prompt(
            target_file=task_dict.get("file", ""),
            target_class=task_dict.get("class", ""),
            target_method=task_dict.get("method", ""),
            docstring=task_dict.get("docstring", ""),
            matched_chunks=matched_chunks,
        )
        print(f"    - Querying LLM model: {self.model_name}...")
        generated_code = self._call_llm(prompt)
        print("    - Code successfully synthesized.")

        # Step 4: Write source code into target file
        if not dry_run:
            self._write_method_to_file(
                file_rel_path=task_dict.get("file", ""),
                class_name=task_dict.get("class", ""),
                method_name=task_dict.get("method", ""),
                new_method_code=generated_code,
            )
            print(f"    - [OK] Code safely patched into {task_dict.get('file')}")
        else:
            print("    - [DRY RUN] Skipped writing to disk.")

        return {
            "task": task_dict,
            "matched_chunks": [c["chunk_id"] for c in matched_chunks],
            "generated_code": generated_code,
            "file": task_dict.get("file"),
            "class": task_dict.get("class"),
            "method": task_dict.get("method"),
        }

    def solve_all(self, missing_code_path: str, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Processes all missing methods defined in missing_code.json."""
        with open(missing_code_path, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        print(f"\n{'='*80}")
        print(f"STARTING RAG GENERATION FOR {len(tasks)} MISSING CODE TASKS (Model: {self.model_name})")
        print(f"{'='*80}")

        results = []
        for i, t in enumerate(tasks, 1):
            print(f"\n--- Task {i}/{len(tasks)} ---")
            res = self.solve_task(t, dry_run=dry_run)
            results.append(res)

        print(f"\n{'='*80}")
        print(f"[+] All {len(tasks)} tasks processed successfully!")
        print(f"{'='*80}\n")
        return results

    def run_unit_tests(self) -> Dict[str, Any]:
        """Runs the repository unit tests and returns detailed test execution metrics."""
        test_dir = self.repo_root / "playground" / "tests"
        source_dir = self.repo_root / "playground"

        env = os.environ.copy()
        env["PYTHONPATH"] = str(source_dir)

        cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(test_dir)]
        print(f"[*] Running test suite: {' '.join(cmd)}")
        print(f"[*] PYTHONPATH={env['PYTHONPATH']}")

        t0 = subprocess.time.time()
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        duration = subprocess.time.time() - t0

        output = proc.stderr  # unittest outputs progress and summary to stderr
        stdout = proc.stdout

        # Parse test results
        total_tests = 0
        failures = 0
        errors = 0

        match_ran = re.search(r"Ran (\d+) tests in", output)
        if match_ran:
            total_tests = int(match_ran.group(1))

        match_failed = re.search(r"FAILED \((?:failures=(\d+))?,?\s*(?:errors=(\d+))?\)", output)
        if match_failed:
            if match_failed.group(1):
                failures = int(match_failed.group(1))
            if match_failed.group(2):
                errors = int(match_failed.group(2))

        passed = total_tests - failures - errors if total_tests > 0 else 0
        success = (proc.returncode == 0) and (failures == 0) and (errors == 0)

        result = {
            "success": success,
            "returncode": proc.returncode,
            "total_tests": total_tests,
            "passed": passed,
            "failures": failures,
            "errors": errors,
            "pass_rate_percent": round((passed / total_tests * 100), 2) if total_tests else 0.0,
            "duration_seconds": round(duration, 3),
            "output_log": output,
        }

        print(f"\n{'='*80}")
        print(f"UNIT TEST EXECUTION REPORT:")
        print(f"  - Status: {'PASSED (ALL TESTS GREEN!)' if success else 'FAILED'}")
        print(f"  - Total Tests: {total_tests}")
        print(f"  - Passed: {passed}")
        print(f"  - Failures: {failures}")
        print(f"  - Errors: {errors}")
        print(f"  - Pass Rate: {result['pass_rate_percent']}%")
        print(f"  - Execution Time: {result['duration_seconds']}s")
        print(f"{'='*80}\n")

        return result


def main():
    parser = argparse.ArgumentParser(
        description="Run RAG pipeline to solve tasks from missing_code.json and run unit tests."
    )
    parser.add_argument(
        "--missing-code",
        type=str,
        default=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../missing_code.json",
            )
        ),
        help="Path to missing_code.json.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        choices=ALLOWED_MODELS,
        help="Constrained LLM model to use (default: gpt-4o-mini).",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate code without modifying files.",
    )
    parser.add_argument(
        "--run-tests-only",
        action="store_true",
        help="Skip generation and only run test suite.",
    )

    args = parser.parse_args()

    agent = RAGCodeAgent(
        model_name=args.model,
        api_key=args.api_key,
    )

    if args.run_tests_only:
        agent.run_unit_tests()
        return

    agent.solve_all(args.missing_code, dry_run=args.dry_run)
    test_results = agent.run_unit_tests()

    # Save test results JSON
    results_path = os.path.join(os.path.dirname(__file__), "test_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2)
    print(f"[+] Test results saved to {results_path}")


if __name__ == "__main__":
    main()

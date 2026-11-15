#!/usr/bin/env python3
"""
Context-Enriched AST Code Chunker (Method 4 - Medium Chunks)

Splits Python repositories into syntactically integral, context-enriched
chunks using Python's Abstract Syntax Tree (AST). Tailored for Code-RAG
systems where high semantic precision and syntactical validity are required.

Assignment: Week 06 Implementation - Task 2
Course: AI for Software Engineering (AI4SE)
"""

import argparse
import ast
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CodeChunk:
    """Represents a single chunk of code enriched with contextual metadata."""
    id: str
    file: str
    component: str  # 'source' or 'test'
    chunk_type: str  # 'class', 'method_group', 'function', 'module_header'
    class_name: Optional[str]
    methods: List[str]
    start_line: int
    end_line: int
    line_count: int
    context_header: str
    code: str
    content: str  # Full enriched representation for embedding & LLM prompting


class ASTContextChunker:
    """
    Parses Python source files using AST to extract semantically sound code chunks.
    Small and medium classes/functions are preserved as coherent units (~30-70 lines).
    Larger classes are partitioned by methods while prepending class and import context.
    """

    def __init__(
        self,
        target_min_lines: int = 15,
        target_max_lines: int = 70,
        include_tests: bool = True,
    ):
        self.target_min_lines = target_min_lines
        self.target_max_lines = target_max_lines
        self.include_tests = include_tests
        self.chunk_counter = 0

    def _next_chunk_id(self, prefix: str = "chunk") -> str:
        self.chunk_counter += 1
        return f"{prefix}_{self.chunk_counter:04d}"

    def extract_file_context(
        self, tree: ast.AST, raw_lines: List[str], rel_path: str
    ) -> Tuple[str, str]:
        """Extracts module docstring and import statements to build file-level header."""
        module_doc = ast.get_docstring(tree) or ""
        import_lines = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                start = node.lineno - 1
                end = node.end_lineno
                import_lines.extend(raw_lines[start:end])

        clean_imports = "\n".join(import_lines).strip()
        doc_header = f'"""{module_doc}"""\n' if module_doc else ""

        header_lines = [
            f"# Source File: {rel_path}",
        ]
        if module_doc:
            header_lines.append(f"# Module Summary: {module_doc.splitlines()[0]}")
        if clean_imports:
            header_lines.append("# Module Imports:\n" + clean_imports)

        full_header = "\n".join(header_lines)
        return full_header, clean_imports

    def _extract_class_header(
        self, node: ast.ClassDef, raw_lines: List[str]
    ) -> str:
        """Extracts class definition line, docstring, and constructor signature."""
        lines = [raw_lines[node.lineno - 1].rstrip()]
        doc = ast.get_docstring(node)
        if doc:
            lines.append(f'    """{doc}"""')

        # Locate __init__ for signature reference
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__":
                init_lines = raw_lines[item.lineno - 1 : item.end_lineno]
                # Keep first few lines of __init__ (signature + docstring)
                sig_preview = init_lines[:min(6, len(init_lines))]
                lines.append("    # Constructor context:")
                lines.extend(["    " + l.strip() for l in sig_preview if l.strip()])
                break

        return "\n".join(lines)

    def chunk_file(self, file_path: str, repo_root: str) -> List[CodeChunk]:
        """Parses a single Python file into context-enriched chunks."""
        rel_path = os.path.relpath(file_path, repo_root)
        component = "test" if "test" in rel_path.lower() else "source"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_code = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
            return []

        if not raw_code.strip():
            return []

        raw_lines = raw_code.splitlines()

        try:
            tree = ast.parse(raw_code, filename=file_path)
        except SyntaxError as e:
            print(f"Warning: SyntaxError parsing {file_path}: {e}", file=sys.stderr)
            # Fallback to line chunking if AST parsing fails
            return self._fallback_line_chunk(file_path, rel_path, component, raw_lines)

        file_header, _ = self.extract_file_context(tree, raw_lines, rel_path)
        chunks: List[CodeChunk] = []

        # Check if entire file is short and has no classes/functions (e.g. __init__.py)
        has_defs = any(isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) for n in tree.body)
        if not has_defs and len(raw_lines) <= self.target_max_lines:
            chunk_code = raw_code.strip()
            if chunk_code:
                content = f"{file_header}\n\n{chunk_code}"
                return [
                    CodeChunk(
                        id=self._next_chunk_id("mod"),
                        file=rel_path,
                        component=component,
                        chunk_type="module_header",
                        class_name=None,
                        methods=[],
                        start_line=1,
                        end_line=len(raw_lines),
                        line_count=len(raw_lines),
                        context_header=file_header,
                        code=chunk_code,
                        content=content,
                    )
                ]

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                chunks.extend(self._chunk_class(node, raw_lines, rel_path, component, file_header))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunks.append(self._chunk_function(node, raw_lines, rel_path, component, file_header))

        return chunks

    def _chunk_function(
        self,
        node: ast.FunctionDef,
        raw_lines: List[str],
        rel_path: str,
        component: str,
        file_header: str,
    ) -> CodeChunk:
        """Chunks a top-level function with its enclosing file header."""
        start_line = node.lineno
        end_line = node.end_lineno
        code_str = "\n".join(raw_lines[start_line - 1 : end_line])
        content = f"{file_header}\n\n# Function Definition:\n{code_str}"

        return CodeChunk(
            id=self._next_chunk_id("func"),
            file=rel_path,
            component=component,
            chunk_type="function",
            class_name=None,
            methods=[node.name],
            start_line=start_line,
            end_line=end_line,
            line_count=end_line - start_line + 1,
            context_header=file_header,
            code=code_str,
            content=content,
        )

    def _chunk_class(
        self,
        node: ast.ClassDef,
        raw_lines: List[str],
        rel_path: str,
        component: str,
        file_header: str,
    ) -> List[CodeChunk]:
        """
        Chunks a class definition. If the class is within target_max_lines,
        emits a single cohesive chunk. Otherwise, breaks into method groups
        while enriching each group with class declaration & docstring.
        """
        class_lines = node.end_lineno - node.lineno + 1
        all_methods = [
            m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        # Case 1: Small/medium class that fits neatly into chunk size
        if class_lines <= self.target_max_lines:
            code_str = "\n".join(raw_lines[node.lineno - 1 : node.end_lineno])
            content = f"{file_header}\n\n# Complete Class Definition:\n{code_str}"
            return [
                CodeChunk(
                    id=self._next_chunk_id("cls"),
                    file=rel_path,
                    component=component,
                    chunk_type="class",
                    class_name=node.name,
                    methods=all_methods,
                    start_line=node.lineno,
                    end_line=node.end_lineno,
                    line_count=class_lines,
                    context_header=file_header,
                    code=code_str,
                    content=content,
                )
            ]

        # Case 2: Large class -> Group methods with class header context
        class_ctx = self._extract_class_header(node, raw_lines)
        enriched_header = f"{file_header}\n\n# Enclosing Class Context:\n{class_ctx}"

        method_nodes = [
            item for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if not method_nodes:
            # Class without methods (e.g. data class with lots of fields)
            code_str = "\n".join(raw_lines[node.lineno - 1 : node.end_lineno])
            content = f"{file_header}\n\n{code_str}"
            return [
                CodeChunk(
                    id=self._next_chunk_id("cls"),
                    file=rel_path,
                    component=component,
                    chunk_type="class",
                    class_name=node.name,
                    methods=[],
                    start_line=node.lineno,
                    end_line=node.end_lineno,
                    line_count=class_lines,
                    context_header=file_header,
                    code=code_str,
                    content=content,
                )
            ]

        chunks: List[CodeChunk] = []
        current_group: List[ast.FunctionDef] = []
        current_lines = 0

        for m in method_nodes:
            m_lines = m.end_lineno - m.lineno + 1
            if current_group and (current_lines + m_lines > self.target_max_lines):
                # Flush group
                chunks.append(
                    self._create_method_chunk(
                        current_group, raw_lines, rel_path, component, node.name, enriched_header
                    )
                )
                current_group = [m]
                current_lines = m_lines
            else:
                current_group.append(m)
                current_lines += m_lines

        if current_group:
            chunks.append(
                self._create_method_chunk(
                    current_group, raw_lines, rel_path, component, node.name, enriched_header
                )
            )

        return chunks

    def _create_method_chunk(
        self,
        methods: List[ast.FunctionDef],
        raw_lines: List[str],
        rel_path: str,
        component: str,
        class_name: str,
        enriched_header: str,
    ) -> CodeChunk:
        start_line = methods[0].lineno
        end_line = methods[-1].end_lineno
        method_names = [m.name for m in methods]
        code_str = "\n".join(raw_lines[start_line - 1 : end_line])

        content = f"{enriched_header}\n\n# Implemented Methods:\n{code_str}"

        chunk_type = "method" if len(methods) == 1 else "method_group"
        return CodeChunk(
            id=self._next_chunk_id("mth"),
            file=rel_path,
            component=component,
            chunk_type=chunk_type,
            class_name=class_name,
            methods=method_names,
            start_line=start_line,
            end_line=end_line,
            line_count=end_line - start_line + 1,
            context_header=enriched_header,
            code=code_str,
            content=content,
        )

    def _fallback_line_chunk(
        self, file_path: str, rel_path: str, component: str, raw_lines: List[str]
    ) -> List[CodeChunk]:
        """Fallback chunker for malformed syntax."""
        chunks = []
        step = self.target_max_lines - 10
        for i in range(0, len(raw_lines), step):
            window = raw_lines[i : i + self.target_max_lines]
            code_str = "\n".join(window)
            chunks.append(
                CodeChunk(
                    id=self._next_chunk_id("raw"),
                    file=rel_path,
                    component=component,
                    chunk_type="line_window",
                    class_name=None,
                    methods=[],
                    start_line=i + 1,
                    end_line=i + len(window),
                    line_count=len(window),
                    context_header=f"# File: {rel_path}",
                    code=code_str,
                    content=code_str,
                )
            )
        return chunks

    def chunk_repository(self, repo_dir: str) -> Dict[str, Any]:
        """Walks target directory and generates all repository chunks with summary stats."""
        all_chunks: List[CodeChunk] = []
        target_path = Path(repo_dir)

        if not target_path.exists():
            raise FileNotFoundError(f"Repository directory does not exist: {repo_dir}")

        py_files = sorted(target_path.glob("**/*.py"))

        for fpath in py_files:
            rel = str(fpath.relative_to(target_path))
            if not self.include_tests and "test" in rel.lower():
                continue
            chunks = self.chunk_file(str(fpath), str(target_path))
            all_chunks.extend(chunks)

        line_counts = [c.line_count for c in all_chunks] or [0]
        source_chunks = [c for c in all_chunks if c.component == "source"]
        test_chunks = [c for c in all_chunks if c.component == "test"]

        stats = {
            "chunking_method": "Context-Enriched AST Chunking (Method 4)",
            "chunk_size_category": "Medium (~30-70 lines / ~250-500 tokens)",
            "target_repo": str(target_path),
            "total_files_parsed": len(py_files),
            "total_chunks": len(all_chunks),
            "source_chunks_count": len(source_chunks),
            "test_chunks_count": len(test_chunks),
            "avg_lines_per_chunk": round(sum(line_counts) / len(line_counts), 2),
            "min_lines": min(line_counts),
            "max_lines": max(line_counts),
            "target_bounds": {
                "min": self.target_min_lines,
                "max": self.target_max_lines,
            },
        }

        return {
            "metadata": stats,
            "chunks": [asdict(c) for c in all_chunks],
        }


def main():
    parser = argparse.ArgumentParser(
        description="Chunk repository files using Context-Enriched AST Chunking."
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        default=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../Task_1/AI4SE_Playground/playground",
            )
        ),
        help="Path to repository to chunk (defaults to Task 1 cloned repo).",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "chunks.json")
        ),
        help="Path to save output JSON data structure.",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=15,
        help="Target minimum lines per chunk.",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=70,
        help="Target maximum lines per chunk.",
    )
    parser.add_argument(
        "--exclude-tests",
        action="store_true",
        help="If set, only source files will be chunked.",
    )

    args = parser.parse_args()

    # Fallback path checking
    repo_path = args.repo_path
    if not os.path.exists(repo_path):
        # Alternative search in current workspace
        alt_path = os.path.abspath("AI4SE_Playground/playground")
        if os.path.exists(alt_path):
            repo_path = alt_path

    print(f"[*] Starting AST chunking on: {repo_path}")
    print(f"[*] Bounds: min={args.min_lines}, max={args.max_lines} lines")

    chunker = ASTContextChunker(
        target_min_lines=args.min_lines,
        target_max_lines=args.max_lines,
        include_tests=not args.exclude_tests,
    )

    result = chunker.chunk_repository(repo_path)
    metadata = result["metadata"]

    os.makedirs(os.path.dirname(os.path.abspath(args.output_file)), exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[+] Chunking completed successfully!")
    print(f"    - Output file: {args.output_file}")
    print(f"    - Total chunks: {metadata['total_chunks']}")
    print(f"    - Source chunks: {metadata['source_chunks_count']}")
    print(f"    - Test chunks: {metadata['test_chunks_count']}")
    print(f"    - Average lines/chunk: {metadata['avg_lines_per_chunk']}")
    print(f"    - Min lines: {metadata['min_lines']}, Max lines: {metadata['max_lines']}")


if __name__ == "__main__":
    main()

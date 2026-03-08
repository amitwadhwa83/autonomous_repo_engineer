"""Task generation agent that discovers improvements from repository analysis."""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

CONTROL_NODES = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match)


class TaskGenerator:
    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or Path.cwd()).resolve()

    def scan_repository(self) -> tuple[list[dict], dict[str, list[str]]]:
        python_files = self._python_files()
        findings: list[dict] = []

        for file_path in python_files:
            relative = str(file_path.relative_to(self.repo_root))
            source = file_path.read_text(encoding="utf-8", errors="ignore")
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue

            long_functions = self._find_long_functions(tree, threshold=80)
            if long_functions:
                findings.append(
                    {
                        "kind": "long_functions",
                        "task_type": "refactor",
                        "description": (
                            f"Refactor long functions in {relative}: "
                            + ", ".join(f"{name} ({size} lines)" for name, size in long_functions)
                        ),
                        "target_files": [relative],
                        "priority": 4,
                    }
                )

            missing_docstrings = self._missing_docstrings(tree)
            if missing_docstrings:
                findings.append(
                    {
                        "kind": "missing_docstrings",
                        "task_type": "documentation",
                        "description": (
                            f"Add missing docstrings in {relative} for: "
                            + ", ".join(missing_docstrings)
                        ),
                        "target_files": [relative],
                        "priority": 3,
                    }
                )

            unused_imports = self._unused_imports(tree)
            if unused_imports:
                findings.append(
                    {
                        "kind": "unused_imports",
                        "task_type": "refactor",
                        "description": (
                            f"Remove unused imports in {relative}: " + ", ".join(unused_imports)
                        ),
                        "target_files": [relative],
                        "priority": 3,
                    }
                )

            complex_functions = self._complex_functions(tree)
            if complex_functions:
                findings.append(
                    {
                        "kind": "complex_functions",
                        "task_type": "optimization",
                        "description": (
                            f"Reduce control-flow complexity in {relative}: "
                            + ", ".join(complex_functions)
                        ),
                        "target_files": [relative],
                        "priority": 5,
                    }
                )

        duplicate_targets = self._duplicate_blocks(python_files)
        if duplicate_targets:
            findings.append(
                {
                    "kind": "duplicate_code",
                    "task_type": "refactor",
                    "description": (
                        "Extract duplicated code blocks shared across: "
                        + ", ".join(sorted(duplicate_targets))
                    ),
                    "target_files": sorted(duplicate_targets),
                    "priority": 4,
                }
            )

        files_without_tests = self._files_without_tests(python_files)
        for relative in files_without_tests:
            findings.append(
                {
                    "kind": "missing_tests",
                    "task_type": "testing",
                    "description": f"Add unit tests for {relative}.",
                    "target_files": [relative],
                    "priority": 4,
                }
            )

        grouped: dict[str, list[str]] = defaultdict(list)
        for finding in findings:
            grouped[finding["task_type"]].append(finding["description"])

        return findings, dict(grouped)

    def findings_to_tasks(self, findings: list[dict], start_index: int = 1) -> list[dict]:
        tasks: list[dict] = []
        for idx, finding in enumerate(findings, start=start_index):
            tasks.append(
                {
                    "task_id": f"TASK-{idx:04d}",
                    "task_type": finding["task_type"],
                    "description": finding["description"],
                    "target_files": finding["target_files"],
                    "priority": int(min(max(finding["priority"], 1), 5)),
                }
            )
        return tasks

    def _python_files(self) -> list[Path]:
        excluded = {".git", ".idea", "__pycache__", ".venv", "venv", "backlog", ".pytest_cache"}
        files: list[Path] = []
        for path in self.repo_root.rglob("*.py"):
            if any(part in excluded for part in path.parts):
                continue
            files.append(path)
        return sorted(files)

    def _find_long_functions(self, tree: ast.Module, threshold: int) -> list[tuple[str, int]]:
        items: list[tuple[str, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and hasattr(node, "end_lineno"):
                length = (node.end_lineno or node.lineno) - node.lineno + 1
                if length > threshold:
                    items.append((node.name, length))
        return items

    def _missing_docstrings(self, tree: ast.Module) -> list[str]:
        missing: list[str] = []
        if ast.get_docstring(tree) is None:
            missing.append("module")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(node) is None:
                    missing.append(node.name)
        return missing

    def _unused_imports(self, tree: ast.Module) -> list[str]:
        imported: set[str] = set()
        used: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != "*":
                        imported.add(alias.asname or alias.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)

        return sorted(imported - used)

    def _complex_functions(self, tree: ast.Module) -> list[str]:
        complex_names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                controls = self._count_control_nodes(node)
                depth = self._max_nested_depth(node)
                if controls >= 12 or depth >= 4:
                    complex_names.append(f"{node.name} (controls={controls}, depth={depth})")
        return complex_names

    def _count_control_nodes(self, node: ast.AST) -> int:
        return sum(1 for child in ast.walk(node) if isinstance(child, CONTROL_NODES))

    def _max_nested_depth(self, node: ast.AST) -> int:
        max_depth = 0

        def walk(current: ast.AST, depth: int) -> None:
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            for child in ast.iter_child_nodes(current):
                if isinstance(child, CONTROL_NODES):
                    walk(child, depth + 1)
                else:
                    walk(child, depth)

        walk(node, 0)
        return max_depth

    def _duplicate_blocks(self, files: list[Path], block_size: int = 6) -> set[str]:
        block_map: dict[str, set[str]] = defaultdict(set)
        for file_path in files:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for idx in range(0, len(lines) - block_size + 1):
                block = "\n".join(line.strip() for line in lines[idx : idx + block_size])
                if block.strip():
                    relative = str(file_path.relative_to(self.repo_root))
                    block_map[block].add(relative)

        duplicates: set[str] = set()
        for locations in block_map.values():
            if len(locations) > 1:
                duplicates.update(locations)
        return duplicates

    def _files_without_tests(self, python_files: list[Path]) -> list[str]:
        test_files = {
            str(path.relative_to(self.repo_root)).replace('\\', '/')
            for path in self.repo_root.rglob("test_*.py")
            if path.is_file()
        }

        missing: list[str] = []
        for path in python_files:
            relative = str(path.relative_to(self.repo_root)).replace('\\', '/')
            if relative.startswith("tests/"):
                continue
            stem = path.stem
            candidates = {
                f"tests/test_{stem}.py",
                f"tests/{stem}_test.py",
            }
            if not any(candidate in test_files for candidate in candidates):
                missing.append(str(path.relative_to(self.repo_root)))

        return sorted(missing)

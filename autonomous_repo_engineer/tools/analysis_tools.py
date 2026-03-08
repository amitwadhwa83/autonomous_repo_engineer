"""Code analysis utilities."""

import ast
from collections import defaultdict
from pathlib import Path


def find_unused_imports(tree: ast.AST) -> list[dict]:
    imported: dict[str, int] = {}
    used: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported[name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                name = alias.asname or alias.name
                imported[name] = node.lineno
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used.add(node.id)

    return [
        {
            "type": "unused_import",
            "line": line,
            "message": f"Imported symbol '{name}' appears unused.",
        }
        for name, line in imported.items()
        if name not in used
    ]


def find_missing_docstrings(tree: ast.Module) -> list[dict]:
    issues: list[dict] = []

    if ast.get_docstring(tree) is None:
        issues.append(
            {
                "type": "missing_docstring",
                "line": 1,
                "message": "Module docstring is missing.",
            }
        )

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node) is None:
                issues.append(
                    {
                        "type": "missing_docstring",
                        "line": node.lineno,
                        "message": f"{node.__class__.__name__} '{node.name}' is missing a docstring.",
                    }
                )

    return issues


def find_long_functions(tree: ast.Module, max_lines: int = 50) -> list[dict]:
    issues: list[dict] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and hasattr(node, "end_lineno"):
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            if length > max_lines:
                issues.append(
                    {
                        "type": "long_function",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' is {length} lines long (>{max_lines}).",
                    }
                )

    return issues


def find_duplicate_blocks(paths: list[Path], block_size: int = 6) -> list[dict]:
    block_map: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for path in paths:
        content = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for idx in range(0, len(content) - block_size + 1):
            raw_block = content[idx : idx + block_size]
            normalized = "\n".join(line.strip() for line in raw_block)
            if normalized.strip():
                block_map[normalized].append((str(path), idx + 1))

    issues: list[dict] = []
    for block, locations in block_map.items():
        if len(locations) > 1:
            files = sorted({Path(location[0]).name for location in locations})
            issues.append(
                {
                    "type": "duplicate_code",
                    "line": locations[0][1],
                    "message": (
                        "Potential duplicate code block detected in "
                        f"{len(locations)} locations across files: {', '.join(files)}."
                    ),
                }
            )

    return issues

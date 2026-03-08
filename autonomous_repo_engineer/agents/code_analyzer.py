"""Code analyzer agent."""

import ast
import logging
from pathlib import Path

from autonomous_repo_engineer.tools.analysis_tools import (
    find_duplicate_blocks,
    find_long_functions,
    find_missing_docstrings,
    find_unused_imports,
)


class CodeAnalyzer:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_files(self, python_file_paths: list[Path], repo_path: Path) -> list[dict]:
        issues: list[dict] = []

        for file_path in python_file_paths:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)
            except SyntaxError as exc:
                relative = str(file_path.relative_to(repo_path))
                issues.append(
                    {
                        "file": relative,
                        "type": "parse_error",
                        "line": exc.lineno or 1,
                        "message": f"Failed to parse file: {exc.msg}",
                    }
                )
                continue
            except OSError as exc:
                relative = str(file_path.relative_to(repo_path))
                issues.append(
                    {
                        "file": relative,
                        "type": "read_error",
                        "line": 1,
                        "message": f"Could not read file: {exc}",
                    }
                )
                continue

            relative = str(file_path.relative_to(repo_path))
            file_issues = []
            file_issues.extend(find_unused_imports(tree))
            file_issues.extend(find_missing_docstrings(tree))
            file_issues.extend(find_long_functions(tree))

            for issue in file_issues:
                issue["file"] = relative
                issues.append(issue)

        for issue in find_duplicate_blocks(python_file_paths):
            issues.append(issue)

        return issues

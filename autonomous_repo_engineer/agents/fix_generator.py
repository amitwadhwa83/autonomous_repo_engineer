"""Fix suggestion generation agent."""

import logging


class FixGenerator:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate(self, issues: list[dict]) -> list[str]:
        if not issues:
            return ["No major issues detected. Consider adding CI checks to keep quality high."]

        issue_types = {issue.get("type") for issue in issues}
        suggestions: list[str] = []

        if "unused_import" in issue_types:
            suggestions.append("Remove unused imports and run a linter such as Ruff or Flake8 in CI.")
        if "missing_docstring" in issue_types:
            suggestions.append("Add module/class/function docstrings to clarify intent and improve maintainability.")
        if "long_function" in issue_types:
            suggestions.append("Split long functions into smaller single-purpose helpers to improve readability and testability.")
        if "duplicate_code" in issue_types:
            suggestions.append("Extract repeated code blocks into shared utility functions to reduce duplication.")
        if "parse_error" in issue_types:
            suggestions.append("Fix syntax errors before running static analysis to get complete issue coverage.")

        suggestions.append("Add pre-commit checks for formatting, linting, and static analysis.")
        return suggestions

import textwrap
from pathlib import Path

from autonomous_repo_engineer.agents.code_analyzer import CodeAnalyzer


def test_code_analyzer_detects_expected_issues(tmp_path: Path) -> None:
    sample = textwrap.dedent(
        '''
        import os
        import math

        def long_fn():
            total = 0
        '''
    )

    # Build function body over 50 lines.
    for i in range(55):
        sample += f"    total += {i}\n"
    sample += "    return total\n"

    file_one = tmp_path / "a.py"
    file_two = tmp_path / "b.py"
    duplicate_block = "\n".join(["x = 1", "y = 2", "z = x + y", "print(z)", "x += 1", "print(x)"])

    file_one.write_text(sample + "\n" + duplicate_block, encoding="utf-8")
    file_two.write_text("\n" + duplicate_block, encoding="utf-8")

    analyzer = CodeAnalyzer()
    issues = analyzer.analyze_files([file_one, file_two], tmp_path)
    issue_types = {issue["type"] for issue in issues}

    assert "unused_import" in issue_types
    assert "missing_docstring" in issue_types
    assert "long_function" in issue_types
    assert "duplicate_code" in issue_types

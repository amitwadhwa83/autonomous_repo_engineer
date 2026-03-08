from pathlib import Path

from autonomous_repo_engineer.agents.task_generator import TaskGenerator


def test_task_generator_creates_tasks(tmp_path: Path) -> None:
    src = tmp_path / "sample.py"
    src.write_text(
        "import os\n"
        "\n"
        "def target():\n"
        "    value = 0\n"
        + "".join("    value += 1\n" for _ in range(90))
        + "    return value\n",
        encoding="utf-8",
    )

    generator = TaskGenerator(repo_root=tmp_path)
    findings, grouped = generator.scan_repository()
    tasks = generator.findings_to_tasks(findings)

    assert tasks
    assert any(task["task_type"] == "refactor" for task in tasks)
    assert isinstance(grouped, dict)
    assert tasks[0]["task_id"].startswith("TASK-")

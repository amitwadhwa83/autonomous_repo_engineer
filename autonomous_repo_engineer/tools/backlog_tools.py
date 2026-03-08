"""Backlog task persistence utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_BACKLOG_PATH = Path("backlog") / "tasks.json"


def ensure_backlog(path: Path = DEFAULT_BACKLOG_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    return path


def load_tasks(path: Path = DEFAULT_BACKLOG_PATH) -> list[dict[str, Any]]:
    backlog_path = ensure_backlog(path)
    try:
        data = json.loads(backlog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []


def save_tasks(tasks: list[dict[str, Any]], path: Path = DEFAULT_BACKLOG_PATH) -> None:
    backlog_path = ensure_backlog(path)
    backlog_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def pop_next_task(path: Path = DEFAULT_BACKLOG_PATH) -> dict[str, Any] | None:
    tasks = load_tasks(path)
    if not tasks:
        return None
    task = tasks.pop(0)
    save_tasks(tasks, path)
    return task


def append_tasks(new_tasks: list[dict[str, Any]], path: Path = DEFAULT_BACKLOG_PATH) -> None:
    tasks = load_tasks(path)
    tasks.extend(new_tasks)
    save_tasks(tasks, path)

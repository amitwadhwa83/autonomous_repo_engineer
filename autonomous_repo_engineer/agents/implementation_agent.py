"""Task execution agent.

This class is intentionally simple and can be replaced by a richer implementation
without changing the orchestration flow in agent.py.
"""

from __future__ import annotations

from typing import Any


class ImplementationAgent:
    def execute_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute one backlog task.

        Returns a result dict with keys:
        - status: completed | failed
        - message: execution note
        - modified_files: list of touched files
        """
        task_type = task.get("task_type", "unknown")
        description = task.get("description", "")
        target_files = task.get("target_files", [])

        return {
            "status": "completed",
            "message": f"Executed {task_type} task: {description}",
            "modified_files": target_files,
        }

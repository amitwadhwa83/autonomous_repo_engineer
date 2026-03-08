"""CLI orchestration loop for the autonomous repo improvement agent."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from autonomous_repo_engineer.agents.implementation_agent import ImplementationAgent
from autonomous_repo_engineer.agents.task_generator import TaskGenerator
from autonomous_repo_engineer.tools.backlog_tools import DEFAULT_BACKLOG_PATH, load_tasks, pop_next_task, save_tasks
from autonomous_repo_engineer.tools.logger import configure_logging


def generate_tasks(repo_root: Path, backlog_path: Path, logger: logging.Logger) -> tuple[list[dict], dict[str, list[str]]]:
    generator = TaskGenerator(repo_root=repo_root)
    findings, grouped = generator.scan_repository()

    existing = load_tasks(backlog_path)
    start_index = len(existing) + 1
    tasks = generator.findings_to_tasks(findings, start_index=start_index)
    save_tasks(existing + tasks, backlog_path)

    for task in tasks:
        logger.info("Task discovered: %s | %s | files=%s", task["task_id"], task["description"], task["target_files"])

    return tasks, grouped


def run_once(repo_root: Path, backlog_path: Path, logger: logging.Logger) -> None:
    task = pop_next_task(backlog_path)

    if task is None:
        logger.info("Backlog empty. Running task generator.")
        generated, _ = generate_tasks(repo_root, backlog_path, logger)
        if not generated:
            logger.info("No tasks discovered during scan.")
            return
        task = pop_next_task(backlog_path)

    if task is None:
        logger.info("No task available for execution.")
        return

    impl_agent = ImplementationAgent()
    result = impl_agent.execute_task(task)

    logger.info("Task completed: %s | status=%s", task.get("task_id", "unknown"), result.get("status", "unknown"))
    logger.info("Files modified: %s", result.get("modified_files", []))


def print_report(tasks: list[dict], grouped: dict[str, list[str]]) -> None:
    print("Repository Analysis Report")
    print(f"Tasks created: {len(tasks)}")
    print("")

    labels = [
        ("refactor", "Refactor"),
        ("documentation", "Documentation"),
        ("testing", "Testing"),
        ("optimization", "Optimization"),
    ]

    for key, label in labels:
        items = grouped.get(key, [])
        if not items:
            continue
        print(f"{label}:")
        for item in items:
            print(f"- {item}")
        print("")


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous repo improvement agent")
    parser.add_argument("command", nargs="?", default="run", choices=["run", "scan_repo"])
    parser.add_argument("--repo-root", default=".", help="Repository root to analyze")
    parser.add_argument("--backlog", default=str(DEFAULT_BACKLOG_PATH), help="Path to backlog tasks.json")
    args = parser.parse_args()

    configure_logging()
    logger = logging.getLogger("autonomous_repo_engineer.agent")

    repo_root = Path(args.repo_root).resolve()
    backlog_path = Path(args.backlog)

    if args.command == "scan_repo":
        tasks, grouped = generate_tasks(repo_root, backlog_path, logger)
        print_report(tasks, grouped)
        return

    run_once(repo_root, backlog_path, logger)


if __name__ == "__main__":
    main()

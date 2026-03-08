"""Repository loading agent."""

from dataclasses import dataclass
import logging
from pathlib import Path

from autonomous_repo_engineer.tools.file_tools import list_all_files, python_files, summarize_architecture
from autonomous_repo_engineer.tools.git_tools import clone_repository


@dataclass
class RepoData:
    repo_path: Path
    files: list[str]
    python_file_paths: list[Path]
    architecture_summary: str


class RepoReader:
    def __init__(self, workspace_dir: Path | None = None) -> None:
        self.workspace_dir = workspace_dir or Path(".repo_workspace")
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_repository(self, repo_url: str) -> RepoData:
        self.logger.info("Cloning repository: %s", repo_url)
        repo_path = clone_repository(repo_url=repo_url, base_dir=self.workspace_dir)

        self.logger.info("Listing files in repository")
        files = list_all_files(repo_path)
        py_files = python_files(repo_path)
        architecture_summary = summarize_architecture(repo_path, files)

        return RepoData(
            repo_path=repo_path,
            files=files,
            python_file_paths=py_files,
            architecture_summary=architecture_summary,
        )

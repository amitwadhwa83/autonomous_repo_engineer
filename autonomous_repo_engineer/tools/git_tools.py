"""Git operations for repository cloning."""

from pathlib import Path
import shutil
import subprocess
import uuid


class GitCloneError(RuntimeError):
    pass


def clone_repository(repo_url: str, base_dir: Path) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    destination = base_dir / f"repo_{uuid.uuid4().hex[:8]}"

    cmd = ["git", "clone", "--depth", "1", repo_url, str(destination)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        shutil.rmtree(destination, ignore_errors=True)
        raise GitCloneError(result.stderr.strip() or "Failed to clone repository")

    return destination

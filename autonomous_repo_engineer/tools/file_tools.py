"""File and repository structure utilities."""

from pathlib import Path


def list_all_files(repo_path: Path) -> list[str]:
    files: list[str] = []
    for path in repo_path.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            files.append(str(path.relative_to(repo_path)))
    return sorted(files)


def python_files(repo_path: Path) -> list[Path]:
    return sorted(
        [
            path
            for path in repo_path.rglob("*.py")
            if path.is_file() and ".git" not in path.parts
        ]
    )


def summarize_architecture(repo_path: Path, files: list[str]) -> str:
    directories = sorted({str(Path(f).parent) for f in files if Path(f).parent != Path(".")})
    top_level = sorted({Path(f).parts[0] for f in files if Path(f).parts})
    return (
        f"Repository contains {len(files)} files. "
        f"Top-level components: {', '.join(top_level) if top_level else 'none'}. "
        f"Detected {len(directories)} directories with source/assets."
    )

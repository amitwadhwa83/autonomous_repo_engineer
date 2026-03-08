"""FastAPI entrypoint for repository analysis."""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException

# Support running this file directly (e.g., PyCharm "Run file").
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from autonomous_repo_engineer.agents.code_analyzer import CodeAnalyzer
from autonomous_repo_engineer.agents.fix_generator import FixGenerator
from autonomous_repo_engineer.agents.repo_reader import RepoReader
from autonomous_repo_engineer.api.schemas import AnalyzeRepoRequest, AnalyzeRepoResponse
from autonomous_repo_engineer.tools.git_tools import GitCloneError
from autonomous_repo_engineer.tools.logger import configure_logging

configure_logging()
logger = logging.getLogger("autonomous_repo_engineer")

app = FastAPI(title="Autonomous GitHub Repo Engineer Agent", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Autonomous GitHub Repo Engineer Agent",
        "status": "ok",
        "docs": "/docs",
        "analyze_endpoint": "/analyze_repo",
    }


@app.post("/analyze_repo", response_model=AnalyzeRepoResponse)
def analyze_repo(request: AnalyzeRepoRequest) -> AnalyzeRepoResponse:
    repo_reader = RepoReader()
    analyzer = CodeAnalyzer()
    fix_generator = FixGenerator()

    try:
        repo_data = repo_reader.load_repository(str(request.repo_url))
        issues = analyzer.analyze_files(repo_data.python_file_paths, repo_data.repo_path)
        suggestions = fix_generator.generate(issues)
        file_listing = ", ".join(repo_data.files) if repo_data.files else "No files found"

        summary = (
            f"{repo_data.architecture_summary} "
            f"Files: {file_listing}. "
            f"Scanned {len(repo_data.python_file_paths)} Python files and found {len(issues)} issues."
        )

        return AnalyzeRepoResponse(summary=summary, issues=issues, suggestions=suggestions)
    except GitCloneError as exc:
        logger.exception("Repository clone failed")
        raise HTTPException(status_code=400, detail=f"Clone failed: {exc}") from exc
    except Exception as exc:  # pragma: no cover
        logger.exception("Unexpected analysis error")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("autonomous_repo_engineer.main:app", host="127.0.0.1", port=8000, reload=True)

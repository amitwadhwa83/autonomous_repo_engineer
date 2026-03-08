from pathlib import Path

from fastapi.testclient import TestClient

from autonomous_repo_engineer.main import app
from autonomous_repo_engineer.agents.repo_reader import RepoData


def test_analyze_repo_endpoint(monkeypatch, tmp_path: Path) -> None:
    def fake_load_repository(self, repo_url: str) -> RepoData:  # noqa: ARG001
        file_path = tmp_path / "sample.py"
        file_path.write_text("import os\n", encoding="utf-8")
        return RepoData(
            repo_path=tmp_path,
            files=["sample.py"],
            python_file_paths=[file_path],
            architecture_summary="Repository contains 1 files.",
        )

    monkeypatch.setattr("autonomous_repo_engineer.agents.repo_reader.RepoReader.load_repository", fake_load_repository)

    client = TestClient(app)
    response = client.post("/analyze_repo", json={"repo_url": "https://github.com/example/repo"})

    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert isinstance(body["issues"], list)
    assert isinstance(body["suggestions"], list)

"""API schema models."""

from pydantic import BaseModel, HttpUrl


class AnalyzeRepoRequest(BaseModel):
    repo_url: HttpUrl


class AnalyzeRepoResponse(BaseModel):
    summary: str
    issues: list[dict]
    suggestions: list[str]

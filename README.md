# Autonomous GitHub Repo Engineer Agent

A modular Python project that clones/analyzes repositories and can autonomously generate improvement tasks.

## Features

- Accepts a GitHub repository URL (FastAPI endpoint)
- Clones repository locally
- Analyzes repository structure and lists files
- Reads Python files and detects:
  - unused imports
  - missing docstrings
  - long functions (>50 lines in API analysis)
  - duplicate code blocks
- Generates improvement suggestions
- Produces architecture summary
- Exposes FastAPI endpoint: `POST /analyze_repo`
- Includes logging, error handling, example usage, and unit tests
- Autonomous backlog workflow:
  - Generates tasks from repository analysis
  - Stores tasks in `backlog/tasks.json`
  - Executes next task from backlog

## Project Structure

```text
autonomous_repo_engineer/
  agents/
    repo_reader.py
    code_analyzer.py
    fix_generator.py
    task_generator.py
    implementation_agent.py
  tools/
    git_tools.py
    file_tools.py
    analysis_tools.py
    backlog_tools.py
    logger.py
  api/
    schemas.py
  main.py
agent.py
backlog/tasks.json
tests/
examples/
```

## API

### Endpoint

`POST /analyze_repo`

### Input

```json
{
  "repo_url": "https://github.com/<owner>/<repo>"
}
```

### Output

```json
{
  "summary": "...",
  "issues": [],
  "suggestions": []
}
```

## Setup

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
pip install -e .
```

## Run API Server

```bash
python run_server.py
```

## Autonomous Agent CLI

### Generate tasks only

```bash
python agent.py scan_repo
```

Example output:

```text
Repository Analysis Report
Tasks created: 7

Refactor:
- utils.py contains long functions

Documentation:
- api_service.py missing docstrings

Testing:
- auth module missing tests
```

### Run one loop iteration

```bash
python agent.py
```

Workflow:

- If backlog is empty: run task generator and create tasks
- Else: execute next task from backlog

Task schema in `backlog/tasks.json`:

```json
{
  "task_id": "TASK-0001",
  "task_type": "refactor",
  "description": "...",
  "target_files": ["path/to/file.py"],
  "priority": 4
}
```

## Logging

The agent logs:

- tasks discovered
- tasks completed
- files modified

## Run Tests

```bash
pytest -q
```

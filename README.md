# Autonomous GitHub Repo Engineer Agent

Autonomous GitHub Repo Engineer Agent analyzes Python repositories and helps improve them in two ways:

1. API analysis mode (`/analyze_repo`) for on-demand repository inspection.
2. Autonomous CLI mode (`agent.py`) for self-generated backlog tasks and task execution.

## Quick Start (2 Minutes)

```powershell
cd <project-root>
python -m pip install -r requirements.txt
python -m pip install -e .
python run_server.py
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and call `POST /analyze_repo`.

For autonomous backlog mode (separate terminal):

```powershell
cd <project-root>
python agent.py scan_repo
python agent.py
```
## What It Does

- Accepts a GitHub repository URL
- Clones repository locally
- Scans repository structure and files
- Detects Python improvement opportunities:
  - unused imports
  - missing docstrings
  - long functions
  - duplicate code blocks
  - files without unit tests
  - complex functions (deep/nested control flow)
- Converts findings into structured tasks and stores them in `backlog/tasks.json`
- Executes tasks from backlog using an implementation agent
- Logs discovered tasks, completed tasks, and modified files

## Project Structure

```text
New project/
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
  backlog/
    tasks.json
  tests/
  examples/
  agent.py
  run_server.py
  requirements.txt
  pyproject.toml
  setup.py
```

## Task Format

Generated tasks are stored in `backlog/tasks.json` with this structure:

```json
{
  "task_id": "TASK-0001",
  "task_type": "refactor",
  "description": "Refactor long functions in utils.py: process_data (112 lines)",
  "target_files": ["utils.py"],
  "priority": 4
}
```

`task_type` values:
- `refactor`
- `documentation`
- `testing`
- `optimization`

## Prerequisites

- Python 3.9+
- Git installed and available in PATH

## Setup (PowerShell)

Run from project root:

```powershell
cd <project-root>
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run API Server

```powershell
cd <project-root>
python run_server.py
```

Server URLs:
- Root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Invoke API from UI

1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Expand `POST /analyze_repo`
3. Click `Try it out`
4. Use request body:

```json
{
  "repo_url": "https://github.com/tiangolo/fastapi"
}
```

5. Click `Execute`

## Invoke API from PowerShell

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/analyze_repo" `
  -ContentType "application/json" `
  -Body '{"repo_url":"https://github.com/tiangolo/fastapi"}'
```

## Important: API vs Task Execution

`POST /analyze_repo` does **analysis only** and returns:
- `summary`
- `issues`
- `suggestions`

It does **not** execute backlog tasks.

Backlog task generation/execution is done via CLI (`agent.py`).

## Autonomous CLI Commands

Run from project root:

### 1. Generate tasks from current repository

```powershell
python agent.py scan_repo
```

Example output:

```text
Repository Analysis Report
Tasks created: 7

Refactor:
- Refactor long functions in utils.py: process_data (112 lines)

Documentation:
- Add missing docstrings in api_service.py for: module, fetch_data

Testing:
- Add unit tests for auth/service.py.
```

### 2. Execute next task

```powershell
python agent.py
```

Workflow:
- If backlog empty: automatically runs task generation.
- Else: executes next backlog task.

## Logging

Logs include:
- tasks discovered
- tasks completed
- files modified

## Run Tests

```powershell
cd <project-root>
python -m pytest -q
```

## Notes

- `ImplementationAgent` is currently a pluggable baseline executor. It can be replaced with a real code-modifying implementation without changing `agent.py` flow.
- Backlog is persisted in `backlog/tasks.json`.
- If clone fails in API mode, endpoint returns HTTP 400 with error details.



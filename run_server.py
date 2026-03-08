"""Convenience launcher for running the FastAPI server from IDEs."""

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "autonomous_repo_engineer.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

import requests


if __name__ == "__main__":
    payload = {"repo_url": "https://github.com/tiangolo/fastapi"}
    response = requests.post("http://127.0.0.1:8000/analyze_repo", json=payload, timeout=120)
    print(response.status_code)
    print(response.json())

import os
import sys
import json
from pathlib import Path

try:
    import httpx
except Exception as e:
    print("Missing dependency httpx. Install with: python -m pip install httpx")
    raise

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

# If backend/.env exists, load it so DEFAULT_MODEL and OLLAMA_BASE_URL are available.
repo_root = Path(__file__).resolve().parent.parent
env_path = repo_root / "backend" / ".env"
if env_path.exists() and load_dotenv:
    load_dotenv(env_path)


def main():
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    # prefer explicit OLLAMA_MODEL, fall back to DEFAULT_MODEL, then gpt-4.1-mini
    model = os.getenv("OLLAMA_MODEL") or os.getenv("DEFAULT_MODEL") or "gpt-4.1-mini"
    url = f"{base}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello from test_ollama.py"},
        ],
    }

    print(f"Testing Ollama at: {url} (model={model})")
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(url, json=payload)
        print("HTTP", r.status_code)
        try:
            body = r.json()
            print(json.dumps(body, indent=2, ensure_ascii=False))
        except Exception:
            print(r.text)
        if r.status_code != 200:
            sys.exit(2)
    except Exception as exc:
        print("Request failed:", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()

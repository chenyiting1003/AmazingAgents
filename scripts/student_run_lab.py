#!/usr/bin/env python3
"""
Student-friendly launcher for the Mini Model UN lab (runs scripts/run_minisim.py).

Usage (from project root, after venv activated):
    python scripts/student_run_lab.py

Or from any cwd:
    python /path/to/amazingmaps/scripts/student_run_lab.py
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MINISIM = ROOT / "scripts" / "run_minisim.py"
DOTENV_SPEC = importlib.util.find_spec("dotenv")
OPENAI_SPEC = importlib.util.find_spec("openai")


def _print(msg: str) -> None:
    print(msg, flush=True)


def main() -> int:
    os.chdir(ROOT)

    _print("")
    _print("========== Mini Model UN Lab — Student launcher ==========")
    _print(f"Project folder: {ROOT}")
    _print("")

    if sys.version_info < (3, 10):
        _print("ERROR: Need Python 3.10 or newer.")
        _print("  Debug: python --version")
        _print("  Fix: Install from https://www.python.org/downloads/ and check \"Add Python to PATH\" on Windows.")
        return 1

    if DOTENV_SPEC is None or OPENAI_SPEC is None:
        _print("ERROR: Missing packages. Activate your virtual environment, then:")
        _print(f"  cd \"{ROOT}\"")
        _print("  pip install -r requirements.txt")
        _print("  Debug: pip show python-dotenv openai")
        return 1

    env_file = ROOT / ".env"
    if not env_file.is_file():
        _print("ERROR: Missing .env file.")
        _print("  Fix: Copy .env.example to .env , then paste your OpenAI API key.")
        _print(f"       cp .env.example .env   (Linux / macOS)")
        _print("       copy .env.example .env  (Windows Command Prompt)")
        return 1

    from dotenv import load_dotenv

    load_dotenv(env_file)

    key = (os.getenv("LLM_API_KEY") or "").strip()
    base = (os.getenv("LLM_BASE_URL") or "").strip()
    model = (os.getenv("LLM_MODEL_NAME") or "").strip()

    if not key or key.startswith("PASTE_"):
        _print("ERROR: LLM_API_KEY not set correctly in .env")
        _print("  Visit https://platform.openai.com/api-keys")
        _print("  Paste your secret key after LLM_API_KEY= in .env (no quotes, no spaces).")
        _print("  Never share your key or commit .env to GitHub.")
        return 1

    if not base:
        _print("ERROR: LLM_BASE_URL is empty in .env")
        _print('  Students should use: LLM_BASE_URL=https://api.openai.com/v1')
        return 1

    if not model:
        _print("ERROR: LLM_MODEL_NAME is empty in .env")
        _print('  Example: LLM_MODEL_NAME=gpt-5 (use exact id from platform.openai.com)')
        return 1

    if not MINISIM.is_file():
        _print(f"ERROR: Missing {MINISIM}")
        return 1

    _print("OK: .env found; starting simulation (calls OpenAI API, may cost a small fee)...")
    _print("Outputs will be saved under outputs/")
    _print("")

    result = subprocess.run(
        [sys.executable, str(MINISIM)],
        cwd=str(ROOT),
        env=os.environ.copy(),
    )
    if result.returncode != 0:
        _print("")
        _print("The simulation script exited with an error. See messages above.")
        _print('Typical fixes: billing enabled on OpenAI account; correct model name; VPN/firewall.')
        return result.returncode

    _print("")
    _print("Optional — view results in browser (second terminal, keep this window open or run in background):")
    _print(f"  python \"{ROOT / 'scripts' / 'serve_lab_ui.py'}\"")
    _print("  Open http://127.0.0.1:8080/ → refresh → tab「继续讨论」for extra rounds (uses API; see model_un_student_continuations.json).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

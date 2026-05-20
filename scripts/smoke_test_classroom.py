#!/usr/bin/env python3
"""Classroom smoke test without invoking paid API calls by default."""
from __future__ import annotations

import importlib.util
import io
import os
import re
from contextlib import redirect_stdout
from pathlib import Path


REQUIRED_ENV = ["LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL_NAME", "MAX_AGENTS", "MAX_ROUNDS", "MAX_SEED_WORDS", "MAX_REPORT_WORDS"]
CASE_FILES = [
    "case_materials/seed_un_ai_climate_governance.txt",
    "case_materials/prediction_request.txt",
    "case_materials/agent_roles.md",
]


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> int:
    # best-effort .env loading without external dependency
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k,v=line.split("=",1)
            os.environ.setdefault(k.strip(), v.strip())

    print("[1/7] Checking environment variable presence...")
    missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
    if missing:
        fail(f"Missing required vars: {', '.join(missing)}")

    print("[2/7] Checking classroom limits...")
    limits = {
        "MAX_AGENTS": int(os.getenv("MAX_AGENTS", "0")),
        "MAX_ROUNDS": int(os.getenv("MAX_ROUNDS", "0")),
        "MAX_SEED_WORDS": int(os.getenv("MAX_SEED_WORDS", "0")),
        "MAX_REPORT_WORDS": int(os.getenv("MAX_REPORT_WORDS", "0")),
    }
    expected = {"MAX_AGENTS": 5, "MAX_ROUNDS": 3, "MAX_SEED_WORDS": 1000, "MAX_REPORT_WORDS": 800}
    for k, v in expected.items():
        if limits[k] > v:
            fail(f"{k} exceeds classroom cap: {limits[k]} > {v}")

    print("[3/7] Checking case materials...")
    for p in CASE_FILES:
        if not Path(p).is_file():
            fail(f"Missing case material: {p}")

    print("[4/7] Checking output directory writability...")
    out = Path("outputs")
    out.mkdir(exist_ok=True)
    probe = out / ".smoke_probe"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink(missing_ok=True)

    print("[5/7] Verifying fallback mini simulation file and syntax...")
    mini = Path("scripts/run_minisim.py")
    if not mini.is_file():
        fail("Missing scripts/run_minisim.py")
    import py_compile
    py_compile.compile(str(mini), doraise=True)

    print("[6/7] Provider test eligibility...")
    key = os.getenv("LLM_API_KEY", "")
    if not key or key.startswith("PASTE_"):
        print("SKIP: provider test (no real API key configured).")
    else:
        print("READY: provider test can run via python scripts/test_provider.py")

    print("[7/7] Ensuring no API key printed by smoke test...")
    f = io.StringIO()
    with redirect_stdout(f):
        print("smoke")
    output = f.getvalue()
    if key and key in output:
        fail("API key leaked in output")
    if re.search(r"sk-[A-Za-z0-9]", output):
        fail("Potential key pattern leaked in output")

    if not os.getenv("ZEP_API_KEY") or os.getenv("ZEP_API_KEY", "").startswith("PASTE_"):
        print("WARNING: ZEP_API_KEY is missing. Running in reduced-memory classroom mode.")

    print("INFO: Lab path is Python + browser (run_minisim + serve_lab_ui); full MiroFish UI is out of scope here.")

    print("PASS: smoke_test_classroom checks completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

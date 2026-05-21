#!/usr/bin/env python3
"""
Student-driven continuation round: reads base transcript from outputs/,
calls LLM with user instruction, appends to outputs/model_un_student_continuations.json.

Uses one chat completion per selected agent (same idea as baseline run_minisim) so each
statement is complete within max_tokens; does not rely on one giant JSON for all agents.

Does NOT modify run_minisim.py or model_un_transcript.json.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
DISCLAIMER = "This is a simulated scenario deliberation, not a factual prediction."


def _continuations_path(base: Path) -> Path:
    return base / "outputs" / "model_un_student_continuations.json"


def _slim_transcript(transcript: dict[str, Any]) -> dict[str, Any]:
    rounds = transcript.get("rounds") or []
    if len(rounds) > 3:
        return {**{k: v for k, v in transcript.items() if k != "rounds"}, "rounds": rounds[-3:]}
    return transcript


def _ensure_continuations_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        path.write_text(
            json.dumps({"disclaimer": DISCLAIMER, "entries": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_continuations(root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    cp = _continuations_path(base)
    _ensure_continuations_file(cp)
    return json.loads(cp.read_text(encoding="utf-8"))


def _single_agent_prompt(agent: str, instruction: str, context: str) -> str:
    """One facilitator-directed statement for a single agent (same structure as baseline rounds)."""
    return (
        f"{DISCLAIMER}\n"
        f"You are only speaking as {agent}.\n"
        "Do not summarize the whole negotiation.\n"
        "Do not write statements for other agents.\n"
        "This is an extra student-directed continuation round; respond only to the facilitator directive.\n"
        "Your output must be 120-180 words.\n"
        "You must include exactly four labelled parts (use these English labels):\n"
        "Demand:\n"
        "Concern:\n"
        "Possible concession:\n"
        "Condition for agreement:\n\n"
        f"Facilitator directive (may be in Chinese):\n{instruction}\n\n"
        "Prior transcript for context (JSON, may be truncated):\n"
        f"{context}\n"
    )


def _round_title_from_instruction(instruction: str) -> str:
    lines = instruction.strip().splitlines()
    line = lines[0].strip() if lines else ""
    if not line:
        return "Student continuation"
    return (line[:77] + "…") if len(line) > 80 else line


def run_continuation(
    *,
    instruction: str,
    agents: list[str] | None,
    root: Path | None = None,
) -> dict[str, Any]:
    """
    Returns {"ok": True, "entry": {...}} or {"ok": False, "error": "..."}
    """
    ins = (instruction or "").strip()
    if not ins:
        return {"ok": False, "error": "Instruction is empty."}

    base = root or ROOT
    load_dotenv(base / ".env")

    key = (os.getenv("LLM_API_KEY") or "").strip()
    base_url = (os.getenv("LLM_BASE_URL") or "").strip()
    model = (os.getenv("LLM_MODEL_NAME") or "").strip()

    if not key or key.startswith("PASTE_"):
        return {"ok": False, "error": "LLM_API_KEY not configured in .env"}
    if not base_url or not model:
        return {"ok": False, "error": "LLM_BASE_URL or LLM_MODEL_NAME missing"}

    tp = base / "outputs" / "model_un_transcript.json"
    if not tp.is_file():
        return {"ok": False, "error": "Base transcript missing. Run python scripts/run_minisim.py first."}

    transcript = json.loads(tp.read_text(encoding="utf-8"))
    roster: list[str] = list(transcript.get("agents") or [])
    if not roster:
        return {"ok": False, "error": "Transcript has no agents list"}

    if agents is None:
        target = roster[:]
    else:
        target = [a for a in agents if a in roster]
        if not target and agents:
            return {"ok": False, "error": "No valid agent names in request."}
        if not target:
            target = roster[:]

    slim = _slim_transcript(transcript)
    context = json.dumps(slim, ensure_ascii=False)
    if len(context) > 24_000:
        context = context[:24_000] + "\n…(truncated for API size)"

    # One API call per selected agent. A single json_object for all agents often hit max_tokens
    # and only the last statement survived in valid JSON.
    per_agent_tokens = int(os.getenv("MAX_CONTINUE_TOKENS_PER_AGENT", "1200"))
    temperature = float(os.getenv("TEMPERATURE", "0.4"))

    client = OpenAI(api_key=key, base_url=base_url)
    statements: list[dict[str, Any]] = []

    for agent_name in target:
        user_content = _single_agent_prompt(agent_name, ins, context)
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=per_agent_tokens,
                messages=[{"role": "user", "content": user_content}],
            )
            statement = (resp.choices[0].message.content or "").strip()
        except Exception as e:
            return {"ok": False, "error": f"{agent_name}: {type(e).__name__}: {e}"}
        if not statement:
            return {"ok": False, "error": f"{agent_name}: empty model response"}
        statements.append({"agent": agent_name, "statement": statement})

    cp = _continuations_path(base)
    _ensure_continuations_file(cp)
    data = json.loads(cp.read_text(encoding="utf-8"))
    entry: dict[str, Any] = {
        "timestamp": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
        "instruction": ins,
        "agents_requested": target,
        "result": {
            "round_title": _round_title_from_instruction(ins),
            "statements": statements,
            "round_summary": None,
        },
    }
    data.setdefault("entries", []).append(entry)
    cp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"ok": True, "entry": entry}

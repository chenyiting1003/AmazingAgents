#!/usr/bin/env python3
"""
Student-driven continuation round: reads base transcript from outputs/,
calls LLM with user instruction, appends to outputs/model_un_student_continuations.json.

Does NOT modify run_minisim.py or model_un_transcript.json.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
DISCLAIMER = "This is a simulated scenario deliberation, not a factual prediction."


def _continuations_path(base: Path) -> Path:
    return base / "outputs" / "model_un_student_continuations.json"


def _parse_json_response(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    if "```" in text:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if m:
            return json.loads(m.group(1).strip())
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("Model did not return valid JSON")


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

    system = (
        f"{DISCLAIMER}\n"
        "You continue an existing Model UN style simulation as a language model. "
        "Follow the user directive for this extra round. "
        "Only produce statements for the agents the user lists. "
        "Each agent statement MUST use exactly these labeled parts (English labels):\n"
        "Demand:\nConcern:\nPossible concession:\nCondition for agreement:\n"
        "120-180 words per agent. One JSON object per agent in the statements array. "
        "Return ONLY valid JSON, no markdown fences."
    )
    user = (
        f"Student / facilitator directive (may be Chinese):\n{ins}\n\n"
        f"Agents who must speak in this round: {json.dumps(target, ensure_ascii=False)}\n\n"
        "Prior transcript (JSON, may be truncated):\n"
        f"{context}\n\n"
        "Return JSON with shape:\n"
        '{"round_title": "short string", '
        '"statements": [{"agent": "<exact name from list>", "statement": "<full text>"}], '
        '"round_summary": "optional <=120 words"}'
    )

    client = OpenAI(api_key=key, base_url=base_url)
    max_tok = int(os.getenv("MAX_CONTINUE_TOKENS", "4096"))

    def _one_call(use_json_object: bool) -> str:
        kwargs: dict[str, Any] = {
            "model": model,
            "temperature": float(os.getenv("TEMPERATURE", "0.4")),
            "max_tokens": max_tok,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if use_json_object:
            kwargs["response_format"] = {"type": "json_object"}
        resp = client.chat.completions.create(**kwargs)
        return (resp.choices[0].message.content or "").strip()

    try:
        try:
            content = _one_call(True)
        except Exception:
            content = _one_call(False)
        parsed = _parse_json_response(content)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    statements = parsed.get("statements")
    if not isinstance(statements, list) or not statements:
        return {"ok": False, "error": "Model JSON missing statements array"}

    cp = _continuations_path(base)
    _ensure_continuations_file(cp)
    data = json.loads(cp.read_text(encoding="utf-8"))
    entry: dict[str, Any] = {
        "timestamp": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
        "instruction": ins,
        "agents_requested": target,
        "result": {
            "round_title": str(parsed.get("round_title") or "Student continuation"),
            "statements": statements,
            "round_summary": parsed.get("round_summary"),
        },
    }
    data.setdefault("entries", []).append(entry)
    cp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"ok": True, "entry": entry}

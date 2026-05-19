#!/usr/bin/env python3
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

AGENTS = [
    "United States",
    "European Union",
    "China",
    "Climate Vulnerable States Coalition",
    "Civil Society and Digital Rights Coalition",
]
ROUNDS = ["Opening positions", "Conflict and concessions", "Revised agreement"]
DISCLAIMER = "This is a simulated scenario deliberation, not a factual prediction."


def words(text: str) -> int:
    return len(text.split())


def cap_words(text: str, limit: int) -> str:
    parts = text.split()
    return " ".join(parts[:limit])


def main() -> int:
    load_dotenv()
    key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "")
    model = os.getenv("LLM_MODEL_NAME", "")
    max_report_words = int(os.getenv("MAX_REPORT_WORDS", "800"))

    if not key or not base_url or not model or key.startswith("PASTE_"):
        print("ERROR: Configure LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL_NAME in .env before running.")
        return 1

    if not os.getenv("ZEP_API_KEY") or os.getenv("ZEP_API_KEY", "").startswith("PASTE_"):
        print("ZEP_API_KEY is missing. Running in reduced-memory classroom mode.")

    seed_path = Path("case_materials/seed_un_ai_climate_governance.txt")
    req_path = Path("case_materials/prediction_request.txt")
    seed = seed_path.read_text(encoding="utf-8")
    request = req_path.read_text(encoding="utf-8")
    if words(seed) > int(os.getenv("MAX_SEED_WORDS", "1000")):
        seed = cap_words(seed, int(os.getenv("MAX_SEED_WORDS", "1000")))

    client = OpenAI(api_key=key, base_url=base_url)
    transcript = {"disclaimer": DISCLAIMER, "rounds": [], "agents": AGENTS, "request": request}
    memory = {a: [] for a in AGENTS}

    for idx, round_name in enumerate(ROUNDS, start=1):
        r = {"round": idx, "title": round_name, "statements": []}
        for agent in AGENTS:
            prompt = (
                f"{DISCLAIMER}\nYou are representing {agent}. Round: {round_name}.\n"
                f"Use the scenario context and speak in 100-130 words.\n"
                f"Recent memory: {memory[agent][-2:]}\n"
                f"Scenario context:\n{seed}\n\nTask:\n{request}"
            )
            resp = client.chat.completions.create(
                model=model,
                temperature=float(os.getenv("TEMPERATURE", "0.4")),
                max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS_PER_CALL", "800")),
                messages=[{"role": "user", "content": prompt}],
            )
            statement = (resp.choices[0].message.content or "").strip()
            memory[agent].append(statement)
            r["statements"].append({"agent": agent, "statement": statement})

        summary_prompt = (
            f"{DISCLAIMER}\nSummarize round {idx} ({round_name}) in 120 words max. "
            "Highlight conflicts and concessions."
        )
        summary_resp = client.chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=300,
            messages=[{"role": "user", "content": summary_prompt + "\n" + json.dumps(r["statements"], ensure_ascii=False)}],
        )
        r["summary"] = (summary_resp.choices[0].message.content or "").strip()
        transcript["rounds"].append(r)

    final_prompt = (
        f"{DISCLAIMER}\nWrite a final report with sections: Scenario summary; Stakeholder positions; "
        "Main conflicts; Emerging concessions; Possible partial agreement; Uncertainty and assumptions; "
        "Validity limitations. Keep under 800 words."
    )
    final_resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS_PER_CALL", "800")),
        messages=[{"role": "user", "content": final_prompt + "\n" + json.dumps(transcript, ensure_ascii=False)}],
    )
    report = (final_resp.choices[0].message.content or "").strip()
    report = report + "\n\n" + DISCLAIMER
    report = cap_words(report, max_report_words)

    outdir = Path("outputs")
    outdir.mkdir(exist_ok=True)
    (outdir / "model_un_transcript.json").write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "model_un_simulation_report.md").write_text(report + "\n", encoding="utf-8")
    print("Simulation complete. Outputs saved to outputs/model_un_transcript.json and outputs/model_un_simulation_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

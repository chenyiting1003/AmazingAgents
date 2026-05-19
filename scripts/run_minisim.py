#!/usr/bin/env python3
import json
import os
import re
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


def validate_role_boundaries(statement: str, current_round_idx: int) -> tuple[bool, list[str]]:
    issues = []
    s = statement.strip()

    required_labels = ["Demand:", "Concern:", "Possible concession:", "Condition for agreement:"]
    for label in required_labels:
        if label not in s:
            issues.append(f"missing_label:{label}")

    for ridx in [1, 2, 3]:
        if ridx != current_round_idx and re.search(rf"\bRound\s*{ridx}\b", s, flags=re.IGNORECASE):
            issues.append(f"mentions_other_round_{ridx}")

    agent_mentions = sum(1 for a in AGENTS if a.lower() in s.lower())
    if agent_mentions >= 4:
        issues.append("mentions_many_agents")

    if re.search(r"revised agreement includes", s, flags=re.IGNORECASE):
        issues.append("agenda_summary_phrase")

    if re.search(r"(overall|in summary|across all rounds|all stakeholders|negotiation as a whole)", s, flags=re.IGNORECASE):
        issues.append("summary_style_phrase")

    word_count = words(s)
    if word_count < 120 or word_count > 180:
        issues.append(f"word_count_out_of_range:{word_count}")

    return (len(issues) > 0), issues


def statement_prompt(agent: str, round_name: str, seed: str, request: str, memory_slice: list[str]) -> str:
    return (
        f"{DISCLAIMER}\n"
        f"You are only speaking as {agent}.\n"
        "Do not summarize the whole negotiation.\n"
        "Do not write statements for other agents.\n"
        "Do not mention future rounds.\n"
        "Do not produce headings for other stakeholders.\n"
        "Only respond for the current round.\n"
        "Your output must be 120-180 words.\n"
        "You must include exactly four labelled parts:\n"
        "Demand:\n"
        "Concern:\n"
        "Possible concession:\n"
        "Condition for agreement:\n\n"
        f"Current round: {round_name}\n"
        f"Recent memory: {memory_slice}\n\n"
        f"Scenario context:\n{seed}\n\n"
        f"Task:\n{request}"
    )


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
    any_role_leakage = False

    for idx, round_name in enumerate(ROUNDS, start=1):
        r = {"round": idx, "title": round_name, "statements": []}
        for agent in AGENTS:
            prompt = statement_prompt(agent, round_name, seed, request, memory[agent][-2:])
            resp = client.chat.completions.create(
                model=model,
                temperature=float(os.getenv("TEMPERATURE", "0.4")),
                max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS_PER_CALL", "800")),
                messages=[{"role": "user", "content": prompt}],
            )
            statement = (resp.choices[0].message.content or "").strip()

            leaked, issues = validate_role_boundaries(statement, idx)
            if leaked:
                retry_prompt = (
                    f"Your previous answer violated the simulation rules by summarising other agents or future rounds. "
                    f"Rewrite only as {agent} for {round_name}.\n"
                    "Follow exactly this format with 120-180 words total:\n"
                    "Demand:\nConcern:\nPossible concession:\nCondition for agreement:\n"
                )
                retry_resp = client.chat.completions.create(
                    model=model,
                    temperature=0.2,
                    max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS_PER_CALL", "800")),
                    messages=[
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": statement},
                        {"role": "user", "content": retry_prompt},
                    ],
                )
                statement_retry = (retry_resp.choices[0].message.content or "").strip()
                leaked_retry, issues_retry = validate_role_boundaries(statement_retry, idx)
                if not leaked_retry:
                    statement = statement_retry
                    leaked = False
                    issues = []
                else:
                    statement = statement_retry
                    leaked = True
                    issues = issues_retry

            any_role_leakage = any_role_leakage or leaked
            memory[agent].append(statement)
            r["statements"].append(
                {
                    "agent": agent,
                    "statement": statement,
                    "statement_role_leakage": leaked,
                    "role_leakage_issues": issues,
                }
            )

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
        "Validity limitations; Role Boundary and Validity Issues. Keep under 800 words."
    )
    final_resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS_PER_CALL", "800")),
        messages=[{"role": "user", "content": final_prompt + "\n" + json.dumps(transcript, ensure_ascii=False)}],
    )
    report = (final_resp.choices[0].message.content or "").strip()
    report += (
        "\n\n## Role Boundary and Validity Issues\n"
        f"Role leakage detected in one or more statements: {'Yes' if any_role_leakage else 'No'}.\n"
        "Leakage means an agent drifted into summarizing other actors or non-current rounds, which reduces role validity.\n"
    )
    report = report + "\n\n" + DISCLAIMER
    report = cap_words(report, max_report_words)

    leakage_count = 0
    variables = {
        "funding_conflict": 0,
        "technology_transfer_conflict": 0,
        "data_governance_conflict": 0,
        "sovereignty_conflict": 0,
        "accountability_conflict": 0,
        "agreement_likelihood": "medium",
        "evidence_snippets": [],
    }
    keywords = {
        "funding_conflict": ["fund", "finance", "funding", "contribution"],
        "technology_transfer_conflict": ["technology transfer", "ip", "intellectual property"],
        "data_governance_conflict": ["data", "governance", "privacy"],
        "sovereignty_conflict": ["sovereignty", "national control", "external monitoring"],
        "accountability_conflict": ["accountability", "audit", "oversight", "transparency"],
    }

    for rnd in transcript["rounds"]:
        for item in rnd["statements"]:
            st = item["statement"].lower()
            if item["statement_role_leakage"]:
                leakage_count += 1
            for k, terms in keywords.items():
                if any(t in st for t in terms):
                    variables[k] = min(5, variables[k] + 1)
            if len(variables["evidence_snippets"]) < 12:
                variables["evidence_snippets"].append(
                    {"agent": item["agent"], "round": rnd["title"], "snippet": item["statement"][:220]}
                )

    if variables["funding_conflict"] + variables["sovereignty_conflict"] >= 7:
        variables["agreement_likelihood"] = "low"
    elif variables["accountability_conflict"] <= 2:
        variables["agreement_likelihood"] = "medium-high"

    role_leakage_report = (
        "# Model UN Role Leakage Report\n\n"
        f"- Total statements with role leakage: {leakage_count}\n"
        f"- Any role leakage detected: {'Yes' if any_role_leakage else 'No'}\n\n"
        "## Why this matters\n"
        "Role leakage weakens validity because agents stop acting as bounded stakeholders and drift into narrative summary.\n"
    )

    outdir = Path("outputs")
    outdir.mkdir(exist_ok=True)
    (outdir / "model_un_transcript.json").write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "model_un_simulation_report.md").write_text(report + "\n", encoding="utf-8")
    (outdir / "model_un_variables.json").write_text(json.dumps(variables, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "model_un_role_leakage_report.md").write_text(role_leakage_report, encoding="utf-8")
    print(
        "Simulation complete. Outputs saved to outputs/model_un_transcript.json, "
        "outputs/model_un_simulation_report.md, outputs/model_un_variables.json, "
        "and outputs/model_un_role_leakage_report.md"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

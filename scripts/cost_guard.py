#!/usr/bin/env python3
import argparse

MAX_AGENTS = 5
MAX_ROUNDS = 3


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate classroom simulation API call volume.")
    parser.add_argument("--agents", type=int, default=5)
    parser.add_argument("--rounds", type=int, default=3)
    args = parser.parse_args()

    agent_calls = args.agents * args.rounds
    summary_calls = args.rounds
    final_report_calls = 1
    total_calls = agent_calls + summary_calls + final_report_calls

    print("Estimated LLM calls:")
    print(f"{args.agents} agents × {args.rounds} rounds = {agent_calls} agent calls")
    print(f"+ {summary_calls} round summaries")
    print(f"+ {final_report_calls} final report")
    print(f"Total approximate calls: {total_calls}\n")

    if args.agents > MAX_AGENTS or args.rounds > MAX_ROUNDS:
      print("WARNING: This exceeds classroom mode recommendations.")
      print(f"Recommended maximums: {MAX_AGENTS} agents and {MAX_ROUNDS} rounds.\n")

    print("Reminder:")
    print("Your API provider may charge based on input and output tokens.")
    print("Keep outputs short for classroom use.")
    print("Use short seed material and avoid increasing rounds or agent count.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

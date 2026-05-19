#!/usr/bin/env python3
import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv


def parse_json_from_text(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def main() -> int:
    load_dotenv()
    key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "")
    model = os.getenv("LLM_MODEL_NAME", "")

    missing = [name for name, val in [("LLM_API_KEY", key), ("LLM_BASE_URL", base_url), ("LLM_MODEL_NAME", model)] if not val or val.startswith("PASTE_")]
    if missing:
        print(f"ERROR: Missing required env vars: {', '.join(missing)}")
        return 1

    client = OpenAI(api_key=key, base_url=base_url)
    messages = [
        {"role": "system", "content": "Return JSON only."},
        {"role": "user", "content": "Return an object with key 'status' and value 'ok'."},
    ]

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content or "{}"
        data = json.loads(content)
        print(f"SUCCESS: JSON mode works. status={data.get('status')}")
        return 0
    except Exception as json_mode_error:
        print(f"WARNING: JSON mode failed ({type(json_mode_error).__name__}). Trying plain text fallback...")

    try:
        resp = client.chat.completions.create(model=model, messages=messages, temperature=0)
        content = resp.choices[0].message.content or ""
        data = parse_json_from_text(content)
        print(f"SUCCESS: Fallback parsing works. status={data.get('status')}")
        return 0
    except Exception as fallback_error:
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/provider_test_raw_response.txt", "w", encoding="utf-8") as f:
            f.write("Provider test failed after JSON mode fallback.\n")
            f.write(f"Error type: {type(fallback_error).__name__}\n")
        print(f"ERROR: Provider test failed: {type(fallback_error).__name__}: {fallback_error}")
        print("Raw failure note saved to outputs/provider_test_raw_response.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())

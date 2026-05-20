# Troubleshooting

## Port 8080 already in use (`serve_lab_ui`)

- Another program is using the default port. Start the lab UI on another port:
  ```bash
  python scripts/serve_lab_ui.py --port 8090
  ```
  Then open `http://127.0.0.1:8090/`.

## Missing `.env`

- Create from template:
  - `cp .env.example .env`

## Invalid API key

- Ensure `LLM_API_KEY` is set and not placeholder text.
- Run `python scripts/test_provider.py`.

## Wrong `LLM_BASE_URL`

- OpenAI: `https://api.openai.com/v1`
- DashScope compatible: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- DeepSeek: `https://api.deepseek.com/v1`

## Provider does not support JSON mode

- Run `python scripts/test_provider.py`.
- The script first tests JSON mode, then falls back to plain text JSON parsing.
- Failure notes may be saved to `outputs/provider_test_raw_response.txt`.

## Zep key missing

- If `ZEP_API_KEY` is missing, the mini simulation may still run with a warning:
  - `ZEP_API_KEY is missing. Running in reduced-memory classroom mode.`

## Simulation too slow

- Keep classroom defaults (5 agents, 3 rounds in baseline script).
- Lower `MAX_OUTPUT_TOKENS_PER_CALL` in `.env` if needed.

## API cost concern

- Use `python scripts/cost_guard.py` to estimate baseline call counts.
- Browser **继续讨论** adds one billed continuation per submit—remind students.

## Lab page shows no data

- Confirm you opened **`http://127.0.0.1:.../` from `serve_lab_ui`**, not `file:///...` on the HTML file.
- Run baseline first: `python scripts/student_run_lab.py` or `run_minisim.py`, then click **刷新结果**.

## Continuation (`/api/continue`) fails

- Baseline `outputs/model_un_transcript.json` must exist.
- Same `venv` as `pip install -r requirements.txt` (needs `openai`, `python-dotenv`).

## Windows path or permission issues

- Run terminal as normal user; use paths without spaces when possible.
- Ensure you have write access to the project folder (for `outputs/`).

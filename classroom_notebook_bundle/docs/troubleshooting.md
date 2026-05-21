# Troubleshooting

## Port 8080 already in use (`serve_lab_ui`)

- Another program is using the default port. In **`Mini_Model_UN_Student_Lab.ipynb`**, set `LAB_UI_PORT = 8090` (or a free port) in the **Start lab UI** cell, **or** from repo root:
  ```bash
  python scripts/serve_lab_ui.py --port 8090
  ```
  Then open `http://127.0.0.1:8090/`.

## Missing `.env`

- Create from template:
  - `cp .env.example .env`

## Invalid API key

- Ensure `LLM_API_KEY` is set and not placeholder text.
- Run the notebook **Optional checks** cell (short API probe).

## Wrong `LLM_BASE_URL`

- **DeepSeek (course default):** `https://api.deepseek.com` (do **not** add `/v1`; the SDK calls `/chat/completions`).
- OpenAI: `https://api.openai.com/v1`
- DashScope compatible: `https://dashscope.aliyuncs.com/compatible-mode/v1`

## Provider does not support JSON mode

- The notebook **Optional checks** cell tries JSON mode, then text fallback.
- Failure notes may be saved to `outputs/provider_test_raw_response.txt`.

## Zep key missing

- If `ZEP_API_KEY` is missing, the mini simulation may still run with a warning:
  - `ZEP_API_KEY is missing. Running in reduced-memory classroom mode.`

## Simulation too slow

- Keep classroom defaults (5 agents, 3 rounds in baseline script).
- Lower `MAX_OUTPUT_TOKENS_PER_CALL` in `.env` if needed.

## API cost concern

- Use the **cost estimate** block at the end of the **Optional checks** cell for approximate baseline call counts.
- Browser **Continue discussion** bills **one API call per selected delegate** per submit—remind students.

## Lab page shows no data

- Confirm you opened **`http://127.0.0.1:.../` from `serve_lab_ui`**, not `file:///...` on the HTML file.
- Run the notebook **Run baseline** cell first (or `python scripts/run_minisim.py`), then click **Refresh results**.

## Continuation (`/api/continue`) fails

- Baseline `outputs/model_un_transcript.json` must exist.
- Same `venv` as `pip install -r requirements.txt` (needs `openai`, `python-dotenv`).

## Windows path or permission issues

- Run terminal as normal user; use paths without spaces when possible.
- Ensure you have write access to the project folder (for `outputs/`).

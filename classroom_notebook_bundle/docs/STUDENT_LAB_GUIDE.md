# Mini Model UN lab — student walkthrough (English)

From clone → configure API → run baseline → browser → optional continuations. Includes outputs, common errors, and quick commands.

---

## For enrolled students

Read this once, then follow **steps A→E**. If stuck, use **Common errors** and `docs/troubleshooting.md`.

Assume you can reach the **DeepSeek API** (`api.deepseek.com`) and **GitHub**. If your instructor allows **OpenAI**, you need access to `platform.openai.com`. Campus networks may block some endpoints.

**Recommended (single file):** at the repo root, open **`Mini_Model_UN_Student_Lab.ipynb`** in Jupyter / VS Code / Cursor. Read the first Markdown cell, then run code cells **top to bottom** — that covers install, preflight, baseline, and the browser lab without extra terminals if you prefer.

---

## Big picture

```
  A   git clone the course repo
  B   Get a personal API key → `.env` (never commit; compare providers if you like)
  C   `python -m venv .venv` → activate → `pip install -r requirements.txt`
  D   Run baseline:
        · Course path: notebook cells “Preflight”, “Optional checks”, “Run baseline”
        · Debug only: `python scripts/run_minisim.py` (same script as the notebook)
        → `outputs/` gets four baseline files (default: three negotiating rounds)
  E   View + optional continuations:
        · Recommended: notebook **Start lab UI** (background server + browser)
        · Or: `python scripts/serve_lab_ui.py`
        → Browser: `http://127.0.0.1:8080/` (port may differ)
        Optional: **Continue discussion** to steer delegates for another round

Do **not** skip **D** before continuations: the web UI needs `model_un_transcript.json`.

---

## What case are we running?

**Topic:** whether the UN should establish a **Global AI and Climate Adaptation Fund**.

**Case materials** (under `case_materials/`):

- `seed_un_ai_climate_governance.txt` — background, tensions, policy modules  
- `prediction_request.txt` — five parties, three agenda rounds, output expectations  
- `agent_roles.md` — role definitions  

**Disclaimer:** outputs are **scenario deliberation** for practice (positions, conflict, concessions, uncertainty, validity). They are **not** forecasts of real policy or any government’s view.

**Stretch (optional):** copy/rename seed and task files to design your own scenario (keep paths consistent with `run_minisim` if you change filenames).

---

## Inputs you must provide

### (1) Bundled materials (usually unchanged)

Paths are relative to project root.

### (2) `.env` (copy from `.env.example`)

**Course default: DeepSeek**

| Variable | Typical value |
|----------|----------------|
| `LLM_API_KEY` | Your key from [DeepSeek](https://platform.deepseek.com/api_keys) |
| `LLM_BASE_URL` | `https://api.deepseek.com` (**no** `/v1` suffix) |
| `LLM_MODEL_NAME` | e.g. `deepseek-chat`; match your console |

**OpenAI (only if allowed):** `https://api.openai.com/v1` and a model id from OpenAI’s dashboard.

**Never:** post keys in chat, email bodies, or public forums; never commit `.env`; do not use someone else’s key.

---

## Outputs (where files go)

### Baseline (after step **D**; re-running **D** usually overwrites these)

Under `outputs/`:

| File | Role |
|------|------|
| `model_un_transcript.json` | Full structured dialogue; baseline for UI + continuations |
| `model_un_simulation_report.md` | Narrative report |
| `model_un_variables.json` | Heuristic keyword-style summary |
| `model_un_role_leakage.md` | Short role-boundary notes |

### Continuations (browser **Continue discussion**)

- `model_un_student_continuations.json` — append-only log of your instructions + model replies.  
- Baseline files above are **not** modified by continuations.

---

## Stack (short)

- Python 3.10+  
- `python-dotenv`, `openai` (OpenAI-compatible HTTP API)  
- Lab UI: `scripts/serve_lab_ui.py` — use `http://127.0.0.1:...`, **not** `file://` on `index.html`.

**Cost:** baseline = many calls; each continuation submit = **one call per checked delegate**.

---

## Steps A–E (detail)

### Step A — Clone

```bash
cd <folder where you keep the lab>
git clone <course GitHub URL>
cd <repo folder>
```

Confirm you see `requirements.txt`, `case_materials`, `scripts`, `web`, etc.

**Common errors:** `git` not found (install Git); SSL/TLS errors (network/proxy); permission denied (use a writable directory).

### Step B — API key and `.env`

1. Sign in at [DeepSeek](https://platform.deepseek.com/), create an API key, note your model ids from docs/console.  
2. In repo root:

```bash
cp .env.example .env
```

3. Edit `.env`: set `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME` (no quotes, no stray spaces).

**Common errors:** placeholder key still set; `401` / invalid key; `model not found`; quota/billing; timeout to `api.deepseek.com` (try another network).

### Step C — Virtual environment

```bash
python -m venv .venv
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

**Common errors:** `python` not found; PowerShell execution policy; pip SSL/proxy.

### Step D — Baseline

In the notebook, run **Run baseline** (or from activated venv at repo root):

```bash
python scripts/run_minisim.py
```

Success: log ends with completion; four files appear under `outputs/`.

**Common errors:** missing `LLM_API_KEY`; connection errors to `LLM_BASE_URL`; wrong working directory.

### Step E — Browser lab

Start UI from the notebook **Start lab UI** cell or:

```bash
python scripts/serve_lab_ui.py
```

Open the printed URL, click **Refresh results**, explore tabs, optionally **Continue discussion**.

**Common errors:** port in use (change `LAB_UI_PORT` or `--port`); opened HTML via `file://` instead of the server.

---

## Class tasks & critique

- Reflection questions: `case_materials/classroom_tasks.md`  
- Validity worksheet: `docs/validity_critique_template.md`

---

## Quick command cheat sheet

```bash
cp .env.example .env          # configure first
python -m venv .venv && source .venv/bin/activate  # or Windows equivalent
pip install -r requirements.txt
python scripts/run_minisim.py
python scripts/serve_lab_ui.py
```

Primary path: **`Mini_Model_UN_Student_Lab.ipynb`** top to bottom.

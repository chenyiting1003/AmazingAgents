# LLM social simulation lab (student guide)

This guide supports **in-class lab practice**. If your section asks for a written deliverable, follow the instructor’s instructions separately.

**How you run the lab:** open **`Mini_Model_UN_Student_Lab.ipynb`** from the repo root and execute cells **top to bottom**. The first cell is the full usage guide.

**Step-by-step (English):** **`docs/STUDENT_LAB_GUIDE.md`**

## What this lab is about

You will run a small **scenario simulation** of a Model United Nations policy discussion about AI and climate adaptation governance. This is a **simulated stakeholder discussion** for learning and critique, not factual forecasting.

## Main workflow (Jupyter)

1. **Configure API** — Copy `.env.example` to `.env` and set `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME`. **Class default is DeepSeek** (`https://api.deepseek.com`); see the student guide for OpenAI if allowed.

2. **Create a venv (recommended)** — `python -m venv .venv` → activate → `pip install -r requirements.txt` (the notebook will also try to install deps).

3. **Run the notebook** — `Mini_Model_UN_Student_Lab.ipynb`: preflight → optional smoke + provider test + cost estimate → **baseline** → **start lab web UI** (browser at `http://127.0.0.1:8080/`).

4. **Continue discussion** (optional) — in the UI; appends to `outputs/model_un_student_continuations.json`; baseline `model_un_transcript.json` is not modified.

**Advanced (instructor/debug only):** from repo root, `python scripts/run_minisim.py` and `python scripts/serve_lab_ui.py` are the same engines the notebook calls; the classroom path is the notebook.

## Required software

- Git  
- Python 3.10+  
- Jupyter / VS Code / Cursor able to open `.ipynb`  
- API key from **DeepSeek** (default) or another OpenAI-compatible provider your instructor allows  

## If something fails

1. Re-run the notebook **Optional checks** cell (smoke + short API probe).  
2. See **`docs/troubleshooting.md`**.

## Validity critique (if assigned)

- `docs/validity_critique_template.md`  
- `case_materials/classroom_tasks.md`

## Cost

You pay your own API usage. Keep defaults (5 agents, 3 rounds). The notebook’s **cost estimate** prints approximate baseline call counts.

## Safety

- Never share API keys.  
- **Never commit `.env`.**  
- Do not paste keys into chat or public forums.

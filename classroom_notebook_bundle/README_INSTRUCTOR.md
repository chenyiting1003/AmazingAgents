# Instructor guide: LLM-enabled social simulation lab

## Teaching goal

Students run and critique a small Model UN **assumption-driven simulation**. Emphasize structured deliberation and validity critique, not factual prediction.

## Recommended timing

- 10 min — introduce LLM-enabled social simulation  
- 10 min — API and environment check (`.env`, `venv`, `pip`)  
- 15 min — explain Model UN case and agents  
- 20 min — students run baseline (**`Mini_Model_UN_Student_Lab.ipynb`**)  
- 15 min — optional: notebook **Start lab UI** + browser + “continue discussion”  
- 20 min — output interpretation  
- 20 min — validity critique and discussion  
- 5 min — final reflection  

## Classroom workflow (this repo)

**Student entry point:** only **`Mini_Model_UN_Student_Lab.ipynb`** (first cell = instructions).  
Core logic lives in `scripts/run_minisim.py`, `scripts/lab_continue.py`, `scripts/serve_lab_ui.py` — the notebook runs the same code via `subprocess` (no duplicate simulation stack).

1. `cp .env.example .env` — **defaults target DeepSeek**; students may switch if you allow.  
2. Notebook cells through **Run baseline** → four baseline files under `outputs/`.  
3. Notebook **Start lab UI** → **http://127.0.0.1:8080/** (or custom port) for transcript, report, and **Continue discussion** (writes `outputs/model_un_student_continuations.json`; does not change `model_un_transcript.json`).

## If something breaks

- Students: re-run preflight and **Optional checks** in the notebook; read `docs/troubleshooting.md`.  
- You may debug with `python scripts/run_minisim.py` / `python scripts/serve_lab_ui.py` from repo root (same as notebook engines).

## Pedagogy / repo design (vs upstream MiroFish)

This checkout is a **compact lab scaffold**, not a full MiroFish reproduction. It includes:

- Classroom limits in `.env.example`: `MAX_AGENTS`, `MAX_ROUNDS`, seed/report word caps, etc.  
- API key via `.env` (protected by `.gitignore`).  
- Case materials under `case_materials/` (Model UN AI–climate fund scenario).  
- Disclaimer in outputs: “This is a simulated scenario deliberation, not a factual prediction.”  
- `scripts/run_minisim.py` — baseline simulation.  
- `scripts/serve_lab_ui.py` + `web/` + `lab_continue.py` — browser viewer and student-led continuation rounds.  
- **Standalone launcher scripts** (`student_run_lab`, `smoke_test_classroom`, `test_provider`, `cost_guard`) were removed; their behavior is **inlined in the notebook** so students have one file to run.

## Known limitations

- Provider connectivity and billing depend on students’ own keys.  
- Zep/GraphRAG full stack is not part of this lab path (optional key may be ignored with a warning).

## Provider checks

- Notebook **Optional checks** cell: smoke + one short completion (JSON mode with fallback).  
- Set provider-specific `LLM_BASE_URL` in `.env` if needed.

## Framing language

Use: scenario simulation, simulated policy discussion, plausible negotiation dynamics, assumption-driven social simulation.

Avoid prediction framing. Require:

> This is a simulated scenario deliberation, not a factual prediction.

## Reset outputs before class

```bash
find outputs -type f ! -name '.gitkeep' -delete
```

## Testing checklist

- [ ] `cp .env.example .env` works  
- [ ] Notebook **Optional checks** passes with your provider  
- [ ] Classroom caps enforced by `run_minisim` / `.env`  
- [ ] Notebook baseline cell writes `outputs/`  
- [ ] Notebook web UI cell serves UI and `/api/continue` (with deps installed)  
- [ ] No API keys printed or committed  

## Security

- **Never commit `.env`.**  
- Do not log or share student keys.

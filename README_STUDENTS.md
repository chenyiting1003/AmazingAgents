# LLM Social Simulation Lab (Student Guide)

## What this lab is about
You will run a small **scenario simulation** of a Model United Nations policy discussion about AI and climate adaptation governance. This is a **simulated stakeholder discussion** for learning and critique, not factual forecasting.

## Two workflows in this repository
1. **Full MiroFish UI workflow (preferred):** use when upstream MiroFish frontend/backend code is present in this repo.
2. **Fallback mini simulation workflow:** use `python scripts/run_minisim.py` if the UI path is unavailable or fails.

## Required software
- Docker Desktop
- Git
- API key from an OpenAI-compatible provider
- Python 3.10+

## Check Docker
```bash
docker --version
docker compose version
```

## Setup
```bash
git clone <classroom-repo-url>
cd llm-social-simulation-lab
cp .env.example .env
```
Then edit `.env` and set:
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL_NAME`

## Full UI workflow (preferred)
```bash
docker compose up -d --build
bash scripts/healthcheck.sh
```
Open:
- http://localhost:3000

If this repository includes the real MiroFish app code, this is the main path for classroom use.

## Fallback mini simulation workflow
If the UI fails or upstream app code is unavailable:
```bash
pip install -r requirements.txt
python scripts/run_minisim.py
```
Outputs are written to `outputs/`.

## What to do if UI fails
1. Run `bash scripts/healthcheck.sh`
2. Run `python scripts/smoke_test_classroom.py`
3. Run `python scripts/test_provider.py`
4. Continue class with `python scripts/run_minisim.py`

## Validity critique
Complete:
- `docs/validity_critique_template.md`
- `case_materials/classroom_tasks.md`

## Cost warning
You are responsible for your own API usage costs.
- Keep runs small.
- Do not increase agent count or round count.
- Use `python scripts/cost_guard.py`.

## Safety warning
- Never share API keys.
- **Never commit `.env`.**
- Do not paste API keys into chat windows.

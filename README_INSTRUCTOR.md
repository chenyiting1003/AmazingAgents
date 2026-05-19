# Instructor Guide: LLM-Enabled Social Simulation Lab

## Teaching goal
Students run and critique a small Model UN **assumption-driven simulation**. Emphasize structured deliberation and validity critique, not factual prediction.

## Recommended timing
- 10 min — introduce LLM-enabled social simulation
- 10 min — API and Docker setup check
- 15 min — explain Model UN case and agents
- 20 min — students run small simulation
- 20 min — output interpretation
- 20 min — validity critique and discussion
- 5 min — final reflection

## Full UI workflow vs fallback workflow
- **Primary path:** full MiroFish UI/backend in Docker, if upstream code is present in this checkout.
- **Fallback path:** `python scripts/run_minisim.py` to keep the class running when UI/backend fails.

## Live demo workflow
1. `cp .env.example .env`
2. Fill API settings.
3. `docker compose up -d --build`
4. `bash scripts/healthcheck.sh`
5. Open `http://localhost:3000`
6. Run 5-agent, 3-round scenario simulation.

## Fallback plan (if UI fails)
```bash
python scripts/smoke_test_classroom.py
python scripts/run_minisim.py
```
This still produces transcript + report outputs for classroom analysis.

## What has been modified from upstream MiroFish
- Classroom limits configured in `.env.example`: `MAX_AGENTS=5`, `MAX_ROUNDS=3`, `MAX_SEED_WORDS=1000`, `MAX_REPORT_WORDS=800`.
- API-key handling via local `.env` and `.gitignore` protection for `.env`.
- Added Zep-missing reduced-memory warning path in fallback simulation.
- Added classroom case materials (`case_materials/*`) for a Model UN scenario.
- Added output export conventions under `outputs/`.
- Added required disclaimer language: “This is a simulated scenario deliberation, not a factual prediction.”
- Added fallback script: `scripts/run_minisim.py`.

## Known limitations
- In this repository snapshot, upstream MiroFish backend/frontend source may be absent; in that case Docker runs placeholder endpoints plus fallback tooling.
- Docker runtime validation depends on host availability of Docker CLI/daemon.
- Provider connectivity depends on external API availability and valid keys.
- Zep/GraphRAG full behavior cannot be validated without upstream integration and external service credentials.

## Provider compatibility notes
- Use `python scripts/test_provider.py`.
- Script tests JSON mode and plain-text JSON fallback.
- Configure provider-specific `LLM_BASE_URL` in `.env`.

## Explain the framing clearly
Use these phrases:
- scenario simulation
- simulated policy discussion
- plausible negotiation dynamics
- assumption-driven social simulation

Avoid prediction framing. Require the line:
> This is a simulated scenario deliberation, not a factual prediction.

## Reset outputs before class
```bash
find outputs -type f ! -name '.gitkeep' -delete
```

## Testing checklist
- [ ] `docker compose up -d --build` completes
- [ ] Frontend reachable at `localhost:3000`
- [ ] Backend reachable at `localhost:5001`
- [ ] `cp .env.example .env` works
- [ ] `python scripts/test_provider.py` works with at least one provider
- [ ] `python scripts/smoke_test_classroom.py` passes
- [ ] Classroom caps (max 5 agents, max 3 rounds) enforced
- [ ] `python scripts/run_minisim.py` runs and writes outputs
- [ ] No API keys printed or exported

## Security reminders
- **Never commit `.env`.**
- Do not log or share student keys.

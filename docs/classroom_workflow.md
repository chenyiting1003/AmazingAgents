# Classroom workflow

1. Clone repo and copy environment template.
2. Add group API key and provider base URL/model in `.env`.
3. Run smoke checks: `python scripts/smoke_test_classroom.py`.
4. Start Docker stack with `docker compose up -d --build`.
5. Open frontend at `http://localhost:3000` and run a 5-agent, 3-round simulation.
6. If UI path is unavailable/fails, run fallback CLI simulation: `python scripts/run_minisim.py`.
7. Export outputs from `outputs/`.
8. Complete `docs/validity_critique_template.md` in groups.
9. Debrief: treat outputs as simulated policy deliberation, not factual prediction.

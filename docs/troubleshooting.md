# Troubleshooting

## Docker is not running
- Start Docker Desktop first.
- Check with:
  - `docker --version`
  - `docker compose version`

## Port 3000 already in use
- Find and stop process using the port:
  - Linux/macOS: `lsof -i :3000`
- Or map another host port in `docker-compose.yml`.

## Port 5001 already in use
- Find and stop process:
  - Linux/macOS: `lsof -i :5001`

## Missing `.env`
- Create it from template:
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
- Failure note is saved to `outputs/provider_test_raw_response.txt`.

## Zep key missing
- If `ZEP_API_KEY` is missing, classroom fallback mode should continue:
  - `ZEP_API_KEY is missing. Running in reduced-memory classroom mode.`

## Simulation too slow
- Keep classroom defaults (5 agents, 3 rounds).
- Lower output length with `MAX_OUTPUT_TOKENS_PER_CALL`.

## API cost concern
- Use `python scripts/cost_guard.py` to estimate calls.
- Keep short seed material and short outputs.

## Frontend loads but backend fails
- Check backend endpoint: `curl -f http://localhost:5001`
- Review container logs: `docker compose logs -f`

## Backend works but simulation fails
- Confirm provider settings in `.env`.
- Run provider test script.

## Windows path or permission issues
- Run commands in PowerShell as normal user first.
- Ensure Docker Desktop file sharing includes project folder.

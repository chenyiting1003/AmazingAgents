#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env file not found at project root."
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

require_non_empty() {
  local name="$1"
  local value="${!name:-}"
  if [[ -z "$value" || "$value" == "PASTE_YOUR_API_KEY_HERE" || "$value" == "PASTE_YOUR_ZEP_KEY_HERE" ]]; then
    echo "ERROR: $name is missing or placeholder in .env"
    exit 1
  fi
}

require_non_empty "LLM_API_KEY"
require_non_empty "LLM_BASE_URL"
require_non_empty "LLM_MODEL_NAME"

if ! curl -fsS "http://localhost:5001" >/dev/null; then
  echo "ERROR: Backend is not reachable at http://localhost:5001"
  exit 1
fi

if ! curl -fsS "http://localhost:3000" >/dev/null; then
  echo "ERROR: Frontend is not reachable at http://localhost:3000"
  exit 1
fi

echo "Healthcheck passed: .env present, required LLM settings set, and ports 3000/5001 reachable."

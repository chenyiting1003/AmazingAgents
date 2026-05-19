#!/usr/bin/env bash
set -euo pipefail

# Prefer real MiroFish app if present in this repository checkout.
# Fallback to placeholder endpoints only when upstream app code is unavailable.
if [[ -f "backend/main.py" && -d "frontend" ]]; then
  echo "Detected candidate MiroFish backend/frontend. Starting real app workflow."
  python backend/main.py &
  # Generic static fallback if frontend build tooling is unavailable in base image.
  # Instructors should replace this with project-native frontend startup command.
  python -m http.server 3000 --directory frontend
else
  echo "WARNING: Real MiroFish backend/frontend not found in repository."
  echo "Running placeholder classroom endpoints only (not full upstream reproduction)."
  python scripts/mock_backend.py &
  python -m http.server 3000 --directory web
fi

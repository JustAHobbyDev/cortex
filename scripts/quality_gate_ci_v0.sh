#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.uv-cache}"
mkdir -p "$UV_CACHE_DIR"

echo "[quality-gate-ci] 1/4 coach smoke checks"
python3 scripts/cortex_project_coach_v0.py --help >/dev/null
python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate-ci] 2/4 decision gap check"
python3 scripts/cortex_project_coach_v0.py decision-gap-check \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate-ci] 3/4 docs and json integrity"
./scripts/ci_validate_docs_and_json_v0.sh

echo "[quality-gate-ci] 4/4 focused coach tests"
uv run --locked --group dev pytest -q tests/test_coach_*.py

echo "[quality-gate-ci] PASS"

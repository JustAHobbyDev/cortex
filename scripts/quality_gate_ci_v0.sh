#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.uv-cache}"
mkdir -p "$UV_CACHE_DIR"

echo "[quality-gate-ci] 1/6 coach smoke checks"
python3 scripts/cortex_project_coach_v0.py --help >/dev/null
python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate-ci] 2/6 decision gap check"
python3 scripts/cortex_project_coach_v0.py decision-gap-check \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate-ci] 3/6 reflection enforcement gate"
python3 scripts/reflection_enforcement_gate_v0.py \
  --project-dir . \
  --required-decision-status promoted \
  --min-scaffold-reports 1 \
  --min-required-status-mappings 1 \
  --format json >/dev/null

echo "[quality-gate-ci] 4/6 project-state boundary gate"
python3 scripts/project_state_boundary_gate_v0.py \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate-ci] 5/6 docs and json integrity"
./scripts/ci_validate_docs_and_json_v0.sh

echo "[quality-gate-ci] 6/6 focused coach tests"
uv run --locked --group dev pytest -q tests/test_coach_*.py

echo "[quality-gate-ci] PASS"

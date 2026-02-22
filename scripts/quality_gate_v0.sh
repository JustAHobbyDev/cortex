#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.uv-cache}"
mkdir -p "$UV_CACHE_DIR"

echo "[quality-gate] 1/8 audit-needed"
python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json \
  --fail-on-required

echo "[quality-gate] 2/8 coach smoke checks"
python3 scripts/cortex_project_coach_v0.py --help >/dev/null
python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate] 3/8 decision gap check"
python3 scripts/cortex_project_coach_v0.py decision-gap-check \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate] 4/8 reflection enforcement gate"
python3 scripts/reflection_enforcement_gate_v0.py \
  --project-dir . \
  --required-decision-status promoted \
  --min-scaffold-reports 1 \
  --min-required-status-mappings 1 \
  --format json >/dev/null

echo "[quality-gate] 5/8 project-state boundary gate"
python3 scripts/project_state_boundary_gate_v0.py \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate] 6/8 temporal playbook release-surface gate"
python3 scripts/temporal_playbook_release_gate_v0.py \
  --project-dir . \
  --format json >/dev/null

echo "[quality-gate] 7/8 docs and json integrity"
./scripts/ci_validate_docs_and_json_v0.sh

echo "[quality-gate] 8/8 focused coach tests"
uv run --locked --group dev pytest -q tests/test_coach_*.py

echo "[quality-gate] PASS"

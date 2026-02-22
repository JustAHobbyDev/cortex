#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.uv-cache}"
mkdir -p "$UV_CACHE_DIR"

run_quiet() {
  local label="$1"
  shift
  local log_file
  log_file="$(mktemp)"
  if ! "$@" >"$log_file" 2>&1; then
    echo "[quality-gate-ci] FAIL: ${label}"
    cat "$log_file"
    rm -f "$log_file"
    return 1
  fi
  rm -f "$log_file"
}

echo "[quality-gate-ci] 1/7 coach smoke checks"
run_quiet "coach help" python3 scripts/cortex_project_coach_v0.py --help
run_quiet "audit-needed smoke" python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json

echo "[quality-gate-ci] 2/7 decision gap check"
run_quiet "decision-gap-check" python3 scripts/cortex_project_coach_v0.py decision-gap-check \
  --project-dir . \
  --format json

echo "[quality-gate-ci] 3/7 reflection enforcement gate"
run_quiet "reflection_enforcement_gate_v0.py" python3 scripts/reflection_enforcement_gate_v0.py \
  --project-dir . \
  --required-decision-status promoted \
  --min-scaffold-reports 1 \
  --min-required-status-mappings 1 \
  --format json

echo "[quality-gate-ci] 4/7 project-state boundary gate"
run_quiet "project_state_boundary_gate_v0.py" python3 scripts/project_state_boundary_gate_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate-ci] 5/7 temporal playbook release-surface gate"
run_quiet "temporal_playbook_release_gate_v0.py" python3 scripts/temporal_playbook_release_gate_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate-ci] 6/7 docs and json integrity"
./scripts/ci_validate_docs_and_json_v0.sh

echo "[quality-gate-ci] 7/7 focused coach tests"
uv run --locked --group dev pytest -q tests/test_coach_*.py

echo "[quality-gate-ci] PASS"

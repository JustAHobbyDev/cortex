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
    echo "[quality-gate] FAIL: ${label}"
    cat "$log_file"
    rm -f "$log_file"
    return 1
  fi
  rm -f "$log_file"
}

echo "[quality-gate] 1/10 quality gate sync check"
run_quiet "quality_gate_sync_check_v0.py" python3 scripts/quality_gate_sync_check_v0.py \
  --ci-script scripts/quality_gate_ci_v0.sh \
  --local-script scripts/quality_gate_v0.sh \
  --format json

echo "[quality-gate] 2/10 audit-needed"
run_quiet "audit-needed --fail-on-required" python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json \
  --fail-on-required

echo "[quality-gate] 3/10 coach smoke checks"
run_quiet "coach help" python3 scripts/cortex_project_coach_v0.py --help
run_quiet "audit-needed smoke" python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json

echo "[quality-gate] 4/10 decision gap check"
run_quiet "decision-gap-check" python3 scripts/cortex_project_coach_v0.py decision-gap-check \
  --project-dir . \
  --format json

echo "[quality-gate] 5/10 reflection enforcement gate"
run_quiet "reflection_enforcement_gate_v0.py" python3 scripts/reflection_enforcement_gate_v0.py \
  --project-dir . \
  --required-decision-status promoted \
  --min-scaffold-reports 1 \
  --min-required-status-mappings 1 \
  --format json

echo "[quality-gate] 6/10 mistake provenance gate"
run_quiet "mistake_candidate_gate_v0.py" python3 scripts/mistake_candidate_gate_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate] 7/10 project-state boundary gate"
run_quiet "project_state_boundary_gate_v0.py" python3 scripts/project_state_boundary_gate_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate] 8/10 temporal playbook release-surface gate"
run_quiet "temporal_playbook_release_gate_v0.py" python3 scripts/temporal_playbook_release_gate_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate] 9/10 docs and json integrity"
./scripts/ci_validate_docs_and_json_v0.sh

echo "[quality-gate] 10/10 focused coach tests"
uv run --locked --group dev pytest -q tests/test_coach_*.py

echo "[quality-gate] PASS"

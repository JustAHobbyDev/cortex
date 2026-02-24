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

echo "[quality-gate] 1/11 quality gate sync check"
run_quiet "quality_gate_sync_check_v0.py" python3 scripts/quality_gate_sync_check_v0.py \
  --ci-script scripts/quality_gate_ci_v0.sh \
  --local-script scripts/quality_gate_v0.sh \
  --format json

echo "[quality-gate] 2/11 audit-needed"
run_quiet "audit-needed --fail-on-required" python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json \
  --fail-on-required

echo "[quality-gate] 3/11 coach smoke checks"
run_quiet "coach help" python3 scripts/cortex_project_coach_v0.py --help
run_quiet "audit-needed smoke" python3 scripts/cortex_project_coach_v0.py audit-needed \
  --project-dir . \
  --format json

echo "[quality-gate] 4/11 decision gap check"
run_quiet "decision-gap-check" python3 scripts/cortex_project_coach_v0.py decision-gap-check \
  --project-dir . \
  --format json

echo "[quality-gate] 5/11 phase4 enforcement blocking harness"
run_quiet "phase4_enforcement_blocking_harness_v0.py" python3 scripts/phase4_enforcement_blocking_harness_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate] 6/11 reflection enforcement gate"
run_quiet "reflection_enforcement_gate_v0.py" python3 scripts/reflection_enforcement_gate_v0.py \
  --project-dir . \
  --required-decision-status promoted \
  --min-scaffold-reports 1 \
  --min-required-status-mappings 1 \
  --require-phase4-enforcement-report \
  --phase4-enforcement-report .cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json \
  --format json

echo "[quality-gate] 7/11 mistake provenance gate"
run_quiet "mistake_candidate_gate_v0.py" python3 scripts/mistake_candidate_gate_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate] 8/11 project-state boundary gate"
run_quiet "project_state_boundary_gate_v0.py" python3 scripts/project_state_boundary_gate_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate] 9/11 temporal playbook release-surface gate"
run_quiet "temporal_playbook_release_gate_v0.py" python3 scripts/temporal_playbook_release_gate_v0.py \
  --project-dir . \
  --format json

echo "[quality-gate] 10/11 docs and json integrity"
./scripts/ci_validate_docs_and_json_v0.sh

echo "[quality-gate] 11/11 focused coach tests"
if [[ "${CORTEX_QG_SKIP_FOCUSED_TESTS:-0}" == "1" ]]; then
  echo "[quality-gate] focused coach tests skipped (CORTEX_QG_SKIP_FOCUSED_TESTS=1)"
else
  uv run --locked --group dev pytest -q \
    tests/test_coach_decision_gap_check.py \
    tests/test_coach_reflection_enforcement_gate.py \
    tests/test_coach_context_load.py \
    tests/test_coach_quality_gate_sync_check.py \
    tests/test_phase4_enforcement_blocking_harness.py \
    tests/test_phase4_governance_debt_harness.py
fi

echo "[quality-gate] PASS"

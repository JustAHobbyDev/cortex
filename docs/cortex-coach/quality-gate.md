# Quality Gate

Use two deterministic commands:
- strict local maintainer gate
- CI correctness gate
- release-grade full matrix gate

Both gates run tests from the locked `dev` dependency group in `pyproject.toml` via `uv.lock`.
Gate scripts set `UV_CACHE_DIR` to a repo-local `.uv-cache/` by default to avoid host-level cache permission issues.

## Run

Preferred:

```bash
just quality-gate
```

Fallback without `just`:

```bash
./scripts/quality_gate_v0.sh
```

CI mode:

```bash
just quality-gate-ci
```

Fallback:

```bash
./scripts/quality_gate_ci_v0.sh
```

Release-grade full matrix mode:

```bash
./scripts/quality_gate_ci_full_v0.sh
```

## What It Checks

`quality-gate` (strict local):

1. `quality_gate_sync_check_v0.py` (fail if local/CI shared gate bundle drifts)
2. `audit-needed` with fail-on-required behavior
3. `decision-gap-check` for governance-impacting dirty files
4. `context_hydration_gate_v0.py compliance` (fail-closed hydration invariant coverage for `new_session` + `window_rollover` + `pre_closeout`)
5. `phase4_enforcement_blocking_harness_v0.py` deterministic enforcement block-rate verification
6. `reflection_enforcement_gate_v0.py` fail-closed checks:
   - no vacuous reflection pass (`min_scaffold_reports >= 1`)
   - required promoted mappings (`min_required_status_mappings >= 1`)
   - governance-impact decision matches must carry valid `reflection_id` + `reflection_report`
7. `mistake_candidate_gate_v0.py` fail-closed check:
   - machine-caught claims require schema-compliant provenance payloads
   - unsupported confidence/status values are blocking
   - legacy unknown provenance must carry migration metadata
8. `project_state_boundary_gate_v0.py` fail-closed check:
   - project-state files are forbidden outside `.cortex/` (`reports/` root blocked by default)
   - expired active waivers are blocking
9. `temporal_playbook_release_gate_v0.py` fail-closed check:
   - unmanaged `playbooks/cortex_*.md` candidates are blocking
   - expired active temporal entries are blocking
   - retired residue in `playbooks/` is blocking
10. docs local-link + JSON integrity
11. focused `cortex-coach` pytest suite:
   - `tests/test_coach_decision_gap_check.py`
   - `tests/test_coach_reflection_enforcement_gate.py`
   - `tests/test_coach_context_load.py`
   - `tests/test_coach_quality_gate_sync_check.py`

`quality-gate-ci`:

1. `quality_gate_sync_check_v0.py` (fail if local/CI shared gate bundle drifts)
2. `decision-gap-check` for governance-impacting dirty files
3. `context_hydration_gate_v0.py compliance` with block-mode thresholds
4. `phase4_enforcement_blocking_harness_v0.py` deterministic enforcement block-rate verification
5. `reflection_enforcement_gate_v0.py` with promoted-status thresholds
6. `mistake_candidate_gate_v0.py` with contract-driven provenance checks
7. `project_state_boundary_gate_v0.py` with contract-driven path checks
8. `temporal_playbook_release_gate_v0.py` with contract-driven release-surface checks
9. docs local-link + JSON integrity
10. focused `cortex-coach` pytest suite:
   - `tests/test_coach_decision_gap_check.py`
   - `tests/test_coach_reflection_enforcement_gate.py`
   - `tests/test_coach_context_load.py`
   - `tests/test_coach_quality_gate_sync_check.py`

`quality-gate-ci-full`:

1. executes `quality-gate-ci` (required checks)
2. executes full coach matrix (`uv run --locked --group dev pytest -q tests/test_coach_*.py`)

## When to Run

- `quality-gate` before merge/release in local maintainer flow
- `quality-gate-ci` in GitHub Actions (and optional local CI parity checks)
- `quality-gate-ci-full` for release-grade full test coverage

## Phase 3 Adapter Operational Add-On

`quality-gate-ci` remains the merge/release boundary authority even when adapter enrichment is unhealthy.
Adapter degradation must never be treated as a release-gate bypass condition.

For adapter-enabled release candidates, run this deterministic validation pack in addition to `quality-gate-ci`:

1. `python3 scripts/phase3_adapter_degradation_harness_v0.py --project-dir . --coach-bin cortex-coach`
2. `python3 scripts/phase3_governance_regression_harness_v0.py --project-dir . --coach-bin cortex-coach`
3. `python3 scripts/phase3_adapter_performance_pack_v0.py --project-dir . --coach-bin cortex-coach`

Required artifact outcomes:
- `.cortex/reports/project_state/phase3_adapter_degradation_report_v0.json`: `summary.pass=true`
- `.cortex/reports/project_state/phase3_adapter_determinism_report_v0.json`: `summary.pass=true`
- `.cortex/reports/project_state/phase3_governance_regression_report_v0.md`: `Status: Pass`
- `.cortex/reports/project_state/phase3_adapter_latency_report_v0.json`: `target_met=true`
- `.cortex/reports/project_state/phase3_adapter_budget_report_v0.json`: `target_met=true`
- `.cortex/reports/project_state/phase3_ci_overhead_report_v0.json`: `target_met=true`

## Phase 5 Rollout Operational Add-On

When executing rollout migration toward Gate F, run these checks in addition to required gate baseline.
Commands 3-5 are implemented in Phase 5 cycle/reliability and adoption packs.

1. `python3 scripts/cortex_project_coach_v0.py rollout-mode --project-dir . --format json`
2. `python3 scripts/cortex_project_coach_v0.py rollout-mode-audit --project-dir . --format json`
3. `python3 scripts/phase5_rollout_reliability_pack_v0.py --project-dir . --cycle-id cycle1`
4. `python3 scripts/phase5_rollout_reliability_pack_v0.py --project-dir . --cycle-id cycle2`
5. `python3 scripts/phase5_rollout_adoption_pack_v0.py --project-dir .`

Required Phase 5 artifact outcomes:
- `.cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json`: `status=pass`
- `.cortex/reports/project_state/phase5_cycle1_rollout_reliability_report_v0.json`: all required checks pass
- `.cortex/reports/project_state/phase5_cycle2_rollout_reliability_report_v0.json`: all required checks pass
- `.cortex/reports/project_state/phase5_reference_implementation_report_v0.md`: at least two reference implementations documented

## Phase 1 Storage/Locking Checks (Design Baseline)

Phase 1 requires deterministic storage/locking validation coverage for tactical mutation commands.
These checks are design baseline requirements and should be implemented as focused contract tests.

Required deterministic cases:

1. Lock acquisition timeout behavior:
- competing mutation request returns stable lock conflict class (`exit code 4`) after timeout.

2. Stale-lock behavior:
- stale lock reclaim path is deterministic and auditable using configured stale threshold.
- non-stale locks are not reclaimed without explicit force-unlock.

3. Concurrent mutation serialization:
- only one mutation acquires writer lock.
- other concurrent mutation attempts block/fail deterministically with no partial writes.

4. Read visibility during mutation:
- concurrent reads return last committed snapshot, never partial mutation state.

5. Idempotent retry behavior:
- re-running same mutation intent after uncertain completion does not duplicate writes.
- retry outcome class is stable (`applied`, `no_op_idempotent`, or lock conflict).

6. Failure recovery integrity:
- simulated interruption does not corrupt tactical indexes.
- subsequent mutation/read operations recover deterministically.

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
3. `cortex-coach` smoke commands
4. `decision-gap-check` for governance-impacting dirty files
5. `reflection_enforcement_gate_v0.py` fail-closed checks:
   - no vacuous reflection pass (`min_scaffold_reports >= 1`)
   - required promoted mappings (`min_required_status_mappings >= 1`)
   - governance-impact decision matches must carry valid `reflection_id` + `reflection_report`
6. `mistake_candidate_gate_v0.py` fail-closed check:
   - machine-caught claims require schema-compliant provenance payloads
   - unsupported confidence/status values are blocking
   - legacy unknown provenance must carry migration metadata
7. `project_state_boundary_gate_v0.py` fail-closed check:
   - project-state files are forbidden outside `.cortex/` (`reports/` root blocked by default)
   - expired active waivers are blocking
8. `temporal_playbook_release_gate_v0.py` fail-closed check:
   - unmanaged `playbooks/cortex_*.md` candidates are blocking
   - expired active temporal entries are blocking
   - retired residue in `playbooks/` is blocking
9. docs local-link + JSON integrity
10. focused `cortex-coach` pytest suite:
   - `tests/test_coach_decision_gap_check.py`
   - `tests/test_coach_reflection_enforcement_gate.py`
   - `tests/test_coach_context_load.py`
   - `tests/test_coach_quality_gate_sync_check.py`

`quality-gate-ci`:

1. `quality_gate_sync_check_v0.py` (fail if local/CI shared gate bundle drifts)
2. `cortex-coach` smoke commands
3. `decision-gap-check` for governance-impacting dirty files
4. `reflection_enforcement_gate_v0.py` with promoted-status thresholds
5. `mistake_candidate_gate_v0.py` with contract-driven provenance checks
6. `project_state_boundary_gate_v0.py` with contract-driven path checks
7. `temporal_playbook_release_gate_v0.py` with contract-driven release-surface checks
8. docs local-link + JSON integrity
9. focused `cortex-coach` pytest suite:
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

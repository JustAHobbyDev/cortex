# Quality Gate

Use two deterministic commands:
- strict local maintainer gate
- CI correctness gate

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
6. `project_state_boundary_gate_v0.py` fail-closed check:
   - project-state files are forbidden outside `.cortex/` (`reports/` root blocked by default)
   - expired active waivers are blocking
7. `temporal_playbook_release_gate_v0.py` fail-closed check:
   - unmanaged `playbooks/cortex_*.md` candidates are blocking
   - expired active temporal entries are blocking
   - retired residue in `playbooks/` is blocking
8. docs local-link + JSON integrity
9. focused `cortex-coach` pytest suite

`quality-gate-ci`:

1. `quality_gate_sync_check_v0.py` (fail if local/CI shared gate bundle drifts)
2. `cortex-coach` smoke commands
3. `decision-gap-check` for governance-impacting dirty files
4. `reflection_enforcement_gate_v0.py` with promoted-status thresholds
5. `project_state_boundary_gate_v0.py` with contract-driven path checks
6. `temporal_playbook_release_gate_v0.py` with contract-driven release-surface checks
7. docs local-link + JSON integrity
8. focused `cortex-coach` pytest suite

## When to Run

- `quality-gate` before merge/release in local maintainer flow
- `quality-gate-ci` in GitHub Actions (and optional local CI parity checks)

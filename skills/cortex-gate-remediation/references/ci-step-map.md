# Quality Gate CI Step Map

## Step map from `scripts/quality_gate_ci_v0.sh`

1. `quality_gate_sync_check_v0.py`
2. `decision-gap-check`
3. `context_hydration_gate_v0.py compliance`
4. `phase4_enforcement_blocking_harness_v0.py`
5. `reflection_enforcement_gate_v0.py`
6. `mistake_candidate_gate_v0.py`
7. `project_state_boundary_gate_v0.py`
8. `temporal_playbook_release_gate_v0.py`
9. `./scripts/ci_validate_docs_and_json_v0.sh`
10. focused pytest bundle

## Targeted reproduction commands

Use the matching command from `scripts/quality_gate_ci_v0.sh` directly, not the full gate, until green.

Example:

```bash
python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir . --format json
```

Then:

```bash
./scripts/quality_gate_ci_v0.sh
```

## Common cleanup command

```bash
git restore .cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json
```

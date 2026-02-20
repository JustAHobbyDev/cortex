# Commands

Examples below use installed CLI form (`cortex-coach`).
Fallback: `uv run python3 scripts/cortex_project_coach_v0.py ...`

## `init`

Bootstrap `.cortex/` artifacts in a target project.

```bash
cortex-coach init \
  --project-dir /path/to/project \
  --project-id my_project \
  --project-name "My Project"
```

Key options:

- `--force`: overwrite existing bootstrap artifacts
- `--lock-timeout-seconds <n>`
- `--lock-stale-seconds <n>`
- `--force-unlock`

## `audit`

Validate lifecycle artifacts and emit a health report.

```bash
cortex-coach audit \
  --project-dir /path/to/project
```

Output:

- `.cortex/reports/lifecycle_audit_v0.json`

## `coach`

Run one lifecycle guidance cycle.

```bash
cortex-coach coach \
  --project-dir /path/to/project
```

Outputs:

- `.cortex/reports/coach_cycle_<timestamp>_v0.json`
- `.cortex/reports/coach_cycle_<timestamp>_v0.md`
- `.cortex/prompts/coach_cycle_prompt_<timestamp>_v0.md`

### `coach --apply`

Generate draft `vN+1` artifact files for eligible actions.

```bash
cortex-coach coach \
  --project-dir /path/to/project \
  --apply
```

### `coach --apply-scope`

Limit draft generation to:

- `direction`
- `governance`
- `design`

Example:

```bash
cortex-coach coach \
  --project-dir /path/to/project \
  --apply \
  --apply-scope direction,design
```

# Cortex Project Coach Runbook v0

## Purpose

Operational guide for using the Project Coach application to:
- bootstrap Cortex artifacts in a new project
- maintain lifecycle integrity via repeatable audits

## Commands

### 1) Initialize a new project

```bash
uv run python3 scripts/cortex_project_coach_v0.py init \
  --project-dir /path/to/project \
  --project-id admin_dash \
  --project-name "Admin Dashboard"
```

Or:

```bash
just coach-init /path/to/project admin_dash "Admin Dashboard"
```

Lock controls (optional):
- `--lock-timeout-seconds <n>`
- `--lock-stale-seconds <n>`
- `--force-unlock`

Expected artifacts in target project:
- `.cortex/manifest_v0.json`
- `.cortex/artifacts/direction_<project_id>_v0.md`
- `.cortex/artifacts/governance_<project_id>_v0.md`
- `.cortex/artifacts/design_<project_id>_v0.dsl`
- `.cortex/artifacts/design_<project_id>_v0.json`
- `.cortex/prompts/project_coach_prompt_<project_id>_v0.md`

### 2) Audit lifecycle health

```bash
uv run python3 scripts/cortex_project_coach_v0.py audit \
  --project-dir /path/to/project
```

Or:

```bash
just coach-audit /path/to/project
```

Expected report:
- `.cortex/reports/lifecycle_audit_v0.json`

Return code:
- `0` on pass
- `1` on fail

### 3) Run one coaching cycle (AI handoff artifacts)

```bash
uv run python3 scripts/cortex_project_coach_v0.py coach \
  --project-dir /path/to/project
```

Or:

```bash
just coach-cycle /path/to/project
```

Expected outputs:
- `.cortex/reports/coach_cycle_<timestamp>_v0.json`
- `.cortex/reports/coach_cycle_<timestamp>_v0.md`
- `.cortex/prompts/coach_cycle_prompt_<timestamp>_v0.md`

Use `--no-sync-phases` to avoid automatic manifest phase syncing.

Auto-generate draft artifacts for actions:

```bash
uv run python3 scripts/cortex_project_coach_v0.py coach \
  --project-dir /path/to/project \
  --apply
```

`--apply` creates draft `vN+1` files for action targets under `.cortex/artifacts/` and records applied/skipped draft results in the cycle report JSON/MD.

Limit draft generation to specific artifact classes:

```bash
uv run python3 scripts/cortex_project_coach_v0.py coach \
  --project-dir /path/to/project \
  --apply \
  --apply-scope direction,design
```

Or:

```bash
just coach-cycle-apply /path/to/project direction,design
```

Valid scopes: `direction`, `governance`, `design`.

### 4) Sequential maintainer flow (fail-fast)

```bash
just coach-maintainer-sequence /path/to/project admin_dash "Admin Dashboard"
```

### 5) Optional re-bootstrap (force)

```bash
uv run python3 scripts/cortex_project_coach_v0.py init \
  --project-dir /path/to/project \
  --project-id admin_dash \
  --project-name "Admin Dashboard" \
  --force
```

## Lifecycle Routine

1. Run `init` once at project start.
2. Edit direction/governance/design artifacts as the project evolves.
3. Run `coach` each planning/review cycle to generate AI-guided next actions.
4. Re-run `audit` at milestones (planning, pre-release, post-release).
5. Treat audit failures as blockers for artifact hygiene.

## Failure Handling

- If `design_schema_validation` fails:
  - edit `.cortex/artifacts/design_<project_id>_v0.dsl`
  - recompile through `init --force` or compile manually with:
    ```bash
    uv run python3 scripts/design_prompt_dsl_compile_v0.py \
      --dsl-file /path/to/project/.cortex/artifacts/design_<project_id>_v0.dsl \
      --out-file /path/to/project/.cortex/artifacts/design_<project_id>_v0.json
    ```
  - rerun `audit`

- If manifest parsing/version fails:
  - restore `.cortex/manifest_v0.json` to valid JSON with `version: "v0"`
  - rerun `audit`

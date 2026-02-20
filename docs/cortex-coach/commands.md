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

## `audit-needed`

Determine whether an audit should run now based on dirty-file risk tiers.

```bash
cortex-coach audit-needed \
  --project-dir /path/to/project
```

JSON mode + CI-friendly fail behavior:

```bash
cortex-coach audit-needed \
  --project-dir /path/to/project \
  --format json \
  --fail-on-required
```

Optional report output:

```bash
cortex-coach audit-needed \
  --project-dir /path/to/project \
  --out-file .cortex/reports/audit_needed_v0.json
```

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

## `context-load`

Generate a bounded context bundle for agent handoff.

```bash
cortex-coach context-load \
  --project-dir /path/to/project \
  --task "design drift" \
  --max-files 10 \
  --max-chars-per-file 2000 \
  --fallback-mode priority
```

Optional file output:

```bash
cortex-coach context-load \
  --project-dir /path/to/project \
  --task "governance updates" \
  --out-file .cortex/reports/agent_context_bundle_v0.json
```

`--fallback-mode priority` enables a fallback chain:
1. restricted budget
2. relaxed budget
3. unrestricted (no file/char limits) if prior levels fail

## `context-policy`

Analyze repository shape and recommend task focus + context budgets.

```bash
cortex-coach context-policy \
  --project-dir /path/to/project \
  --format json \
  --out-file .cortex/reports/context_policy_v0.json
```

## `policy-enable`

Enable an opt-in policy file inside the target project.

```bash
cortex-coach policy-enable \
  --project-dir /path/to/project \
  --policy usage-decision
```

Default output path:
- `.cortex/policies/cortex_coach_usage_decision_policy_v0.md`

Optional overwrite:

```bash
cortex-coach policy-enable \
  --project-dir /path/to/project \
  --policy usage-decision \
  --force
```

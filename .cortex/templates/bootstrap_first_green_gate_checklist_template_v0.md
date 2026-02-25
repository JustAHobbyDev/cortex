# Bootstrap First Green Gate Checklist Template v0

Version: v0
Date: <YYYY-MM-DD>
Project: <project_name> (<project_id>)

## Goal

Reach first required green gate in a new project with deterministic governance setup.

## Sequence

1. Confirm bootstrap contract artifacts exist under `.cortex/`.
2. Run risk gate:
   - `cortex-coach audit-needed --project-dir . --format json`
3. If `audit_required=true`, run coaching + audit:
   - `cortex-coach coach --project-dir .`
   - `cortex-coach audit --project-dir .`
4. Run required CI-aligned gate bundle:
   - `./scripts/quality_gate_ci_v0.sh`

## Exit Criteria

1. Required governance gate bundle passes.
2. No unresolved decision gaps for governance-impacting paths.
3. Hydration and boundary enforcement checks pass in block mode.

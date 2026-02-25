# Cortex Phase 5 Migration Playbook v0

Version: v0  
Status: Active  
Date: 2026-02-25  
Scope: Operator playbook for rollout-mode migration and Gate F handoff

## Purpose

Provide a deterministic operator workflow for progressing from `experimental` toward `default` without weakening governance controls.

## Preconditions

1. Phase 4 Gate E closeout is pass (`.cortex/reports/project_state/phase4_gate_e_measurement_closeout_v0.md`).
2. Rollout mode baseline artifacts exist:
- `contracts/rollout_mode_contract_v0.md`
- `policies/rollout_mode_policy_v0.md`
3. Required governance release-boundary checks are green on current branch.

## Migration Workflow

### Step 1: Baseline capture

1. `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all --format json`
2. `python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir . --format json`
3. `python3 scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`
4. `./scripts/quality_gate_ci_v0.sh`

Record outputs under `.cortex/reports/project_state/phase5_*`.

### Step 2: Rollout mode drill

1. Read current mode:
- `python3 scripts/cortex_project_coach_v0.py rollout-mode --project-dir . --format json`
2. Execute deterministic drill transitions:
- `... rollout-mode --set-mode off --changed-by <actor> --reason "<reason>" --format json`
- `... rollout-mode --set-mode experimental --changed-by <actor> --reason "<reason>" --incident-ref <incident_ref> --format json`
3. Validate transition audit:
- `python3 scripts/cortex_project_coach_v0.py rollout-mode-audit --project-dir . --format json`

### Step 3: Reliability cycle execution

Run Cycle 1 and Cycle 2 packs:

1. `python3 scripts/phase5_rollout_reliability_pack_v0.py --project-dir . --cycle-id cycle1`
2. `python3 scripts/phase5_rollout_reliability_pack_v0.py --project-dir . --cycle-id cycle2`

Required:
- both cycle reliability reports pass
- both cycle governance regression reports pass
- stop-rule incident count remains `0`

### Step 4: Reference implementation verification

1. Execute adoption pack:
- `python3 scripts/phase5_rollout_adoption_pack_v0.py --project-dir .`
2. Confirm:
- reference implementation coverage `>=2`
- operator overhead target within threshold
- transition audit completeness remains `100%`

### Step 5: Default-mode decision gate

Before proposing `experimental -> default`:

1. Create/promote linked governance decision and reflection artifacts.
2. Link Gate F closeout evidence.
3. Perform Maintainer Council review.
4. Apply mode transition with linkage metadata:
- `... rollout-mode --set-mode default --decision-refs <...> --reflection-refs <...> --audit-refs <...> ...`

## Rollback Procedure

If any stop-rule is triggered:

1. Transition to `experimental` or `off` immediately.
2. Attach incident reference in transition metadata.
3. Run stabilization cycle:
- `audit --all`
- `decision-gap-check`
- `reflection_enforcement_gate_v0.py`
- `quality_gate_ci_v0.sh`
4. Record incident summary in project-state reports before resuming rollout work.

## Operator Handoff Checklist

1. Current rollout mode and last transition id are documented.
2. Latest `phase5_mode_transition_audit_report_v0.json` is present and pass.
3. Latest cycle reliability artifacts are present and pass.
4. Active residual risks have owners and dates.
5. Next planned action is recorded in phase board and linked artifacts.

# Client Onboarding Pilot Calibration Report v0

Version: v0  
Status: Complete (Calibration Findings Open)  
Date: 2026-02-25  
Ticket: `CT-005`  
Reference project: internal Cortex reference worktree (`cortex-main-worktree-2026-02-25`)

## Purpose

Validate onboarding module timing, failure modes, and rubric thresholds using one internal reference project before external rollout.

## Evidence Artifacts

1. `.cortex/reports/project_state/client_onboarding_pilot_calibration_data_v0.json`
2. `.cortex/reports/project_state/client_onboarding_pilot_command_runs_v0.ndjson`
3. `contracts/client_onboarding_certification_scorecard_schema_v0.json`
4. `docs/cortex-coach/client_training_labs_v0.md`

## Pilot Summary

Total commands executed: `24`  
Pass: `13`  
Fail: `11`  
Total measured wall time: `21.888s`  
Median command time: `0.353s`

## Module Timing and Outcome

| Module | Commands | Pass | Fail | Total Time (ms) | Median (ms) | Outcome |
|---|---:|---:|---:|---:|---:|---|
| M2 | 8 | 5 | 3 | 10760 | 353 | Partial pass; `audit --format json` compatibility issue + environment bootstrap failure in clean worktree run. |
| M3 | 5 | 4 | 1 | 2679 | 356 | Partial pass; reflection enforcement correctly fails when `reflection_report` linkage is invalid/missing. |
| M4 | 4 | 0 | 4 | 1238 | 304 | Blocked; installed `cortex-coach` command surface lacks `rollout-mode` and `rollout-mode-audit`. |
| M5 | 7 | 4 | 3 | 7211 | 382 | Partial pass; repeats audit format issue, reflection linkage failure mode, and clean-env quality gate dependency bootstrap failure. |

## Validated Failure Modes

1. `audit --format json` is not supported by the currently installed `cortex-coach` binary.
2. `rollout-mode` / `rollout-mode-audit` are unavailable on the currently installed `cortex-coach` binary.
3. Reflection enforcement gate fails closed when a promoted decision references a non-existent `reflection_report`.
4. Clean-worktree `quality_gate_ci_v0.sh` can fail if dependencies are not pre-provisioned (in this environment, network-restricted dependency fetch failed).

## Rubric Threshold Calibration

A reference scorecard instance was validated against `contracts/client_onboarding_certification_scorecard_schema_v0.json`.

Observed calibration result:

1. Weighted score `84.8` vs required minimum `85.0` -> fail by score.
2. `operational_reliability` scored `78` vs minimum `85` -> category fail.
3. Hard fail condition `rollback_drill_failed=true` -> overall fail.

Calibration conclusion: current rubric thresholds are appropriately strict and correctly prevent certification when rollout/operational reliability is not ready.

## Readiness Decision

`CT-005` is complete as a calibration activity, but external onboarding rollout remains conditional on remediation of the blocking compatibility and environment prerequisites.

## Required Remediations for CT-006

1. Add command-surface preflight checks for onboarding labs (verify `audit --format json`, `rollout-mode`, and `rollout-mode-audit` support before M2/M4 start).
2. Define and enforce supported `cortex-coach` minimum version/capability contract for client onboarding.
3. Add deterministic dependency bootstrap/offline cache guidance so quality-gate execution is reproducible in clean environments.
4. Add explicit M3 verification step that `reflection_report` path exists before decision promotion.

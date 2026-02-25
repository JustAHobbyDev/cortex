# Rollout Mode Policy v0

Version: v0  
Status: Active  
Scope: governance rules for rollout-mode transitions and default-mode eligibility

## Purpose

Enforce governance-controlled rollout progression so tactical defaults cannot be activated without explicit evidence, reversible controls, and audit traceability.

## Policy Rules

1. Governance authority
- Rollout mode changes are governance decisions, not runtime-only toggles.
- Runtime support is necessary but insufficient for default-mode activation.

2. Allowed modes
- Only `off`, `experimental`, and `default` are valid rollout modes.
- Unknown mode values are invalid and must fail closed.

3. Default-mode guardrail
- `default` is forbidden unless Gate F closeout exists and is linked to promoted decision + reflection artifacts.
- Absence of linkage metadata is a blocking condition.

4. Rollback readiness
- Rollback from `default` to `experimental` or `off` must remain available at all times.
- Rollback transitions require explicit incident/recovery rationale.

5. Auditability
- Every mode transition must be appended to project-local transition history within project boundary root.
- Transition history records must include actor, timestamp, reason, and linkage metadata.

6. Governance gate continuity
- Required governance release-boundary checks remain mandatory in all rollout modes.
- Rollout mode must not bypass decision/reflection/audit boundary checks.

7. Experimental baseline
- Until Gate F closeout is published and approved, effective mode must remain `experimental`.

## Roles and Ownership

- `Maintainer Council`:
  - approves `default` mode transition decisions.
  - approves policy-level changes to rollout semantics.
- `Runtime Reliability Lead`:
  - operates runtime mode controls and transition logging.
  - executes rollback and stabilization actions when stop-rules trigger.
- `CI/Gate Owner`:
  - verifies mode-transition audit completeness.
  - verifies required governance gate continuity under each mode.

## Enforcement

- Local/CI checks may enforce this policy through runtime audit reports and policy gates.
- Missing required linkage or malformed transition metadata is blocking for rollout progression.
- Emergency rollback execution is allowed immediately but must be followed by auditable transition records.

## Evidence and Artifacts

- Contract source: `contracts/rollout_mode_contract_v0.md`
- Runtime transition audit artifact: `.cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json`
- Gate F closeout artifact: `.cortex/reports/project_state/phase5_gate_f_measurement_closeout_v0.md`

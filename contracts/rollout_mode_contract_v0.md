# Rollout Mode Contract v0

Canonical: true

Version: v0  
Status: Draft  
Scope: Phase 5 rollout control semantics for `off`, `experimental`, and `default` modes

## Purpose

Define deterministic rollout-mode behavior and transition requirements so default-mode activation remains governance-controlled, reversible, and auditable.

## Contract Sources

- `playbooks/cortex_phase5_rollout_migration_ticket_breakdown_v0.md`
- `playbooks/cortex_phase5_measurement_plan_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `policies/rollout_mode_policy_v0.md`
- `specs/cortex_project_coach_spec_v0.md`

## Mode Definitions

### `off`

- Tactical acceleration features are disabled.
- Required governance release-boundary gates remain active.
- Intended for incident stabilization and recovery windows.

### `experimental`

- Tactical features may run behind explicit controls.
- Required governance release-boundary gates remain active and authoritative.
- This is the baseline operating mode before Gate F closeout.

### `default`

- Tactical features are enabled by default under established policy controls.
- Governance gates remain mandatory; default mode does not relax governance authority.
- Entry into `default` requires Gate F closeout and linked governance decision artifacts.

## Transition Contract

State is represented by:

- current mode (`off`, `experimental`, `default`)
- transition timestamp
- transition actor
- transition rationale metadata
- linkage metadata (decision, reflection, and audit references)

Transition records must be append-only and deterministic in ordering.

## Transition Preconditions

For all transitions:

- transition actor and reason are required.
- transition event must be recorded in mode-transition audit trail.

Additional preconditions for `-> default`:

- at least one linked promoted decision reference.
- at least one linked reflection scaffold/report reference.
- at least one linked required-gate audit reference.
- Gate F readiness evidence present.

Additional preconditions for `default -> experimental|off`:

- rollback reason and incident/recovery reference required.
- stabilization-cycle expectation recorded.

## Rollback and Kill-Switch Semantics

- Rollback chain must remain valid: `default -> experimental -> off`.
- Emergency rollback must be executable without external adapter dependency.
- Rollback transitions are auditable and must preserve required governance gate behavior.

## Audit Completeness Requirements

Mode-transition audit output must include:

- total transition count
- transition completeness rate
- missing linkage findings by transition id
- per-transition `from_mode`/`to_mode` values
- timestamp and actor metadata

Audit completeness target for Gate F: `100%`.

## Determinism and Compatibility Requirements

- Identical mode-transition input and state must produce identical normalized JSON output.
- Omitted optional flags must preserve backward-compatible behavior.
- JSON output must remain parseable and machine-evaluable for CI and governance automation.

## Phase 5 Binding

This contract is normative for:

- `PH5-001` rollout-mode baseline policy/spec alignment
- `PH5-002` runtime mode controls and audit integration
- Gate F rollout readiness evaluation in `playbooks/cortex_phase5_measurement_plan_v0.md`

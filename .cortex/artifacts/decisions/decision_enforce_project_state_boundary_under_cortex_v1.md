# Decision: Enforce project-state boundary under .cortex

DecisionID: dec_20260222T063136Z_enforce_project_state_bo
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-22T06:31:36Z
PromotedAt: 2026-02-22T06:31:41Z
ImpactScope: governance, policy, workflow, ci, tooling, docs
LinkedArtifacts:
- `.cortex/policies/project_state_boundary_waivers_v0.json`
- `.cortex/reports/project_state_boundary_migration_v0.md`
- `contracts/project_state_boundary_contract_v0.json`
- `policies/project_state_boundary_policy_v0.md`
- `specs/project_state_boundary_spec_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `scripts/project_state_boundary_gate_v0.py`
- `scripts/quality_gate_v0.sh`
- `scripts/quality_gate_ci_v0.sh`
- `docs/cortex-coach/quality-gate.md`
- `docs/cortex-coach/commands.md`
- `docs/cortex-coach/quickstart.md`
- `playbooks/design_ontology_validation_runbook_v0.md`
- `README.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Project-specific operational artifacts must live under .cortex by default, with fail-closed boundary checks and time-bounded waiver exceptions.

## Rationale
Protect distribution surfaces from project-state drift and keep repository authority boundaries deterministic for maintainers and downstream adopters.

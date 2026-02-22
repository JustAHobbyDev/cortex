# Decision: Establish context hydration contract and policy baseline

DecisionID: dec_20260222T131253Z_establish_context_hydrat
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-22T13:12:53Z
PromotedAt: 2026-02-22T13:12:59Z
ImpactScope: governance, workflow, runtime
LinkedArtifacts:
- `.cortex/reports/project_state/ph0_012_context_hydration_baseline_closeout_v0.md`
- `contracts/context_hydration_receipt_schema_v0.json`
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `policies/context_hydration_policy_v0.md`
- `specs/cortex_project_coach_spec_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Adopt PH0-012 context hydration baseline with policy, schema, and spec integration, with runtime enforcement staged separately.

## Rationale
This prevents governance drift from stale context windows while keeping rollout incremental and auditable.

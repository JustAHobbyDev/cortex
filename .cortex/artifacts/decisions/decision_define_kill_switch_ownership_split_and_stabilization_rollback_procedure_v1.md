# Decision: Define kill-switch ownership split and stabilization rollback procedure

DecisionID: dec_20260223T045729Z_define_kill_switch_owner
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-23T04:57:29Z
PromotedAt: 2026-02-23T04:57:38Z
ImpactScope: governance, workflow, runtime
LinkedArtifacts:
- `.cortex/reports/project_state/ph0_006_kill_switch_rollback_controls_closeout_v0.md`
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Define PH0-006 governance controls so stop-rule ownership remains in cortex policy while kill-switch execution remains in cortex-coach operations, with explicit stabilization-cycle requirements.

## Rationale
Explicit ownership and recovery flow reduce emergency-response ambiguity and prevent governance bypass during incident handling.

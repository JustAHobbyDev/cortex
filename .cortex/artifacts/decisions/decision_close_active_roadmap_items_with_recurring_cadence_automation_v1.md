# Decision: Close active roadmap items with recurring cadence automation

DecisionID: dec_20260225T091902Z_close_active_roadmap_ite
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-25T09:19:02Z
PromotedAt: 2026-02-25T09:19:06Z
ImpactScope: governance, roadmap, operations
LinkedArtifacts:
- `.cortex/reports/project_state/phase5_recurring_cadence_report_v0.json`
- `playbooks/cortex_phase6_bootstrap_gdd_ticket_breakdown_v0.md`
- `playbooks/cortex_phase6_measurement_plan_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `scripts/phase5_recurring_cadence_pack_v0.py`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Active roadmap items were defined but not fully operationalized with a recurring evidence command/output. Recurring pattern: Roadmap statuses can remain active after phase closeout unless recurring checks are turned into explicit scripts + artifacts. Adopt reusable rule: When a roadmap item is active around recurring verification, implement a deterministic automation command and evidence artifact before marking it done.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

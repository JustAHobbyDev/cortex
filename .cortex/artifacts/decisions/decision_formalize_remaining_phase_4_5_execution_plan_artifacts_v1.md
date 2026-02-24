# Decision: Formalize remaining Phase 4/5 execution plan artifacts

DecisionID: dec_20260224T104225Z_formalize_remaining_phas
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-24T10:42:25Z
PromotedAt: 2026-02-24T10:42:33Z
ImpactScope: governance, workflow
LinkedArtifacts:
- `playbooks/cortex_phase4_measurement_plan_v0.md`
- `playbooks/cortex_phase4_promotion_enforcement_ticket_breakdown_v0.md`
- `playbooks/cortex_phase5_measurement_plan_v0.md`
- `playbooks/cortex_phase5_rollout_migration_ticket_breakdown_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Plan-level governance artifacts were changed without a linked promoted decision. Recurring pattern: Roadmap and ticket-board updates can drift from decision coverage when added quickly. Adopt reusable rule: When governance-impact playbooks or roadmap artifacts change, capture+promote a linked decision in the same change set.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

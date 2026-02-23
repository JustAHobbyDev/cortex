# Decision: Require mandatory Phase 1 entry checklist in Phase 0 handoff

DecisionID: dec_20260223T072014Z_require_mandatory_phase_
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-23T07:20:14Z
PromotedAt: 2026-02-23T07:20:17Z
ImpactScope: governance, workflow
LinkedArtifacts:
- `.cortex/reports/project_state/ph0_009_maintainer_closeout_handoff_package_v0.md`
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `playbooks/fixed_policy_vs_implementation_choice_matrix_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Phase 0 handoff could be interpreted as complete without a deterministic entry-condition checklist, increasing risk of ambiguous Phase 1 start criteria. Recurring pattern: Narrative handoff summaries without explicit pass/fail entry conditions make readiness judgments inconsistent across sessions and maintainers. Adopt reusable rule: PH0 handoff must include a mandatory Phase 1 entry-condition checklist with pass/fail status and evidence links, plus owned open-question registry.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

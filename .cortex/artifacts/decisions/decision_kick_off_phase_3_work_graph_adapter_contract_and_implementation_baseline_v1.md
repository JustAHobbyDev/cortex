# Decision: Kick off Phase 3 work-graph adapter contract and implementation baseline

DecisionID: dec_20260224T082639Z_kick_off_phase_3_work_gr
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-24T08:26:39Z
PromotedAt: 2026-02-24T08:26:43Z
ImpactScope: governance, workflow, planning
LinkedArtifacts:
- `.cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json`
- `contracts/context_load_work_graph_adapter_contract_v0.md`
- `contracts/temporal_playbook_release_surface_contract_v0.json`
- `docs/cortex-coach/agent-context-loader.md`
- `docs/cortex-coach/commands.md`
- `playbooks/cortex_phase3_measurement_plan_v0.md`
- `playbooks/cortex_phase3_work_graph_adapter_ticket_breakdown_v0.md`
- `specs/cortex_project_coach_spec_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Phase 3 adapter kickoff changes touched governance-impacting docs/playbooks without fresh decision linkage. Recurring pattern: When starting a new phase, planning/spec artifacts can be added before a decision entry captures authority and scope boundaries. Adopt reusable rule: When opening a new phase board or measurement plan, capture and promote a decision linking all governance-impacting kickoff artifacts in the same change.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

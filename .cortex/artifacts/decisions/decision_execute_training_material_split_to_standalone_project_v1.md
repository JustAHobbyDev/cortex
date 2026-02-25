# Decision: Execute training material split to standalone project

DecisionID: dec_20260225T175933Z_execute_training_materia
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-25T17:59:33Z
PromotedAt: 2026-02-25T17:59:39Z
ImpactScope: governance, training, docs, operations
LinkedArtifacts:
- `docs/cortex-coach/README.md`
- `docs/cortex-coach/client_ai_governance_fundamentals_v0.md`
- `docs/cortex-coach/client_training_external_repo_v0.md`
- `docs/cortex-coach/client_training_labs_v0.md`
- `docs/cortex-coach/client_training_project_boundary_and_handoff_v0.md`
- `playbooks/cortex_client_onboarding_training_execution_board_v0.md`
- `playbooks/cortex_client_onboarding_training_track_v0.md`
- `playbooks/cortex_phase6_measurement_plan_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Training artifacts remained in core repo after deciding they should be owned by a dedicated training project. Recurring pattern: Without an explicit extraction pass, ownership shifts can stop at policy/contracts while content remains colocated in core runtime repo. Adopt reusable rule: When deciding a domain should become its own project, perform an explicit extraction pass that leaves only compatibility stubs and integration contracts in the core repo.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

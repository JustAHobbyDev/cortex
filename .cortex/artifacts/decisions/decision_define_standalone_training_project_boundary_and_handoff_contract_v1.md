# Decision: Define standalone training project boundary and handoff contract

DecisionID: dec_20260225T174336Z_define_standalone_traini
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-25T17:43:36Z
PromotedAt: 2026-02-25T17:43:39Z
ImpactScope: governance, training, docs, contracts
LinkedArtifacts:
- `docs/cortex-coach/README.md`
- `docs/cortex-coach/client_training_project_boundary_and_handoff_v0.md`
- `playbooks/cortex_client_onboarding_training_execution_board_v0.md`
- `playbooks/cortex_client_onboarding_training_track_v0.md`
- `contracts/client_training_project_handoff_schema_v0.json`
- `.cortex/templates/client_training_project_handoff_manifest_template_v0.json`
- `.cortex/templates/client_onboarding_completion_report_template_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Training expansion content was added without a formal repo boundary and version-pinned handoff interface, leaving ownership and compatibility implicit. Recurring pattern: Enablement assets can sprawl in core repos when separation contracts are not defined before expansion. Adopt reusable rule: Before scaling training assets, define a standalone-project boundary and a machine-checkable handoff contract with version pinning and required interfaces.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

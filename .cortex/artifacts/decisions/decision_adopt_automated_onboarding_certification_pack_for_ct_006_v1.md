# Decision: Adopt automated onboarding certification pack for CT-006

DecisionID: dec_20260225T035900Z_adopt_automated_onboardi
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-25T03:59:00Z
PromotedAt: 2026-02-25T03:59:00Z
ImpactScope: governance, docs, training
LinkedArtifacts:
- `scripts/client_onboarding_certification_pack_v0.py`
- `.cortex/reports/project_state/client_onboarding_certification_pack_v0.json`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `playbooks/cortex_client_onboarding_training_execution_board_v0.md`
- `playbooks/cortex_client_onboarding_training_track_v0.md`
- `docs/cortex-coach/client_training_labs_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Use a dedicated certification-pack script to generate scorecard, validate schema, and enforce recurring post-onboarding cadence checks.

## Rationale
This consolidates onboarding pass/fail logic into a deterministic artifact and keeps cadence governance machine-checkable.

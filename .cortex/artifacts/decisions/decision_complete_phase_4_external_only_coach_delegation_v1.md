# Decision: Complete phase 4 external-only coach delegation

DecisionID: dec_20260220T144052Z_complete_phase_4_externa
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-20T14:40:52Z
PromotedAt: 2026-02-20T14:40:56Z
ImpactScope: governance, decoupling, runtime, docs
LinkedArtifacts:
- `scripts/cortex_project_coach_v0.py`
- `playbooks/cortex_coach_decoupling_plan_v0.md`
- `docs/cortex-coach/migration_to_standalone_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Remove in-repo coach runtime fallback and make cortex coach entrypoints delegate to installed standalone cortex-coach; finalize ownership-boundary governance docs.

## Rationale
Phase 3 parity is complete and standalone coach is operational; retaining internal runtime risks boundary drift.

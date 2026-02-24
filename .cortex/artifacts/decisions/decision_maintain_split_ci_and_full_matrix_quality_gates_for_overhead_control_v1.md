# Decision: Maintain split CI and full-matrix quality gates for overhead control

DecisionID: dec_20260224T051744Z_maintain_split_ci_and_fu
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-24T05:17:44Z
PromotedAt: 2026-02-24T05:18:04Z
ImpactScope: governance, workflow, ci
LinkedArtifacts:
- `scripts/phase2_performance_governance_pack_v0.py`
- `scripts/quality_gate_ci_full_v0.sh`
- `scripts/quality_gate_ci_v0.sh`
- `scripts/quality_gate_sync_check_v0.py`
- `scripts/quality_gate_v0.sh`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: PH2 CI overhead measurement exceeded target because required CI gate was carrying full coach test matrix scope. Recurring pattern: Required and full-matrix gate responsibilities drifted together over time, increasing required CI runtime beyond budget. Adopt reusable rule: Keep required CI on governance-critical focused tests and run full coach matrix in dedicated full gate script for release-grade coverage.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

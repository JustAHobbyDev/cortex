# Decision: Prioritize governance completeness over decoupling

DecisionID: dec_20260220T120228Z_prioritize_governance_co
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-20T12:02:28Z
PromotedAt: 2026-02-20T12:02:31Z
ImpactScope: governance, policy, workflow, decoupling
LinkedArtifacts:
- `playbooks/cortex_coach_decoupling_plan_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `scripts/quality_gate_v0.sh`
- `scripts/quality_gate_ci_v0.sh`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Set governance completeness and enforceability as higher priority than coach/cortex decoupling; decoupling milestones depend on active governance-completeness checks.

## Rationale
Recent misses showed that integrity checks pass even when decision capture completeness is incomplete; priority must shift to close this governance gap first.

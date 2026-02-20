# Decision: Require decision reflection for operating-layer changes

DecisionID: dec_20260220T112459Z_require_decision_reflect
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-20T11:24:59Z
PromotedAt: 2026-02-20T11:25:02Z
ImpactScope: governance, policy, workflow, tooling
LinkedArtifacts:
- `policies/decision_reflection_policy_v0.md`
- `scripts/cortex_project_coach_v0.py`
- `docs/cortex-coach/commands.md`
- `tests/test_coach_policy_enable.py`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
When implementation changes alter governance/process behavior, capture and promote a decision artifact before closeout.

## Rationale
Prevents important operating decisions from being implicit in diffs and improves traceability across policy/runtime.

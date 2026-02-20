# Decision: Require agent-agnostic reflection loop for governance learning

DecisionID: dec_20260220T151640Z_require_agent_agnostic_r
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-20T15:16:40Z
PromotedAt: 2026-02-20T15:16:46Z
ImpactScope: governance, policy, workflow
LinkedArtifacts:
- `policies/decision_reflection_policy_v0.md`
- `.cortex/policies/cortex_coach_decision_reflection_policy_v0.md`
- `playbooks/claude_meta_compare_and_agent_agnostic_reflection_plan_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Adopt assistant-neutral reflect->abstract->generalize->encode->validate loop and encode outputs in operating artifacts.

## Rationale
Ensure reflection governance portability across agents and keep durable repo-based memory.

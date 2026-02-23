# Decision: Establish Phase 1 tactical memory command-family baseline and measurement gate

DecisionID: dec_20260223T075856Z_establish_phase_1_tactic
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-23T07:58:56Z
PromotedAt: 2026-02-23T07:59:02Z
ImpactScope: governance, workflow, specs, docs
LinkedArtifacts:
- `contracts/tactical_memory_command_family_contract_v0.md`
- `docs/cortex-coach/commands.md`
- `playbooks/cortex_phase1_measurement_plan_v0.md`
- `playbooks/cortex_phase1_tactical_memory_command_contract_ticket_breakdown_v0.md`
- `specs/cortex_project_coach_spec_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Phase 1 implementation could start without a shared command-family contract baseline, causing inconsistent command semantics and weak automation guarantees. Recurring pattern: Feature design starts before a common CLI/output/exit-code contract exists, leading to drift across commands and reviews. Adopt reusable rule: Before implementing a new command family, publish a shared contract baseline and measurement gate criteria, then link them to execution tickets.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

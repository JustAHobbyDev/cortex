# Decision: Require schema-bound memory-record policy invariants before Phase 1 implementation

DecisionID: dec_20260223T080624Z_require_schema_bound_mem
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-23T08:06:24Z
PromotedAt: 2026-02-23T08:06:28Z
ImpactScope: governance, workflow, specs, policy
LinkedArtifacts:
- `contracts/tactical_memory_record_schema_v0.json`
- `playbooks/cortex_phase1_tactical_memory_command_contract_ticket_breakdown_v0.md`
- `policies/tactical_data_policy_v0.md`
- `specs/cortex_project_coach_spec_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Phase 1 memory-record contract work touched tactical data policy without explicit decision linkage, risking undocumented governance drift. Recurring pattern: Schema and policy evolve during design tickets, but decision linkage is missed when only one governance file is already linked. Adopt reusable rule: When a Phase ticket updates tactical data policy or other governance-impact files, capture and promote a decision that links all changed governance artifacts before closeout.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

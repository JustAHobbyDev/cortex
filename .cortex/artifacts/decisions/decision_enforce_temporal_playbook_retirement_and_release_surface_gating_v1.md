# Decision: Enforce temporal playbook retirement and release-surface gating

DecisionID: dec_20260222T144850Z_enforce_temporal_playboo
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-22T14:48:50Z
PromotedAt: 2026-02-22T14:48:53Z
ImpactScope: governance, policy, workflow, ci, tooling
LinkedArtifacts:
- `contracts/temporal_playbook_release_surface_contract_v0.json`
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `policies/temporal_playbook_release_surface_policy_v0.md`
- `scripts/quality_gate_ci_v0.sh`
- `scripts/quality_gate_v0.sh`
- `scripts/temporal_playbook_release_gate_v0.py`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Mistake observed: Temporal Cortex-development playbooks lacked explicit lifecycle metadata and deterministic release-surface enforcement. Recurring pattern: Project-scoped playbooks drift into durable release surface when temporal status and expiry are not contract-bound. Adopt reusable rule: Require contract-managed lifecycle metadata for cortex_* playbooks and fail closed on unmanaged, expired, or disposition-violating entries.

## Rationale
Promote durable, auditable learning so repeated mistakes are prevented across sessions.

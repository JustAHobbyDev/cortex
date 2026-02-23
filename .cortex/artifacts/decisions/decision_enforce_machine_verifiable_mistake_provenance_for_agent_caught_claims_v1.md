# Decision: Enforce machine-verifiable mistake provenance for agent-caught claims

DecisionID: dec_20260223T053208Z_enforce_machine_verifiab
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-23T05:32:08Z
PromotedAt: 2026-02-23T05:32:12Z
ImpactScope: governance, workflow, runtime
LinkedArtifacts:
- `.cortex/reports/project_state/ph0_014_mistake_provenance_gate_closeout_v0.md`
- `contracts/mistake_candidate_schema_v0.json`
- `policies/mistake_detection_provenance_policy_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `scripts/mistake_candidate_gate_v0.py`
- `scripts/quality_gate_v0.sh`
- `scripts/quality_gate_ci_v0.sh`
- `docs/cortex-coach/quality-gate.md`
- `.cortex/reports/mistake_candidates_v0.json`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Define PH0-014 mistake provenance contract and policy, require schema-compliant candidate records for machine-caught claims, and enforce fail-closed provenance checks in local and CI quality gates.

## Rationale
This removes ambiguity around agent-caught mistake claims and prevents ungrounded assertions from passing governance closeout.

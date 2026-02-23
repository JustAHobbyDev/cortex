# PH0-014 Machine-Caught Mistake Provenance Contract + Gate Closeout v0

Version: v0  
Status: Accepted  
Date: 2026-02-23  
Scope: Phase 0 ticket PH0-014 closeout evidence

## Objective

Close PH0-014 by enforcing machine-verifiable mistake provenance through contract schema, policy controls, deterministic gate enforcement, and release-boundary quality-gate integration.

## Ticket Criteria Verification

PH0-014 acceptance criteria from `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`:

1. A versioned mistake-candidate schema defines required provenance fields (`detected_by`, `detector`, `evidence_refs`, `rule_violated`, `confidence`, `status`).
2. Policy forbids reporting/claiming agent-caught mistakes without machine-recorded provenance meeting schema requirements.
3. Deterministic gate fails when machine-caught claims are missing required provenance/evidence or use unsupported confidence/status values.
4. Local and CI quality gates include the provenance gate before release-boundary checks complete.
5. Existing mistake/reflection artifacts have migration/backfill guidance with explicit handling for unknown legacy provenance.

## Evidence Mapping

Primary artifacts reviewed:

- `contracts/mistake_candidate_schema_v0.json`
  - Defines required provenance fields and supported enum semantics.
  - Defines machine-caught evidence requirements and legacy backfill metadata requirements.
- `policies/mistake_detection_provenance_policy_v0.md`
  - Forbids ungrounded machine-caught claims and defines legacy migration/backfill handling.
- `.cortex/reports/mistake_candidates_v0.json`
  - Canonical structured mistake-candidate report with explicit `unknown_legacy` migration entry.
- `specs/cortex_project_coach_spec_v0.md`
  - Adds mistake provenance policy/contract linkage into governance rules.
- `scripts/mistake_candidate_gate_v0.py`
  - Deterministic fail-closed enforcement for required fields, enum support, machine evidence minimums, and legacy backfill semantics.
- `scripts/quality_gate_v0.sh`
- `scripts/quality_gate_ci_v0.sh`
  - Both include mistake provenance gate before release-boundary checks complete.
- `tests/test_coach_mistake_candidate_gate.py`
  - Verifies pass case, missing-evidence failure, and unsupported enum failure behavior.

## Governance Check Evidence

Executed during PH0-014 closeout pass:

1. `uv run --locked --group dev pytest -q tests/test_coach_mistake_candidate_gate.py`
2. `python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir . --format json`
3. `python3 scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`
4. `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all --format json`
5. `./scripts/quality_gate_ci_v0.sh`

Results:

- targeted pytest: `3 passed in 2.70s`
- decision-gap-check: `status=pass`, `uncovered_files=0`, `run_at=2026-02-23T05:33:17Z`
- reflection_enforcement_gate_v0.py: `status=pass`, `findings=0`, `run_at=2026-02-23T05:33:18Z`
- audit (`all`): `status=pass`, `artifact_conformance=pass`, `run_at=2026-02-23T05:33:38Z`
- quality gate CI script: `PASS`, focused suite `41 passed in 53.98s`

## Decision

Decision tracking entry:

- `decision_id`: `dec_20260223T053208Z_enforce_machine_verifiab`
- `status`: `promoted`
- decision artifact: `.cortex/artifacts/decisions/decision_enforce_machine_verifiable_mistake_provenance_for_agent_caught_claims_v1.md`
- reflection scaffold: `.cortex/reports/reflection_scaffold_ph0_014_mistake_provenance_gate_v0.json`

PH0-014 is marked `done`.  
Machine-caught mistake claims are now governed by explicit provenance contract + policy and fail-closed local/CI enforcement.

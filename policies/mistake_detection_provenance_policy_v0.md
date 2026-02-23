# Mistake Detection Provenance Policy v0

Version: v0  
Status: Active  
Scope: machine-caught mistake claim provenance and enforcement

## Purpose

Ensure claims about machine-caught or agent-caught mistakes are machine-verifiable, reviewable, and traceable to deterministic evidence.

## Policy Rules

1. Any machine-caught mistake claim MUST be recorded in the contract-defined mistake candidate report file (`candidate_file` in `contracts/mistake_candidate_schema_v0.json`).
2. Candidate entries MUST satisfy `contracts/mistake_candidate_schema_v0.json`.
3. Reporting a machine-caught mistake claim without schema-compliant provenance is forbidden.
4. Unsupported confidence/status values are forbidden.
5. `unknown_legacy` provenance is allowed only for migration/backfill handling and must include required migration metadata.

## Required Provenance Fields

Every mistake candidate entry MUST include:

- `detected_by`
- `detector`
- `evidence_refs`
- `rule_violated`
- `confidence`
- `status`

Machine-caught entries (`detected_by=machine`) additionally require:

- detector fields from contract `machine_requirements.required_detector_fields`
- evidence reference count >= contract `machine_requirements.minimum_evidence_refs`

## Legacy Migration and Backfill Guidance

For historical claims with missing provenance:

1. Record as `detected_by=unknown_legacy`.
2. Set `confidence=unknown_legacy` and `status=unknown_legacy`.
3. Include migration metadata required by contract:
   - `legacy_reason`
   - `migration_action`
   - `owner`
   - `backfill_due`
4. Backfill or reclassify the claim before `backfill_due`.

If legacy provenance cannot be recovered by deadline, the claim must be retired or explicitly reclassified as non-machine-caught.

## Enforcement

- Deterministic gate: `scripts/mistake_candidate_gate_v0.py`
- Local enforcement path: `scripts/quality_gate_v0.sh`
- CI enforcement path: `scripts/quality_gate_ci_v0.sh`

Gate failures are blocking for release-boundary quality gates.

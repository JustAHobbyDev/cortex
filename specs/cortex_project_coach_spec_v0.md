# Cortex Project Coach Spec

Version: v0  
Status: Experimental (Governance-Amended)  
Inputs:
- `README.md` repository purpose and admission criteria
- `philosophy/ontology_architecture_map_v0.md` layer model
- `specs/spec_spec_v0.md` governance and spec structure
- `specs/design_ontology_schema_spec_v0.md` design ontology baseline
- `contracts/promotion_contract_schema_v0.json` promotion contract schema
- `policies/tactical_data_policy_v0.md` tactical data policy
- `scripts/design_prompt_dsl_compile_v0.py` DSL compiler
- `scripts/design_ontology_validate_v0.py` ontology validator

## Purpose

Define an application that guides project creation with AI assistance, maintains required Cortex artifacts across the lifecycle, and safely supports tactical runtime memory/work context without weakening governance authority.

## Scope

- In scope:
  - Bootstrap of required lifecycle artifacts for a new project.
  - Ongoing artifact audit/status reporting across lifecycle phases.
  - Deterministic output files for automation and AI prompt handoff.
  - Experimental tactical plane features under explicit governance and policy controls.
  - Promotion workflows from tactical signals to canonical decision/governance artifacts.
- Out of scope:
  - Hosting or UI framework decisions (CLI-first in v0).
  - Remote synchronization and multi-user conflict resolution.
  - Replacing external issue trackers/work systems as canonical governance authority.

## Core Definitions

- `Project Coach`: CLI application that initializes and audits `.cortex/` artifacts in a target project.
- `Lifecycle Manifest`: machine-readable contract for project metadata and phase completion.
- `Governance Plane`: canonical artifacts/policies that define authoritative project governance.
- `Tactical Plane`: fast runtime memory/work context used for execution acceleration.
- `Promotion Contract`: required evidence and linkage to convert tactical signals into canonical artifacts.
- `External Adapter`: optional runtime integration that reads tactical signals from external systems.

## Determinism and Drift Tests

- Bootstrap determinism: running `init` twice without changes must not rewrite existing files unless `--force` is used.
- Audit determinism: identical project state must produce identical normalized audit status except timestamp fields.
- Schema drift test: design ontology JSON in target project must validate against the canonical schema.
- Context determinism: identical repo state and args must produce stable selected-file ordering and stable fallback metadata.
- Promotion determinism: identical tactical input bundle must produce consistent promotion candidate normalization.

## Governance Rules

### Canonical Authority

- Governance plane artifacts are authoritative by default.
- Tactical plane output is non-authoritative until promoted.

### Promotion Contract

Any governance-impacting tactical closure must provide:

1. decision/reflection linkage
2. impacted artifact linkage
3. rationale/evidence summary
4. promotion trace entry in deterministic report outputs

Canonical schema:
- `contracts/promotion_contract_schema_v0.json`

Validation requirements:
- Missing decision/reflection linkage is invalid.
- Empty impacted artifact linkage is invalid.
- Missing rationale/evidence summary is invalid.
- Missing promotion trace metadata is invalid.

### Tactical Data Policy

- Tactical storage must prohibit secrets/credentials/PII by policy.
- Tactical records must support TTL/pruning/compaction.
- Redaction controls must be available for non-compliant tactical payloads.
- Canonical policy source: `policies/tactical_data_policy_v0.md`.

### External Adapter Policy

- Adapters are optional and read-only by default.
- Adapter integrations MUST NOT write or directly mutate canonical governance artifacts.
- Adapter failures/timeouts must degrade to governance-only behavior.
- Adapter failures/timeouts MUST NOT block mandatory governance checks (`audit`, `decision-gap-check`, `reflection-completeness-check`).
- Adapter data must carry provenance metadata.
- Adapter data must carry freshness metadata (`adapter_fetched_at`, `source_updated_at`, `staleness_seconds`).
- If freshness metadata is missing or stale beyond threshold, runtime must warn and treat adapter signals as advisory only.

### Enforcement Ladder

- Level 0: advisory warnings only
- Level 1: local blocking for governance-impacting gaps
- Level 2: CI blocking for required governance checks
- Level changes require policy update and versioned release notes

### Boundary Discipline

- Project Coach mutates only `.cortex/` paths in target projects unless an explicit policy-governed exception is added.
- Existing user files outside `.cortex/` are never rewritten by default behavior.

### Rollback/Kill-Switch

- Runtime must support disabling tactical plane and adapters independently.
- Governance checks must continue functioning when tactical features are disabled.

### Capacity Governance

- Session sequencing should use 5-hour usage windows and weekly usage signals.
- Rollout progression should pause when capacity stop-rules are triggered.

## Failure Modes

- Target project lacks write permissions for `.cortex/`.
- Design DSL compiles but generated JSON fails schema constraints.
- Lifecycle manifest exists but version mismatches required format.
- Tactical plane stores prohibited content and redaction fails.
- Adapter latency/failure path blocks mandatory governance commands.
- Promotion gaps allow governance-impacting closures without required linkage.
- Rollout exceeds stop-rule thresholds without pause/escalation.

## Success Criteria (v0)

- CLI exists at `scripts/cortex_project_coach_v0.py`.
- `init` command scaffolds `.cortex/` with required files.
- `audit` command emits `.cortex/reports/lifecycle_audit_v0.json`.
- Audit includes design ontology schema validation result.
- `coach` command emits cycle action artifacts (`.json`, `.md`, AI prompt) for iterative maintenance.
- `coach --apply` generates deterministic draft `vN+1` artifacts for eligible action targets under `.cortex/artifacts/` and logs applied/skipped outcomes.
- `coach --apply-scope` constrains draft generation by artifact class (`direction`, `governance`, `design`) with fail-closed validation on unknown scopes.
- Tactical features (if enabled) never bypass decision/reflection/audit governance checks.
- Adapter outages do not block governance-only operation paths.

## Immediate Next Step

Wire promotion schema and tactical data policy validation into runtime reports and CI checks.

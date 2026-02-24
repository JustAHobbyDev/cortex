# Cortex Project Coach Spec

Version: v0  
Status: Experimental (Governance-Amended)  
Inputs:
- `README.md` repository purpose and admission criteria
- `philosophy/ontology_architecture_map_v0.md` layer model
- `specs/spec_spec_v0.md` governance and spec structure
- `specs/design_ontology_schema_spec_v0.md` design ontology baseline
- `contracts/promotion_contract_schema_v0.json` promotion contract schema
- `contracts/context_hydration_receipt_schema_v0.json` context hydration receipt contract schema
- `contracts/mistake_candidate_schema_v0.json` mistake candidate provenance contract schema
- `contracts/project_state_boundary_contract_v0.json` project-state path boundary contract
- `contracts/tactical_memory_command_family_contract_v0.md` tactical memory command family baseline contract
- `contracts/tactical_memory_record_schema_v0.json` tactical memory record payload contract schema
- `contracts/tactical_memory_search_result_schema_v0.json` tactical memory search result contract schema
- `contracts/tactical_memory_prime_bundle_schema_v0.json` tactical memory prime bundle contract schema
- `contracts/tactical_memory_diff_schema_v0.json` tactical memory diff contract schema
- `contracts/tactical_memory_prune_schema_v0.json` tactical memory prune contract schema
- `contracts/context_load_retrieval_contract_v0.md` context-load retrieval/ranking contract baseline
- `policies/cortex_coach_cli_output_contract_policy_v0.md` CLI output contract policy
- `policies/context_hydration_policy_v0.md` context hydration policy
- `policies/mistake_detection_provenance_policy_v0.md` mistake provenance policy
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

- `Project Coach`: CLI application that initializes and audits .cortex/ artifacts in a target project.
- `Lifecycle Manifest`: machine-readable contract for project metadata and phase completion.
- `Governance Plane`: canonical artifacts/policies that define authoritative project governance.
- `Tactical Plane`: fast runtime memory/work context used for execution acceleration.
- `Promotion Contract`: required evidence and linkage to convert tactical signals into canonical artifacts.
- `Context Hydration`: deterministic preflight loading of required governance capsule artifacts for a fresh runtime window.
- `Hydration Receipt`: machine-readable proof that required governance capsule artifacts were loaded and validated recently.
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
- `memory-record` payloads must validate against `contracts/tactical_memory_record_schema_v0.json` before persistence.
- Unknown/additional payload fields are invalid under schema (`additionalProperties: false`) and must fail closed.
- `memory-record` persistence requires explicit write-lock metadata; lock acquisition failure blocks persistence.
- Canonical policy source: `policies/tactical_data_policy_v0.md`.

### Mistake Detection Provenance Policy

- Machine-caught mistake claims must be recorded in structured candidate artifacts.
- Candidate provenance fields must satisfy contract-required fields and enum semantics.
- Unsupported confidence/status values are invalid.
- Legacy unknown provenance is allowed only through explicit migration/backfill markers.
- Canonical contract source: `contracts/mistake_candidate_schema_v0.json`.
- Canonical policy source: `policies/mistake_detection_provenance_policy_v0.md`.

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

### CLI Output Contract

- Non-interactive commands must support `--format text|json`.
- Omitted `--format` must preserve historical text behavior.
- JSON mode must emit parseable command payloads for automation.
- Integration shim support is allowed only for output normalization and must not alter governance logic.

### Tactical Memory Command Family Baseline (Phase 1)

Canonical baseline contract:
- `contracts/tactical_memory_command_family_contract_v0.md`

Required command set:
- `memory-record`
- `memory-search`
- `memory-prime`
- `memory-diff`
- `memory-prune`
- `memory-promote`

Shared contract expectations:
- `--project-dir` required for all commands.
- `--format text|json` required for non-interactive automation compatibility.
- Mutation commands must expose lock controls (`--lock-timeout-seconds`, `--lock-stale-seconds`, `--force-unlock`).
- Identical inputs and repo state must produce deterministic normalized outputs (excluding timestamp fields).

Baseline exit code semantics for command-family automation:
- `0`: success
- `2`: invalid arguments/contract shape violation
- `3`: policy violation
- `4`: lock/state conflict
- `5`: internal runtime failure

### `memory-search` Contract Baseline (PH1-003)

Canonical schema source:
- `contracts/tactical_memory_search_result_schema_v0.json`

Query input and filter semantics:
- Query payload includes explicit raw and normalized query fields.
- Filter payload must be machine-readable and deterministic (`content_classes_any`, `tags_any`, `tags_all`, optional capture-time bounds).
- Empty/invalid query/filter combinations are represented in deterministic output payloads.

Ranking and ordering determinism:
- Result ranking must expose numeric `score` and bounded `confidence` fields per hit.
- Deterministic tie-break order is fixed to:
  - `score_desc`
  - `captured_at_desc`
  - `record_id_asc`
- Search results must include provenance metadata (`source_kind`, `source_ref`, `source_refs`) for each returned record.

No-match semantics:
- No-match output must be machine-readable with `result_count=0`, empty `results`, and explicit `no_match` reason.
- No-match output must preserve stable payload shape for automation parity.

### `memory-prime` Contract Baseline (PH1-004)

Canonical schema source:
- `contracts/tactical_memory_prime_bundle_schema_v0.json`

Input and output bundle semantics:
- Priming input must include explicit task/query references and requested result limit.
- Priming output must include a deterministic bundle with stable entry order and per-entry provenance references.
- Bundle entries must include source references for each selected tactical record.

Budget enforcement requirements:
- Budget controls are explicit and machine-readable:
  - `max_records`
  - `max_chars`
  - `per_record_max_chars`
- Output includes deterministic `selected_count` and `selected_char_count`.

Truncation and overflow behavior:
- Truncation behavior must be explicit and auditable in output payload.
- Truncation metadata must include:
  - whether truncation was applied
  - truncation reason class
  - dropped record ids
  - truncated record/char counts
- Same inputs and budget parameters must produce stable truncation outcomes.

### `memory-diff` and `memory-prune` Mutation Safety Baseline (PH1-005)

Canonical schema sources:
- `contracts/tactical_memory_diff_schema_v0.json`
- `contracts/tactical_memory_prune_schema_v0.json`

Diff semantics:
- `memory-diff` uses stable comparison keys (`record_id`) and deterministic output ordering.
- Diff output must provide machine-readable change classification (`added`, `removed`, `modified`, `unchanged`).
- Diff entries must include provenance lineage references for traceability.

Prune policy and dry-run semantics:
- `memory-prune` eligibility must be explicit and machine-readable (age/TTL, retention class, policy-violation class).
- `dry_run=true` must be deterministic and must not mutate records.
- Prune outcomes must be machine-readable with deterministic action ordering and explicit reason codes.

Provenance lineage retention:
- Diff and prune outputs must preserve lineage references (`source_refs`, optional `ancestor_record_ids`) for each affected record.

### `memory-promote` Governance Bridge Baseline (PH1-006)

Canonical contract sources:
- `contracts/promotion_contract_schema_v0.json`
- `docs/cortex-coach/commands.md`

Output mapping requirements:
- `memory-promote` must map tactical outputs to promotion-required fields:
  - decision/reflection linkage -> `decision_reflection_linkage`
  - impacted artifact linkage -> `impacted_artifacts`
  - rationale and evidence references -> `rationale_evidence_summary`
  - promotion trace and tactical lineage -> `promotion_trace_metadata`
- Bridge metadata must identify `bridge_command=memory-promote` for bridge-produced promotions.

Failure mode requirements (fail closed):
- Missing any required promotion contract section must produce deterministic blocking failure.
- Failure output must include stable failure class for missing linkage/evidence categories.
- Governance-impacting bridge operations must not emit success output when required promotion fields are incomplete.

Non-governance separation requirements:
- Non-governance tactical outputs must be explicitly marked and must not be treated as canonical governance closure.
- Governance-impacting promotions must remain on canonical decision/reflection/promotion pathways.

### Tactical Storage and Locking Determinism Baseline (PH1-007)

Canonical design sources:
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/quality-gate.md`

Lock acquisition and stale-lock behavior:
- Mutation commands must acquire a deterministic single-writer lock before mutation.
- Lock acquisition timeout must return stable lock/state conflict class (`exit code 4`).
- Stale lock reclaim is allowed only when staleness threshold is exceeded or explicit force-unlock is provided.

Concurrent read/write expectations:
- Concurrent reads may proceed from the most recent committed snapshot during active mutation.
- Concurrent mutation requests must serialize through lock ownership (first lock owner proceeds; others block/fail deterministically).
- Partial mutation visibility is disallowed.

Idempotency and retry behavior:
- Retried mutation requests with identical mutation intent must not produce duplicate records or duplicate prune actions.
- Retry outcome classification must be deterministic (`applied`, `no_op_idempotent`, or stable lock conflict failure).

Failure handling and deterministic recovery:
- Mutation writes must be fail-safe (either fully committed or fully rolled back).
- On interruption/failure, recovery path must preserve index integrity and deterministic subsequent behavior.
- Recovery diagnostics must be machine-readable for post-incident analysis.

### `context-load` Retrieval and Context Quality Baseline (Phase 2 / PH2-001)

Canonical contract sources:
- `contracts/context_load_retrieval_contract_v0.md`
- `playbooks/cortex_phase2_measurement_plan_v0.md`
- `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`

Retrieval pipeline requirements:
- `context-load` must use deterministic candidate assembly and ranking for identical input and repository state.
- Ranking must expose component score breakdown and deterministic combined score ordering.
- Ranking contract and score fields must remain machine-readable in JSON output for automation.

Weighting and profile controls:
- Retrieval weighting mode must be explicit and bounded by contract-defined presets.
- Retrieval profile selection (`small`, `medium`, `large`) must map to frozen evaluation fixtures for Gate C comparability.
- Omitted weighting/profile controls must preserve backward-compatible deterministic defaults.

Deterministic tie-break requirements:
- Tie-break chain must remain fixed and documented in canonical contract.
- Equal-score candidates must never rely on runtime-randomized ordering.
- Ordering behavior must remain stable across repeated runs and process restarts.

Context budget and overflow behavior:
- Ranked output must honor context budget limits and fallback sequence behavior.
- Dropped/truncated candidates must emit deterministic machine-readable metadata.
- Budget overflow must not silently discard provenance/confidence fields for selected entries.

Provenance and confidence requirements:
- Selected context entries must include stable provenance metadata for traceability.
- Confidence values must be normalized and bounded for deterministic downstream scoring.
- Retrieval output remains tactical (non-authoritative) until promoted through governance contracts.

Fixture freeze requirements:
- Gate C measurement and relevance comparisons must use the frozen fixture set at `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`.
- Fixture changes require version bump and explicit baseline reset note in closeout artifacts.

### Context Hydration Enforcement

- Runtime must support issuing hydration receipts and validating freshness before governance-impacting mutation/closeout paths.
- Receipt payload contract source: `contracts/context_hydration_receipt_schema_v0.json`.
- Policy source of trigger events, freshness thresholds, and override semantics: `policies/context_hydration_policy_v0.md`.
- Freshness validation must include governance capsule hash checks and git HEAD drift checks.
- `advisory`/`warn`/`block` rollout is allowed, but `block` mode is required at governance-impacting closeout boundaries.
- Missing or stale hydration receipt must fail closed for governance-impacting mutation/closeout commands unless an explicit override is logged.

### Boundary Discipline

- Project Coach mutates only .cortex/ paths in target projects unless an explicit policy-governed exception is added.
- Existing user files outside .cortex/ are never rewritten by default behavior.
- Project-specific operational artifacts are expected under .cortex/; forbidden outside roots are defined by `contracts/project_state_boundary_contract_v0.json`.

### Rollback/Kill-Switch

- Runtime must support disabling tactical plane and adapters independently.
- Governance checks must continue functioning when tactical features are disabled.

### Capacity Governance

- Session sequencing should use 5-hour usage windows and weekly usage signals.
- Rollout progression should pause when capacity stop-rules are triggered.

## Failure Modes

- Target project lacks write permissions for .cortex/.
- Design DSL compiles but generated JSON fails schema constraints.
- Lifecycle manifest exists but version mismatches required format.
- Tactical plane stores prohibited content and redaction fails.
- Adapter latency/failure path blocks mandatory governance commands.
- Promotion gaps allow governance-impacting closures without required linkage.
- Rollout exceeds stop-rule thresholds without pause/escalation.

## Success Criteria (v0)

- CLI exists at `scripts/cortex_project_coach_v0.py`.
- `init` command scaffolds .cortex/ with required files.
- `audit` command emits .cortex/reports/lifecycle_audit_v0.json.
- Audit includes design ontology schema validation result.
- `coach` command emits cycle action artifacts (`.json`, `.md`, AI prompt) for iterative maintenance.
- `coach --apply` generates deterministic draft `vN+1` artifacts for eligible action targets under .cortex/artifacts/ and logs applied/skipped outcomes.
- `coach --apply-scope` constrains draft generation by artifact class (`direction`, `governance`, `design`) with fail-closed validation on unknown scopes.
- Tactical features (if enabled) never bypass decision/reflection/audit governance checks.
- Adapter outages do not block governance-only operation paths.

## Immediate Next Step

Wire promotion schema and tactical data policy validation into runtime reports and CI checks.

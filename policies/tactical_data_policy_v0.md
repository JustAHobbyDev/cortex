# Tactical Data Policy v0

Version: v0  
Status: Draft  
Scope: tactical plane runtime storage and retrieval

## Purpose

Define minimum data safety controls for tactical memory/work context so execution speed gains do not weaken governance, privacy, or security posture.

## Policy Rules

1. Tactical data is non-authoritative working context and MUST NOT be treated as canonical governance evidence unless promoted.
2. Tactical storage is allowed only for data classes explicitly permitted by this policy.
3. Violations of prohibited classes require immediate redaction and incident note linkage.

## Prohibited Data Classes

The following classes MUST NOT be stored in tactical records:

- secrets (API keys, auth tokens, signing keys)
- credentials (passwords, session cookies, private cert material)
- direct personal data (PII) beyond minimal public attribution needed for repository governance
- regulated or contractual restricted data not explicitly approved for tactical handling

## Required Controls

### Governance Capsule Hydration Coupling (PH6-002)

1. Tactical and adapter slices MUST be loaded only after a valid governance capsule hydration receipt is available for the current context window.
2. Required hydration trigger coverage for governed closeout paths is:
   - `new_session`
   - `window_rollover`
   - `pre_closeout`
3. If hydration freshness checks fail, runtime MUST degrade to governance-only behavior and block governance-impacting closeout when enforcement mode is `block`.
4. Hydration receipt payloads must conform to `contracts/context_hydration_receipt_schema_v0.json` and policy rules in `policies/context_hydration_policy_v0.md`.

### TTL, Pruning, and Compaction

1. Tactical records MUST have TTL metadata.
2. Expired records MUST be pruned on the next scheduled maintenance cycle.
3. Compaction must preserve reference integrity for any record still linked by open governance work.

### Redaction Behavior

1. Redaction must remove prohibited fields before record persistence.
2. Redaction actions must emit a traceable audit note (record id, reason class, timestamp).
3. Redaction failure must prevent persistence of the affected payload.

### Sanitization Failure Handling

1. If sanitization fails, runtime MUST fail closed for the affected payload and continue governance-only command paths.
2. The failure event must be logged with enough metadata to support post-incident review.
3. Repeated sanitization failures in one cycle trigger tactical-plane disable until incident review completes.

### `memory-record` Contract Baseline (PH1-002)

Canonical schema source:
- `contracts/tactical_memory_record_schema_v0.json`

1. Persisted tactical records from `memory-record` MUST validate against the canonical schema.
2. Required record fields include record id, capture timestamp, source/provenance metadata, content class, and tags.
3. Unknown/additional fields are invalid and MUST fail closed (`additionalProperties: false` contract discipline).
4. Write operations MUST carry lock metadata (`lock_id`, `lock_acquired_at`, timeout values); lock failure blocks persistence.
5. Allowed `content_class` values for `memory-record` are:
   - `governance_context`
   - `implementation_note`
   - `decision_signal`
   - `risk_note`
   - `task_state`
   - `reference_excerpt`
   - `incident_note`

### Redaction and Blocking Semantics for `memory-record`

1. If prohibited content is detected and safe redaction is possible, payload may persist only with `sanitization.status=redacted` and explicit `redaction_actions`.
2. If prohibited content cannot be safely redacted, payload MUST be rejected with `sanitization.status=blocked` and no record persistence.
3. Rejected/blocked events must include traceable incident metadata for review.

### `memory-diff` and `memory-prune` Mutation Safety Baseline (PH1-005)

Canonical schema sources:
- `contracts/tactical_memory_diff_schema_v0.json`
- `contracts/tactical_memory_prune_schema_v0.json`

1. Diff outputs MUST use stable comparison keys and deterministic ordering.
2. Diff and prune outputs MUST preserve provenance lineage references for every affected record.
3. Prune eligibility MUST be policy-bound and machine-readable (TTL/age, retention class, policy-violation class).
4. `memory-prune` MUST support deterministic dry-run behavior; dry-run MUST NOT mutate tactical records.
5. Prune actions MUST include explicit decision (`prune` or `skip`) and reason code.

## Enforcement and Evidence

Required evidence for policy conformance:

- policy linkage in `specs/cortex_project_coach_spec_v0.md`
- session flow linkage in `playbooks/session_governance_hybrid_plan_v0.md`
- runtime validation implementation notes (Phase 1+)

## Ownership and Escalation

- Policy owner: `Governance Policy Lead` with `Security & Data Policy Lead` execution ownership in Phase 0.
- Exceptions require `Maintainer Council` approval and linked decision/reflection artifacts.

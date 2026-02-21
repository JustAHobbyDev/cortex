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

## Enforcement and Evidence

Required evidence for policy conformance:

- policy linkage in `specs/cortex_project_coach_spec_v0.md`
- session flow linkage in `playbooks/session_governance_hybrid_plan_v0.md`
- runtime validation implementation notes (Phase 1+)

## Ownership and Escalation

- Policy owner: `Governance Policy Lead` with `Security & Data Policy Lead` execution ownership in Phase 0.
- Exceptions require `Maintainer Council` approval and linked decision/reflection artifacts.

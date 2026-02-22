# Context Hydration Policy v0

Version: v0  
Status: Active  
Scope: Cortex governance workflows and `cortex-coach` runtime preflight behavior

## Purpose

Ensure every fresh or renewed context window starts from a current governance capsule before governance-impacting mutation or closeout actions.

## Governance Capsule (Required Inputs)

- .cortex/manifest_v0.json
- .cortex/reports/lifecycle_audit_v0.json
- .cortex/reports/decision_candidates_v0.json
- policies/cortex_coach_final_ownership_boundary_v0.md
- policies/project_state_boundary_policy_v0.md
- playbooks/cortex_vision_master_roadmap_v1.md

## Hydration Trigger Events

1. `new_session`
2. `window_rollover`
3. `pre_mutation`
4. `pre_closeout`

## Hydration Receipt Contract

- Receipt payload MUST validate against `contracts/context_hydration_receipt_schema_v0.json`.
- Latest receipt path: .cortex/reports/context_hydration/latest.json
- History path: .cortex/reports/context_hydration/history/

## Freshness Rules

A hydration receipt is stale if any condition is true:

1. Receipt age exceeds policy max age threshold (default: 45 minutes).
2. Receipt was emitted for an older git HEAD than current working HEAD.
3. Governance capsule hashes in the receipt no longer match current artifact content.
4. Event is `pre_mutation` or `pre_closeout` and no valid receipt exists.

## Enforcement Rules

1. `advisory` mode is allowed for read-only exploration.
2. `block` mode is required for governance-impacting mutating commands and closeout paths.
3. Runtime MUST fail closed for governance-impacting mutation/closeout when receipt is stale or missing.
4. `warn` mode may be used only as transitional rollout behavior.

## Override Rule

Emergency override is allowed only when all conditions are met:

1. Explicit override reason is provided at command time.
2. Override action is logged in deterministic runtime report output.
3. Follow-up decision/reflection linkage is captured in canonical governance records.

## Ownership Boundary

1. Policy requirements and thresholds are governed in `cortex`.
2. Runtime event detection, receipt generation, and freshness checks are implemented in `cortex-coach`.
3. Threshold or contract changes require synchronized policy + contract updates.

## Rollout Note

Phase 0 defines policy and contract baseline. Runtime command-level enforcement can be enabled in staged modes (`advisory` -> `warn` -> `block`) without changing canonical authority semantics.

# Cortex / cortex-coach Final Ownership Boundary v0

Version: v0  
Status: Active  
Scope: cross-repo operating boundary

## Authority Model

1. Governance Plane Authority
- Canonical governance authority MUST live in `cortex` artifacts and policies.
- Tactical runtime outputs MUST be treated as non-authoritative unless promoted via governance contracts.

2. Tactical Plane Authority
- Tactical capture/retrieval/adapters live in `cortex-coach` runtime implementation.
- Tactical runtime state MUST NOT directly redefine governance policy/spec authority.

## Cortex Owns

- governance model and policy definitions
- contract definitions and contract evolution decisions
- project-state boundary policy/contracts that define where non-distributable project artifacts may live
- canonical asset/schema/template source artifacts
- promotion contract requirements (evidence, linkage, approval expectations)
- enforcement policy levels (advisory vs blocking, local vs CI)
- rollout stop-rules and kill-switch policy definitions
- fixture export strategy used for compatibility testing

## `cortex-coach` Owns

- runtime CLI behavior
- audit/check execution logic
- context-loading execution behavior
- tactical plane runtime features and storage behavior
- external adapter implementations and degradation logic
- package/release/distribution lifecycle

## Operating Rules

1. Boundary discipline
- `cortex` should not host new coach runtime feature implementation.
- Runtime changes should land in `cortex-coach`, with contract-impact notes linked back to `cortex`.

2. Canonical authority rule
- No tactical feature or adapter may bypass decision/reflection/audit governance requirements.
- Promotion is required for tactical content to become canonical.
- Adapter or tactical signals MUST NOT be accepted as sole closure evidence for governance-impacting work.

3. Adapter rule
- External adapters must be optional, read-only by default, and fail-open to governance-only mode.

4. Emergency control rule
- Kill-switch semantics are defined in `cortex` policy.
- Operational kill-switch execution is implemented and operated by `cortex-coach`.

## Stop-Rule and Rollback Ownership Matrix (PH0-006)

1. Stop-rule definition ownership
- `cortex` policy/playbook artifacts define rollout pause triggers and recovery criteria.
- Source of normative trigger set: `playbooks/cortex_vision_master_roadmap_v1.md` (`Release Gates and Stop-Rules`).

2. Operational trigger evaluation and kill-switch execution
- `cortex-coach` runtime/operators evaluate live stop-rule telemetry and initiate tactical/adapter disable actions.
- Emergency runtime execution authority sits with `cortex-coach` maintainers; policy authority remains with `cortex` maintainers.

3. Stabilization-cycle procedure ownership
- Procedure contract source: `playbooks/session_governance_hybrid_plan_v0.md` (`Kill-Switch and Rollback`).
- Stabilization cycle must run governance checks before any tactical capability re-enable decision.

4. Recovery approval boundary
- Recovery from kill-switch state requires incident review plus threshold recovery evidence.
- Approval of post-incident governance changes remains with `cortex` maintainers and must be decision/reflection linked.

## Override and Escalation Ownership

- Policy and contract override approval: `cortex` maintainers (`Maintainer Council` during Phase 0 execution).
- Runtime emergency disable execution: `cortex-coach` maintainers.
- Post-incident governance requirement changes: `cortex` maintainers.
- All override decisions MUST be linked to decision/reflection artifacts in canonical governance records.

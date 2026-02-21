# Cortex / cortex-coach Final Ownership Boundary v0

Version: v0  
Status: Active  
Scope: cross-repo operating boundary

## Authority Model

1. Governance Plane Authority
- Canonical governance authority lives in `cortex` artifacts and policies.
- Tactical runtime outputs are non-authoritative unless promoted via governance contracts.

2. Tactical Plane Authority
- Tactical capture/retrieval/adapters live in `cortex-coach` runtime implementation.
- Tactical runtime state must not directly redefine governance policy/spec authority.

## Cortex Owns

- governance model and policy definitions
- contract definitions and contract evolution decisions
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

3. Adapter rule
- External adapters must be optional, read-only by default, and fail-open to governance-only mode.

4. Emergency control rule
- Kill-switch semantics are defined in `cortex` policy.
- Operational kill-switch execution is implemented and operated by `cortex-coach`.

## Override and Escalation Ownership

- Policy and contract override approval: `cortex` maintainers.
- Runtime emergency disable execution: `cortex-coach` maintainers.
- Post-incident governance requirement changes: `cortex` maintainers.

# Cortex / cortex-coach Final Ownership Boundary v0

Version: v0
Status: Active
Scope: cross-repo operating boundary

## Cortex Owns

- governance model and policy definitions
- contract definitions and contract evolution decisions
- canonical asset/schema/template source artifacts
- fixture export strategy used for compatibility testing

## `cortex-coach` Owns

- runtime CLI behavior
- audit/check execution logic
- context-loading execution behavior
- package/release/distribution lifecycle

## Operating Rule

- `cortex` should not host new coach runtime feature implementation.
- `cortex` entrypoints may delegate to installed `cortex-coach` for migration and compatibility.
- runtime changes should land in `cortex-coach`, with contract-impact notes linked back to `cortex`.

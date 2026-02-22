# Project State Boundary Policy v0

Version: v0  
Status: Active  
Scope: `cortex` repository boundary and all `cortex-coach` target projects

## Purpose

Prevent project-instance state from polluting distributable Cortex product surfaces.

## Default Rule (Normative)

1. Project boundary root is configurable via `contracts/project_state_boundary_contract_v0.json` (`project_state_root`).
2. Default project boundary root MUST be .cortex/ unless explicitly set otherwise by policy-governed contract update.
3. Project-specific operational artifacts MUST live under the configured project boundary root.
4. Project-specific operational artifacts MUST NOT be created or committed outside the configured boundary root by default.
5. Repository-level product artifacts outside the configured boundary root MUST remain reusable and distribution-safe.

## Forbidden Root Rule (v0)

Under the repository root, reports/ is treated as project-state-only and is forbidden outside the configured project boundary root.

Canonical location for project-state reports is:
- <project_state_root>/reports/

## Exception (Waiver) Rule

Temporary exceptions are allowed only when all fields are provided in:
- .cortex/policies/project_state_boundary_waivers_v0.json

Required waiver fields:
- `path`
- `reason`
- `decision_id`
- `owner`
- `expires_on` (UTC date, `YYYY-MM-DD`)
- `status` (`active` or `retired`)

Expired active waivers are blocking.

## Enforcement

`scripts/project_state_boundary_gate_v0.py` is mandatory in local and CI quality gates.

The gate must fail when:
- any forbidden-root file exists outside configured `project_state_root` without an active waiver
- any active waiver is expired

## Migration Rule

When boundary violations are discovered:
1. Move violating artifacts into .cortex/ (preferred).
2. Update references deterministically.
3. Use waivers only when migration cannot be completed immediately in the same change.

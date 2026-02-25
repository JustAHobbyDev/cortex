# Project State Boundary Contract v0

Version: v0  
Status: Active  
Source of truth payload: `contracts/project_state_boundary_contract_v0.json`

## Purpose

Define the machine-enforced boundary for project-instance operational state and the forbidden roots outside that boundary.

## Contract Fields

1. `version`
- Must be `v0`.

2. `project_state_root`
- Configurable boundary root for project-state artifacts.
- Default is `.cortex`.

3. `forbidden_outside_project_state_roots`
- List of roots that are treated as project-state-only and blocked outside `project_state_root`.
- v0 default includes `reports`.

4. `waiver_file`
- Path to waiver registry file (`.cortex/policies/project_state_boundary_waivers_v0.json` by default).

## Normative Rules

1. `project_state_root` is configurable by contract update, but default boundary remains `.cortex`.
2. Any path under a forbidden root that is outside `project_state_root` is blocking unless covered by an active, unexpired waiver.
3. Expired active waivers are blocking.
4. Gate implementation authority is `scripts/project_state_boundary_gate_v0.py`.

## Enforcement Linkage

- Policy source: `policies/project_state_boundary_policy_v0.md`
- Gate: `scripts/project_state_boundary_gate_v0.py`
- Measurement artifact target: `.cortex/reports/project_state/phase6_boundary_conformance_report_v0.json`

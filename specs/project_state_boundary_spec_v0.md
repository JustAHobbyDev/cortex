# Project State Boundary Spec v0

Version: v0  
Status: Experimental (Enforced)  
Scope: repository layout governance and release-surface hygiene

## Purpose

Specify deterministic checks that keep project-instance state inside `.cortex/`.

## Inputs

- `policies/project_state_boundary_policy_v0.md`
- `contracts/project_state_boundary_contract_v0.json`
- `.cortex/policies/project_state_boundary_waivers_v0.json` (optional)

## Core Definitions

- `Project State`: artifact tied to current repository operations, active execution history, internal closeout, or local research evidence.
- `Product Surface`: reusable/distributable Cortex assets (code, contracts, templates, policy/spec docs) intended for broad reuse.
- `Forbidden Root`: repository root path that cannot hold project-state files outside `.cortex/`.

## Boundary Contract (v0)

1. `.cortex/` is the canonical project-state root.
2. `reports/` is a forbidden root outside `.cortex/`.
3. Waivers are temporary and date-bounded.

## Deterministic Enforcement Behavior

`project_state_boundary_gate_v0.py` MUST:

1. Load contract from `contracts/project_state_boundary_contract_v0.json`.
2. Enumerate tracked and untracked repository files.
3. Classify each file by path root.
4. Fail on forbidden-root files outside `.cortex/`, unless covered by active non-expired waiver.
5. Fail on expired active waivers.
6. Emit one JSON object in `--format json` mode.

## Failure Modes

- Forbidden-root files committed outside `.cortex/`.
- Temporary waiver expiry not renewed/retired.
- Invalid waiver file JSON.
- Missing/invalid boundary contract.

## Success Criteria (v0)

- Quality gates fail closed when `reports/*` files appear outside `.cortex/`.
- Existing project reports are migrated under `.cortex/reports/`.
- Waiver lifecycle is explicit and time-bounded.

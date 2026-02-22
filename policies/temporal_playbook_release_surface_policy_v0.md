# Temporal Playbook Release Surface Policy v0

Version: v0  
Status: Active  
Scope: `cortex` playbook release-surface hygiene and temporal artifact lifecycle

## Purpose

Prevent project-specific and time-scoped Cortex development playbooks from shipping as durable product release surface artifacts.

## Classification Rule

1. Playbooks under `playbooks/` whose names start with `cortex_` and end with `.md` are treated as temporal candidates by default.
2. Non-temporal exceptions must be explicitly allowlisted in `contracts/temporal_playbook_release_surface_contract_v0.json`.
3. Temporal playbooks must have explicit owner, disposition, and expiration metadata in the contract.

## Required Metadata Contract

Contract source:
- `contracts/temporal_playbook_release_surface_contract_v0.json`

Each temporal playbook entry MUST include:
- `path`
- `owner`
- `status` (`active` or `retired`)
- `release_action` (`archive_to_cortex`, `remove`, or `exclude_from_release`)
- `reason`
- `expires_on` (UTC date, `YYYY-MM-DD`)

## Release-Surface Rule (Normative)

1. Active temporal playbooks are permitted only while within `expires_on`.
2. Expired active temporal playbooks are blocking.
3. Retired temporal playbooks with `release_action` of `archive_to_cortex` or `remove` must not remain under `playbooks/`.
4. Temporal playbooks may not be included in distributable release surface once retired.
5. Durable product guidance should be distilled into canonical playbooks/specs/policies before temporal artifacts are retired.

## Enforcement

`scripts/temporal_playbook_release_gate_v0.py` is mandatory in local and CI quality gates.

The gate must fail when:
- a temporal candidate is unmanaged (missing contract entry or allowlist exception)
- an active temporal playbook is expired
- a retired temporal playbook remains in the playbook release surface contrary to disposition
- required contract fields are missing/invalid

## Ownership and Escalation

- Primary owner: `Conformance QA Lead`
- Reviewer authority: `Maintainer Council`
- Disposition conflicts escalate to `Program Lead`, then `Maintainer Council`

## Migration Rule

When temporal playbooks reach expiration or completion:
1. Mark disposition outcome in contract and ticket closeout artifacts.
2. Move/archive/remove the temporal artifact according to contract.
3. Preserve necessary historical evidence in the project-state reports directory under `.cortex`.

# PH0-013 Temporal Playbook Release Surface Closeout v0

Version: v0  
Status: Accepted  
Date: 2026-02-22  
Scope: Phase 0 ticket PH0-013 closeout evidence

## Objective

Close PH0-013 by enforcing deterministic temporal playbook lifecycle controls so project-specific/time-scoped Cortex playbooks do not drift into durable release surface.

## Ticket Criteria Verification

PH0-013 acceptance criteria from `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`:

1. Temporal playbook classification rule is defined (including required status/expiry/disposition metadata).
2. Release-surface admission rule is defined: temporal/project-specific playbooks must be retired, archived under .cortex, or excluded from release packaging before release.
3. CI/release quality gate includes a deterministic check that fails on expired/unretired temporal playbooks in distributable surface.
4. Existing Cortex-development-specific playbooks have explicit disposition plans and owners.

## Evidence Mapping

Primary artifacts reviewed:

- `policies/temporal_playbook_release_surface_policy_v0.md`
  - Defines temporal candidate classification, required metadata, normative release-surface rules, and enforcement ownership.
- `contracts/temporal_playbook_release_surface_contract_v0.json`
  - Defines `classification_globs`, durable allowlist exceptions, and temporal playbook entries with owner/status/release_action/reason/expires_on.
- `scripts/temporal_playbook_release_gate_v0.py`
  - Implements fail-closed checks for unmanaged temporal candidates, invalid contract metadata, expired active entries, and retired residue violations.
- `scripts/quality_gate_ci_v0.sh`
- `scripts/quality_gate_v0.sh`
  - Both now run temporal release-surface enforcement before docs/test validation.

## Governance Check Evidence

Executed during PH0-013 closeout pass:

1. `python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir . --format json`
  - Result: `status=pass`, `uncovered_files=0`
  - `run_at=2026-02-22T14:54:23Z`
2. `python3 scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`
  - Result: `status=pass`, `findings=0`
  - `run_at=2026-02-22T14:54:24Z`
3. `python3 scripts/project_state_boundary_gate_v0.py --project-dir . --format json`
  - Result: `status=pass`, `violation_count=0`
  - `run_at=2026-02-22T14:54:23Z`
4. `python3 scripts/temporal_playbook_release_gate_v0.py --project-dir . --format json`
  - Result: `status=pass`, `candidate_count=9`, `unmanaged_candidate_count=0`, `expired_active_count=0`
  - `run_at=2026-02-22T14:54:23Z`
5. `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all --format json`
  - Result: `status=pass`, `artifact_conformance=pass`, `unsynced_decisions=pass`
  - `run_at=2026-02-22T14:54:16Z`
6. `./scripts/quality_gate_ci_v0.sh`
  - Result: `PASS`
  - Focused tests: `35 passed in 52.00s`

Local strict gate note:
- `./scripts/quality_gate_v0.sh` currently exits at step `1/8` (`audit-needed`) with `status=required` while high-risk governance files are dirty in the working tree. This is expected pre-commit behavior.

## Decision

Decision tracking entry:

- `decision_id`: `dec_20260222T144850Z_enforce_temporal_playboo`
- `status`: `promoted`
- decision artifact: `.cortex/artifacts/decisions/decision_enforce_temporal_playbook_retirement_and_release_surface_gating_v1.md`
- reflection scaffold: `.cortex/reports/reflection_scaffold_20260222T144843Z_enforce_temporal_playboo_v0.json`

PH0-013 is marked `done`.

# Session Governance Hybrid Plan v0

Version: v0  
Status: Draft  
Scope: Cortex maintainer and agent session workflow

## Goal

Balance speed during active work with strong governance enforcement at merge/release boundaries, including tactical runtime features and optional external adapters.

## Operating Assumption

- Governance plane is authoritative.
- Tactical plane can accelerate execution but cannot close governance-impacting work without promotion and linkage.

## Default Session Flow

1. Session start
- run `cortex-coach audit-needed --project-dir . --format json`
- confirm operational mode:
  - run `cortex-coach rollout-mode --project-dir . --format json`
  - tactical features enabled/disabled
  - adapter enabled/disabled
  - kill-switch state
- if usage pressure is high, shift session goal to validation/docs tasks

2. Initial governance guard
- if `audit_required=true` or `audit_recommended=true`:
  - run `cortex-coach audit --project-dir . --audit-scope cortex-only`

3. During implementation
- use tactical capture/retrieval workflows only as non-authoritative working memory
- rerun `cortex-only` audit after significant lifecycle/policy/decision changes
- if external adapter is enabled and unhealthy, continue in governance-only mode and record degraded-warning evidence in `.cortex/reports/project_state/`

4. Promotion checkpoint (before closing governance-impacting work)
- ask:
  - did this work change governance, policy, release gates, safety posture, or maintainer workflow?
- if yes:
  - run `cortex-coach decision-capture ...`
  - run `cortex-coach decision-promote ...` when approved
  - run `cortex-coach decision-gap-check --project-dir . --format json`
  - run `cortex-coach reflection-completeness-check --project-dir . --format json`

5. Before merge/release
- run `cortex-coach audit --project-dir . --audit-scope all`
- run `cortex-coach decision-gap-check --project-dir . --format json`
- run `cortex-coach reflection-completeness-check --project-dir . --format json`
- run `cortex-coach rollout-mode-audit --project-dir . --format json` during Phase 5 rollout cycles
- run CI quality gate (`just quality-gate-ci`)
- when adapter-enabled runtime paths changed in the cycle, run:
  - `python3 scripts/phase3_adapter_degradation_harness_v0.py --project-dir . --coach-bin cortex-coach`
  - `python3 scripts/phase3_governance_regression_harness_v0.py --project-dir . --coach-bin cortex-coach`
  - `python3 scripts/phase3_adapter_performance_pack_v0.py --project-dir . --coach-bin cortex-coach`

Output-contract note:
- For deterministic machine parsing across all commands in this repo, use the delegator entrypoint (`python3 scripts/cortex_project_coach_v0.py`) with `--format json` where needed.

Phase 5 migration note:
- Use `playbooks/cortex_phase5_migration_playbook_v0.md` as the operator handoff source when preparing Gate F closeout.

## Client Onboarding Certification Automation (CT-006)

Certification workflow ownership has moved to the standalone training project.

In `cortex`:

1. `scripts/client_onboarding_certification_pack_v0.py` is a compatibility shim (`status=moved`).
2. Canonical training-project reference is `docs/cortex-coach/client_training_external_repo_v0.md`.
3. Boundary/handoff contract is `docs/cortex-coach/client_training_project_boundary_and_handoff_v0.md`.

## Enforcement Ladder in Session Operations

1. Advisory mode
- warnings surfaced, local continuation allowed

2. Local blocking mode
- local closeout blocked for governance-impacting gaps

3. CI blocking mode
- protected branch/release blocked until governance checks pass

Escalation to stricter levels should follow policy versioning and release notes.

## Enforcement Ladder Mapping Matrix (PH0-005)

| Level | Semantics | Local Behavior | CI/Release Behavior | Escalation Rule |
|---|---|---|---|---|
| Level 0 (`advisory`) | Signals only; no closure block. | Surface warnings and recommended remediation steps. | No CI block from ladder alone. | Escalate to Level 1 after repeated governance-impacting misses in active work. |
| Level 1 (`local_blocking`) | Governance-impacting closeout is blocked locally on required-gap failures. | Block local closeout until `decision-gap-check` and `reflection-completeness-check` pass. | CI remains non-blocking for these checks unless separately required. | Escalate to Level 2 when misses reach release boundary or recur across cycles. |
| Level 2 (`ci_blocking`) | Required governance checks are merge/release gates. | Local flow mirrors CI-required checks before push. | Block protected branch/release on failed required checks. | Downgrade only through explicit policy change and release-note documentation. |

## Release Boundary Required Check Mapping (PH0-005)

Required checks at merge/release boundary:

1. `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all`
2. `python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir .`
3. `python3 scripts/cortex_project_coach_v0.py reflection-completeness-check --project-dir .`
4. `./scripts/quality_gate_ci_v0.sh`

Operational mapping:

- `audit --audit-scope all`: lifecycle governance conformance and drift checks.
- `decision-gap-check`: governance-impacting dirty-file linkage enforcement.
- `reflection-completeness-check`: reflection to decision linkage completeness enforcement.
- `quality_gate_ci_v0.sh`: integrity checks plus focused coach tests and docs/json validation.

## Policy Change Process for Ladder Levels (PH0-005)

1. Propose level change with rationale, scope, and expected impact.
2. Link proposal to decision/reflection artifacts and affected policy/spec files.
3. Obtain `Maintainer Council` approval before applying change to release gates.
4. Publish versioned release notes describing old level, new level, and effective date.
5. Run one stabilization cycle and record observed effects before any further level increase.

## Tactical and Adapter Safeguards

- Tactical records must follow data-class policy (no secrets/PII).
- Tactical data policy source: `policies/tactical_data_policy_v0.md`.
- Adapter integrations are read-only and optional.
- Adapter failure must degrade to governance-only behavior, never hard-block governance commands.
- Sanitization failure on tactical payloads must fail closed for that payload and continue governance-only execution.

## Adapter Degradation Procedure (PH3-007)

1. Detect degradation via `context-load` warnings (`adapter_degraded:*` or `adapter_warning:stale_item`).
2. Continue closeout in governance-only mode; adapter signals are informational only.
3. Re-run required governance commands (`audit --all`, `decision-gap-check`, reflection gate) and require pass before release activity continues.
4. Produce/update Phase 3 adapter artifacts in `.cortex/reports/project_state/`.
5. Do not bypass release boundary checks because of adapter outages; release authority remains governance + quality-gate checks.

## Kill-Switch and Rollback

When stop-rules trigger:

1. Confirm trigger against normative stop-rule set in `playbooks/cortex_vision_master_roadmap_v1.md`.
2. Disable tactical features and/or adapters via runtime kill switch.
3. Run stabilization cycle (audit, checks, tests; no new tactical capability activation).
4. Resume normal flow only after incident review and threshold recovery.

Ownership split:

- Policy authority: `cortex` maintainers define stop-rules and recovery criteria in policy/playbooks.
- Runtime execution: `cortex-coach` maintainers/operators execute kill-switch actions and stabilization runs.
- Boundary source: `policies/cortex_coach_final_ownership_boundary_v0.md`.

Stabilization cycle checklist:

1. `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all --format json`
2. `python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir . --format json`
3. `python3 scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`
4. `./scripts/quality_gate_ci_v0.sh`

## Capacity Governance Cadence

Weekly cadence:

1. Start-of-week checkpoint (Monday): record Codex usage from `/status` and the Codex usage dashboard before scheduling session windows.
2. Mid-week checkpoint (Wednesday): if weekly usage pressure reaches 80% or higher, downgrade the remainder of the week to validation-first workload (fewer implementation windows, no phase-expansion starts).
3. Review-load guard: keep code-review scheduling under the planned weekly review cap and defer non-critical review-heavy work when pressure is rising.
4. End-of-week checkpoint (Friday): update weekly capacity notes in `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md` and carry unfinished implementation into the next cycle instead of skipping governance gates.

Post-Gate-F recurring rollout cadence check:

1. Run:
- `python3 scripts/phase5_recurring_cadence_pack_v0.py --project-dir . --ci-runs 3 --format json --out-file .cortex/reports/project_state/phase5_recurring_cadence_report_v0.json`
2. Require `transition_audit.status=pass` and `transition_completeness_rate=1.0`.
3. Record CI-overhead delta trend from `.cortex/reports/project_state/phase5_recurring_cadence_report_v0.json` in weekly governance review notes.
4. If overhead drift remains above legacy threshold for two consecutive weekly checkpoints, open a maintenance ticket to refresh baseline policy and/or optimize gate runtime.

Budget source note:
- Use the planning envelope and sequencing guidance from the Mulch+Beads synthesized plan proposal report as the default capacity baseline unless superseded by newer approved policy.

## Optional Future Automation

- Add a wrapper (`just session-open`) that runs startup checks automatically.
- Add CI rule to require `--audit-scope all` for protected branches.
- Add automated mode switch to force governance-only behavior when adapter health degrades.

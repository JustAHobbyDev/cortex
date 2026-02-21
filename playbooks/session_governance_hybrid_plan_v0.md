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
- if external adapter is enabled and unhealthy, continue in governance-only mode

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
- run CI quality gate (`just quality-gate-ci`)

Output-contract note:
- For deterministic machine parsing across all commands in this repo, use the delegator entrypoint (`python3 scripts/cortex_project_coach_v0.py`) with `--format json` where needed.

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

## Kill-Switch and Rollback

When stop-rules trigger:

1. Disable tactical features and/or adapters via runtime kill switch.
2. Run stabilization cycle (audit, checks, tests; no new tactical capability activation).
3. Resume normal flow only after incident review and threshold recovery.

## Capacity Governance Cadence

Weekly cadence:

1. Review live usage status and weekly pressure signals.
2. If pressure is high early in week, prioritize governance validation tasks.
3. Avoid scheduling review-heavy milestones above planned weekly review limits.
4. Carry unfinished implementation into next cycle instead of skipping governance gates.

## Optional Future Automation

- Add a wrapper (`just session-open`) that runs startup checks automatically.
- Add CI rule to require `--audit-scope all` for protected branches.
- Add automated mode switch to force governance-only behavior when adapter health degrades.

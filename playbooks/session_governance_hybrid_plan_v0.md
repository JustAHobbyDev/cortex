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

## Enforcement Ladder in Session Operations

1. Advisory mode
- warnings surfaced, local continuation allowed

2. Local blocking mode
- local closeout blocked for governance-impacting gaps

3. CI blocking mode
- protected branch/release blocked until governance checks pass

Escalation to stricter levels should follow policy versioning and release notes.

## Tactical and Adapter Safeguards

- Tactical records must follow data-class policy (no secrets/PII).
- Adapter integrations are read-only and optional.
- Adapter failure must degrade to governance-only behavior, never hard-block governance commands.

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

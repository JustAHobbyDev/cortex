# Session Governance Hybrid Plan v0

Version: v0
Status: Draft
Scope: Cortex maintainer and agent session workflow

## Goal

Balance speed during active work with strong governance enforcement at merge/release boundaries.

## Default Session Flow

1. Session start:
   - run `cortex-coach audit-needed --project-dir . --format json`
2. If `audit_required=true` or `audit_recommended=true`:
   - run `cortex-coach audit --project-dir . --audit-scope cortex-only`
3. During implementation:
   - rerun `cortex-only` audit after significant lifecycle/policy/decision changes
4. Before merge/release:
   - run `cortex-coach audit --project-dir . --audit-scope all`
   - run `cortex-coach decision-gap-check --project-dir . --format json`
   - run CI quality gate (`just quality-gate-ci`)

## Decision Reflection Step

Before closeout, ask:
- Did this work change governance, policy, release gates, safety posture, or maintainer workflow?

If yes:
- `cortex-coach decision-capture ...`
- `cortex-coach decision-promote ...`
- ensure linked artifacts are committed

## Enforcement Targets

- Local default: `cortex-only` keeps feedback fast and focused.
- Release/merge gate: `all` prevents governance drift across broader repo artifacts.
- CI: fails on governance violations, including `decision-gap-check`.

## Optional Future Automation

- Add a wrapper (`just session-open`) that runs startup checks automatically.
- Add CI rule to require `--audit-scope all` for protected branches.

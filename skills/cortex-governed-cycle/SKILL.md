---
name: cortex-governed-cycle
description: "Execute the standard Cortex governance cycle for non-trivial work: audit-needed decision, coach/audit execution, decision-reflection capture, required quality-gate validation, and clean closeout hygiene. Use for meaningful code, policy, playbook, contract, CI, or release-surface changes in Cortex-governed repositories."
---

# Cortex Governed Cycle

## Overview

Run Cortex implementation work through the required governance loop. Use this workflow to keep decisions, audits, and gate evidence consistent before closeout.

## Workflow

1. Assess whether work is non-trivial and governance-impacting.
2. Run preflight `audit-needed` and branch on `audit_required`.
3. Run `coach` + `audit` when required.
4. Capture and promote decision/reflection artifacts when behavior, policy, or gates changed.
5. Run required quality gate.
6. Remove incidental generated artifact noise before commit.
7. Report clean git state and gate status in handoff.

Use `references/commands.md` for exact command blocks.

## Scope Heuristics

Treat work as governance-impacting when it touches:

- `policies/`, `playbooks/`, `contracts/`, `specs/`
- `.cortex/artifacts/` and `.cortex/reports/` governance evidence
- `scripts/quality_gate*.sh` or governance gate scripts
- `scripts/cortex_project_coach_v0.py`

Treat tiny typo-only edits as low-risk, but still run required gate before merge/release.

## Closeout Rules

1. Never close out with unresolved gate failures.
2. Never leave decision-gap uncovered files unlinked when governance-impact changes were made.
3. Never keep incidental generated timestamp-only noise in commit diff.

## References

- `references/commands.md`: canonical command sequence and cleanup commands

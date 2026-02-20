# Decision Reflection Policy v0

Version: v0
Status: Active
Scope: Cortex operating layer and maintainer workflows

## Purpose

Ensure important workflow/governance decisions are reflected in operating artifacts and not left implicit in implementation changes.

## Rule

Before closing substantial work, run a decision reflection check:

1. Did this change affect governance, policy, release gates, safety posture, or maintainer workflow?
2. If yes:
   - capture with `cortex-coach decision-capture`
   - include impact scope and linked artifacts
   - promote with `cortex-coach decision-promote` when accepted
3. If no:
   - explicitly record that no operating-layer decision was introduced

## Trigger Examples

- quality gate behavior changes
- dependency/toolchain determinism changes
- contract compatibility policy changes
- audit severity/risk posture changes
- policy or governance document changes

## Expected Outcome

Every operating-significant decision has:

- a decision artifact
- linked code/doc/policy updates
- traceability across governance and implementation layers

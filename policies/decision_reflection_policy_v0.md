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

## Agent-Agnostic Reflection Loop (Required)

This loop is mandatory for governance-relevant mistakes and applies to any coding assistant.

1. Reflect:
   - describe the concrete failure and why it happened
2. Abstract:
   - extract the recurring pattern behind the instance
3. Generalize:
   - define a reusable rule with boundary conditions
4. Encode:
   - write or update durable artifacts in this order:
     - decision artifact in `.cortex/artifacts/decisions/`
     - policy/playbook updates in `policies/` or `playbooks/` as needed
     - prompt/context guidance in `.cortex/prompts/` only when execution behavior must change
5. Validate:
   - run governance checks (`decision-gap-check`, `reflection_enforcement_gate_v0.py`, and relevant audits) before closeout

## Portability Constraint

- The loop must not depend on assistant-specific files or branding.
- Do not require `CLAUDE.md`, `AGENTS.md`, or any single-agent document as the system of record.
- Canonical operating memory remains repository artifacts under `.cortex/`, `policies/`, `playbooks/`, and related tracked outputs.

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

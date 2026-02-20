# Cortex Coach Decision Reflection Policy

Version: v0
Status: Active
Scope: This repository (`/home/d/codex/cortex`)

## Purpose

Ensure important process/governance decisions made during implementation are captured and reflected in operating artifacts, not left implicit in code diffs.

## Rule

Before closing a substantial task, run a decision reflection step:

1. Ask: "Did this work change operating behavior, governance, policy, release gates, safety posture, or maintainer workflow?"
2. If yes:
   - run `cortex-coach decision-capture`
   - include concrete impact scope and linked artifacts
   - promote with `cortex-coach decision-promote` when accepted
3. If no:
   - proceed without capture
   - note that no operating-layer decision was introduced

## Agent-Agnostic Reflection Contract

This contract is required for governance-relevant learning and is assistant-neutral.

1. Reflect:
   - identify the concrete failure in the attempted change
2. Abstract:
   - derive the recurring pattern
3. Generalize:
   - define the reusable directive and limits
4. Encode:
   - persist changes in repository operating artifacts in this order:
     - `.cortex/artifacts/decisions/`
     - `policies/` or `playbooks/` when broader behavior changes
     - `.cortex/prompts/` only when execution prompting must change
5. Validate:
   - run `cortex-coach decision-gap-check` and project audit checks before closeout

## Portability Constraint

- This policy must work with Codex, Claude, and other assistants.
- Reflection outputs must be auditable from checked-in artifacts, not chat memory.
- Do not make assistant-specific docs the canonical governance memory.

## Trigger Examples

Treat these as likely requiring decision capture:

- quality-gate behavior changes
- dependency/toolchain determinism changes
- contract compatibility rules
- audit/validation severity or blocking logic changes
- operating policy additions/removals

## Minimum Decision Entry Requirements

Each captured decision should include:

- clear decision statement
- rationale/tradeoff
- impact scope tags
- linked artifacts updated by the decision

## Enforcement Style

This policy is enforced as operating discipline, and can be promoted to CI policy checks when mature.

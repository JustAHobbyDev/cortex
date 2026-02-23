# Fixed Policy vs Implementation Choice Matrix v0

Version: v0  
Status: Active  
Scope: governance handoff and execution boundary classification

## Purpose

Define how Cortex classifies decisions as either fixed policy or implementation choice so teams can preserve governance integrity while maintaining delivery speed.

## Why Use Both

Using both categories gives a clear authority boundary:

- fixed policy defines non-negotiable governance behavior
- implementation choice preserves engineering flexibility where variation is acceptable

## Fixed Policy

Pros:

- Enforces stable guardrails for safety, governance, and release boundaries.
- Improves auditability and cross-session consistency.
- Reduces drift from ad hoc interpretation.

Cons:

- Slower to change because policy updates require formal governance flow.
- Can reduce implementation flexibility if overused.
- Policy surface can bloat if low-impact items are classified as fixed.

## Implementation Choice

Pros:

- Enables faster iteration and local optimization.
- Supports experimentation and reversible design changes.
- Reduces policy churn for low-risk engineering details.

Cons:

- Increases variance across contributors and sessions.
- Creates drift risk if choices are not tracked and reviewed.
- Can weaken comparability if too many critical items remain non-fixed.

## Rule of Thumb

Classify as fixed policy when behavior affects:

- governance authority
- safety/compliance
- release-blocking gates
- non-bypass control expectations

Classify as implementation choice when behavior is:

- reversible
- performance/tooling focused
- project-context dependent
- non-authoritative to governance closure semantics

## Required Review Behavior

At handoff and major phase boundaries:

1. Confirm the matrix still reflects current practice.
2. Promote any repeated high-impact implementation choices to fixed policy when needed.
3. Record classification changes via decision/reflection linkage.

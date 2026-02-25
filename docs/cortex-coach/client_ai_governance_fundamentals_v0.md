# Client AI Governance Fundamentals v0

Version: v0  
Status: Active  
Scope: Core teaching material for onboarding module `M0`

## Purpose

Provide a clear, reusable baseline for teaching:

1. What AI governance is.
2. What problems AI governance solves.
3. How AI governance works in practice.
4. How Cortex implements AI governance inside a project.

## 1) What AI Governance Is

AI governance is the set of rules, controls, evidence, and accountability mechanisms that keep AI-assisted delivery safe, auditable, and aligned with project intent.

In practical terms, governance answers:

1. Who is allowed to decide what.
2. What checks must pass before closeout or release.
3. How decisions and exceptions are recorded.
4. How drift, mistakes, and risk are detected and corrected.

## 2) Problems AI Governance Solves

Without governance, teams commonly hit:

1. Untracked decision drift:
- Important behavior changes without clear decision records.
2. Unsafe speed:
- Fast iteration with missing safety checks or weak release discipline.
3. Accountability gaps:
- No clear owner for policy exceptions or failures.
4. Non-reproducible outcomes:
- Different operators/agents produce different quality and evidence.
5. Hidden operational risk:
- AI output quality looks good locally but fails at merge/release boundary.

## 3) How AI Governance Works

A practical governance system combines five layers:

1. Policy:
- Defines non-negotiable rules and authority boundaries.
2. Contracts:
- Machine-checkable schemas/specs for required outputs and behavior.
3. Gates:
- Deterministic checks that enforce pass/fail behavior before closeout.
4. Evidence:
- Durable artifacts proving what happened and why.
5. Escalation:
- Explicit owner/reviewer paths for exceptions and unresolved risk.

## 4) How Cortex Implements AI Governance in a Project

Cortex applies those layers through concrete project mechanics:

1. Project-state boundary:
- Project-local lifecycle state is constrained under `.cortex/` by policy and gate enforcement.
2. Deterministic command surface:
- `cortex-coach` commands and scripts emit machine-readable outputs for auditability.
3. Required release-boundary gates:
- Checks such as `audit`, `decision-gap-check`, reflection enforcement, hydration compliance, and boundary gate block unsafe closeout.
4. Decision and reflection discipline:
- Governance-impacting changes require linked decisions/reflections and promotion flow.
5. Rollout controls:
- Mode transitions (`off|experimental|default`) remain auditable and reversible.

## 5) Teaching Flow for Module M0

Recommended sequence:

1. Define terms:
- Governance Plane, Tactical Plane, Promotion Plane.
2. Map risks:
- Show one concrete failure mode per governance problem above.
3. Map controls:
- Show which Cortex control prevents each failure mode.
4. Run a quick evidence walkthrough:
- Open recent gate artifacts and trace decision -> reflection -> gate pass.
5. Confirm ownership:
- Assign Program Lead, Governance Owner, and reviewer responsibilities.

## 6) Minimum M0 Exit Check (AI Governance Portion)

The team should be able to explain:

1. Why required gates exist and what they protect.
2. Which actions are blocked vs advisory.
3. How decisions/reflections are linked to governance-impacting changes.
4. Where to find evidence artifacts for audit and closeout.

## 7) Suggested Evidence for M0

1. Team operating charter with named governance owners.
2. One-page control map (problem -> Cortex control -> artifact path).
3. M0 completion note linked from onboarding completion report.

# Claude-Meta Comparison + Agent-Agnostic Reflection Integration Plan v0

## Purpose
- Compare .cortex/aviadr1/claude-meta with `cortex + cortex-coach`.
- Define how to adopt the useful reflection loop pattern without coupling it to a specific agent.

## Sources
- https://github.com/aviadr1/claude-meta
- Local repo governance/runtime artifacts under .cortex/, `policies/`, `playbooks/`, and `scripts/`.

## Executive Summary
- `claude-meta` optimizes for lightweight, in-session self-improvement through a markdown-first loop: reflect -> abstract -> generalize -> write rule.
- `cortex + cortex-coach` optimizes for enforceable governance, auditable decisions, and CI-integrated controls across sessions.
- The right synthesis is to keep `cortex` as the system of record and add an agent-agnostic reflection contract that any assistant can execute.

## Compare and Contrast

### Primary Unit of Control
- `claude-meta`: one evolving instruction document (`CLAUDE.md`) plus meta-rules.
- `cortex + cortex-coach`: multiple explicit operating layers (policies, decisions, plans, audits, runbooks).

### Enforcement Model
- `claude-meta`: behavior shaped mainly by prompt structure and disciplined usage.
- `cortex + cortex-coach`: behavior checked with scripts, audits, policy boundaries, and quality gates.

### Learning Loop
- `claude-meta`: human notices mistake, asks for reflection, agent writes back into guidance doc.
- `cortex + cortex-coach`: decisions should be promoted into governance artifacts and validated by checks.

### Portability Across Agents
- `claude-meta`: currently branded around Claude and `CLAUDE.md`.
- `cortex + cortex-coach`: already oriented to project governance, but reflection prompts still need a generic contract.

### Failure Modes
- `claude-meta`: rule sprawl, inconsistent structure, weak external verification.
- `cortex + cortex-coach`: process overhead, missed reflection capture if policy discipline is not maintained.

## Integration Goal
- Preserve `cortex` governance authority.
- Add a standard reflection loop that works with any agent (`Codex`, `Claude`, others) without changing project guarantees.

## Agent-Agnostic Reflection Contract

### Trigger
- Any recurring mistake, policy bypass, quality-gate failure root cause, or repeated reviewer correction.

### Required Loop
1. Reflect: describe what failed in the specific change attempt.
2. Abstract: identify the recurring pattern, not just the instance.
3. Generalize: define a reusable directive and boundary condition.
4. Encode: write/update operating-layer artifacts in this order:
   - Decision artifact under .cortex/artifacts/decisions/
   - Policy/playbook update in `policies/` or `playbooks/` when needed
   - Prompt/context update under .cortex/prompts/ only if execution guidance must change
5. Validate: run decision/audit checks and confirm no new governance gap.

### Normative Requirements
- The loop must never be tied to an agent-specific filename (`CLAUDE.md`, etc.).
- The loop output must be reviewable as normal repo artifacts.
- The loop must produce at least one durable, auditable artifact when a governance-relevant decision is made.

## Proposed Implementation in Cortex

### Phase A: Prompt + Policy Normalization
- Add an explicit "Agent-Agnostic Reflection Loop" section to `policies/decision_reflection_policy_v0.md`.
- Add a reusable prompt template in .cortex/prompts/ that uses neutral language (`assistant` or `agent`).

### Phase B: Coach Runtime Support
- Add a coach command (or option) that scaffolds reflection outputs:
  - suggested decision filename
  - policy/playbook touchpoints
  - checklist for audit follow-through
- Keep command wording agent-neutral.

### Phase C: Governance Completeness Tracking
- Extend decision checks so a flagged reflection event must map to:
  - decision artifact presence
  - optional policy/playbook update rationale
  - closure evidence in audit reports

### Phase D: Adoption Pattern
- During reviews: if "same mistake twice" occurs, invoke reflection contract immediately.
- During closeout: verify reflection outputs are integrated before final plan closure.

### Phase E: Project-Agnostic Gate Framework + Project Adapters
- Define a portable gate framework in `cortex-coach` with:
  - stable governance core checks (`audit-needed`, `decision-gap-check`, `reflection-completeness-check`, `audit`)
  - pluggable project adapters for toolchain checks (for example `pytest`, `npm`, `cargo`, custom scripts)
- Treat generated gate scripts as project-scaffold outputs, not universal hardcoded policy.
- Prefer executable gates over instructions-only prompts for enforcement-critical checks.
- Keep project-specific checks configurable by manifest/config contract rather than embedded assumptions.

## Minimal Prompt Template (Agent-Agnostic)
- "Reflect on this mistake. Abstract the underlying pattern. Generalize a reusable rule. Encode the rule into cortex operating artifacts (decision first, then policy/playbook updates as needed), and run governance checks."

## Guardrails
- Do not treat transient implementation choices as governance decisions.
- Do not skip decision promotion when a workflow/tooling standard is chosen for future sessions.
- Do not rely on private chat memory; rely on checked-in artifacts.

## Success Criteria
- Reflection loop can be run by any agent with equivalent outputs.
- Decision-gap checks remain pass while reflection coverage increases.
- New contributors can understand prior learning from repo artifacts alone.

## Notes
- This plan intentionally keeps `cortex` as the canonical operating layer; it imports the loop discipline from `claude-meta`, not its agent-specific document contract.

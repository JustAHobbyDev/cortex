# Cortex Vision Master Roadmap v1

## Purpose

Define the end-to-end path from current state to a friction-reduced, project-agnostic governance operating layer that can safely incorporate tactical runtime memory and work-graph context.

## Current Baseline

- `cortex`: governance/source-of-truth artifacts are active and enforced.
- `cortex-coach`: standalone runtime exists with decision and reflection enforcement.
- CI/local gates are functional but still repo-specific in shape.

## Vision Target

`cortex + cortex-coach` should provide:

1. Fast onboarding (first-success in minutes)
2. Strong governance integrity (decision + reflection + audit traceability)
3. Project-agnostic portability (framework core + project adapters)
4. Low operational overhead (minimal command burden)
5. Durable learning across sessions and agents

## Vision Expansion: Dual-Plane Model

### Governance Plane (authoritative)

- Canonical artifacts in .cortex/ and governance directories are the only source of truth for policy/spec/decision authority.
- Release and merge gates MUST evaluate governance plane artifacts as the authoritative closure source.

### Tactical Plane (non-authoritative by default)

- Runtime may capture fast tactical memory/work context to improve execution speed.
- Tactical outputs are advisory until promoted through governance rules and MUST NOT close governance-impacting work alone.

### Promotion Plane (bridge contract)

- Tactical insights become canonical only through explicit promotion with evidence and linked artifacts.
- Governance-impacting changes must not close without decision/reflection linkage.
- Promotion schema is defined in `contracts/promotion_contract_schema_v0.json`.

## Non-Negotiable Constraints

- Governance enforcement remains artifact-based, not chat-memory-based.
- Runtime behavior belongs in `cortex-coach`; governance model belongs in `cortex`.
- Project-specific checks remain adapter-based, not hardcoded.
- Tactical plane cannot bypass governance gates.
- External adapters are optional and must fail-open to governance-only mode.

## Roadmap Phases

### Phase 0: Governance Lock-In

Goal: codify dual-plane authority, promotion contracts, and stop-rules.

Deliverables:
- Policy/spec updates for canonical authority and promotion requirements.
- Tactical data policy (content class limits, retention, redaction, prohibitions) in `policies/tactical_data_policy_v0.md`.
- Promotion contract schema in `contracts/promotion_contract_schema_v0.json`.
- Adapter safety policy (read-only, timeout, degradation behavior).
- Rollback/kill-switch rules and ownership matrix.

Exit Criteria:
- Cross-repo boundary and governance responsibilities are unambiguous.
- Stop-rules and emergency controls are documented and approved.

### Phase 1: Tactical Memory Foundation

Goal: add fast tactical capture and retrieval behind experimental controls.

Deliverables:
- Runtime tactical commands and schemas.
- Setup/onboarding integrations for supported agent environments.
- Deterministic tactical storage and mutation guardrails.

Exit Criteria:
- Tactical commands are deterministic and bounded.
- Governance checks show no regression.

### Phase 2: Retrieval and Context Quality

Goal: improve context relevance under strict budgets.

Deliverables:
- Ranked retrieval and deterministic tie-breakers.
- Tactical compaction/pruning policy.
- Source provenance and confidence annotations in context bundles.

Exit Criteria:
- Relevance improves without context-budget or latency regressions.

### Phase 3: External Work-Graph Adapter

Goal: support optional ingestion of tactical execution signals (for example Beads).

Deliverables:
- Read-only adapter contract and implementation.
- Timeout/circuit-breaker behavior with governance-only fallback.
- Adapter health and provenance reporting.

Exit Criteria:
- Adapter outages cannot block governance operations.
- No hidden dependency on external system for mandatory gates.

### Phase 4: Promotion and Enforcement Hardening

Goal: convert tactical learning into durable governance assets with strict linkage.

Deliverables:
- Promotion assistant and evidence scoring flow.
- Enforcement ladder integration for decision/reflection completeness.
- Governance debt visibility (ready/blocked governance actions).

Exit Criteria:
- Governance coverage metrics improve or hold steady.
- Unlinked governance-impacting closures are blocked.

### Phase 5: Rollout and Migration

Goal: move from experimental to default operation safely.

Deliverables:
- Rollout modes: `off`, `experimental`, `default`.
- Migration playbooks and operator guides.
- Cross-project reference implementations.

Exit Criteria:
- SLO and gate reliability thresholds pass for two consecutive cycles.
- Adoption targets are met without governance regression.

## Milestones and Sequencing

1. Phase 0 completes before any tactical feature is default-on.
2. Phase 1 and 2 complete before external adapter default use.
3. Phase 3 must pass degradation tests before broader adoption.
4. Phase 4 must pass governance linkage checks before default-on promotion.
5. Phase 5 begins only after prior gate stability.

## Release Gates and Stop-Rules

### Required Gates

- Decision-gap and reflection completeness checks pass at release boundary.
- Audit (`--audit-scope all`) passes at release boundary.

### Stop-Rules (rollout pause triggers)

- `context-load` p95 exceeds target for two consecutive cycles.
- CI mandatory governance runtime increase exceeds threshold for two consecutive cycles.
- Any adapter incident causes governance gate false pass/fail behavior.
- Reflection/decision coverage trend drops below threshold.

### Recovery

- Force `off` or `experimental` mode via kill switch.
- Run stabilization cycle (no new tactical capability activation).
- Resume rollout only after incident postmortem and threshold recovery.

## Capacity-Aware Sequencing (Codex Plus)

- Plan work in 5-hour session windows, not fixed weekly tokens.
- Respect weekly review gates and dashboard `/status` usage signals.
- If weekly usage pressure is high by mid-week, defer feature expansion and run validation-only tasks.

## Success Metrics

- Onboarding:
  - median time from install to first green gate
- Reliability:
  - rate of governance-impact changes with decision coverage
- Reflection quality:
  - reflection scaffold -> decision mapping rate
- Portability:
  - number of projects/stacks running adapter-based gates
- Operator overhead:
  - median commands executed per feature/change closeout
- Stability:
  - rollout stop-rule triggers per quarter

## Risks and Mitigations

- Risk: tactical plane dilutes governance rigor.
  - Mitigation: canonical-authority rule + promotion-only durability.
- Risk: external adapters increase runtime fragility.
  - Mitigation: read-only adapter policy + fail-open governance-only fallback.
- Risk: rollout outpaces account capacity.
  - Mitigation: capacity-aware sequencing tied to live usage signals.
- Risk: drift between `cortex` contract and `cortex-coach` runtime.
  - Mitigation: paired contract/runtime updates and contract tests.

## Immediate Next Actions

1. Land Phase 0 policy/spec updates in `cortex`.
2. Wire runtime and CI checks to promotion schema and tactical data policy.
3. Define adapter interface spec and degradation tests.
4. Validate enforcement ladder mapping against current quality gates.

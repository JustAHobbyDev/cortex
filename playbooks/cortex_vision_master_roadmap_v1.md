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

## Governance Driven Development for Swarms (Normative)

Swarm execution is a tactical acceleration layer, not an authority layer. Cortex MUST enforce governance closure semantics even when multi-agent runtimes are active.

### Swarm-GDD Rules

1. Governance-impacting closure requires linked decision and reflection artifacts.
2. Swarm runtime outputs are non-authoritative until promoted through governance plane artifacts.
3. Swarm mutation rights are capability-scoped and least-privilege by default.
4. Swarm failures must degrade safely (`swarm -> single-agent -> governance-only`).
5. Canonical release/merge closure is blocked unless required governance gates pass.

### Required Swarm Gate Bundle

At release boundary and governance-impact merge boundaries, all checks below MUST pass:

1. `cortex-coach decision-gap-check --project-dir . --format json`
2. `cortex-coach reflection-completeness-check --project-dir . --required-decision-status promoted --format json`
3. `cortex-coach audit --project-dir . --audit-scope all --format json`
4. `scripts/project_state_boundary_gate_v0.py --project-dir . --format json`
5. `scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`

### Swarm Gate Execution Mapping (PH0-011)

| Required Swarm Gate | Local execution path | CI/release execution path | Mapping note |
|---|---|---|---|
| `decision-gap-check` | `scripts/quality_gate_v0.sh` (step 4 of 9) | `scripts/quality_gate_ci_v0.sh` (step 3 of 8) | direct command execution in both gates |
| `reflection-completeness-check` | `scripts/quality_gate_v0.sh` (step 5 of 9) via `scripts/reflection_enforcement_gate_v0.py` | `scripts/quality_gate_ci_v0.sh` (step 4 of 8) via `scripts/reflection_enforcement_gate_v0.py` | enforced through reflection gate wrapper (which runs completeness checks and linkage thresholds) |
| `audit --audit-scope all` | pre-merge/release flow in `playbooks/session_governance_hybrid_plan_v0.md` | pre-merge/release flow in `playbooks/session_governance_hybrid_plan_v0.md` | required boundary check before running quality gate |
| `project_state_boundary_gate_v0.py` | `scripts/quality_gate_v0.sh` (step 6 of 9) | `scripts/quality_gate_ci_v0.sh` (step 5 of 8) | direct fail-closed path boundary enforcement |
| `reflection_enforcement_gate_v0.py` | `scripts/quality_gate_v0.sh` (step 5 of 9) | `scripts/quality_gate_ci_v0.sh` (step 4 of 8) | direct fail-closed enforcement of decision/reflection linkage |

This mapping is the normative Swarm-GDD local/CI execution contract for Phase 0 baseline.

### Swarm-GDD Exit Criteria

Swarm governance readiness is achieved only when:

1. Swarm authority, closeout, and degradation rules are codified in policy/spec artifacts.
2. Required Swarm Gate Bundle is mapped into local + CI quality execution paths.
3. Kill-switch ownership and stabilization-cycle workflow are documented and tested.
4. At least one end-to-end swarm-governed change closes with full decision/reflection/audit linkage and no gate bypass.

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

### Phase 6: Bootstrap and GDD Scale-Out

Goal: make Cortex a deterministic bootstrap layer for new projects and governed multi-agent execution.

Deliverables:
- Bootstrap flow for fresh repos with required governance artifacts and gates wired by default.
- Governance capsule hydration invariants for session start and context rollover.
- Configurable project-boundary contract with `.cortex` as default boundary root.
- Role/capability pack for multi-agent GDD operation with fail-safe degradation.
- Gate G measurement and closeout package.

Exit Criteria:
- Fresh-repo bootstrap reaches first required green gate within target budget.
- Hydration and boundary conformance checks are pass and auditable.
- Pilot repos demonstrate governed closeout without bypass.

## Milestones and Sequencing

1. Phase 0 completes before any tactical feature is default-on.
2. Phase 1 and 2 complete before external adapter default use.
3. Phase 3 must pass degradation tests before broader adoption.
4. Phase 4 must pass governance linkage checks before default-on promotion.
5. Phase 5 begins only after prior gate stability.
6. Swarm runtime adoption beyond experimental is blocked until Swarm-GDD Exit Criteria are met.
7. Phase 6 begins only after Gate F closeout and default-mode governance linkage are complete.

## Release Gates and Stop-Rules

### PH0-006 Ownership Split

- `cortex` owns stop-rule definitions, rollback policy semantics, and recovery approval criteria.
- `cortex-coach` owns runtime kill-switch operation and stabilization-cycle execution.
- Canonical ownership boundary source: `policies/cortex_coach_final_ownership_boundary_v0.md`.
- Operational procedure source: `playbooks/session_governance_hybrid_plan_v0.md`.

### Required Gates

- Decision-gap and reflection completeness checks pass at release boundary.
- Audit (`--audit-scope all`) passes at release boundary.
- Project-state boundary gate passes at release boundary.
- Reflection enforcement gate passes at release boundary.

### Stop-Rules (rollout pause triggers)

- `context-load` p95 exceeds target for two consecutive cycles.
- CI mandatory governance runtime increase exceeds threshold for two consecutive cycles.
- Any adapter incident causes governance gate false pass/fail behavior.
- Reflection/decision coverage trend drops below threshold.
- Swarm rollout beyond `experimental` is blocked until Swarm-GDD Exit Criteria and at least one verified end-to-end gate-sequence note are present.

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

1. Done: Gate F closeout artifacts and default-mode decision linkage are published.
  - Current state: Gate F closeout published and default mode activated with audited linkage.
2. Done: keep rollout transitions auditable and reversible; preserve `default -> experimental -> off` rollback readiness.
  - Evidence: `.cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json`
3. Done: track quality-gate CI overhead and transition-audit completeness in recurring governance cadence.
  - Evidence: `.cortex/reports/project_state/phase5_recurring_cadence_report_v0.json`;`playbooks/session_governance_hybrid_plan_v0.md`
4. Done: route expansion through Phase 6 definitions (kickoff board + measurement baseline).
  - `playbooks/cortex_phase6_bootstrap_gdd_ticket_breakdown_v0.md`
  - `playbooks/cortex_phase6_measurement_plan_v0.md`
5. Done: complete PH6-002 hydration invariants and PH6-003 configurable boundary contract baselines.
  - `scripts/context_hydration_gate_v0.py`
  - `.cortex/reports/project_state/phase6_hydration_compliance_report_v0.json`
  - `scripts/phase6_boundary_conformance_harness_v0.py`
  - `.cortex/reports/project_state/phase6_boundary_conformance_report_v0.json`
6. Done: complete PH6-004 deterministic bootstrap scaffolder for fresh project initialization and first-green-gate workflow.
  - `scripts/cortex_project_coach_v0.py`
  - `docs/cortex-coach/quickstart.md`
  - `docs/cortex-coach/commands.md`
  - `.cortex/templates/bootstrap_first_green_gate_checklist_template_v0.md`
  - `.cortex/reports/project_state/phase6_bootstrap_scaffold_report_v0.json`
7. Done: complete PH6-005 GDD role + capability pack to formalize role minimums, permissions, and escalation matrix.
  - `playbooks/cortex_phase0_role_charters_v0.md`
  - `docs/cortex-coach/README.md`
  - `.cortex/reports/project_state/phase6_role_capability_pack_report_v0.md`
8. Done: complete PH6-006 bootstrap readiness harness + certification evidence for first-green-gate portability checks.
  - `scripts/client_onboarding_certification_pack_v0.py`
  - `.cortex/reports/project_state/phase6_bootstrap_readiness_report_v0.json`
  - `.cortex/reports/project_state/client_onboarding_certification_pack_v0.json`
9. Done: complete PH6-007 external pilot validation on non-Cortex seed repos.
  - `scripts/phase6_external_pilot_harness_v0.py`
  - `.cortex/reports/project_state/phase6_external_pilot_report_v0.md`
  - `.cortex/reports/project_state/phase6_external_pilot_report_v0.json`
10. Done: complete PH6-008 Gate G closeout + next-phase recommendation package.
  - `.cortex/reports/project_state/phase6_gate_g_measurement_closeout_v0.md`
  - `.cortex/reports/project_state/phase6_operator_overhead_report_v0.json`
11. Done: client enablement track is established with execution board and CT-006 certification automation evidence.
12. Next: define next expansion phase scope and measurement baseline, starting with a larger external portability matrix.

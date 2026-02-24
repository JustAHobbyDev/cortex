# Cortex Phase 2 Retrieval and Context Quality Ticket Breakdown v0

Version: v0  
Status: Draft  
Date: 2026-02-24  
Scope: Phase 2 implementation ticket set for retrieval quality and context-loader upgrades in `cortex-coach`

## Purpose

Open a bounded, measurable Phase 2 ticket set so retrieval relevance and context quality improve without weakening governance integrity or budget constraints.

## Source Inputs

- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_phase2_measurement_plan_v0.md`
- `.cortex/reports/project_state/phase1_gate_b_measurement_closeout_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`
- `policies/tactical_data_policy_v0.md`

## Guardrails (Non-Negotiable)

- Governance plane remains authoritative; tactical retrieval outputs stay non-authoritative until promoted.
- Phase 2 outputs remain behind experimental controls.
- Non-interactive command outputs remain automatable (`--format text|json`).
- Retrieval ranking and tie-break behavior must be deterministic.
- Context budget and latency targets remain bounded and measured.
- External adapter behavior is out of Phase 2 scope (Phase 3).

## Execution Order

1. `PH2-001` retrieval contract and baseline freeze
2. `PH2-002` to `PH2-005` retrieval/runtime quality features
3. `PH2-006` to `PH2-007` evaluation, hardening, and regression validation
4. `PH2-008` Gate C closeout package

## Execution Board

Status vocabulary:
- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

| Ticket | Title | Status | Owner (Suggested Role) | Primary Reviewer (Suggested Role) | Target Week | Target Date | Blockers | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PH2-001 | Retrieval Contract Baseline + Query Profile Freeze | done | Contract/Schema Lead | Runtime Reliability Lead | Week 5 | 2026-03-24 | - | `contracts/context_load_retrieval_contract_v0.md`;`.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`;`specs/cortex_project_coach_spec_v0.md`;`docs/cortex-coach/commands.md` | Contract + fixture freeze landed in `cortex` commit `63d53fb`. |
| PH2-002 | `context-load` Ranked Retrieval + Deterministic Tie-Breaks | done | Runtime Reliability Lead | Contract/Schema Lead | Week 5 | 2026-03-27 | - | `specs/cortex_project_coach_spec_v0.md`;`docs/cortex-coach/commands.md`;`cortex-coach` runtime/tests | Runtime ranked retrieval/tie-break implementation landed in `cortex-coach` commit `af6385b`. |
| PH2-003 | Evidence/Outcome Weighting Option | done | Runtime Reliability Lead | Governance Policy Lead | Week 5 | 2026-03-29 | - | `specs/cortex_project_coach_spec_v0.md`;`docs/cortex-coach/commands.md`;`cortex-coach` runtime/tests | Bounded weighting presets + deterministic tests + invalid-mode fail-closed checks landed in `cortex-coach` commit `af6385b`. |
| PH2-004 | Tactical Compaction + Stale-Pruning Policy Integration | done | Security & Data Policy Lead | Governance Enforcement Lead | Week 6 | 2026-04-01 | - | `policies/tactical_data_policy_v0.md`;`specs/cortex_project_coach_spec_v0.md`;`cortex-coach` runtime/tests | Runtime compaction policy controls (`disabled|stale_only|stale_and_duplicate`), protected-class/tag safeguards, deterministic reason codes, and regression tests landed in `cortex-coach` commit `358c702`. |
| PH2-005 | Provenance + Confidence Enrichment in Context Bundles | done | Governance Enforcement Lead | Contract/Schema Lead | Week 6 | 2026-04-03 | - | `specs/cortex_project_coach_spec_v0.md`;`docs/cortex-coach/commands.md`;`contracts/`;`cortex-coach` runtime/tests | `context-load` now emits per-entry provenance (`source_kind/source_ref/source_refs`) and bounded confidence metadata with deterministic regression coverage in `cortex-coach` commit `573f292`. |
| PH2-006 | Retrieval Evaluation Fixture Set + Scoring Harness | todo | Conformance QA Lead | Runtime Reliability Lead | Week 7 | 2026-04-07 | PH2-002,PH2-003,PH2-005 | `.cortex/reports/project_state/phase2_retrieval_relevance_report_v0.json`;`.cortex/reports/project_state/phase2_retrieval_determinism_report_v0.json` | Publish fixed evaluation profiles and deterministic relevance scoring outputs. |
| PH2-007 | Performance/Budget Hardening + Governance Non-Regression Pack | todo | CI/Gate Owner | Conformance QA Lead | Week 7 | 2026-04-10 | PH2-004,PH2-005,PH2-006 | `.cortex/reports/project_state/phase2_latency_report_v0.json`;`.cortex/reports/project_state/phase2_context_budget_report_v0.json`;`.cortex/reports/project_state/phase2_ci_overhead_report_v0.json`;`.cortex/reports/project_state/phase2_governance_regression_report_v0.md` | Confirm Phase 2 stays inside latency/context/CI budgets and required gates remain green. |
| PH2-008 | Gate C Measurement Closeout and Readiness Determination | todo | Program Lead | Maintainer Council | Week 7 | 2026-04-12 | PH2-001,PH2-002,PH2-003,PH2-004,PH2-005,PH2-006,PH2-007 | `.cortex/reports/project_state/phase2_gate_c_measurement_closeout_v0.md`;`playbooks/cortex_phase2_measurement_plan_v0.md` | Publish Gate C pass/fail determination with explicit residual-risk ownership if needed. |

## Tickets

### PH2-001: Retrieval Contract Baseline + Query Profile Freeze

Objective:
- Define explicit Phase 2 retrieval semantics and freeze evaluation profiles before runtime changes.

Primary artifacts:
- `contracts/context_load_retrieval_contract_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/commands.md`
- `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`

Acceptance criteria:
- `context-load` retrieval ranking strategy and tie-break order are explicit.
- Weighting option contract shape and bounds are explicit.
- Fixed evaluation profiles (`small`, `medium`, `large`) and query sets are declared and frozen.
- JSON output semantics and error classes remain machine-parsable.

Evidence:
- `contracts/context_load_retrieval_contract_v0.md`
- `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/commands.md`

### PH2-002: `context-load` Ranked Retrieval + Deterministic Tie-Breaks

Objective:
- Implement deterministic ranked retrieval in `context-load`.

Primary artifacts:
- `cortex-coach` runtime implementation and tests
- `specs/cortex_project_coach_spec_v0.md`

Acceptance criteria:
- Deterministic ranking order is enforced for repeated identical input/state.
- Tie-break chain is explicit and stable.
- No-match and low-confidence behavior remains deterministic and machine-readable.
- Existing command contract compatibility remains intact.

Evidence:
- runtime/test updates in `cortex-coach`
- linked spec updates

### PH2-003: Evidence/Outcome Weighting Option

Objective:
- Add an optional weighting mode that improves context utility while preserving determinism and safety.

Primary artifacts:
- `cortex-coach` runtime/tests
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/commands.md`

Acceptance criteria:
- Weighting parameters are bounded and validated.
- Default behavior remains backward-compatible when option is omitted.
- Same input/weights/state produce deterministic normalized output.
- Invalid weighting inputs fail with deterministic error classing.

Evidence:
- runtime/test/spec/doc updates under paths above

### PH2-004: Tactical Compaction + Stale-Pruning Policy Integration

Objective:
- Integrate compaction and stale-pruning behavior for tactical records under explicit policy constraints.

Primary artifacts:
- `policies/tactical_data_policy_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `cortex-coach` runtime/tests

Acceptance criteria:
- Compaction/pruning eligibility rules are explicit and machine-readable.
- Protected record classes cannot be removed by compaction workflow.
- Dry-run and apply modes produce deterministic action summaries.
- Reason codes and lineage references are retained for each action.

Evidence:
- policy/spec/runtime/test updates under paths above

### PH2-005: Provenance + Confidence Enrichment in Context Bundles

Objective:
- Improve traceability and trust of retrieved context payloads.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/commands.md`
- `contracts/` (new or updated context bundle schema artifacts)

Acceptance criteria:
- Each returned context item includes provenance references.
- Confidence fields are normalized and bounded.
- Bundle ordering and metadata shape are deterministic.
- Output remains compatible with existing promotion/linkage flows.

Evidence:
- contract/spec/doc updates
- runtime/test updates in `cortex-coach`

### PH2-006: Retrieval Evaluation Fixture Set + Scoring Harness

Objective:
- Create deterministic evaluation harness for relevance and ordering outcomes.

Primary artifacts:
- `.cortex/reports/project_state/phase2_retrieval_relevance_report_v0.json`
- `.cortex/reports/project_state/phase2_retrieval_determinism_report_v0.json`

Acceptance criteria:
- Fixture profiles and query set are frozen and referenced in artifacts.
- Relevance scores are reproducible across repeated runs.
- Determinism report includes repeat-run ranking hash consistency checks.
- Artifact schema and field naming are stable for CI parsing.

Evidence:
- report artifacts above

### PH2-007: Performance/Budget Hardening + Governance Non-Regression Pack

Objective:
- Validate that Phase 2 improvements stay inside performance and governance boundaries.

Primary artifacts:
- `.cortex/reports/project_state/phase2_latency_report_v0.json`
- `.cortex/reports/project_state/phase2_context_budget_report_v0.json`
- `.cortex/reports/project_state/phase2_ci_overhead_report_v0.json`
- `.cortex/reports/project_state/phase2_governance_regression_report_v0.md`

Acceptance criteria:
- Latency and context-size budgets meet Phase 2 thresholds.
- Mandatory CI runtime overhead remains within threshold.
- Required governance gates remain pass.
- Any non-critical residual findings are owner-assigned and time-bounded.

Evidence:
- report artifacts above

### PH2-008: Gate C Measurement Closeout and Readiness Determination

Objective:
- Close Phase 2 with explicit Gate C pass/fail decision and owned residual risks.

Primary artifacts:
- `.cortex/reports/project_state/phase2_gate_c_measurement_closeout_v0.md`
- `playbooks/cortex_phase2_measurement_plan_v0.md`

Acceptance criteria:
- `PH2-001` through `PH2-007` are marked `done` with evidence links.
- Every Phase 2 measurement target has explicit pass/fail outcome.
- Gate C determination is explicit and evidence-linked.
- Residual risks/questions include owner and due date.

Evidence:
- closeout artifact above

## Capacity Envelope (Phase 2, Option B)

Planning defaults:
- `<= 3` five-hour windows/week
- `<= 7` cloud tasks/week
- `<= 5` code reviews/week

Adjustment rules:
- If weekly usage is `>= 80%` by Wednesday, cut to constrained mode for remaining sessions.
- If weekly lockout occurs, run stabilization-only week before new Phase 2 scope begins.

## Definition of Done (Phase 2 Ticket Set)

This ticket set is complete when:

1. `PH2-001` through `PH2-008` are marked `done` with evidence links.
2. Gate C measurement closeout is published with explicit pass/fail criteria and outcomes.
3. Retrieval/context quality improvements are delivered without unresolved governance authority-boundary ambiguity.

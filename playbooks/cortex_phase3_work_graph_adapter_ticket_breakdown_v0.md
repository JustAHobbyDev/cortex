# Cortex Phase 3 External Work-Graph Adapter Ticket Breakdown v0

Version: v0  
Status: Draft  
Date: 2026-02-24  
Scope: Phase 3 implementation ticket set for external work-graph adapter integration in `cortex-coach`

## Purpose

Deliver a bounded, read-only adapter layer that enriches tactical context with execution-state signals without introducing governance dependency on external systems.

## Source Inputs

- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `.cortex/reports/project_state/beads_comparative_research_report_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_phase3_measurement_plan_v0.md`
- `.cortex/reports/project_state/phase2_gate_c_measurement_closeout_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `specs/agent_context_loader_spec_v0.md`
- `contracts/context_load_work_graph_adapter_contract_v0.md`

## Guardrails (Non-Negotiable)

- Adapter integration is optional, read-only, and non-authoritative.
- Governance plane remains canonical authority for closure.
- Adapter failure/timeout must fail open to governance + task slices.
- Mandatory governance commands cannot depend on adapter availability.
- Retrieval ordering and adapter selection behavior remain deterministic.
- Adapter slice remains context-budget bounded and observable.

## Execution Order

1. `PH3-001` contract baseline and fixture freeze
2. `PH3-002` and `PH3-003` runtime adapter ingestion and metadata normalization
3. `PH3-004` to `PH3-007` degradation validation, budget/perf hardening, and docs/runbooks
4. `PH3-008` Gate D closeout package

## Execution Board

Status vocabulary:
- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

| Ticket | Title | Status | Owner (Suggested Role) | Primary Reviewer (Suggested Role) | Target Week | Target Date | Blockers | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PH3-001 | Work-Graph Adapter Contract Baseline + Scenario Freeze | done | Contract/Schema Lead | Governance Policy Lead | Week 8 | 2026-04-15 | PH2 complete | `contracts/context_load_work_graph_adapter_contract_v0.md`;`.cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json`;`specs/cortex_project_coach_spec_v0.md`;`playbooks/cortex_phase3_measurement_plan_v0.md` | Phase 3 contract and frozen scenario baseline landed in `cortex` during kickoff. |
| PH3-002 | `context-load` Adapter Slice Ingestion (Read-only, Opt-in) | done | Runtime Reliability Lead | Contract/Schema Lead | Week 8 | 2026-04-17 | PH3-001 | `cortex-coach` runtime/tests/docs (`commit 0d96be6`) | Adds `--adapter-mode beads_file` + bounded adapter slice inclusion behind explicit opt-in controls. |
| PH3-003 | Adapter Provenance + Freshness Normalization | done | Runtime Reliability Lead | Governance Enforcement Lead | Week 8 | 2026-04-19 | PH3-001 | `cortex-coach` runtime/tests/docs (`commit 0d96be6`) | Adapter entries emit normalized provenance (`source_kind=adapter_signal`) and freshness/staleness metadata with deterministic warnings. |
| PH3-004 | Adapter Degradation/Circuit-Breaker Validation Harness | todo | Conformance QA Lead | Runtime Reliability Lead | Week 9 | 2026-04-22 | PH3-002,PH3-003 | `.cortex/reports/project_state/phase3_adapter_degradation_report_v0.json`;`.cortex/reports/project_state/phase3_adapter_determinism_report_v0.json` | Validate timeout/decode/missing-file degradation paths remain deterministic and fail-open. |
| PH3-005 | Governance Non-Regression Under Adapter Failure | todo | Governance Enforcement Lead | Conformance QA Lead | Week 9 | 2026-04-24 | PH3-004 | `.cortex/reports/project_state/phase3_governance_regression_report_v0.md` | Prove mandatory governance commands pass when adapter is unhealthy/unavailable. |
| PH3-006 | Adapter Latency + Context Budget Hardening | todo | CI/Gate Owner | Runtime Reliability Lead | Week 9 | 2026-04-26 | PH3-002,PH3-003 | `.cortex/reports/project_state/phase3_adapter_latency_report_v0.json`;`.cortex/reports/project_state/phase3_adapter_budget_report_v0.json`;`.cortex/reports/project_state/phase3_ci_overhead_report_v0.json` | Ensure adapter-on mode stays within latency/context/CI overhead budgets. |
| PH3-007 | Operator Docs/Runbook + Release-Surface Hardening | todo | Program Lead | Maintainer Council | Week 10 | 2026-04-29 | PH3-004,PH3-005,PH3-006 | `docs/cortex-coach/commands.md`;`playbooks/session_governance_hybrid_plan_v0.md`;`docs/cortex-coach/quality-gate.md` | Formalize adapter operational guidance, degradation procedures, and release boundary behavior. |
| PH3-008 | Gate D Measurement Closeout and Readiness Determination | todo | Program Lead | Maintainer Council | Week 10 | 2026-05-01 | PH3-001,PH3-002,PH3-003,PH3-004,PH3-005,PH3-006,PH3-007 | `.cortex/reports/project_state/phase3_gate_d_measurement_closeout_v0.md`;`playbooks/cortex_phase3_measurement_plan_v0.md` | Publish explicit Gate D pass/fail determination with owned residual risks. |

## Definition of Done (Phase 3 Ticket Set)

This ticket set is complete when:

1. `PH3-001` through `PH3-008` are marked `done` with evidence links.
2. Gate D closeout is published with explicit metric outcomes and pass/fail determination.
3. Adapter-path failures are proven non-blocking for mandatory governance workflows.

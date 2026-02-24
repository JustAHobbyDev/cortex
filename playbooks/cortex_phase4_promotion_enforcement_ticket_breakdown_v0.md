# Cortex Phase 4 Promotion and Enforcement Hardening Ticket Breakdown v0

Version: v0  
Status: Draft  
Date: 2026-02-24  
Scope: Phase 4 implementation ticket set for promotion-flow hardening and governance enforcement integration

## Purpose

Convert tactical outputs into durable governance assets through explicit promotion linkage, deterministic evidence scoring, and fail-closed governance enforcement.

## Source Inputs

- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_phase4_measurement_plan_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `.cortex/reports/project_state/phase3_gate_d_measurement_closeout_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `contracts/promotion_contract_schema_v0.json`

## Guardrails (Non-Negotiable)

- Governance plane remains authoritative for closure.
- Tactical artifacts are non-authoritative until promoted with linked governance evidence.
- Governance-impacting closure without linked decision/reflection must be blocked.
- Enforcement and scoring behavior must remain deterministic for repeated identical input/state.
- Phase 4 must not introduce dependency on external adapter health for mandatory governance gates.

## Execution Order

1. `PH4-001` contract baseline and fixture freeze
2. `PH4-002` and `PH4-003` promotion assistant mapping and evidence scoring
3. `PH4-004` and `PH4-005` enforcement hardening and governance-debt visibility
4. `PH4-006` and `PH4-007` regression and performance validation pack
5. `PH4-008` Gate E closeout package

## Execution Board

Status vocabulary:
- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

| Ticket | Title | Status | Owner (Suggested Role) | Primary Reviewer (Suggested Role) | Target Week | Target Date | Blockers | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PH4-001 | Promotion/Enforcement Contract Baseline + Fixture Freeze | done | Contract/Schema Lead | Governance Policy Lead | Week 11 | 2026-05-04 | PH3 complete | `contracts/promotion_enforcement_contract_v0.md`;`.cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json`;`playbooks/cortex_phase4_measurement_plan_v0.md`;`specs/cortex_project_coach_spec_v0.md`;`.cortex/fixtures/phase4_promotion/` | Phase 4 baseline contract + frozen fixture set landed with spec/measurement linkage and concrete fixture payloads. |
| PH4-002 | Promotion Assistant Candidate Mapping | done | Runtime Reliability Lead | Contract/Schema Lead | Week 11 | 2026-05-06 | PH4-001 | `cortex-coach` runtime/tests (`c1f4f85`);`docs/cortex-coach/commands.md`;`specs/cortex_project_coach_spec_v0.md` | `promotion-candidates` command implemented with deterministic candidate normalization + enforcement recommendation mapping. |
| PH4-003 | Evidence Scoring + Deterministic Candidate Ranking | done | Runtime Reliability Lead | Governance Enforcement Lead | Week 11 | 2026-05-08 | PH4-001,PH4-002 | `scripts/phase4_promotion_candidate_harness_v0.py`;`.cortex/reports/project_state/phase4_promotion_candidate_quality_report_v0.json`;`.cortex/reports/project_state/phase4_promotion_determinism_report_v0.json` | Frozen-fixture scoring harness and deterministic ranking evidence reports generated (`30` replay runs per case, `100%` consistency). |
| PH4-004 | Enforcement Ladder Integration for Unlinked Closure Blocking | done | Governance Enforcement Lead | CI/Gate Owner | Week 11 | 2026-05-10 | PH4-001,PH4-002 | `scripts/reflection_enforcement_gate_v0.py`;`scripts/quality_gate_v0.sh`;`scripts/quality_gate_ci_v0.sh`;`scripts/phase4_enforcement_blocking_harness_v0.py`;`.cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json` | Enforced Phase 4 blocking report requirement in reflection gate + CI/local quality gates; deterministic unlinked-closure blocking report generated. |
| PH4-005 | Governance Debt Visibility (Ready/Blocked Governance Actions) | done | Governance Enforcement Lead | Program Lead | Week 12 | 2026-05-12 | PH4-004 | `scripts/phase4_governance_debt_harness_v0.py`;`.cortex/reports/project_state/phase4_governance_debt_visibility_report_v0.json`;`docs/cortex-coach/commands.md` | Debt visibility harness/report now emits deterministic `ready`/`blocked` queues with owner + next-action coverage at `100%` on frozen fixtures. |
| PH4-006 | Governance Non-Regression Under Promotion Flow | done | Conformance QA Lead | Governance Policy Lead | Week 12 | 2026-05-14 | PH4-003,PH4-004,PH4-005 | `scripts/phase4_promotion_governance_regression_harness_v0.py`;`.cortex/reports/project_state/phase4_governance_regression_report_v0.md` | Regression harness executed with Phase 4 enforcement/debt checks and required governance gates (`mistake`, boundary, temporal, reflection) all passing. |
| PH4-007 | Promotion Path Latency/Budget + CI Overhead Hardening | done | CI/Gate Owner | Runtime Reliability Lead | Week 12 | 2026-05-16 | PH4-003,PH4-004 | `scripts/phase4_promotion_performance_pack_v0.py`;`.cortex/reports/project_state/phase4_latency_report_v0.json`;`.cortex/reports/project_state/phase4_ci_overhead_report_v0.json` | Performance pack generated with `n=30` latency runs/profile and `n=5` CI runs; includes offline reproducibility probe mode + weekly overhead tracking guardrail metadata. |
| PH4-008 | Gate E Measurement Closeout and Readiness Determination | todo | Program Lead | Maintainer Council | Week 12 | 2026-05-17 | PH4-001,PH4-002,PH4-003,PH4-004,PH4-005,PH4-006,PH4-007 | `.cortex/reports/project_state/phase4_gate_e_measurement_closeout_v0.md`;`playbooks/cortex_phase4_measurement_plan_v0.md` | Publish explicit Gate E pass/fail determination with owned residual risks. |

## Definition of Done (Phase 4 Ticket Set)

This ticket set is complete when:

1. `PH4-001` through `PH4-008` are marked `done` with evidence links.
2. Gate E closeout is published with explicit metric outcomes and pass/fail determination.
3. Unlinked governance-impacting tactical closures are proven fail-closed at enforced boundaries.

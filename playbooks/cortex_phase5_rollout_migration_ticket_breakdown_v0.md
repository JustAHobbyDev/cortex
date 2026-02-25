# Cortex Phase 5 Rollout and Migration Ticket Breakdown v0

Version: v0  
Status: Draft  
Date: 2026-02-24  
Scope: Phase 5 implementation ticket set for rollout controls, migration, and Gate F readiness

## Purpose

Move from experimental operation toward default mode using explicit rollout controls, repeatable migration artifacts, and two-cycle reliability validation.

## Source Inputs

- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_phase5_measurement_plan_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `.cortex/reports/project_state/phase3_gate_d_measurement_closeout_v0.md`
- `playbooks/cortex_phase4_promotion_enforcement_ticket_breakdown_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`

## Guardrails (Non-Negotiable)

- Default mode changes are governance decisions, not runtime-only toggles.
- Required governance gates remain release-boundary authority in every rollout mode.
- Rollout must remain reversible (`default -> experimental -> off`) with audited transition history.
- Cross-project migration guidance must preserve `.cortex` project-state boundary and governance controls.
- Phase 5 does not weaken decision/reflection linkage requirements established in earlier phases.

## Execution Order

1. `PH5-001` rollout-mode contract and policy baseline
2. `PH5-002` to `PH5-004` runtime controls + migration/reference implementation pack
3. `PH5-005` and `PH5-006` two-cycle reliability/SLO validation
4. `PH5-007` adoption/overhead verification
5. `PH5-008` Gate F closeout and default-mode determination

## Execution Board

Status vocabulary:
- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

| Ticket | Title | Status | Owner (Suggested Role) | Primary Reviewer (Suggested Role) | Target Week | Target Date | Blockers | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PH5-001 | Rollout Mode Contract + Policy Baseline (`off`,`experimental`,`default`) | done | Governance Policy Lead | Maintainer Council | Week 13 | 2026-05-18 | PH4 complete | `contracts/rollout_mode_contract_v0.md`;`policies/rollout_mode_policy_v0.md`;`specs/cortex_project_coach_spec_v0.md`;`playbooks/cortex_phase5_measurement_plan_v0.md` | Rollout mode semantics, transition preconditions, rollback constraints, and Gate F linkage guardrails formalized in contract/policy/spec artifacts. |
| PH5-002 | Runtime Mode Controls + Kill-Switch/Audit Integration | todo | Runtime Reliability Lead | Governance Enforcement Lead | Week 13 | 2026-05-20 | PH5-001 | `cortex-coach` runtime/tests;`docs/cortex-coach/commands.md`;`.cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json` | Deterministic runtime mode switching with auditable transition records. |
| PH5-003 | Migration Playbook + Operator Handoff Guide | todo | Program Lead | Maintainer Council | Week 13 | 2026-05-21 | PH5-001 | `playbooks/cortex_phase5_migration_playbook_v0.md`;`docs/cortex-coach/quality-gate.md`;`playbooks/session_governance_hybrid_plan_v0.md` | Migration process must preserve governance controls and release-boundary checks. |
| PH5-004 | Cross-Project Reference Implementation Pack | todo | Delivery Operations Lead | Conformance QA Lead | Week 13 | 2026-05-22 | PH5-002,PH5-003 | `.cortex/reports/project_state/phase5_reference_implementation_report_v0.md` | Publish at least two reference implementations with explicit boundary/gate evidence. |
| PH5-005 | Cycle 1 Reliability/SLO Validation Pack | todo | CI/Gate Owner | Runtime Reliability Lead | Week 14 | 2026-05-24 | PH5-002 | `scripts/phase5_rollout_reliability_pack_v0.py`;`.cortex/reports/project_state/phase5_cycle1_rollout_reliability_report_v0.json`;`.cortex/reports/project_state/phase5_cycle1_governance_regression_report_v0.md` | First required stable cycle for Gate F. |
| PH5-006 | Cycle 2 Reliability/SLO Validation Pack | todo | CI/Gate Owner | Runtime Reliability Lead | Week 14 | 2026-05-27 | PH5-005 | `scripts/phase5_rollout_reliability_pack_v0.py`;`.cortex/reports/project_state/phase5_cycle2_rollout_reliability_report_v0.json`;`.cortex/reports/project_state/phase5_cycle2_governance_regression_report_v0.md` | Second consecutive required stable cycle for Gate F. |
| PH5-007 | Adoption Metrics + Operator Overhead Verification | todo | Delivery Operations Lead | Program Lead | Week 14 | 2026-05-29 | PH5-004,PH5-006 | `.cortex/reports/project_state/phase5_adoption_metrics_report_v0.json`;`.cortex/reports/project_state/phase5_operator_overhead_report_v0.json` | Confirms adoption targets and operational overhead remain acceptable under rollout controls. |
| PH5-008 | Gate F Closeout + Default Mode Decision | todo | Program Lead | Maintainer Council | Week 14 | 2026-05-31 | PH5-001,PH5-002,PH5-003,PH5-004,PH5-005,PH5-006,PH5-007 | `.cortex/reports/project_state/phase5_gate_f_measurement_closeout_v0.md`;`playbooks/cortex_phase5_measurement_plan_v0.md`;`.cortex/artifacts/decisions/` | Publishes Gate F decision and default-mode recommendation with explicit council approval trail. |

## Definition of Done (Phase 5 Ticket Set)

This ticket set is complete when:

1. `PH5-001` through `PH5-008` are marked `done` with evidence links.
2. Two consecutive reliability cycles satisfy Gate F metric thresholds.
3. Default-mode decision is explicitly published with linked governance decision artifacts.

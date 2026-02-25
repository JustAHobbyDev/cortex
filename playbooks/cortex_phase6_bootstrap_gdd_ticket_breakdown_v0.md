# Cortex Phase 6 Bootstrap and GDD Ticket Breakdown v0

Version: v0  
Status: Active  
Date: 2026-02-25  
Scope: Phase 6 implementation ticket set for project bootstrap portability and Governance Driven Development (GDD) scale-out

## Purpose

Define the next execution phase after Gate F so Cortex can bootstrap governance in new projects with deterministic setup, boundary-safe defaults, and context-hydration enforcement.

## Source Inputs

- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_client_onboarding_training_track_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `playbooks/cortex_phase5_migration_playbook_v0.md`
- `playbooks/cortex_phase5_measurement_plan_v0.md`
- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `.cortex/reports/project_state/beads_comparative_research_report_v0.md`

## Guardrails (Non-Negotiable)

- `.cortex` remains the default project boundary unless explicitly configured otherwise.
- Bootstrap automation must preserve required release-boundary governance gates.
- Context-hydration automation must not bypass policy/spec/decision authority.
- Multi-agent workflows remain capability-scoped and fail-safe to governance-only operation.
- New-project bootstrap evidence must be reproducible under `.cortex/reports/project_state/`.

## Execution Order

1. `PH6-001` phase scope + acceptance baseline
2. `PH6-002` governance capsule hydration invariants and context-rollover enforcement
3. `PH6-003` configurable project boundary contract (default `.cortex`)
4. `PH6-004` deterministic bootstrap scaffolding flow for new repos
5. `PH6-005` role/capability pack for GDD swarm operation
6. `PH6-006` bootstrap readiness harness + certification artifact
7. `PH6-007` external pilot validation across at least two fresh repos
8. `PH6-008` Gate G closeout + recommendation for next expansion phase

## Execution Board

Status vocabulary:
- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

| Ticket | Title | Status | Owner (Suggested Role) | Primary Reviewer (Suggested Role) | Target Week | Target Date | Blockers | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PH6-001 | Phase 6 Scope + Acceptance Baseline | done | Program Lead | Maintainer Council | Week 15 | 2026-06-03 | - | `playbooks/cortex_phase6_bootstrap_gdd_ticket_breakdown_v0.md`;`playbooks/cortex_phase6_measurement_plan_v0.md`;`playbooks/cortex_vision_master_roadmap_v1.md`;`.cortex/reports/project_state/phase5_recurring_cadence_report_v0.json` | Phase contract, metrics, sequencing, and recurring cadence evidence are now baselined for execution handoff. |
| PH6-002 | Governance Capsule Hydration Invariants | done | Governance Policy Lead | Runtime Reliability Lead | Week 15 | 2026-06-05 | - | `scripts/context_hydration_gate_v0.py`;`.cortex/reports/project_state/phase6_hydration_compliance_report_v0.json`;`policies/context_hydration_policy_v0.md`;`policies/tactical_data_policy_v0.md`;`specs/agent_context_loader_spec_v0.md`;`scripts/quality_gate_ci_v0.sh` | Hydration gate now enforces deterministic `new_session` + `window_rollover` coverage and fail-closed `pre_closeout` verification in block mode. |
| PH6-003 | Configurable Project Boundary Contract | done | Governance Enforcement Lead | Contract/Schema Lead | Week 16 | 2026-06-10 | - | `contracts/project_state_boundary_contract_v0.json`;`contracts/project_state_boundary_contract_v0.md`;`scripts/project_state_boundary_gate_v0.py`;`scripts/phase6_boundary_conformance_harness_v0.py`;`.cortex/reports/project_state/phase6_boundary_conformance_report_v0.json` | Boundary root configurability is now contract-documented and validated with deterministic default-vs-override conformance checks; default remains `.cortex`. |
| PH6-004 | Bootstrap Scaffolder for New Projects | done | Delivery Operations Lead | Program Lead | Week 16 | 2026-06-12 | - | `scripts/cortex_project_coach_v0.py`;`docs/cortex-coach/quickstart.md`;`docs/cortex-coach/commands.md`;`.cortex/templates/bootstrap_first_green_gate_checklist_template_v0.md`;`.cortex/reports/project_state/phase6_bootstrap_scaffold_report_v0.json`;`tests/test_coach_bootstrap_scaffold.py` | Added deterministic `bootstrap-scaffold` flow with fail-closed required-path validation, checklist generation, and first-green-gate command/report emission. |
| PH6-005 | GDD Role + Capability Pack | done | Maintainer Council | Governance Policy Lead | Week 17 | 2026-06-17 | - | `playbooks/cortex_phase0_role_charters_v0.md`;`docs/cortex-coach/README.md`;`.cortex/reports/project_state/phase6_role_capability_pack_report_v0.md` | Minimum role set, command/capability matrix, and escalation SLA matrix are now formalized for multi-agent bootstrap and governed delivery. |
| PH6-006 | Bootstrap Readiness Harness + Certification | done | Conformance QA Lead | CI/Gate Owner | Week 17 | 2026-06-19 | - | `scripts/client_onboarding_certification_pack_v0.py`;`.cortex/reports/project_state/phase6_bootstrap_readiness_report_v0.json`;`.cortex/reports/project_state/client_onboarding_certification_pack_v0.json`;`playbooks/cortex_phase6_measurement_plan_v0.md` | Certification harness now emits a dedicated Phase 6 bootstrap readiness artifact with threshold checks for first-green-gate time, required gate reliability, and critical safety incidents. |
| PH6-007 | External Pilot Validation | done | Program Lead | Delivery Operations Lead | Week 18 | 2026-06-24 | - | `scripts/phase6_external_pilot_harness_v0.py`;`.cortex/reports/project_state/phase6_external_pilot_report_v0.md`;`.cortex/reports/project_state/phase6_external_pilot_report_v0.json` | Deterministic pilot harness validates bootstrap portability on two non-Cortex seed repos (`python_api_service` and `node_dashboard_app`); bootstrap portability bundle now enables raw hydration portability without manual capsule seeding. |
| PH6-008 | Gate G Closeout + Next-Phase Recommendation | done | Program Lead | Maintainer Council | Week 18 | 2026-06-27 | PH6-001,PH6-002,PH6-003,PH6-004,PH6-005,PH6-006,PH6-007 | `.cortex/reports/project_state/phase6_gate_g_measurement_closeout_v0.md`;`.cortex/reports/project_state/phase6_operator_overhead_report_v0.json`;`.cortex/reports/project_state/phase6_external_pilot_report_v0.json`;`scripts/phase6_operator_overhead_pack_v0.py`;`playbooks/cortex_phase6_measurement_plan_v0.md` | Gate G closeout is pass; all thresholds met, external raw portability is 2/2, and next-phase expansion recommendation is published. |

## Definition of Done (Phase 6 Ticket Set)

This ticket set is complete when:

1. `PH6-001` through `PH6-008` are marked `done` with evidence links.
2. Fresh-project bootstrap flow reaches first green required gate deterministically in target budget.
3. Governance capsule hydration and boundary constraints are enforced and auditable.

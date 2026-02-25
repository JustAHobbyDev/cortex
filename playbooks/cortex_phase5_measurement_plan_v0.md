# Cortex Phase 5 Measurement Plan v0

Version: v0  
Status: Closed (Gate F Pass)  
Date: 2026-02-24  
Scope: Measurement and validation plan for rollout controls, migration readiness, and Gate F determination

## Purpose

Define Gate F criteria for moving from experimental operation to default mode only after sustained reliability, governance safety, and operator-overhead thresholds are met.

## Source Inputs

- `playbooks/cortex_phase5_rollout_migration_ticket_breakdown_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `playbooks/cortex_phase4_measurement_plan_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`
- `contracts/rollout_mode_contract_v0.md`
- `policies/rollout_mode_policy_v0.md`

## Scope

In scope:
- rollout mode contract validation (`off`, `experimental`, `default`).
- two-cycle reliability validation under required governance gates.
- mode-transition auditability and rollback drill verification.
- migration/reference implementation readiness evidence.
- adoption and operator-overhead measurements.
- Gate F pass/fail determination criteria.

Out of scope:
- new tactical feature families beyond previously approved phase scope.
- changes to canonical governance authority model.
- post-default-on optimization phases outside Gate F closeout.

## Measurement Principles

- Stability over speed: default mode requires sustained performance across consecutive cycles.
- Governance non-regression is mandatory in all rollout modes.
- Every mode transition must be auditable and reversible.
- Adoption evidence must include governance-safe reference implementations.
- Artifacts must be reproducible and versioned under `.cortex/reports/project_state/`.

## Metrics and Targets

| Metric | Target | Method | Evidence Artifact | Gate |
|---|---|---|---|---|
| Required governance gate reliability | `100%` pass in Cycle 1 and Cycle 2 | run full required governance bundle each cycle | `.cortex/reports/project_state/phase5_cycle1_rollout_reliability_report_v0.json`;`.cortex/reports/project_state/phase5_cycle2_rollout_reliability_report_v0.json` | F |
| Consecutive stable cycles | `>=2` consecutive cycles meeting all Gate F metrics | compare cycle-level summaries and stop-rule outcomes | `.cortex/reports/project_state/phase5_gate_f_measurement_closeout_v0.md` | F |
| CI mandatory governance runtime delta | `<= 10%` vs Phase 4 baseline median for each cycle | median wall-time comparison over `>=5` runs/cycle | `.cortex/reports/project_state/phase5_cycle1_rollout_reliability_report_v0.json`;`.cortex/reports/project_state/phase5_cycle2_rollout_reliability_report_v0.json` | F |
| Stop-rule critical incidents | `0` governance false pass/false fail incidents across both cycles | incident log + gate-run review | `.cortex/reports/project_state/phase5_gate_f_measurement_closeout_v0.md` | F |
| Mode-transition audit completeness | `100%` transitions include linked decision/reflection/audit metadata | validate transition log schema and linkage fields | `.cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json` | F |
| Rollback drill success | `100%` planned rollback drills complete successfully | execute deterministic rollback/recovery drill(s) and verify gate status | `.cortex/reports/project_state/phase5_cycle1_rollout_reliability_report_v0.json`;`.cortex/reports/project_state/phase5_cycle2_rollout_reliability_report_v0.json` | F |
| Reference implementation coverage | `>=2` project references with no governance regression | migration/reference validation pack with required gates | `.cortex/reports/project_state/phase5_reference_implementation_report_v0.md` | F |
| Operator overhead | median closeout command count within `+20%` of Phase 4 baseline | compare operator command telemetry against baseline | `.cortex/reports/project_state/phase5_operator_overhead_report_v0.json` | F |

## Cycle Structure

Cycle 1:
- execute required governance bundle and rollout-mode checks.
- run CI-overhead sample (`n>=5`).
- run rollback drill.
- publish cycle 1 reliability/governance artifacts.

Cycle 2:
- repeat Cycle 1 measurement bundle with no relaxed thresholds.
- confirm no critical stop-rule incidents.
- publish cycle 2 reliability/governance artifacts.

## Gate F Pass/Fail Criteria

Gate F passes only when all conditions are true:

1. Cycle 1 and Cycle 2 both satisfy every metric in `Metrics and Targets`.
2. Required governance gates remain pass across both cycles.
3. Transition audit trail is complete and rollback drills pass.
4. Reference implementation and adoption evidence meet thresholds.
5. Default-mode recommendation is linked to explicit governance decision artifacts.

Gate F fails if any metric misses threshold in either cycle or if governance safety regresses.

## Planned Harness Commands

Cycle reliability pack:

```bash
python3 scripts/phase5_rollout_reliability_pack_v0.py \
  --project-dir . \
  --cycle-id cycle1
```

Repeat with:

```bash
python3 scripts/phase5_rollout_reliability_pack_v0.py \
  --project-dir . \
  --cycle-id cycle2
```

Expected outputs:
- `.cortex/reports/project_state/phase5_cycle1_rollout_reliability_report_v0.json`
- `.cortex/reports/project_state/phase5_cycle1_governance_regression_report_v0.md`
- `.cortex/reports/project_state/phase5_cycle2_rollout_reliability_report_v0.json`
- `.cortex/reports/project_state/phase5_cycle2_governance_regression_report_v0.md`

Migration/adoption pack:

```bash
python3 scripts/phase5_rollout_adoption_pack_v0.py \
  --project-dir .
```

Expected outputs:
- `.cortex/reports/project_state/phase5_reference_implementation_report_v0.md`
- `.cortex/reports/project_state/phase5_adoption_metrics_report_v0.json`
- `.cortex/reports/project_state/phase5_operator_overhead_report_v0.json`
- `.cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json`

## Planned Artifacts

- `.cortex/reports/project_state/phase5_cycle1_rollout_reliability_report_v0.json`
- `.cortex/reports/project_state/phase5_cycle1_governance_regression_report_v0.md`
- `.cortex/reports/project_state/phase5_cycle2_rollout_reliability_report_v0.json`
- `.cortex/reports/project_state/phase5_cycle2_governance_regression_report_v0.md`
- `.cortex/reports/project_state/phase5_reference_implementation_report_v0.md`
- `.cortex/reports/project_state/phase5_adoption_metrics_report_v0.json`
- `.cortex/reports/project_state/phase5_operator_overhead_report_v0.json`
- `.cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json`
- `.cortex/reports/project_state/phase5_gate_f_measurement_closeout_v0.md`

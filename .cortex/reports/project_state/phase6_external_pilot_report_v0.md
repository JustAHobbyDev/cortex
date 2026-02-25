# Phase 6 External Pilot Report v0

Version: v0  
Date: 2026-02-25  
Status: pass  
Ticket: PH6-007

## Scope

Validate Cortex bootstrap portability on at least two non-Cortex seed repos with different stack shapes.

## Summary

- Pilots run: 2
- Pilot pass count: 2
- Distinct stack shapes: 2
- Portability without capsule seed (pass count): 0

## Target Results

- `core_portability_pass_rate_met`: `True`
- `operator_overhead_target_met`: `True`
- `pilot_count_met`: `True`
- `stack_diversity_met`: `True`

## Pilot Results

### pilot_python_api

- Stack shape: `python_api_service`
- Status: `pass`
- Command count: `8`
- Operator overhead target met: `True`
- Raw hydration portability: `False`

Checks:
- `bootstrap_scaffold`: `pass`
- `bootstrap_baseline_commit`: `pass`
- `audit_needed`: `pass`
- `decision_gap_check`: `pass`
- `project_state_boundary_gate`: `pass`
- `context_hydration_raw`: `fail`
- `context_hydration_seeded`: `pass`

Findings:
- Hydration compliance fails on a raw seed repo until governance capsule policy/playbook files are seeded.

### pilot_node_dashboard

- Stack shape: `node_dashboard_app`
- Status: `pass`
- Command count: `8`
- Operator overhead target met: `True`
- Raw hydration portability: `False`

Checks:
- `bootstrap_scaffold`: `pass`
- `bootstrap_baseline_commit`: `pass`
- `audit_needed`: `pass`
- `decision_gap_check`: `pass`
- `project_state_boundary_gate`: `pass`
- `context_hydration_raw`: `fail`
- `context_hydration_seeded`: `pass`

Findings:
- Hydration compliance fails on a raw seed repo until governance capsule policy/playbook files are seeded.

## Decision

External pilot portability validated on two non-Cortex seed repos across distinct stack shapes. Core bootstrap + boundary + decision-gap checks pass deterministically; hydration requires seeded governance capsule files in raw repos and then passes.

## Follow-On

1. Use seeded governance capsule bundle as part of external bootstrap package.
2. Execute PH6-008 Gate G closeout with this pilot evidence.

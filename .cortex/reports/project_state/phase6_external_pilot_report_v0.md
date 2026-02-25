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
- Portability without capsule seed (pass count): 2

## Target Results

- `core_portability_pass_rate_met`: `True`
- `operator_overhead_target_met`: `True`
- `pilot_count_met`: `True`
- `raw_portability_pass_rate_met`: `True`
- `stack_diversity_met`: `True`

## Pilot Results

### pilot_python_api

- Stack shape: `python_api_service`
- Status: `pass`
- Command count: `7`
- Operator overhead target met: `True`
- Raw hydration portability: `True`

Checks:
- `bootstrap_scaffold`: `pass`
- `bootstrap_baseline_commit`: `pass`
- `audit_needed`: `pass`
- `decision_gap_check`: `pass`
- `project_state_boundary_gate`: `pass`
- `context_hydration_raw`: `pass`
- `context_hydration_seeded`: `not_run`

### pilot_node_dashboard

- Stack shape: `node_dashboard_app`
- Status: `pass`
- Command count: `7`
- Operator overhead target met: `True`
- Raw hydration portability: `True`

Checks:
- `bootstrap_scaffold`: `pass`
- `bootstrap_baseline_commit`: `pass`
- `audit_needed`: `pass`
- `decision_gap_check`: `pass`
- `project_state_boundary_gate`: `pass`
- `context_hydration_raw`: `pass`
- `context_hydration_seeded`: `not_run`

## Decision

External pilot portability validated on two non-Cortex seed repos across distinct stack shapes. Bootstrap, boundary, decision-gap, and hydration checks now pass on raw seeded repos without manual governance capsule backfill.

## Follow-On

1. Expand pilot matrix to at least four stack shapes and rerun portability checks quarterly.
2. Use this report as Gate G evidence and next-phase expansion baseline.

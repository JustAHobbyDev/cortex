# Phase 3 Governance Regression Report v0

Version: v0  
Status: Pass  
Date: 2026-02-24  
Scope: Governance non-regression verification for adapter-unhealthy scenarios

## Source Inputs

- `.cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json`
- `.cortex/reports/project_state/phase3_adapter_degradation_report_v0.json`
- `contracts/context_load_work_graph_adapter_contract_v0.md`

## Commands

- context probe base command: `/tmp/cortex-coach/.venv/bin/python /tmp/cortex-coach/scripts/cortex_project_coach_v0.py context-load ...`
- decision gap: `python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir /home/d/codex/cortex --format json`
- reflection gate: `python3 scripts/reflection_enforcement_gate_v0.py --project-dir /home/d/codex/cortex --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`
- audit all: `python3 scripts/cortex_project_coach_v0.py audit --project-dir /home/d/codex/cortex --audit-scope all --format json`

## Summary

- cases evaluated: `8`
- passing cases: `8`
- total elapsed seconds: `18.90105`
- overall result: `pass`

## Case Results

| Case | Failure Mode | Context Probe | Decision Gap | Reflection Gate | Audit All | Pass |
|---|---|---|---|---|---|---|
| `small:s_small_adapter_missing_file:q_small_adapter_blocker_resolution` | `missing_file` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `small:s_small_adapter_missing_file:q_small_adapter_ready_next_action` | `missing_file` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `medium:s_medium_adapter_stale_metadata:q_medium_governance_blocker_and_owner` | `stale_metadata` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `medium:s_medium_adapter_stale_metadata:q_medium_ready_work_priority_order` | `stale_metadata` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `medium:s_medium_adapter_invalid_json:q_medium_governance_blocker_and_owner` | `invalid_json_or_payload_fault` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `medium:s_medium_adapter_invalid_json:q_medium_ready_work_priority_order` | `invalid_json_or_payload_fault` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `large:s_large_adapter_timeout_simulated:q_large_noise_control_and_focus` | `timeout_simulated` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `large:s_large_adapter_timeout_simulated:q_large_degradation_non_blocking_validation` | `timeout_simulated` | `pass` | `pass` | `pass` | `pass` | `pass` |

## Conclusion

Required governance commands remained passing across all adapter-unhealthy probes.

_Generated at: `2026-02-24T10:18:06Z`_

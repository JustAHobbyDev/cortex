# Phase 4 Governance Regression Report v0

- Generated: 2026-02-24
- Run At (UTC): 2026-02-24T16:08:44Z
- Project Dir: `/home/d/codex/cortex`
- Overall Status: **PASS**

## Summary

- Checks Executed: 6
- Pass: 6
- Fail: 0

## Check Results

| Check | Status | Return Code | Payload Status |
|---|---|---:|---|
| `phase4_enforcement_blocking` | `pass` | `0` | `pass` |
| `phase4_governance_debt_visibility` | `pass` | `0` | `pass` |
| `reflection_enforcement` | `pass` | `0` | `pass` |
| `mistake_candidate_gate` | `pass` | `0` | `pass` |
| `project_state_boundary_gate` | `pass` | `0` | `pass` |
| `temporal_playbook_release_gate` | `pass` | `0` | `pass` |

## Details

### `phase4_enforcement_blocking`

- Script: `phase4_enforcement_blocking_harness_v0.py`
- Status: `pass`
- Return Code: `0`
- Command: `python3 /home/d/codex/cortex/scripts/phase4_enforcement_blocking_harness_v0.py --project-dir /home/d/codex/cortex --format json --out-file .cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json`
- Summary:
```json
{
  "blocked_unlinked_count": 4,
  "linked_closure_false_block_rate": 0.0,
  "linked_false_block_count": 0,
  "linked_governance_attempt_count": 5,
  "unlinked_closure_block_rate": 1.0,
  "unlinked_governance_attempt_count": 4
}
```

### `phase4_governance_debt_visibility`

- Script: `phase4_governance_debt_harness_v0.py`
- Status: `pass`
- Return Code: `0`
- Command: `python3 /home/d/codex/cortex/scripts/phase4_governance_debt_harness_v0.py --project-dir /home/d/codex/cortex --format json`
- Summary:
```json
{
  "blocked_count": 2,
  "debt_item_count": 3,
  "next_action_coverage_rate": 1.0,
  "owner_coverage_rate": 1.0,
  "ready_count": 1,
  "required_visibility_coverage_rate": 1.0
}
```

### `reflection_enforcement`

- Script: `reflection_enforcement_gate_v0.py`
- Status: `pass`
- Return Code: `0`
- Command: `python3 /home/d/codex/cortex/scripts/reflection_enforcement_gate_v0.py --project-dir /home/d/codex/cortex --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --require-phase4-enforcement-report --phase4-enforcement-report .cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json --format json`
- Summary:
```json
{
  "decision_match_count": 0,
  "governance_impact_file_count": 0,
  "required_status_entry_count": 25,
  "required_status_mapping_count": 25,
  "scaffold_reports_scanned": 25
}
```

### `mistake_candidate_gate`

- Script: `mistake_candidate_gate_v0.py`
- Status: `pass`
- Return Code: `0`
- Command: `python3 /home/d/codex/cortex/scripts/mistake_candidate_gate_v0.py --project-dir /home/d/codex/cortex --format json`

### `project_state_boundary_gate`

- Script: `project_state_boundary_gate_v0.py`
- Status: `pass`
- Return Code: `0`
- Command: `python3 /home/d/codex/cortex/scripts/project_state_boundary_gate_v0.py --project-dir /home/d/codex/cortex --format json`

### `temporal_playbook_release_gate`

- Script: `temporal_playbook_release_gate_v0.py`
- Status: `pass`
- Return Code: `0`
- Command: `python3 /home/d/codex/cortex/scripts/temporal_playbook_release_gate_v0.py --project-dir /home/d/codex/cortex --format json`

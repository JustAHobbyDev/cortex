# PH1 Runtime Implementation Handoff for cortex-coach v0

Version: v0  
Status: Completed  
Date: 2026-02-23  
Scope: Runtime implementation handoff from `cortex` governance/contracts to `cortex-coach` runtime owner

## Purpose

Transfer Phase 1 implementation-ready contract scope to `cortex-coach` maintainers without violating ownership boundaries.

Boundary source:
- `policies/cortex_coach_final_ownership_boundary_v0.md`

## Ownership Constraint (Normative)

`cortex` owns governance/contracts/specs.  
`cortex-coach` owns runtime CLI behavior, storage, and execution logic.

Result:
- Runtime command implementation for tactical memory must land in `cortex-coach`.
- `cortex` should only receive contract-impact follow-up updates and linked decision artifacts.

## Required Runtime Implementation Order

1. `memory-record`
2. `memory-search`
3. `memory-prime`
4. `memory-diff`
5. `memory-prune`
6. `memory-promote`

This preserves dependency chain from capture -> retrieval -> priming -> mutation safety -> governance bridge.

## Contract Inputs to Implement

- `contracts/tactical_memory_command_family_contract_v0.md`
- `contracts/tactical_memory_record_schema_v0.json`
- `contracts/tactical_memory_search_result_schema_v0.json`
- `contracts/tactical_memory_prime_bundle_schema_v0.json`
- `contracts/tactical_memory_diff_schema_v0.json`
- `contracts/tactical_memory_prune_schema_v0.json`
- `contracts/promotion_contract_schema_v0.json`
- `specs/cortex_project_coach_spec_v0.md`

## Per-Command Runtime Acceptance (cortex-coach)

### `memory-record`
- Validate payloads against `tactical_memory_record_schema_v0.json`.
- Enforce sanitization/redaction/blocked semantics.
- Enforce write-lock controls (`timeout`, `stale`, `force-unlock`).

### `memory-search`
- Emit schema-compliant result payload.
- Enforce deterministic ranking tie-break:
  - `score_desc`
  - `captured_at_desc`
  - `record_id_asc`
- Emit deterministic no-match payload.

### `memory-prime`
- Enforce explicit bundle budgets:
  - `max_records`
  - `max_chars`
  - `per_record_max_chars`
- Emit deterministic truncation metadata and provenance references.

### `memory-diff`
- Use stable comparison key (`record_id`).
- Emit deterministic change ordering and machine-readable change classes.
- Preserve lineage references in each diff entry.

### `memory-prune`
- Support deterministic dry-run.
- Enforce eligibility criteria (TTL/retention/policy-violation classes).
- Emit deterministic action decisions (`prune`/`skip`) with reason codes and lineage.

### `memory-promote`
- Map bridge output to promotion contract required fields.
- Fail closed on missing required linkage/evidence metadata.
- Mark non-governance outputs explicitly to avoid canonical closure confusion.

## Required Runtime Test Coverage (cortex-coach)

Determinism:
- repeat-run normalized output hash checks for each command
- stable ordering/tie-break tests

Locking and concurrency:
- lock timeout/stale-lock reclaim behavior
- single-writer serialization under concurrent mutation requests
- read snapshot stability during active mutation

Idempotency/recovery:
- retry without duplicate mutations
- interruption/recovery integrity checks

Governance non-regression:
- decision/reflection/audit checks unaffected by tactical command failures
- release-boundary quality gate parity preserved

## Measurement Artifact Expectations

Populate measurement artifacts defined in:
- `playbooks/cortex_phase1_measurement_plan_v0.md`

Required outputs:
- `.cortex/reports/project_state/phase1_latency_baseline_v0.json`
- `.cortex/reports/project_state/phase1_latency_tactical_v0.json`
- `.cortex/reports/project_state/phase1_ci_overhead_report_v0.json`
- `.cortex/reports/project_state/phase1_prime_budget_report_v0.json`
- `.cortex/reports/project_state/phase1_determinism_report_v0.json`
- `.cortex/reports/project_state/phase1_locking_report_v0.json`
- `.cortex/reports/project_state/phase1_governance_regression_report_v0.md`

## Evidence Baseline in cortex (Completed)

Phase 1 design board and Gate B package are complete:
- `playbooks/cortex_phase1_tactical_memory_command_contract_ticket_breakdown_v0.md`
- `.cortex/reports/project_state/ph1_008_gate_b_readiness_validation_pack_v0.md`

## Transfer Checklist

1. [x] Open matching implementation tickets in `cortex-coach`.
2. [x] Link each runtime ticket back to the canonical contract paths above.
3. [x] Implement command-by-command in the required order.
4. [x] Run per-command + full regression gates after each merge.
5. [x] Back-link runtime implementation PRs to `cortex` decision artifacts where contracts/policies evolve.

## Completion Evidence (2026-02-23)

### Runtime Implementation Sequence (cortex-coach main)

1. `0debf84` - `memory-record`
2. `37c0c64` - `memory-search`
3. `4df9280` - `memory-prime`
4. `b579764` - `memory-diff`
5. `cf3c5b5` - `memory-prune`
6. `1af71d0` - `memory-promote`

Backlink artifact:
- `.cortex/reports/project_state/phase1_runtime_backlink_evidence_v0.md`

### Measurement and Governance Evidence

Measurement artifacts populated:
- `.cortex/reports/project_state/phase1_latency_baseline_v0.json`
- `.cortex/reports/project_state/phase1_latency_tactical_v0.json`
- `.cortex/reports/project_state/phase1_ci_overhead_report_v0.json`
- `.cortex/reports/project_state/phase1_prime_budget_report_v0.json`
- `.cortex/reports/project_state/phase1_determinism_report_v0.json`
- `.cortex/reports/project_state/phase1_locking_report_v0.json`
- `.cortex/reports/project_state/phase1_governance_regression_report_v0.md`
- `.cortex/reports/project_state/phase1_gate_b_measurement_closeout_v0.md`

Governance gate rerun evidence:
- `decision-gap-check`: pass (`run_at=2026-02-23T22:44:18Z`)
- `reflection_enforcement_gate_v0.py`: pass (`run_at=2026-02-23T22:44:28Z`)
- `audit --audit-scope all`: pass (`run_at=2026-02-23T22:44:35Z`, `artifact_conformance=warn`)
- `cortex` quality gate CI: `PASS` (`41 passed in 52.49s`)
- `cortex-coach` quality gate CI: `PASS` (`60 passed in 95.51s`)

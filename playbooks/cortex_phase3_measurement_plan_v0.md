# Cortex Phase 3 Measurement Plan v0

Version: v0  
Status: Draft  
Date: 2026-02-24  
Scope: Measurement and validation plan for Phase 3 external work-graph adapter integration

## Purpose

Define deterministic, budget-aware Gate D criteria for optional adapter enrichment so external-system failures never degrade governance correctness.

## Source Inputs

- `playbooks/cortex_phase3_work_graph_adapter_ticket_breakdown_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `.cortex/reports/project_state/beads_comparative_research_report_v0.md`
- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `.cortex/reports/project_state/phase2_gate_c_measurement_closeout_v0.md`
- `contracts/context_load_work_graph_adapter_contract_v0.md`
- `.cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json`

## Scope

In scope:
- adapter slice ingestion correctness and deterministic normalization.
- fail-open degradation behavior for adapter parse/freshness/availability failures.
- governance non-regression when adapter path is unhealthy.
- adapter-on latency/context-size/CI overhead budget validation.
- Gate D pass/fail determination criteria.

Out of scope:
- non-Beads external adapter implementations beyond contract compatibility.
- default-on rollout determination (Phase 5 / Gate F).
- promotion enforcement hardening (Phase 4).

## Measurement Principles

- Optionality first: adapter enrichment must remain optional and non-authoritative.
- Deterministic first: identical input/state produces stable normalized output.
- Fail-open safety: adapter failures never block mandatory governance workflows.
- Bounded overhead: adapter-on mode stays within explicit latency/context/CI limits.
- Reproducibility: all outputs are versioned artifacts under `.cortex/reports/project_state/`.

## Metrics and Targets

| Metric | Target | Method | Evidence Artifact | Gate |
|---|---|---|---|---|
| Adapter degradation safety | `100%` fail-open outcomes across frozen failure scenarios | run frozen degradation fixtures (`missing_file`, `invalid_json`, stale metadata, timeout-simulated) and assert no hard-fail on `context-load` | `.cortex/reports/project_state/phase3_adapter_degradation_report_v0.json` | D |
| Adapter ranking determinism | `100%` normalized ordering consistency | repeat each adapter-enabled query/scenario `>=30` times and compare ranking hashes | `.cortex/reports/project_state/phase3_adapter_determinism_report_v0.json` | D |
| Governance non-regression under adapter failure | `100%` pass on required governance gates | run required gate bundle with adapter unhealthy scenarios active | `.cortex/reports/project_state/phase3_governance_regression_report_v0.md` | D |
| `context-load` p95 latency (adapter enabled) | `<= 2.5s` | timed adapter-enabled runs across frozen profiles/scenarios (`n>=30` per profile) | `.cortex/reports/project_state/phase3_adapter_latency_report_v0.json` | D |
| Adapter context budget compliance | `100%` runs within configured file/char limits | parse adapter-enabled bundle metadata over `n>=50` runs | `.cortex/reports/project_state/phase3_adapter_budget_report_v0.json` | D |
| CI mandatory governance runtime delta | `<= 10%` vs Phase 2 required-gate baseline | compare median wall time over `>=5` runs before/after adapter path enablement | `.cortex/reports/project_state/phase3_ci_overhead_report_v0.json` | D |

## Fixture Freeze

Canonical Phase 3 fixture source:
- `.cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json`

Rules:
- Do not change scenarios/queries during a baseline-vs-post comparison cycle.
- Any fixture change requires version bump and Gate D baseline reset note.

## Gate D Pass/Fail Criteria

Gate D passes only when all conditions are true:

1. All Phase 3 measurement artifacts listed in this plan are present.
2. Every metric in `Metrics and Targets` meets thresholds.
3. Adapter degradation tests show no governance-command blocking behavior.
4. Required governance gates pass in adapter-healthy and adapter-unhealthy runs.
5. Residual non-critical findings are owner-assigned and time-bounded in closeout.

Gate D fails if any required metric misses threshold or any required governance gate regresses under adapter scenarios.

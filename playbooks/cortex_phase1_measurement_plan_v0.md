# Cortex Phase 1 Measurement Plan v0

Version: v0  
Status: Draft  
Date: 2026-02-23  
Scope: Measurement and validation plan for Phase 1 tactical memory command contracts and implementation readiness

## Purpose

Define deterministic, budget-aware measurement criteria for Phase 1 so tactical memory features can be implemented and validated without governance regression.

## Source Inputs

- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `playbooks/cortex_phase1_tactical_memory_command_contract_ticket_breakdown_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `specs/cortex_project_coach_spec_v0.md`

## Scope

In scope:
- Phase 1 tactical command family measurement (`memory-record`, `memory-search`, `memory-prime`, `memory-diff`, `memory-prune`, `memory-promote`).
- Determinism and locking behavior.
- Context-budget and CI-overhead impact.
- Gate B pass/fail measurement criteria.

Out of scope:
- External adapter reliability/performance (Phase 3).
- Default-on rollout criteria (Phase 5 / Gate F).

## Measurement Principles

- Deterministic first: repeated identical inputs produce identical normalized outputs.
- Governance safety first: tactical features cannot degrade governance checks or release-boundary controls.
- Budget bounded: context and CI runtime overhead remain inside explicit limits.
- Reproducible evidence: all results are emitted to versioned artifacts under `.cortex/reports/project_state/`.

## Metrics and Targets

| Metric | Target | Method | Evidence Artifact | Gate |
|---|---|---|---|---|
| `context-load` p95 latency (governance-only mode) | `<= 1.5s` | timed command runs on fixed fixture set (n>=30) | `.cortex/reports/project_state/phase1_latency_baseline_v0.json` | B |
| `context-load` p95 latency (tactical memory enabled, no adapter) | `<= 2.0s` | same fixture set and sample size as baseline | `.cortex/reports/project_state/phase1_latency_tactical_v0.json` | B |
| CI mandatory governance pipeline runtime delta | `<= 10%` vs pre-Phase-1 baseline | compare median wall time over >=5 runs before/after | `.cortex/reports/project_state/phase1_ci_overhead_report_v0.json` | B |
| `memory-prime` bundle budget compliance | `100%` runs within configured size budget | parse output bundle size and ordering fields over n>=30 runs | `.cortex/reports/project_state/phase1_prime_budget_report_v0.json` | B |
| Command determinism (all memory commands) | `100%` deterministic normalized outputs for repeated identical inputs | run each command >=20 repeats; compare normalized hashes | `.cortex/reports/project_state/phase1_determinism_report_v0.json` | B |
| Locking safety for concurrent mutation commands | `0` unhandled lock races; deterministic conflict outcomes | concurrent write/mutate stress test matrix | `.cortex/reports/project_state/phase1_locking_report_v0.json` | B |
| Governance non-regression | `100%` pass on required governance gates | run full quality gate suite after Phase 1 changes | `.cortex/reports/project_state/phase1_governance_regression_report_v0.md` | B |

## Workload Profiles

Use three fixed profiles for every performance comparison:

1. Small: low artifact count, short tactical history.
2. Medium: representative active project profile.
3. Large: long tactical history and high retrieval cardinality.

All profile inputs must be frozen per run series and referenced in evidence artifacts.

## Baseline and Comparison Plan

1. Capture pre-implementation baselines:
- `context-load` latency (governance-only mode)
- CI runtime baseline

2. Capture post-implementation measurements:
- tactical-enabled latency
- command determinism and locking behavior
- prime budget compliance
- CI runtime delta

3. Compare using medians and p95 values per workload profile.

## Gate B Measurement Criteria (Pass/Fail)

Gate B passes only when all conditions are true:

1. All measurement artifacts listed in this plan exist and are complete.
2. Every metric in `Metrics and Targets` meets target thresholds.
3. Determinism and locking reports have zero unresolved critical findings.
4. Full governance quality-gate run passes with no new required-check failures.
5. Any residual non-critical findings are explicitly owner-assigned and time-bounded in a closeout report.

Gate B fails if any required metric misses target, or any governance gate regresses.

## Execution Cadence

- During Phase 1 implementation weeks, run focused measurement checks at least twice weekly.
- Run full measurement suite before requesting Phase 1 closeout.
- If usage pressure triggers constrained mode, prioritize determinism/locking and governance non-regression checks before additional feature work.

## Ownership

- Primary owner: Runtime Reliability Lead.
- Measurement contract reviewer: Conformance QA Lead.
- Governance reviewer: Governance Policy Lead.

## Planned Artifacts

- `.cortex/reports/project_state/phase1_latency_baseline_v0.json`
- `.cortex/reports/project_state/phase1_latency_tactical_v0.json`
- `.cortex/reports/project_state/phase1_ci_overhead_report_v0.json`
- `.cortex/reports/project_state/phase1_prime_budget_report_v0.json`
- `.cortex/reports/project_state/phase1_determinism_report_v0.json`
- `.cortex/reports/project_state/phase1_locking_report_v0.json`
- `.cortex/reports/project_state/phase1_governance_regression_report_v0.md`
- `.cortex/reports/project_state/phase1_gate_b_measurement_closeout_v0.md`

# Cortex Phase 2 Measurement Plan v0

Version: v0  
Status: Draft  
Date: 2026-02-24  
Scope: Measurement and validation plan for Phase 2 retrieval and context quality upgrades

## Purpose

Define deterministic, budget-aware Gate C measurement criteria so retrieval relevance can improve without latency, CI, or governance regressions.

## Source Inputs

- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `playbooks/cortex_phase2_retrieval_context_ticket_breakdown_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `contracts/context_load_retrieval_contract_v0.md`
- `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`
- `.cortex/reports/project_state/phase1_gate_b_measurement_closeout_v0.md`

## Scope

In scope:
- Ranked retrieval quality in `context-load`.
- Deterministic tie-break and weighting behavior validation.
- Context bundle budget compliance.
- Tactical compaction/stale-pruning safety validation.
- Gate C pass/fail measurement criteria.

Out of scope:
- External adapter reliability/performance (Phase 3).
- Promotion enforcement hardening (Phase 4).
- Default-on rollout criteria (Phase 5 / Gate F).

## Measurement Principles

- Deterministic first: repeated identical input/state produces identical normalized output except timestamp fields.
- Relevance must be measured on frozen, versioned evaluation fixtures.
- Budget bounded: context size, latency, and CI runtime overhead stay inside explicit limits.
- Governance safety first: tactical retrieval improvements cannot degrade required governance gates.
- Reproducible evidence: all outputs are emitted as versioned artifacts under `.cortex/reports/project_state/`.

## Metrics and Targets

| Metric | Target | Method | Evidence Artifact | Gate |
|---|---|---|---|---|
| Retrieval relevance uplift (`ndcg_at_5`) | `>= +10%` vs Phase 2 pre-change baseline | run frozen query fixture set across `small|medium|large` profiles; compare median score | `.cortex/reports/project_state/phase2_retrieval_relevance_report_v0.json` | C |
| Must-have context hit rate (`top_k_recall`) | `>= 0.80` and not lower than baseline | labeled fixture set with expected context ids; evaluate top-k recall | `.cortex/reports/project_state/phase2_retrieval_relevance_report_v0.json` | C |
| Ranking determinism | `100%` normalized ordering consistency for repeated runs | repeat each query/profile `>=30` times; compare normalized ranking hashes | `.cortex/reports/project_state/phase2_retrieval_determinism_report_v0.json` | C |
| Context bundle budget compliance | `100%` runs within configured record/char limits | parse bundle metadata over `n>=50` runs across profiles | `.cortex/reports/project_state/phase2_context_budget_report_v0.json` | C |
| Compaction/pruning safety | `0` protected-record removals; `100%` reason-code coverage | compaction/pruning stress suite with protected and eligible fixture classes | `.cortex/reports/project_state/phase2_compaction_policy_report_v0.json` | C |
| `context-load` p95 latency (tactical-only, no adapter) | `<= 2.0s` | timed runs on frozen profiles, `n>=30` per profile | `.cortex/reports/project_state/phase2_latency_report_v0.json` | C |
| CI mandatory governance runtime delta | `<= 10%` vs current post-Phase-1 baseline | compare median wall time over `>=5` runs before/after Phase 2 changes | `.cortex/reports/project_state/phase2_ci_overhead_report_v0.json` | C |
| Governance non-regression | `100%` pass on required governance gates | run release-boundary required gate bundle post-Phase-2 changes | `.cortex/reports/project_state/phase2_governance_regression_report_v0.md` | C |

## Workload Profiles and Fixture Freeze

Use three frozen profiles:

1. Small: low tactical history and narrow query scope.
2. Medium: representative active project profile.
3. Large: high-cardinality tactical history with stale/noise pressure.

Fixture rules:
- Freeze fixture corpus and labeled expected outputs before implementation comparison runs.
- Include fixture version id and hash in each measurement artifact.
- Do not change fixture set during a baseline-vs-post comparison cycle.
- Canonical fixture source for Phase 2 Gate C: `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`.

## Baseline and Comparison Plan

1. Pre-change baseline capture:
- Retrieval relevance and recall baseline on frozen fixture set.
- Determinism baseline for current retrieval path.
- Latency and CI baseline using current required gates.

2. Post-change measurement capture:
- Relevance, recall, determinism, context-budget compliance.
- Compaction/pruning safety outcomes.
- Latency and CI runtime delta.
- Governance non-regression run.

3. Comparison method:
- Use per-profile medians and p95 where applicable.
- Report aggregate and per-profile deltas.
- Mark failed metrics with explicit cause, owner, and remediation note.

## Gate C Measurement Criteria (Pass/Fail)

Gate C passes only when all conditions are true:

1. All artifacts listed in `Planned Artifacts` exist and are complete.
2. Every metric in `Metrics and Targets` meets target thresholds.
3. Determinism and compaction safety reports have zero unresolved critical findings.
4. Required governance gates pass with no new required-check failures.
5. Any residual non-critical findings are explicitly owner-assigned and time-bounded in closeout.

Gate C fails if any required metric misses threshold or any required governance gate regresses.

## Execution Cadence

- During Phase 2 implementation weeks, run focused relevance/determinism checks at least twice weekly.
- Run full measurement suite before requesting Gate C closeout.
- If usage pressure triggers constrained mode, prioritize determinism, budget compliance, and governance non-regression checks before additional feature expansion.

## Harness Command (PH2-006)

Deterministic fixture-driven retrieval evaluation command:

```bash
python3 scripts/phase2_retrieval_eval_harness_v0.py \
  --project-dir . \
  --coach-bin /tmp/cortex-coach/.venv/bin/cortex-coach \
  --legacy-loader-script scripts/agent_context_loader_v0.py
```

Command outputs:
- `.cortex/reports/project_state/phase2_retrieval_relevance_report_v0.json`
- `.cortex/reports/project_state/phase2_retrieval_determinism_report_v0.json`

Performance/budget + governance non-regression pack command:

```bash
python3 scripts/phase2_performance_governance_pack_v0.py \
  --project-dir . \
  --coach-bin /tmp/cortex-coach/.venv/bin/cortex-coach \
  --cortex-coach-repo /tmp/cortex-coach
```

Command outputs:
- `.cortex/reports/project_state/phase2_latency_report_v0.json`
- `.cortex/reports/project_state/phase2_context_budget_report_v0.json`
- `.cortex/reports/project_state/phase2_ci_overhead_report_v0.json`
- `.cortex/reports/project_state/phase2_governance_regression_report_v0.md`

## Ownership

- Primary owner: Runtime Reliability Lead.
- Measurement contract reviewer: Conformance QA Lead.
- Governance reviewer: Governance Policy Lead.
- CI overhead reviewer: CI/Gate Owner.

## Planned Artifacts

- `.cortex/reports/project_state/phase2_retrieval_relevance_report_v0.json`
- `.cortex/reports/project_state/phase2_retrieval_determinism_report_v0.json`
- `.cortex/reports/project_state/phase2_context_budget_report_v0.json`
- `.cortex/reports/project_state/phase2_compaction_policy_report_v0.json`
- `.cortex/reports/project_state/phase2_latency_report_v0.json`
- `.cortex/reports/project_state/phase2_ci_overhead_report_v0.json`
- `.cortex/reports/project_state/phase2_governance_regression_report_v0.md`
- `.cortex/reports/project_state/phase2_gate_c_measurement_closeout_v0.md`

# Cortex Phase 4 Measurement Plan v0

Version: v0  
Status: Draft  
Date: 2026-02-24  
Scope: Measurement and validation plan for promotion-flow and governance-enforcement hardening

## Purpose

Define deterministic Gate E criteria that verify tactical-to-governance promotion pathways improve linkage quality while preserving strict governance safety.

## Source Inputs

- `playbooks/cortex_phase4_promotion_enforcement_ticket_breakdown_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `.cortex/reports/project_state/phase3_gate_d_measurement_closeout_v0.md`
- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `contracts/promotion_contract_schema_v0.json`
- `contracts/promotion_enforcement_contract_v0.md`
- `.cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json`

## Scope

In scope:
- promotion assistant candidate mapping and scoring quality.
- deterministic promotion candidate ranking.
- fail-closed enforcement for unlinked governance-impacting closures.
- governance debt visibility coverage (`ready`, `blocked`, owner/action visibility).
- promotion-path latency and CI overhead budget validation.
- Gate E pass/fail determination criteria.

Out of scope:
- rollout-mode default-on determination (Phase 5 / Gate F).
- long-horizon adoption metrics and migration pack outcomes (Phase 5).
- additional external adapter implementations beyond Phase 3 baseline compatibility.

## Measurement Principles

- Governance first: promotion assistance cannot bypass decision/reflection/audit closure controls.
- Deterministic first: repeated identical input/state yields stable candidate ordering/scoring.
- Explainability: candidate scores and blocking outcomes must expose machine-readable reasons.
- Budget bounded: promotion/enforcement additions must stay within latency and CI overhead limits.
- Reproducibility: all artifacts are versioned under `.cortex/reports/project_state/`.

## Metrics and Targets

| Metric | Target | Method | Evidence Artifact | Gate |
|---|---|---|---|---|
| Promotion contract validity rate | `100%` candidate payloads schema-valid | run frozen promotion fixture set and validate against promotion contract schema | `.cortex/reports/project_state/phase4_promotion_candidate_quality_report_v0.json` | E |
| Promotion ranking determinism | `100%` normalized ordering consistency | repeat each promotion scenario `>=30` runs and compare ranking hashes | `.cortex/reports/project_state/phase4_promotion_determinism_report_v0.json` | E |
| Unlinked closure block rate | `100%` required block on unlinked governance-impact attempts | run synthetic/unlinked closure probes against enforced checks | `.cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json` | E |
| Linked closure false-block rate | `<= 5%` on valid linked governance-impact attempts | run linked control fixtures and track unexpected blocks | `.cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json` | E |
| Governance debt visibility coverage | `100%` required debt fixtures surfaced with state+owner/action fields | fixture-driven debt report validation | `.cortex/reports/project_state/phase4_governance_debt_visibility_report_v0.json` | E |
| Promotion-path p95 latency | `<= 2.5s` | timed promotion/evidence-scan operations across frozen fixtures (`n>=30` per profile) | `.cortex/reports/project_state/phase4_latency_report_v0.json` | E |
| CI mandatory governance runtime delta | `<= 10%` vs Phase 3 required-gate baseline | compare median `quality_gate_ci` wall time over `>=5` runs | `.cortex/reports/project_state/phase4_ci_overhead_report_v0.json` | E |
| Governance non-regression | `100%` pass on required governance gates | run required release-boundary governance bundle with promotion flow active | `.cortex/reports/project_state/phase4_governance_regression_report_v0.md` | E |

## Fixture Freeze

Canonical Phase 4 fixture source:
- `.cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json`

Rules:
- Freeze scenarios before baseline-vs-post comparisons.
- Include fixture artifact version/hash in generated reports.
- Any scenario/query change requires fixture version bump and Gate E baseline reset note.

## Gate E Pass/Fail Criteria

Gate E passes only when all conditions are true:

1. All Phase 4 measurement artifacts listed in this plan are present.
2. Every metric in `Metrics and Targets` meets thresholds.
3. Enforcement blocking checks prove unlinked governance-impacting closure attempts are blocked.
4. Required governance gates pass with no new required-check regressions.
5. Residual non-critical findings are owner-assigned and time-bounded in closeout.

Gate E fails if any required metric misses threshold or if governance closure can proceed without required linkage.

## Planned Harness Commands

Promotion candidate quality + determinism:

```bash
python3 scripts/phase4_promotion_candidate_harness_v0.py \
  --project-dir .
```

Expected outputs:
- `.cortex/reports/project_state/phase4_promotion_candidate_quality_report_v0.json`
- `.cortex/reports/project_state/phase4_promotion_determinism_report_v0.json`

Enforcement/debt/governance regression pack:

```bash
python3 scripts/phase4_promotion_governance_regression_harness_v0.py \
  --project-dir .
```

Expected outputs:
- `.cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json`
- `.cortex/reports/project_state/phase4_governance_debt_visibility_report_v0.json`
- `.cortex/reports/project_state/phase4_governance_regression_report_v0.md`

Performance and CI-overhead pack:

```bash
python3 scripts/phase4_promotion_performance_pack_v0.py \
  --project-dir .
```

Expected outputs:
- `.cortex/reports/project_state/phase4_latency_report_v0.json`
- `.cortex/reports/project_state/phase4_ci_overhead_report_v0.json`

## Planned Artifacts

- `.cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json`
- `.cortex/reports/project_state/phase4_promotion_candidate_quality_report_v0.json`
- `.cortex/reports/project_state/phase4_promotion_determinism_report_v0.json`
- `.cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json`
- `.cortex/reports/project_state/phase4_governance_debt_visibility_report_v0.json`
- `.cortex/reports/project_state/phase4_latency_report_v0.json`
- `.cortex/reports/project_state/phase4_ci_overhead_report_v0.json`
- `.cortex/reports/project_state/phase4_governance_regression_report_v0.md`
- `.cortex/reports/project_state/phase4_gate_e_measurement_closeout_v0.md`

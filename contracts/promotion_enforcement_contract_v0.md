# Promotion and Enforcement Contract v0

Canonical: true

Version: v0  
Status: Draft  
Scope: Phase 4 promotion-flow and governance-enforcement baseline contract

## Purpose

Define deterministic promotion-assistant and enforcement semantics so tactical evidence can be converted into canonical governance actions without bypassing decision/reflection closure rules.

## Contract Sources

- `playbooks/cortex_phase4_promotion_enforcement_ticket_breakdown_v0.md`
- `playbooks/cortex_phase4_measurement_plan_v0.md`
- `.cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json`
- `contracts/promotion_contract_schema_v0.json`
- `specs/cortex_project_coach_spec_v0.md`

## Input Contract Baseline

Required:
- `project_dir`
- promotion context input bundle (tactical candidates + governance context capsule)

Optional (Phase 4 baseline):
- `promotion_profile` (`small`, `medium`, `large`; default: `medium`)
- `candidate_limit` (bounded integer)
- `score_mode` (`uniform`, `evidence_bias`; default: `evidence_bias`)
- enforcement mode (`advisory`, `local_blocking`, `ci_blocking`)

## Promotion Mapping Requirements

- Promotion assistant output must map to `contracts/promotion_contract_schema_v0.json`.
- Candidate records must include:
  - deterministic `candidate_id`
  - decision/reflection linkage signals
  - impacted artifact candidates
  - rationale/evidence summary references
  - promotion trace metadata references
- Missing required mapping sections must be explicit and machine-readable.

## Scoring and Ordering Requirements

- Candidate ranking must be deterministic with fixed tie-break chain:
  1. `combined_score_desc`
  2. `evidence_coverage_desc`
  3. `governance_impact_priority_asc`
  4. `candidate_id_asc`
- Runtime-randomized ordering is disallowed.
- Score breakdown fields must remain bounded and machine-readable.

## Enforcement Blocking Requirements

- Governance-impacting closure attempts without required decision/reflection linkage must fail closed.
- Required release-boundary governance checks remain authoritative:
  - `decision-gap-check`
  - reflection enforcement gate
  - `audit --audit-scope all`
  - quality-gate required checks
- Linked governance-impacting closures should not be blocked except for explicit policy failures.

## Governance Debt Visibility Requirements

- Runtime must expose deterministic governance debt slices with:
  - state classification (`ready`, `blocked`)
  - owner/action fields
  - dependency linkage references
- Debt visibility output is advisory and non-authoritative until promoted.

## Budget and Performance Requirements

- Promotion/evidence-scan operations must remain within bounded runtime budgets.
- CI mandatory governance runtime delta target for Phase 4 is `<=10%` against Phase 3 required-gate baseline.
- Performance measurements must be reproducible from frozen fixture inputs.

## Fixture Freeze Binding

Gate E evaluation must use:
- `.cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json`

Any fixture profile/scenario/query change requires:
1. fixture version bump, and
2. explicit Gate E baseline reset note in closeout artifact.

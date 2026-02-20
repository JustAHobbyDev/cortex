# Cortex Coach Decoupling Plan v0

## Purpose

Define how `cortex` and `cortex-coach` can be developed together while becoming separate projects with clear implementation boundaries.

## Priority Order (Updated)

1. Governance completeness and enforceability.
2. Coach/Cortex decoupling execution.

Decoupling work should proceed only insofar as governance completeness is maintained or improved.

## North Star

`cortex` remains the cognitive governance source (principles/specs/policies/templates).  
`cortex-coach` becomes an installable runtime tool that consumes Cortex-compatible assets via a stable contract.

## Separation Boundary

`cortex` owns:
- conceptual model
- governance/spec artifacts
- asset definitions and templates
- contract evolution decisions

`cortex-coach` owns:
- CLI/runtime behavior
- audit/check implementations
- context loading behavior
- packaging, release, and distribution

## Core Design: Producer/Consumer Contract

1. Cortex is the producer of versioned coach assets.
2. Coach is the consumer/executor of those assets.
3. Compatibility is explicit via `asset_contract_version`.
4. Coach must fail closed on unsupported contract versions.

## Required Contract Surface (v0 target)

- manifest schema expectations
- spec registry shape
- policy artifact expectations
- decision artifact schema
- report file schema expectations (where required)
- required/optional asset paths

## Co-Development Workflow (Two Repos)

1. Propose design/governance change in `cortex` first.
2. Add contract impact note in the Cortex change.
3. Implement runtime delta in `cortex-coach`.
4. Link paired PRs (`cortex` + `cortex-coach`).
5. Merge only when both compatibility checks pass.

## Testing Strategy

- Keep canonical fixture bundles exported from `cortex`.
- In `cortex-coach` CI, run contract tests against those fixture bundles.
- In `cortex` CI, run compatibility smoke test against pinned `cortex-coach`.
- No shared runtime code across repos; share fixtures/contracts only.

## Versioning Model

- `cortex` publishes `asset_contract_version`.
- `cortex-coach` declares supported contract versions.
- Breaking contract change requires explicit version bump + migration notes.
- `cortex` pins recommended `cortex-coach` version for maintainers.

## Governance Rules

- No new runtime features land in Cortex-only paths after Phase 2 starts.
- Every contract change must include:
  - compatibility statement
  - migration guidance
  - test fixture update
- Every coach release must include supported contract matrix.

## Execution Checklist

## Phase 1: Internal Contract Refactor (in current repo)

### Tasks

- [x] Define `coach_asset_contract_v0` spec file in Cortex.
- [x] Add explicit asset-loader abstraction in coach runtime.
- [x] Remove hard-coded same-repo path assumptions where contract assets are consumed.
- [x] Add `coach contract-check` command for compatibility validation.
- [x] Add test fixtures for valid/invalid contract version scenarios.

### Acceptance Criteria

- [x] Coach can run with default bundled assets.
- [x] Coach can run with override assets path (`--assets-dir` or equivalent).
- [x] Unsupported contract versions fail with clear errors.
- [x] CI includes contract compatibility tests.

## Phase 2: Standalone Coach Repository

### Tasks

- [x] Create `cortex-coach` repository with package + CLI + docs + CI.
- [x] Move runtime/test/docs assets from Cortex to new repo.
- [x] Publish install instructions (`uv tool install` and pip fallback).
- [x] Add release tagging/versioning workflow for coach.
- [x] Add compatibility matrix doc (`coach_version` -> `asset_contract_version`).

### Acceptance Criteria

- [x] `cortex-coach` installs and runs without cloning Cortex.
- [x] New repo CI passes unit + contract tests.
- [x] Versioned release artifact is published.
- [x] Compatibility matrix is documented and tested.

## Phase 3: Dual-Path Stabilization

### Tasks

- [x] Keep temporary wrapper commands in Cortex that call installed coach.
- [x] Run parity checks between in-repo implementation and external coach.
- [x] Capture differences and fix until behavior is aligned.
- [x] Freeze in-repo coach feature development (bugfix-only mode).

### Acceptance Criteria

- [x] Parity test suite passes for key commands (`init`, `audit`, `coach`, `context-load`, decision commands).
- [x] No unresolved blocking behavior differences.
- [x] Cortex docs default to external coach usage.

Phase 3 evidence:
- `reports/phase3_parity_check_report_v0.md`
- `policies/cortex_in_repo_coach_bugfix_only_mode_v0.md`

## Phase 4: Full Decoupling

### Tasks

- [x] Convert `scripts/cortex_project_coach_v0.py` to thin external-only delegator.
- [x] Remove in-repo coach runtime implementation from Cortex.
- [x] Keep thin wrappers + docs for external coach usage.
- [x] Archive migration notes for users transitioning from in-repo scripts.
- [x] Update governance docs to reflect final ownership boundary.

### Acceptance Criteria

- [x] Cortex has no runtime coach code dependency on internal scripts.
- [x] All maintainer workflows run through external `cortex-coach`.
- [x] Migration docs and troubleshooting are complete.

Phase 4 evidence:
- `scripts/cortex_project_coach_v0.py` (external-only delegator)
- `docs/cortex-coach/migration_to_standalone_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`

## Operating Cadence

- Weekly: sync review between Cortex contract changes and coach runtime changes.
- Per PR: include contract impact statement in both repos when applicable.
- Pre-release: run compatibility matrix checks against latest Cortex fixture bundle.

## Work Tracking Fields

Use this minimal issue template in both repos:

- `Type`: contract | runtime | fixture | docs | migration
- `Phase`: 1 | 2 | 3 | 4
- `Contract Impact`: none | backward-compatible | breaking
- `Paired PR`: link to related PR in other repo
- `Acceptance`: checklist item(s) this issue closes

## Decision Gate Rules

- Do not start Phase 2 until all Phase 1 acceptance criteria are met.
- Do not start Phase 4 until parity is proven in Phase 3.
- Breaking contract changes require migration notes before merge.

## Priority 0: Governance Completeness Enforcement

Treat governance-completeness enforcement as the highest-priority track:

- [x] Add `decision-gap-check` (or equivalent) to detect governance-impacting file changes without a corresponding new decision capture/promotion.
- [x] Integrate that check into `quality-gate` and `quality-gate-ci`.
- [x] Keep decoupling milestones conditional on this enforcement path being active and passing.

## Priority 0 Enforcement Rule (Measurable)

Block advancing Phase 2+ checkboxes in this plan when either condition is true:

- `quality-gate-ci` fails on `decision-gap-check` in the current branch, or
- `decision-gap-check` exits non-zero for governance-impacting dirty files during maintainer review.

Allow Phase 2+ advancement only when:

- `decision-gap-check` is green, and
- linked decision artifacts exist for governance-impacting changes.

## Decoupling Dependency Rule

- Phase 2+ decoupling tasks should not advance while Priority 0 enforcement is red.

## Closeout Scope

Phases 1-4 are complete, including Phase 2 release-process follow-ups.

## Status

Closed v1 (Phases 1-4 completed; decoupling delivered).

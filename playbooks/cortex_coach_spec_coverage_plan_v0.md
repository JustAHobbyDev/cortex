# Cortex Coach Spec Coverage Plan v0

## Purpose

Define the next implementation phase for detecting unspecced areas in target projects and turning those gaps into actionable coach outputs.

## Problem

Current `cortex-coach` validates lifecycle structure and design schema integrity, but does not determine whether major project areas are unspecced.

## Scope

- In scope:
  - required spec inventory contract
  - audit checks for missing/stale/orphan specs
  - coach action generation for unspecced areas
  - optional draft stub generation for missing specs
- Out of scope:
  - deep semantic correctness of every spec body
  - domain-specific lints beyond contract-level checks (v0)

## Planned Deliverables

1. `spec_registry_v0.json` contract
- Canonical registry of required spec domains and expected file patterns.
- Supports priority and blocking severity.

2. Audit extension
- New spec-coverage section in lifecycle audit output.
- Detect:
  - missing required specs
  - stale specs (code changed but linked spec not updated)
  - orphan specs (spec exists without mapped domain target)

3. Coach extension
- Include `spec_coverage_actions` in cycle outputs.
- Prioritize blocking unspecced areas first.

4. Optional draft stubs
- `coach --apply` can generate missing `v0`/`v1` spec stubs from registry templates.

## Execution Steps

1. Add registry schema + example registry artifact.
2. Implement audit collector for registry-aware coverage checks.
3. Emit structured coverage report in .cortex/reports/lifecycle_audit_v0.json.
4. Add coverage-driven coach action generation.
5. Add scoped draft generation for missing specs.
6. Update docs and runbook with coverage workflow.

## Validation Plan

- Positive case: project with complete mapped specs => coverage pass.
- Missing case: required domain absent => blocking coverage finding.
- Stale case: mapped source changed after spec timestamp => stale finding.
- Orphan case: unmatched spec file => warning finding.

## Commit Plan

1. Code + contracts for registry and audit.
2. Coach integration + draft generation.
3. Docs and examples.

## Status

Saved, not yet executed.

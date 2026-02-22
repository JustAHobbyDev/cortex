# Cortex Adoption Delta Plan v0

## Purpose

Adopt the highest-value process strengths observed in `../ai-development-patterns` while preserving Cortex's current advantages (executable governance and context-control tooling).

## Outcome Target

Within 3 small PRs, Cortex should have:
- CI-based quality gate automation for docs/spec/policy integrity
- focused automated tests for core `cortex-coach` behaviors
- a single maintainer quality command for local + CI parity

## PR 1 — CI Validation Skeleton

### Scope

Add a minimal GitHub Actions workflow that enforces core repository integrity checks on push/PR.

### Changes

1. Add .github/workflows/cortex-validation.yml with jobs:
- `markdown-link-check` for `README.md`, `docs/`, `playbooks/`, `specs/`
- `json-parse-check` for .cortex/templates/*.json, .cortex/*.json (if present)
- `coach-smoke-check`:
  - `python3 scripts/cortex_project_coach_v0.py --help`
  - `python3 scripts/cortex_project_coach_v0.py audit-needed --project-dir . --format json`

2. Add lightweight helper script:
- `scripts/ci_validate_docs_and_json_v0.sh`

### Acceptance Criteria

- Workflow runs on PRs to `main`.
- Fails on malformed JSON or broken local markdown links.
- Produces clear per-job failure messages.

---

## PR 2 — Coach Test Suite (Core Behaviors)

### Scope

Create a focused test suite for high-risk `cortex-coach` command paths.

### Changes

1. Add `tests/` harness (pytest):
- `tests/test_coach_audit_needed.py`
- `tests/test_coach_context_load.py`
- `tests/test_coach_context_policy.py`
- `tests/test_coach_policy_enable.py`
- `tests/test_coach_spec_coverage.py`

2. Add `tests/conftest.py` with temp-project fixtures.
3. Add `tests/requirements.txt` and/or use project deps via `uv`.

### Acceptance Criteria

- Tests cover success + failure paths (including lock timeout and fallback metadata).
- `uv run pytest -q` passes locally.
- CI workflow from PR 1 executes this test suite.

---

## PR 3 — Unified Quality Gate Command

### Scope

Provide one deterministic command that maintainers and CI can both run.

### Changes

1. Add `just quality-gate` recipe chaining:
- `coach-audit-needed` (JSON mode)
- coach smoke checks
- docs/link checks
- test suite

2. Add `scripts/quality_gate_v0.sh` for environments without `just`.
3. Add docs:
- `docs/cortex-coach/quality-gate.md`
- update `README.md` and maintainer runbook with one-command gate guidance

### Acceptance Criteria

- `just quality-gate` is green in normal repo state.
- CI can invoke the same command/script without divergence.
- Documentation states exactly when gate must be run (pre-merge / pre-release).

---

## Non-Goals (for this plan)

- Expanding pattern catalog size to mirror `ai-development-patterns`
- Replacing Cortex ontology/governance model with another structure
- Heavy external-link checks on every push (can be scheduled later)

## Why This Sequence

1. CI skeleton first creates immediate enforcement.
2. Tests second increase confidence in executable governance.
3. Unified gate third reduces process drift between local and CI execution.

## Status

- PR 1: completed
- PR 2: completed
- PR 3: completed

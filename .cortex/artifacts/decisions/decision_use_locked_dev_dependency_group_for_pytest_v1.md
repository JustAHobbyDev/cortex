# Decision: Use locked dev dependency group for pytest

DecisionID: dec_20260220T112623Z_use_locked_dev_dependenc
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-20T11:26:23Z
PromotedAt: 2026-02-20T11:26:26Z
ImpactScope: governance, ci, tooling, quality-gate
LinkedArtifacts:
- `pyproject.toml`
- `uv.lock`
- `scripts/quality_gate_v0.sh`
- `scripts/quality_gate_ci_v0.sh`
- `docs/cortex-coach/quality-gate.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Adopt a pinned dev dependency group in pyproject and require uv run --locked --group dev for quality-gate test execution.

## Rationale
Ensures deterministic pytest/toolchain resolution across local and CI runs; avoids floating uv run --with pytest behavior.

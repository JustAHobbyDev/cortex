# Decision: Fix decoupled coach entrypoint shadowing in CI and scripts

DecisionID: dec_20260220T211718Z_fix_decoupled_coach_entr
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-20T21:17:18Z
PromotedAt: 2026-02-20T21:17:21Z
ImpactScope: governance, ci, tooling, docs
LinkedArtifacts:
- `pyproject.toml`
- `.github/workflows/cortex-validation.yml`
- `scripts/quality_gate_ci_v0.sh`
- `scripts/quality_gate_v0.sh`
- `scripts/cortex_coach_wrapper_v0.sh`
- `docs/cortex-coach/commands.md`
- `docs/cortex-coach/faq.md`
- `docs/cortex-coach/install.md`
- `docs/cortex-coach/quickstart.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Remove stale local cortex-coach entrypoint metadata, install standalone coach in CI, and call delegator via python3 to avoid uv shadowing side effects.

## Rationale
Prevents ModuleNotFoundError from broken local script shadowing and aligns execution with external-only coach ownership.

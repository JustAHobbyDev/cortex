# Decision: Gate onboarding labs with command-surface preflight

DecisionID: dec_20260225T034446Z_gate_onboarding_labs_wit
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-25T03:44:46Z
PromotedAt: 2026-02-25T03:44:47Z
ImpactScope: governance, docs, training
LinkedArtifacts:
- `scripts/client_onboarding_command_preflight_v0.py`
- `docs/cortex-coach/client_training_labs_v0.md`
- `docs/cortex-coach/README.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Introduce a required command-surface preflight script and enforce its use before M2 and M4 labs.

## Rationale
CT-005 pilot showed command capability drift can invalidate onboarding runs; preflight blocks early and provides deterministic remediation guidance.

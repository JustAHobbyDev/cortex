# Decision: Require universal JSON format contract for non-interactive coach commands

DecisionID: dec_20260221T230319Z_require_universal_json_f
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-21T23:03:19Z
PromotedAt: 2026-02-21T23:03:31Z
ImpactScope: governance, workflow, ci, tooling
LinkedArtifacts:
- `policies/cortex_coach_cli_output_contract_policy_v0.md`
- `scripts/cortex_project_coach_v0.py`
- `specs/cortex_project_coach_spec_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `docs/cortex-coach/commands.md`
- `docs/cortex-coach/troubleshooting.md`
- `tests/test_coach_format_contract.py`
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `.cortex/reports/project_state/ph0_005_enforcement_ladder_mapping_evidence_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
All non-interactive coach commands must support --format text|json with default text preserved; temporary delegator output shims are allowed until standalone parity is complete.

## Rationale
Automation and governance checks require deterministic machine-parseable outputs, and backward compatibility prevents breaking existing text-mode workflows.

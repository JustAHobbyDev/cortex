# Client Training Split Execution Report v0

- Date: 2026-02-25
- Scope: Execute split of client training material from `cortex` core repo into standalone training project ownership.
- Status: pass

## Decision

Training material ownership is now externalized. `cortex` keeps governance/runtime authority plus integration contracts and compatibility stubs.

## Canonical Reference

1. `docs/cortex-coach/client_training_external_repo_v0.md`
2. `docs/cortex-coach/client_training_project_boundary_and_handoff_v0.md`

## Compatibility-Stub Paths Retained in Cortex

1. `docs/cortex-coach/client_ai_governance_fundamentals_v0.md`
2. `docs/cortex-coach/client_training_labs_v0.md`
3. `playbooks/cortex_client_onboarding_training_track_v0.md`
4. `playbooks/cortex_client_onboarding_training_execution_board_v0.md`
5. `.cortex/templates/client_onboarding_completion_report_template_v0.md`
6. `contracts/client_onboarding_certification_scorecard_schema_v0.json`
7. `scripts/client_onboarding_command_preflight_v0.py`
8. `scripts/client_onboarding_certification_pack_v0.py`

## Contracts Preserved in Cortex

1. `contracts/client_training_project_handoff_schema_v0.json`
2. `.cortex/templates/client_training_project_handoff_manifest_template_v0.json`

## Quality Notes

1. Compatibility stubs are intentionally thin and non-authoritative.
2. Legacy paths remain resolvable to avoid historical-reference breakage.
3. Full training curriculum/labs/certification ownership is expected in standalone training project.

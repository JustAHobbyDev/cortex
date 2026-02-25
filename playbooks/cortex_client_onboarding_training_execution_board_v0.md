# Cortex Client Onboarding Training Execution Board v0

Version: v0  
Status: Active  
Date: 2026-02-25  
Scope: Execution board for building and operationalizing the client onboarding training track

## Purpose

Translate the client onboarding training track into owned, evidence-backed execution tickets.

## Source Inputs

- `playbooks/cortex_client_onboarding_training_track_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `docs/cortex-coach/README.md`
- `docs/cortex-coach/quickstart.md`
- `docs/cortex-coach/quality-gate.md`

## Execution Order

1. Baseline onboarding program contract (`CT-001` to `CT-003`)
2. Training delivery assets and labs (`CT-004`)
3. Pilot and calibration (`CT-005`)
4. Automation and recurring operating cadence (`CT-006`)

## Execution Board

Status vocabulary:
- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

| Ticket | Title | Status | Owner (Suggested Role) | Primary Reviewer (Suggested Role) | Target Date | Blockers | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|
| CT-001 | Training Track Execution Board Baseline | done | Program Lead | Maintainer Council | 2026-02-25 | - | `playbooks/cortex_client_onboarding_training_execution_board_v0.md`;`playbooks/cortex_client_onboarding_training_track_v0.md` | Establishes owned execution sequence and evidence contract. |
| CT-002 | Onboarding Completion Report Template | done | Delivery Operations Lead | Governance Policy Lead | 2026-02-25 | CT-001 | `.cortex/templates/client_onboarding_completion_report_template_v0.md` | Standardizes final onboarding closeout and sign-off evidence. |
| CT-003 | Certification Scorecard JSON Schema | done | Contract/Schema Lead | Conformance QA Lead | 2026-02-25 | CT-001 | `contracts/client_onboarding_certification_scorecard_schema_v0.json` | Enables machine-checkable certification scoring and pass/fail determinations. |
| CT-004 | Module Lab Guide Pack (`M2`-`M5`) | done | Delivery Operations Lead | Runtime Reliability Lead | 2026-03-07 | CT-002,CT-003 | `docs/cortex-coach/client_training_labs_v0.md`;`docs/cortex-coach/README.md` | Deterministic command checklists and expected artifact outputs are now documented for `M2`-`M5`. |
| CT-005 | Internal Pilot Completion + Calibration Report | done | Program Lead | Maintainer Council | 2026-03-14 | - | `.cortex/reports/project_state/client_onboarding_pilot_calibration_report_v0.md`;`.cortex/reports/project_state/client_onboarding_pilot_calibration_data_v0.json`;`.cortex/reports/project_state/client_onboarding_pilot_command_runs_v0.ndjson` | Reference-project calibration completed; command-surface and environment prerequisite gaps captured for CT-006 remediation. |
| CT-006 | Certification Workflow Automation + Recurring Cadence | in_progress | Conformance QA Lead | CI/Gate Owner | 2026-03-21 | command-surface upgrade + completion report population for final pass | `scripts/client_onboarding_certification_pack_v0.py`;`.cortex/reports/project_state/client_onboarding_certification_pack_v0.json`;`playbooks/session_governance_hybrid_plan_v0.md` | Certification pack automation + cadence scheduling implemented; current run fails closed on known rollout command-surface and completion-report readiness gaps. |

## Definition of Done

This execution board is complete when:

1. `CT-001` through `CT-006` are marked `done` with evidence links.
2. At least one internal pilot team achieves certification using the rubric and schema.
3. Certification outputs are reproducible and auditable through defined artifacts.

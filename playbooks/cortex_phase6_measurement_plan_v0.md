# Cortex Phase 6 Measurement Plan v0

Version: v0  
Status: Active  
Date: 2026-02-25  
Scope: Measurement and validation plan for project bootstrap portability and Governance Driven Development (GDD) scale-out

## Purpose

Define Gate G criteria that prove Cortex can bootstrap new projects quickly while preserving strict governance authority, boundary controls, and context-hydration invariants.

## Source Inputs

- `playbooks/cortex_phase6_bootstrap_gdd_ticket_breakdown_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_client_onboarding_training_track_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `.cortex/reports/project_state/beads_comparative_research_report_v0.md`

## Scope

In scope:
- bootstrap-to-first-green-gate time for new repos.
- governance-capsule hydration compliance at session start and context rollover.
- project-boundary default/override enforcement and auditability.
- required governance-gate reliability in bootstrapped projects.
- operator command overhead during bootstrap and first governed closeout.

Out of scope:
- replacing canonical governance authority model.
- broad runtime memory feature expansion outside approved contracts.
- production-scale swarm orchestration beyond capability-policy scope.

## Measurement Principles

- Bootstrap speed does not trade off governance integrity.
- Boundary safety is default-on and explicit overrides are auditable.
- Hydration checks are deterministic and fail-closed for required governance context.
- Evidence must be reproducible, machine-readable, and rooted under `.cortex/reports/project_state/`.

## Metrics and Targets

| Metric | Target | Method | Evidence Artifact | Gate |
|---|---|---|---|---|
| Bootstrap time to first required green gate | `<= 30 minutes` median across pilots | run bootstrap flow on fresh repos and measure elapsed wall time to first full required-gate pass | `.cortex/reports/project_state/phase6_bootstrap_readiness_report_v0.json` | G |
| Governance capsule hydration compliance | `100%` for required session-start and rollover events | run hydration checks over deterministic event fixtures | `.cortex/reports/project_state/phase6_hydration_compliance_report_v0.json` | G |
| Boundary policy conformance | `100%` project-state writes within configured boundary (`.cortex` default) | execute boundary gate checks with default and explicit override scenarios | `.cortex/reports/project_state/phase6_boundary_conformance_report_v0.json` | G |
| Required governance gate reliability | `100%` pass on bootstrap pilot closeout runs | run release-boundary required gate bundle in each pilot repo | `.cortex/reports/project_state/phase6_bootstrap_readiness_report_v0.json` | G |
| Operator overhead | median closeout command count `<= 12` for first governed closeout | capture command telemetry during pilot workflow | `.cortex/reports/project_state/phase6_operator_overhead_report_v0.json` | G |
| Critical safety incidents | `0` false pass / false fail governance incidents | incident register + artifact review over pilot period | `.cortex/reports/project_state/phase6_gate_g_measurement_closeout_v0.md` | G |

## Gate G Pass/Fail Criteria

Gate G passes only when all conditions are true:

1. All Phase 6 measurement artifacts listed in this plan are present.
2. Every metric in `Metrics and Targets` meets threshold.
3. Required governance gates remain authoritative in every tested bootstrap flow.
4. Boundary-default and boundary-override behaviors are policy-conformant and auditable.

Gate G fails if any threshold is missed or if governance authority can be bypassed in bootstrap flows.

## Planned Harness Commands

Hydration compliance:

```bash
python3 scripts/context_hydration_gate_v0.py compliance \
  --project-dir . \
  --enforcement-mode block \
  --emit-events new_session,window_rollover \
  --verify-event pre_closeout \
  --required-events new_session,window_rollover \
  --out-file .cortex/reports/project_state/phase6_hydration_compliance_report_v0.json
```

Boundary conformance:

```bash
python3 scripts/phase6_boundary_conformance_harness_v0.py \
  --project-dir . \
  --out-file .cortex/reports/project_state/phase6_boundary_conformance_report_v0.json
```

Bootstrap scaffolder:

```bash
python3 scripts/cortex_project_coach_v0.py bootstrap-scaffold \
  --project-dir . \
  --project-id cortex \
  --project-name "Cortex" \
  --skip-init \
  --force \
  --format json
```

Bootstrap readiness harness + certification:

Training certification ownership has moved to the standalone training project.
In this repository, `scripts/client_onboarding_certification_pack_v0.py` is a compatibility shim (`status=moved`).
Historical Phase 6 readiness artifacts remain in `.cortex/reports/project_state/`.

External pilot validation harness:

```bash
python3 scripts/phase6_external_pilot_harness_v0.py \
  --project-dir . \
  --json-out-file .cortex/reports/project_state/phase6_external_pilot_report_v0.json \
  --out-file .cortex/reports/project_state/phase6_external_pilot_report_v0.md \
  --format json
```

Operator overhead report:

```bash
python3 scripts/phase6_operator_overhead_pack_v0.py \
  --project-dir . \
  --external-pilot-file .cortex/reports/project_state/phase6_external_pilot_report_v0.json \
  --out-file .cortex/reports/project_state/phase6_operator_overhead_report_v0.json \
  --format json
```

## Planned Artifacts

- `.cortex/reports/project_state/phase6_bootstrap_readiness_report_v0.json`
- `.cortex/reports/project_state/phase6_hydration_compliance_report_v0.json`
- `.cortex/reports/project_state/phase6_boundary_conformance_report_v0.json`
- `.cortex/reports/project_state/phase6_operator_overhead_report_v0.json`
- `.cortex/reports/project_state/phase6_external_pilot_report_v0.md`
- `.cortex/reports/project_state/phase6_external_pilot_report_v0.json`
- `.cortex/reports/project_state/phase6_gate_g_measurement_closeout_v0.md`

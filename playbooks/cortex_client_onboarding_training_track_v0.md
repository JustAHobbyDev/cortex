# Cortex Client Onboarding Training Track v0

Version: v0  
Status: Active  
Date: 2026-02-25  
Scope: End-to-end client enablement program for operating Cortex and cortex-coach safely and effectively

## Purpose

Define a repeatable training track that gets new client teams from initial setup to independent, governance-safe operation of Cortex.

## Outcomes

By the end of the track, a client team can:

1. Bootstrap and run Cortex in a project with deterministic outputs.
2. Operate required governance checks without bypasses.
3. Capture/promote decisions with reflection linkage.
4. Execute release-boundary closeout with auditable evidence.
5. Run in default mode with reversible rollback controls.

## Target Personas

| Persona | Primary Need | Mandatory Modules |
|---|---|---|
| Executive Sponsor | Understand governance value, rollout risk, and adoption KPIs | M0, M1, M6 |
| Program/Delivery Lead | Own rollout sequencing and closeout readiness | M0, M1, M2, M4, M6 |
| Engineering Lead | Integrate gates into day-to-day workflow and CI | M1, M2, M3, M4, M5 |
| Governance Owner | Enforce decision/reflection/audit discipline | M1, M3, M4, M5, M6 |
| Daily Contributor | Use core command flows safely and efficiently | M1, M2, M4 |

## Training Architecture

| Module | Name | Duration | Format | Exit Artifact |
|---|---|---:|---|---|
| M0 | Orientation and Operating Model | 60-90 min | Instructor-led | Team operating charter and role map |
| M1 | Core Foundations | 2-3 hours | Guided workshop | Green local quality-gate run |
| M2 | Operator Workflow | 3-4 hours | Hands-on lab | Completed session closeout sequence |
| M3 | Governance Enforcement | 3-4 hours | Hands-on lab | Decision + reflection + audit linkage set |
| M4 | Rollout and Recovery | 2-3 hours | Drill-based lab | Verified rollback + transition-audit pass |
| M5 | Project Integration | 1 day | Embedded pairing | Client repo integration PR with evidence |
| M6 | Certification and Handoff | 60-90 min | Review panel | Onboarding completion report and go-live approval |

## Module Details

### M0: Orientation and Operating Model

- Explain Governance Plane / Tactical Plane / Promotion Plane.
- Clarify ownership split: policy/spec authority vs runtime execution.
- Confirm client boundaries (`project_state_root`) and artifact discipline.

Completion criteria:
- Role ownership agreed.
- Success metrics and rollout stop-rules accepted.

### M1: Core Foundations

- Install and verify `cortex-coach`.
- Run `init`, `audit-needed`, `audit`, and `quality-gate-ci`.
- Understand project-boundary enforcement and deterministic outputs.

Completion criteria:
- Local required gate bundle passes.
- Team can explain each required gate and its failure semantics.

### M2: Operator Workflow

- Session-start workflow (`audit-needed`, mode check, scope check).
- During-implementation guardrails.
- Pre-merge/release sequence and evidence expectations.

Completion criteria:
- Simulated change completed with no gate bypass.
- Operator can produce complete closeout command transcript + outputs.

### M3: Governance Enforcement

- Decision capture and promotion lifecycle.
- Reflection scaffold requirements and completeness mapping.
- Mistake provenance and enforcement-gate behavior.

Completion criteria:
- At least one promoted decision linked to reflection report and artifacts.
- `decision-gap-check` and reflection enforcement pass under review.

### M4: Rollout and Recovery

- Rollout mode semantics (`off`, `experimental`, `default`).
- Transition metadata requirements and transition audit.
- Rollback drill (`default -> experimental -> off` readiness).

Completion criteria:
- Successful mode transition + post-transition audit pass.
- Successful rollback drill with incident linkage.

### M5: Project Integration

- Integrate command flows and gate invocation into client CI.
- Verify local + CI behavior parity.
- Confirm docs/runbooks for client team handoff.

Completion criteria:
- Integration PR merged with full governance evidence.
- CI gate pass in client environment.

### M6: Certification and Handoff

- Review all module artifacts against checklist.
- Evaluate readiness risks and owners.
- Grant go-live approval or assign remediation actions.

Completion criteria:
- Onboarding completion report approved.
- Post-onboarding cadence assigned (weekly for 4 weeks, then monthly).

## Standard Delivery Cadence

### Track A: Accelerated (2 weeks)

- Week 1: M0, M1, M2
- Week 2: M3, M4, M5, M6

Use when:
- Client has dedicated owner coverage and strong CI maturity.

### Track B: Standard (4 weeks)

- Week 1: M0, M1
- Week 2: M2, M3
- Week 3: M4, M5
- Week 4: M6 + stabilization checkpoint

Use when:
- Client needs broader stakeholder alignment and adoption support.

## Required Program Assets

1. Instructor deck for M0-M1.
2. Lab guides for M2-M5 with fixed success checks.
3. Client onboarding completion report template.
4. Certification checklist + scoring rubric.
5. FAQ and triage playbook for common gate failures.

## Baseline Implemented Artifacts (v0)

1. Execution board: `playbooks/cortex_client_onboarding_training_execution_board_v0.md`
2. Onboarding completion report template: `.cortex/templates/client_onboarding_completion_report_template_v0.md`
3. Certification scorecard schema: `contracts/client_onboarding_certification_scorecard_schema_v0.json`

## Certification Rubric (Baseline)

| Category | Weight | Pass Threshold |
|---|---:|---:|
| Governance integrity (decision/reflection/audit) | 35% | >= 85% |
| Operational reliability (gates, CI, rollback) | 35% | >= 85% |
| Team readiness (role clarity, handoff quality) | 20% | >= 80% |
| Documentation quality (runbooks, evidence traceability) | 10% | >= 80% |

Hard fail conditions:
- Any required governance gate bypass.
- Unlinked governance-impacting closure.
- Inability to execute rollback drill safely.

## Success Metrics

| Metric | Target |
|---|---|
| Time to first green gate in client repo | <= 1 business day |
| First release with full governance linkage | <= 2 weeks from kickoff |
| Required gate pass rate during first month | >= 95% |
| Rollback drill completion rate | 100% |
| Operator command burden trend | non-increasing by week 4 |

## Post-Onboarding Governance Cadence

1. Week 1-4: weekly check-ins, artifact audit, and gate health review.
2. Month 2+: monthly governance review and drift check.
3. Triggered intervention when stop-rules fire or linkage coverage drops.

## Program Exit Criteria

Training track is complete when all conditions are true:

1. Client team passes certification rubric.
2. All required module artifacts are present and linked.
3. Client repo demonstrates at least one complete governance-safe closeout.
4. Stabilization cadence and ownership map are accepted.

## Immediate Build Plan

1. Done: publish onboarding execution board and baseline ownership mapping.
2. Done: add onboarding completion report template under `.cortex/templates/`.
3. Done: add certification rubric JSON schema for machine-checkable scorecards.
4. Done: author module lab guides (`M2`-`M5`) with deterministic command checklists.
5. Done: pilot with one internal reference project and publish calibration evidence (`.cortex/reports/project_state/client_onboarding_pilot_calibration_report_v0.md`).
6. Done: execute CT-006 certification automation and cadence controls with passing evidence in `.cortex/reports/project_state/client_onboarding_certification_pack_v0.json`, supported by preflight + completion artifacts.

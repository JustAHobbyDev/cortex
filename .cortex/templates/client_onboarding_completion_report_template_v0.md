# Client Onboarding Completion Report Template v0

Version: v0  
Artifact: client_onboarding_completion_report_v0  
Date: <YYYY-MM-DD>  
Client: <client_name>  
Project: <project_name>  
Track Variant: <accelerated|standard|custom>  
Program Lead: <name>  
Governance Owner: <name>  
Reviewer: <name>

## Scope

Summarize onboarding execution, evidence, certification outcome, and go-live readiness.

## Module Completion Summary

| Module | Status (`pass`/`fail`) | Completion Date | Primary Evidence |
|---|---|---|---|
| M0 Orientation and Operating Model | <status> | <date> | <artifact_path> |
| M1 Core Foundations | <status> | <date> | <artifact_path> |
| M2 Operator Workflow | <status> | <date> | <artifact_path> |
| M3 Governance Enforcement | <status> | <date> | <artifact_path> |
| M4 Rollout and Recovery | <status> | <date> | <artifact_path> |
| M5 Project Integration | <status> | <date> | <artifact_path> |
| M6 Certification and Handoff | <status> | <date> | <artifact_path> |

## Required Gate Evidence

1. `decision-gap-check` result: <artifact_path>
2. `reflection_enforcement_gate` result: <artifact_path>
3. `audit --audit-scope all` result: <artifact_path>
4. `project_state_boundary_gate` result: <artifact_path>
5. `quality_gate_ci` result: <artifact_path>

## Certification Result

- Scorecard artifact: `<artifact_path>`
- Overall status: `<pass|fail>`
- Weighted score (%): `<value>`
- Hard-fail conditions triggered: `<none|list>`

## Risk Register

| Risk | Severity | Owner | Mitigation | Target Date | Status |
|---|---|---|---|---|---|
| <risk_1> | <low|medium|high> | <owner> | <mitigation> | <date> | <open|closed> |
| <risk_2> | <low|medium|high> | <owner> | <mitigation> | <date> | <open|closed> |

## Go-Live Decision

- Decision: `<approved|conditional|blocked>`
- Decision Rationale: <text>
- Conditions (if conditional): <text>
- Next Checkpoint Date: <YYYY-MM-DD>

## Sign-Off

- Program Lead: <name> / <date>
- Governance Owner: <name> / <date>
- Client Sponsor: <name> / <date>

## Linked Artifacts

1. `playbooks/cortex_client_onboarding_training_track_v0.md`
2. `playbooks/cortex_client_onboarding_training_execution_board_v0.md`
3. `contracts/client_onboarding_certification_scorecard_schema_v0.json`

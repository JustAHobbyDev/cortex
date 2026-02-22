# Decision: Artifact conformance remediation pass for legacy governance docs

DecisionID: dec_20260222T082515Z_artifact_conformance_rem
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-22T08:25:15Z
PromotedAt: 2026-02-22T08:26:29Z
ImpactScope: governance, workflow, docs
LinkedArtifacts:
- `playbooks/agent_deploy_flow_v0.md`
- `playbooks/agent_executor_runbook_v0.md`
- `playbooks/beads_boundary_audit_v0.md`
- `playbooks/claude_session_closeout_runbook_v0.md`
- `playbooks/cortex_adoption_delta_plan_v0.md`
- `playbooks/cortex_coach_spec_coverage_plan_v0.md`
- `playbooks/cortex_coach_stage1_steering_quality_plan_v0.md`
- `playbooks/cortex_project_coach_runbook_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/generate_project_history_v0.md`
- `playbooks/incorporate_scene_into_graph_v0.md`
- `playbooks/namespace_boundary_audit_v0.md`
- `playbooks/project_manager_consultation_loop_v0.md`
- `playbooks/project_manager_recurring_cycle_skill_v0.md`
- `playbooks/second_brain_portable_bootstrap_v0.md`
- `playbooks/shell_embedding_audit_v0.md`
- `playbooks/structural_audit_runbook_v0.md`
- `playbooks/vision_alignment_audit_v0.md`
- `policies/cortex_coach_usage_decision_policy_v0.md`
- `policies/cortex_maintainer_mode_tracking_policy_v0.md`
- `policies/governance_gradient_spec_v0.md`
- `policies/oq3_autonomy_risk_policy_v0.md`
- `policies/scene_namespace_boundary_v0.md`
- `policies/session_tracking_externalization_v0.md`
- `policies/terminology_standard_v0.md`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Normalize legacy governance/playbook references to remove artifact-conformance drift signals while preserving policy intent and project-boundary defaults.

## Rationale
Audit findings were dominated by legacy reference-path and foreign project token patterns in non-executable docs. Remediation keeps enforcement focused on actionable drift and restores clean audit baselines.

# Cortex Phase 0 Governance Ticket Breakdown v0

Version: v0  
Status: Draft  
Scope: Phase 0 execution tickets for dual-plane governance lock-in

## Purpose

Provide an executable Phase 0 ticket set derived from:

- `playbooks/cortex_vision_master_roadmap_v1.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `specs/agent_context_loader_spec_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `playbooks/cortex_phase0_role_charters_v0.md`
- .cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md

## Execution Order

1. `PH0-001` through `PH0-004` (authority + contracts)
2. `PH0-005`, `PH0-006`, `PH0-010`, `PH0-011`, `PH0-012`, `PH0-013`, and `PH0-014` (enforcement + controls + boundary + swarm GDD + hydration + release-surface + mistake-provenance hygiene)
3. `PH0-007` and `PH0-008` (capacity governance + verification)
4. `PH0-009` (closeout package)

## Execution Board (Fillable)

Status vocabulary:
- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

Update cadence:
- Update board at least once per working day.
- Run weekly checkpoint at end of week before scheduling next week.
- Fill role-to-individual mapping before moving any ticket to `in_progress`.
- If solo-maintainer exception is active, follow compensating controls in `playbooks/cortex_phase0_role_charters_v0.md`.

Suggested role labels:
- `Governance Policy Lead`
- `Contract/Schema Lead`
- `Security & Data Policy Lead`
- `Adapter Safety Lead`
- `Governance Enforcement Lead`
- `Runtime Reliability Lead`
- `Delivery Operations Lead`
- `Conformance QA Lead`
- `Program Lead`
- `CI/Gate Owner`
- `Maintainer Council`

### Individual Mapping (Fillable)

Map role labels to specific people/accounts before execution begins.

| Role Label | Primary Individual / Account | Backup Individual / Account | Notes |
|---|---|---|---|
| Governance Policy Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Contract/Schema Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Security & Data Policy Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Adapter Safety Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Governance Enforcement Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Runtime Reliability Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Delivery Operations Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Conformance QA Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Program Lead | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| CI/Gate Owner | Dan Schmidt (`@JustAHobbyDev`) | Maintainer Council (interim) | Solo-maintainer interim mapping; add named secondary maintainer before Phase 1. |
| Maintainer Council | Dan Schmidt (`@JustAHobbyDev`) | tbd | Solo-maintainer exception expires 2026-03-08; expand to at least two maintainers before Phase 1 gate elevation. |

| Ticket | Title | Status | Owner (Suggested Role) | Primary Reviewer (Suggested Role) | Target Week | Target Date | Blockers | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PH0-001 | Canonical Authority and Dual-Plane Policy Lock-In | done | Governance Policy Lead | Maintainer Council | Week 1 | 2026-02-27 | - | .cortex/reports/project_state/ph0_001_canonical_authority_closeout_v0.md;policies/cortex_coach_final_ownership_boundary_v0.md;playbooks/cortex_vision_master_roadmap_v1.md | council review captured; acceptance criteria satisfied; dependent tickets unblocked |
| PH0-002 | Promotion Contract Schema v0 | done | Contract/Schema Lead | Governance Policy Lead | Week 1 | 2026-02-27 | - | .cortex/reports/project_state/ph0_002_promotion_contract_schema_closeout_v0.md;contracts/promotion_contract_schema_v0.json;specs/cortex_project_coach_spec_v0.md | required fields + invalid-linkage validation rules verified; closeout evidence captured |
| PH0-003 | Tactical Data Policy v0 | done | Security & Data Policy Lead | Governance Policy Lead | Week 1 | 2026-02-27 | - | .cortex/reports/project_state/ph0_003_tactical_data_policy_closeout_v0.md;policies/tactical_data_policy_v0.md;specs/cortex_project_coach_spec_v0.md;playbooks/session_governance_hybrid_plan_v0.md | closeout evidence captured; acceptance criteria satisfied |
| PH0-004 | External Adapter Safety Contract v0 | done | Adapter Safety Lead | Runtime Reliability Lead | Week 1 | 2026-02-27 | PH0-001 | .cortex/reports/project_state/ph0_004_adapter_safety_reviewer_pass_v0.md;specs/cortex_project_coach_spec_v0.md;specs/agent_context_loader_spec_v0.md | done after required one-session review hold |
| PH0-005 | Enforcement Ladder Contract and CI Mapping | done | Governance Enforcement Lead | CI/Gate Owner | Week 2 | 2026-03-06 | - | .cortex/reports/project_state/ph0_005_enforcement_ladder_mapping_evidence_v0.md;.cortex/artifacts/decisions/decision_require_universal_json_format_contract_for_non_interactive_coach_commands_v1.md;playbooks/session_governance_hybrid_plan_v0.md;policies/cortex_coach_cli_output_contract_policy_v0.md;scripts/quality_gate_ci_v0.sh;scripts/quality_gate_v0.sh;specs/cortex_project_coach_spec_v0.md | acceptance criteria verified with updated governance checks and CI gate evidence |
| PH0-010 | Project-State Boundary Root Config + Enforcement | done | Governance Enforcement Lead | Maintainer Council | Week 1 | 2026-02-22 | PH0-001 | contracts/project_state_boundary_contract_v0.json;policies/project_state_boundary_policy_v0.md;specs/project_state_boundary_spec_v0.md;scripts/project_state_boundary_gate_v0.py;scripts/quality_gate_v0.sh;scripts/quality_gate_ci_v0.sh;.cortex/reports/project_state_boundary_migration_v0.md;.cortex/artifacts/decisions/decision_enforce_project_state_boundary_under_cortex_v1.md | implemented configurable `project_state_root` (default .cortex/) and fail-closed gate; migrated legacy top-level project-state reports under .cortex/reports/ |
| PH0-006 | Kill-Switch and Rollback Governance Controls | todo | Runtime Reliability Lead | Governance Enforcement Lead | Week 2 | 2026-03-06 | - | tbd | ready after PH0-001 closeout |
| PH0-007 | Capacity Governance Cadence (Codex Plus) | todo | Delivery Operations Lead | Runtime Reliability Lead | Week 2 | 2026-03-06 | - | tbd | ready after PH0-001 closeout |
| PH0-011 | Swarm Governance Driven Development Baseline | todo | Governance Enforcement Lead | Maintainer Council | Week 2 | 2026-03-06 | PH0-001,PH0-005,PH0-006,PH0-010 | playbooks/cortex_vision_master_roadmap_v1.md;playbooks/cortex_phase0_governance_ticket_breakdown_v0.md;scripts/quality_gate_ci_v0.sh;scripts/reflection_enforcement_gate_v0.py | formalize Swarm-GDD gates and exit criteria before broader swarm adoption |
| PH0-012 | Context Hydration Contract + Preflight Policy Baseline | done | Governance Enforcement Lead | Governance Policy Lead | Week 1 | 2026-02-22 | - | .cortex/reports/project_state/ph0_012_context_hydration_baseline_closeout_v0.md;contracts/context_hydration_receipt_schema_v0.json;policies/context_hydration_policy_v0.md;specs/cortex_project_coach_spec_v0.md | phase-0 baseline landed; runtime command-level enforcement rollout remains follow-on work |
| PH0-013 | Temporal Playbook Retirement + Release Surface Gate | done | Conformance QA Lead | Maintainer Council | Week 2 | 2026-03-06 | PH0-010 | .cortex/reports/project_state/ph0_013_temporal_playbook_release_surface_closeout_v0.md;contracts/temporal_playbook_release_surface_contract_v0.json;policies/temporal_playbook_release_surface_policy_v0.md;scripts/temporal_playbook_release_gate_v0.py;scripts/quality_gate_v0.sh;scripts/quality_gate_ci_v0.sh;.cortex/artifacts/decisions/decision_enforce_temporal_playbook_retirement_and_release_surface_gating_v1.md | temporal classification contract + fail-closed release-surface gate implemented with promoted decision linkage |
| PH0-014 | Machine-Caught Mistake Provenance Contract + Gate | todo | Governance Enforcement Lead | Conformance QA Lead | Week 2 | 2026-03-06 | PH0-005 | tbd | formalize machine-verifiable mistake detection provenance and prevent ungrounded agent-caught claims |
| PH0-008 | Phase 0 Conformance Verification Pack | todo | Conformance QA Lead | Governance Policy Lead | Week 2 | 2026-03-06 | PH0-001,PH0-002,PH0-003,PH0-004,PH0-005,PH0-006,PH0-007,PH0-010,PH0-011,PH0-012,PH0-013,PH0-014 | tbd | |
| PH0-009 | Maintainer Closeout and Handoff Package | todo | Program Lead | Maintainer Council | Week 2 | 2026-03-06 | PH0-008 | tbd | |

## Weekly Checkpoint Template (Fillable)

Use this at end of each week:

| Week | Date Range | Completed Tickets | In Progress | Blocked | Capacity Notes (/status/dashboard) | Next-Week Plan | Decision/Policy Escalations |
|---|---|---|---|---|---|---|---|
| Week 1 | 2026-02-23 to 2026-03-01 | tbd | tbd | tbd | tbd | tbd | tbd |
| Week 2 | 2026-03-02 to 2026-03-08 | tbd | tbd | tbd | tbd | tbd | tbd |

## Tickets

### PH0-001: Canonical Authority and Dual-Plane Policy Lock-In

Objective:
- Finalize canonical authority language and non-bypass rules as enforceable policy text.

Primary artifacts:
- `policies/cortex_coach_final_ownership_boundary_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`

Acceptance criteria:
- Governance plane authority is explicitly normative.
- Tactical plane non-authoritative status is explicit.
- Adapter non-bypass rule is explicit.
- Override/escalation owners are explicit.

Evidence:
- Merged policy/playbook diffs with changelog note.

### PH0-002: Promotion Contract Schema v0

Objective:
- Define machine-readable promotion contract fields and requiredness for tactical -> canonical promotion.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `contracts/promotion_contract_schema_v0.json`

Acceptance criteria:
- Required fields defined:
  - decision/reflection linkage
  - impacted artifact linkage
  - rationale/evidence summary
  - promotion trace metadata
- Validation rules specified for missing/invalid linkage.

Evidence:
- Contract artifact committed and referenced in spec.

### PH0-003: Tactical Data Policy v0

Objective:
- Define data class restrictions and lifecycle controls for tactical plane storage.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `policies/tactical_data_policy_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`

Acceptance criteria:
- Explicit prohibited classes (secrets/credentials/PII) documented.
- Required controls documented:
  - TTL/pruning/compaction
  - redaction behavior
  - sanitization failure handling

Evidence:
- Policy text linked from spec and session runbook.

### PH0-004: External Adapter Safety Contract v0

Objective:
- Define adapter behavior contract for optional external tactical sources.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `specs/agent_context_loader_spec_v0.md`

Acceptance criteria:
- Read-only default rule is explicit.
- Timeout/degradation behavior is explicit (governance-only fallback).
- Provenance/freshness requirements are explicit.
- Adapter failure cannot block mandatory governance checks.

Evidence:
- Spec-level adapter contract section and fallback semantics documented.

### PH0-005: Enforcement Ladder Contract and CI Mapping

Objective:
- Convert advisory/local/CI enforcement ladder into explicit operational mapping.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `scripts/quality_gate_ci_v0.sh` (mapping note only in Phase 0; behavior changes later)

Acceptance criteria:
- Level 0/1/2 semantics documented with escalation rules.
- Release boundary required checks explicitly mapped.
- Policy change process for level changes is documented.

Evidence:
- Updated runbook section plus a mapping matrix committed.

### PH0-010: Project-State Boundary Root Config + Enforcement

Objective:
- Enforce a configurable project-state boundary root with .cortex/ as the default.

Primary artifacts:
- `contracts/project_state_boundary_contract_v0.json`
- `policies/project_state_boundary_policy_v0.md`
- `specs/project_state_boundary_spec_v0.md`
- `scripts/project_state_boundary_gate_v0.py`
- `scripts/quality_gate_v0.sh`
- `scripts/quality_gate_ci_v0.sh`
- .cortex/reports/project_state_boundary_migration_v0.md

Acceptance criteria:
- Boundary root is contract-defined via `project_state_root`.
- Default boundary root is .cortex/ unless policy-governed override is applied.
- Local and CI quality gates fail on forbidden project-state paths outside configured boundary root.
- Waiver exceptions are explicit and time-bounded with expiry enforcement.
- Legacy top-level project-state reports are migrated under .cortex/reports/.

Evidence:
- Boundary policy/spec/contract and gate merged with migration report and linked promoted decision artifact.

### PH0-006: Kill-Switch and Rollback Governance Controls

Objective:
- Define emergency disable and recovery expectations for tactical plane and adapters.

Primary artifacts:
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`

Acceptance criteria:
- Kill-switch ownership split is explicit (`cortex` policy, `cortex-coach` operation).
- Stop-rules are explicit and actionable.
- Stabilization-cycle procedure is documented.

Evidence:
- Cross-referenced stop-rule and rollback sections in all three artifacts.

### PH0-007: Capacity Governance Cadence (Codex Plus)

Objective:
- Formalize weekly usage review cadence and workload throttling rules.

Primary artifacts:
- .cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md
- `playbooks/session_governance_hybrid_plan_v0.md`

Acceptance criteria:
- Weekly checkpoint process documented using dashboard/`/status`.
- Mid-week pressure downgrade behavior documented.
- Review-heavy scheduling guard documented.

Evidence:
- Capacity cadence section linked from session plan.

### PH0-011: Swarm Governance Driven Development Baseline

Objective:
- Define and enforce the minimum governance contract required for multi-agent swarm execution.

Primary artifacts:
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `scripts/quality_gate_ci_v0.sh`
- `scripts/reflection_enforcement_gate_v0.py`

Acceptance criteria:
- Swarm governance rules are normative and explicit:
  - governance-impact closures require decision + reflection linkage
  - swarm outputs are non-authoritative until promoted
  - kill-switch degradation path is explicit
- Swarm gate bundle is explicitly listed and mapped to local + CI execution.
- Swarm adoption stop-rule is explicit: no default-on/broader swarm rollout before Swarm-GDD exit criteria are met.
- At least one verification note captures the intended end-to-end gate sequence for swarm-governed closeout.

Evidence:
- Roadmap and Phase 0 ticket board diffs with Swarm-GDD section and gate mapping.

### PH0-012: Context Hydration Contract + Preflight Policy Baseline

Objective:
- Establish deterministic policy + contract baseline for governance capsule hydration before mutation/closeout work.

Primary artifacts:
- `policies/context_hydration_policy_v0.md`
- `contracts/context_hydration_receipt_schema_v0.json`
- `specs/cortex_project_coach_spec_v0.md`
- .cortex/reports/project_state/ph0_012_context_hydration_baseline_closeout_v0.md

Acceptance criteria:
- Context hydration trigger events are explicitly policy-defined.
- Hydration freshness rules are explicitly policy-defined.
- Machine-readable hydration receipt schema is defined and versioned.
- Coach spec references hydration policy/contract and fail-closed enforcement expectations for governance-impacting paths.
- Ticket closeout evidence records governance check pass state.

Evidence:
- Policy + contract + spec diffs and closeout report committed.

### PH0-013: Temporal Playbook Retirement + Release Surface Gate

Objective:
- Prevent shipping temporal/project-specific Cortex-development playbooks in the distributable Cortex release surface.

Primary artifacts:
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `contracts/temporal_playbook_release_surface_contract_v0.json`
- `policies/temporal_playbook_release_surface_policy_v0.md`
- `scripts/temporal_playbook_release_gate_v0.py`
- `scripts/quality_gate_ci_v0.sh`
- `scripts/quality_gate_v0.sh`
- .cortex/reports/project_state/ph0_013_temporal_playbook_release_surface_closeout_v0.md

Acceptance criteria:
- Temporal playbook classification rule is defined (including required status/expiry/disposition metadata).
- Release-surface admission rule is defined: temporal/project-specific playbooks must be retired, archived under .cortex, or excluded from release packaging before release.
- CI/release quality gate includes a deterministic check that fails on expired/unretired temporal playbooks in distributable surface.
- Existing Cortex-development-specific playbooks have explicit disposition plans and owners.

Evidence:
- Policy/runbook/gate diffs and closeout report committed.

### PH0-014: Machine-Caught Mistake Provenance Contract + Gate

Objective:
- Make mistake detection claims machine-verifiable by enforcing explicit provenance, detector evidence, and confidence/status semantics.

Primary artifacts:
- `contracts/mistake_candidate_schema_v0.json`
- `policies/mistake_detection_provenance_policy_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `scripts/mistake_candidate_gate_v0.py`
- `scripts/quality_gate_ci_v0.sh`
- `scripts/quality_gate_v0.sh`
- `.cortex/reports/project_state/ph0_014_mistake_provenance_gate_closeout_v0.md`

Acceptance criteria:
- A versioned mistake-candidate schema defines required provenance fields (`detected_by`, `detector`, `evidence_refs`, `rule_violated`, `confidence`, `status`).
- Policy forbids reporting/claiming agent-caught mistakes without machine-recorded provenance meeting schema requirements.
- Deterministic gate fails when machine-caught claims are missing required provenance/evidence or use unsupported confidence/status values.
- Local and CI quality gates include the provenance gate before release-boundary checks complete.
- Existing mistake/reflection artifacts have migration/backfill guidance with explicit handling for unknown legacy provenance.

Evidence:
- Schema/policy/spec/gate diffs and closeout report committed.

### PH0-008: Phase 0 Conformance Verification Pack

Objective:
- Provide deterministic verification checklist proving Phase 0 governance lock-in is complete.

Primary artifacts:
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- .cortex/reports/project_state/ (new Phase 0 verification report expected in implementation)

Acceptance criteria:
- Checklist includes all PH0 tickets with pass/fail status.
- Evidence links for each ticket are recorded.
- Outstanding gaps are listed with owner and target date.

Evidence:
- Published verification report under .cortex/reports/project_state/.

### PH0-009: Maintainer Closeout and Handoff Package

Objective:
- Package Phase 0 decisions so Phase 1 implementation can start without governance ambiguity.

Primary artifacts:
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- .cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md

Acceptance criteria:
- Phase 1 entry conditions are explicitly listed.
- Open questions (if any) are enumerated with owner.
- Handoff summary includes “what is fixed policy vs what is implementation choice.”

Evidence:
- Final Phase 0 closeout note committed in .cortex/reports/project_state/.

## Capacity-Aware Scheduling (Option B Default)

Default weekly envelope for Phase 0 execution:

- `<= 2` five-hour windows/week
- `<= 3` cloud tasks/week
- `<= 2` code reviews/week

If weekly usage pressure exceeds threshold before Thursday:

- shift remaining work to docs/spec validation only
- defer any new scope ticket start to next week

## Definition of Done (Phase 0)

Phase 0 is complete when:

1. `PH0-001` through `PH0-014` are marked complete with evidence links.
2. Gate A conditions from .cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md are met.
3. Maintainers confirm Phase 1 can start without unresolved governance authority questions.

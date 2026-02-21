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
- `reports/mulch_beads_synthesized_plan_proposal_v0.md`

## Execution Order

1. `PH0-001` through `PH0-004` (authority + contracts)
2. `PH0-005` and `PH0-006` (enforcement + controls)
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
| PH0-001 | Canonical Authority and Dual-Plane Policy Lock-In | in_progress | Governance Policy Lead | Maintainer Council | Week 1 | 2026-02-27 | - | policies/cortex_coach_final_ownership_boundary_v0.md;playbooks/cortex_vision_master_roadmap_v1.md | authority wording hardened; pending council review |
| PH0-002 | Promotion Contract Schema v0 | in_progress | Contract/Schema Lead | Governance Policy Lead | Week 1 | 2026-02-27 | PH0-001 | contracts/promotion_contract_schema_v0.json;specs/cortex_project_coach_spec_v0.md | schema drafted in parallel; closure gated on PH0-001 |
| PH0-003 | Tactical Data Policy v0 | in_progress | Security & Data Policy Lead | Governance Policy Lead | Week 1 | 2026-02-27 | PH0-001 | policies/tactical_data_policy_v0.md;specs/cortex_project_coach_spec_v0.md;playbooks/session_governance_hybrid_plan_v0.md | policy drafted in parallel; closure gated on PH0-001 |
| PH0-004 | External Adapter Safety Contract v0 | done | Adapter Safety Lead | Runtime Reliability Lead | Week 1 | 2026-02-27 | PH0-001 | reports/ph0_004_adapter_safety_reviewer_pass_v0.md;specs/cortex_project_coach_spec_v0.md;specs/agent_context_loader_spec_v0.md | done after required one-session review hold |
| PH0-005 | Enforcement Ladder Contract and CI Mapping | in_progress | Governance Enforcement Lead | CI/Gate Owner | Week 2 | 2026-03-06 | PH0-002 | reports/ph0_005_enforcement_ladder_mapping_evidence_v0.md;playbooks/session_governance_hybrid_plan_v0.md;scripts/quality_gate_ci_v0.sh;specs/cortex_project_coach_spec_v0.md | evidence complete; pending PH0-002 closure before final review/done |
| PH0-006 | Kill-Switch and Rollback Governance Controls | todo | Runtime Reliability Lead | Governance Enforcement Lead | Week 2 | 2026-03-06 | PH0-001 | tbd | |
| PH0-007 | Capacity Governance Cadence (Codex Plus) | todo | Delivery Operations Lead | Runtime Reliability Lead | Week 2 | 2026-03-06 | PH0-001 | tbd | |
| PH0-008 | Phase 0 Conformance Verification Pack | todo | Conformance QA Lead | Governance Policy Lead | Week 2 | 2026-03-06 | PH0-001,PH0-002,PH0-003,PH0-004,PH0-005,PH0-006,PH0-007 | tbd | |
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
- `reports/mulch_beads_synthesized_plan_proposal_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`

Acceptance criteria:
- Weekly checkpoint process documented using dashboard/`/status`.
- Mid-week pressure downgrade behavior documented.
- Review-heavy scheduling guard documented.

Evidence:
- Capacity cadence section linked from session plan.

### PH0-008: Phase 0 Conformance Verification Pack

Objective:
- Provide deterministic verification checklist proving Phase 0 governance lock-in is complete.

Primary artifacts:
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `reports/` (new Phase 0 verification report expected in implementation)

Acceptance criteria:
- Checklist includes all PH0 tickets with pass/fail status.
- Evidence links for each ticket are recorded.
- Outstanding gaps are listed with owner and target date.

Evidence:
- Published verification report under `reports/`.

### PH0-009: Maintainer Closeout and Handoff Package

Objective:
- Package Phase 0 decisions so Phase 1 implementation can start without governance ambiguity.

Primary artifacts:
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `reports/mulch_beads_synthesized_plan_proposal_v0.md`

Acceptance criteria:
- Phase 1 entry conditions are explicitly listed.
- Open questions (if any) are enumerated with owner.
- Handoff summary includes “what is fixed policy vs what is implementation choice.”

Evidence:
- Final Phase 0 closeout note committed in `reports/`.

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

1. `PH0-001` through `PH0-009` are marked complete with evidence links.
2. Gate A conditions from `reports/mulch_beads_synthesized_plan_proposal_v0.md` are met.
3. Maintainers confirm Phase 1 can start without unresolved governance authority questions.

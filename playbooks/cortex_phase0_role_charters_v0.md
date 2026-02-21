# Cortex Phase 0 Role Charters v0

Version: v0  
Status: Draft  
Scope: Phase 0 governance lock-in execution roles

## Purpose

Define role-level responsibilities for Phase 0 so ownership is explicit before work begins.  
This charter makes role labels actionable by specifying:

- mandate and scope
- decision rights
- evidence obligations
- escalation paths
- coverage expectations

## Authority and Boundary Rules

1. Canonical authority for governance policy remains in `cortex` governance artifacts.
2. Tactical runtime behavior remains implemented and operated in `cortex-coach`.
3. No role may approve changes outside its boundary defined in `policies/cortex_coach_final_ownership_boundary_v0.md`.
4. Blocking-ticket reviewer must be different from the ticket owner.
5. Policy or contract override decisions require `Maintainer Council` approval.

## Coverage and Escalation Rules

1. Every role must have a named primary and backup before ticket execution starts.
2. If a primary role owner is unavailable for more than one working day, backup assumes ownership.
3. If owner and reviewer disagree on a blocking issue for more than one working day, escalate to `Maintainer Council`.
4. Evidence links are required before a ticket can move to `done`.

## Role Charters

| Role | Mandate | Primary Tickets | Decision Rights | Required Evidence | Escalation |
|---|---|---|---|---|---|
| Governance Policy Lead | Lock canonical governance language and authority model for Phase 0. | PH0-001 | Accept/reject governance policy wording and dual-plane authority framing, within maintainer policy constraints. | Linked policy/playbook diff and changelog note. | Escalate cross-boundary conflicts or unresolved authority ambiguity to `Maintainer Council`. |
| Contract/Schema Lead | Define promotion contract schema and validation semantics. | PH0-002 | Set required fields and validation behavior for tactical to canonical promotion contracts. | Contract artifact commit plus spec linkage. | Escalate normative conflicts to `Governance Policy Lead`; unresolved items to `Maintainer Council`. |
| Security & Data Policy Lead | Define tactical data-class restrictions and lifecycle controls. | PH0-003 | Set prohibited classes and minimum controls (TTL, redaction, sanitization handling). | Policy text linked from spec and session runbook. | Escalate security-risk exceptions to `Governance Policy Lead` and `Maintainer Council`. |
| Adapter Safety Lead | Define safe behavior contract for optional external adapters. | PH0-004 | Set adapter safety defaults (read-only, optional, fail-open degradation to governance-only mode). | Spec-level adapter contract section with fallback semantics. | Escalate reliability/safety tradeoff conflicts to `Runtime Reliability Lead`; then `Maintainer Council`. |
| Governance Enforcement Lead | Translate governance policy into enforceable ladder semantics and gate mapping. | PH0-005 | Define level semantics, escalation rules, and required check mapping at release boundary. | Enforcement matrix and runbook mapping commit. | Escalate CI enforceability conflicts to `CI/Gate Owner` and then `Maintainer Council`. |
| Runtime Reliability Lead | Own kill-switch and rollback operational governance controls. | PH0-006 | Approve operational stop-rules and stabilization-cycle readiness criteria. | Cross-referenced kill-switch and rollback sections in required artifacts. | Escalate runtime safety incidents or unresolved operational risk to `Maintainer Council`. |
| Delivery Operations Lead | Own capacity governance cadence and workload throttling policy. | PH0-007 | Set weekly throughput envelope, pressure downgrade behavior, and review-load guardrails. | Session-governance capacity section linked to planning artifact. | Escalate sustained capacity breaches to `Program Lead` and `Maintainer Council`. |
| Conformance QA Lead | Produce deterministic Phase 0 verification and evidence pack. | PH0-008 | Determine pass/fail on checklist completeness and evidence sufficiency; cannot waive hard requirements alone. | Published Phase 0 verification report with per-ticket evidence links. | Escalate failed mandatory criteria to `Governance Policy Lead` and `Maintainer Council`. |
| Program Lead | Orchestrate sequencing, dependency tracking, and handoff closeout. | PH0-009 | Set execution order, milestone readiness, and handoff completeness criteria; does not override policy authority. | Phase 0 closeout note with entry conditions and unresolved-question ownership. | Escalate schedule/ownership deadlocks to `Maintainer Council`. |
| CI/Gate Owner | Ensure CI gate behavior and policy mapping are operationally feasible. | Reviewer on PH0-005 (and related gate changes) | Approve technical gate implementation plan and CI wiring feasibility. | CI mapping references and gate execution notes. | Escalate CI reliability or branch-protection conflicts to `Maintainer Council`. |
| Maintainer Council | Final governance approver for boundary, override, and closeout decisions. | Reviewer on PH0-001, PH0-009 | Approve policy/contract overrides and final Phase 0 handoff acceptance. | Decision notes linked in closeout package. | Final escalation endpoint for unresolved Phase 0 governance disputes. |

## Operational Use

1. Fill role-to-individual mapping in `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md` before moving any Phase 0 ticket to `in_progress`.
2. Use this charter as the source of truth if role responsibility interpretation conflicts with ticket shorthand labels.
3. Update this charter via normal governance change flow when responsibilities materially change.

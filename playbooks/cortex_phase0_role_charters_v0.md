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

## Interim Solo-Maintainer Exception (Phase 0 Only)

Effective window:
- 2026-02-21 through 2026-03-08 (Phase 0 target window)

Exception:
- A single maintainer may temporarily hold owner and reviewer roles where a second maintainer is not yet assigned.

Compensating controls:
1. Ticket cannot move to `done` without explicit evidence links in the execution board.
2. Ticket must pass local governance gate checks before `done` (`audit --audit-scope all`, gap checks, quality gate command).
3. Ticket should remain at `review` for at least one working session before `done`.
4. Phase 1 gate elevation is blocked until `Maintainer Council` has at least two named maintainers.

## Phase 6 GDD Minimum Role + Capability Pack (PH6-005)

Purpose:
- provide a portable minimum role/capability contract for multi-agent bootstrap and governed delivery flows.

Minimum role set (required before external bootstrap pilots):

| Role | Minimum Coverage Rule |
|---|---|
| Program Lead | Owns sequencing, dependency arbitration, and closeout readiness. |
| Governance Policy Lead | Owns canonical policy language and authority semantics. |
| Governance Enforcement Lead | Owns gate mapping and blocking rule behavior. |
| Runtime Reliability Lead | Owns rollback, kill-switch, and fail-safe degradation criteria. |
| Delivery Operations Lead | Owns execution cadence and capacity throttling decisions. |
| Conformance QA Lead | Owns reproducibility checks and pass/fail evidence packaging. |
| Maintainer Council | Final authority for override approval and unresolved escalations. |

Command/capability matrix (minimum):

| Command Surface | Operator Role(s) | Approval Role(s) | Rule |
|---|---|---|---|
| `bootstrap-scaffold`, `init` | Delivery Operations Lead | Program Lead | Bootstrap execution cannot mark ticket `done` without QA evidence. |
| `audit-needed`, `audit` | Conformance QA Lead, Delivery Operations Lead | Governance Enforcement Lead | Audit failures are blocking for governance-impacting closeout. |
| `decision-capture`, `decision-promote` | Governance Policy Lead | Maintainer Council (for overrides) | Promotion authority remains canonical-governance scoped. |
| `reflection-scaffold` | Governance Enforcement Lead, Program Lead | Governance Policy Lead | Required when repeatable mistake patterns are detected. |
| `rollout-mode`, `rollout-mode-audit` | Runtime Reliability Lead | Maintainer Council (default activation/rollback exceptions) | Default-mode transitions require decision/reflection/audit linkage. |
| `quality_gate_v0.sh`, `quality_gate_ci_v0.sh` | Conformance QA Lead | Governance Enforcement Lead | Required gate bundle is mandatory before merge/release. |

Escalation matrix (minimum):

| Trigger | Initial Owner | Escalate To | SLA |
|---|---|---|---|
| Owner/reviewer deadlock on blocking finding | Program Lead | Maintainer Council | 1 working day |
| Gate failure with unclear policy interpretation | Governance Enforcement Lead | Governance Policy Lead then Maintainer Council | same working session |
| Rollback/kill-switch dispute | Runtime Reliability Lead | Maintainer Council | immediate |
| Capacity stop-rule breach or sustained overload | Delivery Operations Lead | Program Lead then Maintainer Council | 1 working day |
| Missing backup coverage for required role | Program Lead | Maintainer Council | before ticket moves to `in_progress` |

Coverage invariants for GDD operation:

1. Every active ticket must have distinct owner and reviewer unless an explicitly documented solo-maintainer exception is active.
2. Every required role must have a named backup before external pilot bootstrap work starts.
3. Capability grants are least-privilege by default and scoped to ticket needs.
4. Override approvals must be decision/reflection linked in canonical governance artifacts.

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

# Cortex Phase 1 Tactical Memory Command Contract Ticket Breakdown v0

Version: v0  
Status: Draft  
Date: 2026-02-23  
Scope: Phase 1 design ticket set for `cortex-coach` tactical memory command contracts

## Purpose

Open a contract-first Phase 1 ticket set so tactical memory features can be implemented behind experimental controls without weakening governance authority.

## Source Inputs

- `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_phase1_measurement_plan_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`

## Guardrails (Non-Negotiable)

- Governance plane remains authoritative; tactical outputs are non-authoritative until promoted.
- Phase 1 outputs stay behind experimental controls.
- Non-interactive command outputs must remain automatable (`--format text|json`).
- Determinism and locking must be explicit in contracts before implementation begins.
- Adapter behavior is out of Phase 1 scope (Phase 3).

## Execution Order

1. `PH1-001` common command contract baseline
2. `PH1-002` through `PH1-007` per-command contracts and shared storage semantics
3. `PH1-008` Gate B readiness and closeout package

## Execution Board

Status vocabulary:
- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

| Ticket | Title | Status | Owner (Suggested Role) | Primary Reviewer (Suggested Role) | Target Week | Target Date | Blockers | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PH1-001 | Tactical Memory Command Family Contract Baseline | done | Contract/Schema Lead | Governance Policy Lead | Week 2 | 2026-03-03 | PH0 complete | `contracts/tactical_memory_command_family_contract_v0.md`;`specs/cortex_project_coach_spec_v0.md`;`docs/cortex-coach/commands.md` | Shared CLI contract, error model, and output schemas baselined in canonical contract + spec/docs references. |
| PH1-002 | `memory-record` Contract + Record Schema | done | Contract/Schema Lead | Security & Data Policy Lead | Week 2 | 2026-03-05 | PH1-001 | `contracts/tactical_memory_record_schema_v0.json`;`specs/cortex_project_coach_spec_v0.md`;`policies/tactical_data_policy_v0.md` | Capture contract baseline includes required fields, sanitization/redaction semantics, deterministic unknown-field rejection, and write-lock expectations. |
| PH1-003 | `memory-search` Contract + Ranking Determinism | done | Runtime Reliability Lead | Contract/Schema Lead | Week 2 | 2026-03-07 | PH1-001 | `contracts/tactical_memory_search_result_schema_v0.json`;`specs/cortex_project_coach_spec_v0.md` | Retrieval query/filter semantics, deterministic tie-breakers, provenance/confidence fields, and machine-readable no-match payload are defined. |
| PH1-004 | `memory-prime` Contract + Budget Enforcement | done | Runtime Reliability Lead | Governance Enforcement Lead | Week 3 | 2026-03-10 | PH1-003 | `contracts/tactical_memory_prime_bundle_schema_v0.json`;`specs/cortex_project_coach_spec_v0.md` | Priming input/output contract, budget controls, and deterministic truncation/overflow semantics are defined. |
| PH1-005 | `memory-diff` + `memory-prune` Mutation Safety Contract | done | Governance Enforcement Lead | Security & Data Policy Lead | Week 3 | 2026-03-12 | PH1-001,PH1-002 | `contracts/tactical_memory_diff_schema_v0.json`;`contracts/tactical_memory_prune_schema_v0.json`;`specs/cortex_project_coach_spec_v0.md`;`policies/tactical_data_policy_v0.md` | Stable diff keys/output, prune eligibility+dry-run semantics, deterministic machine-readable outcomes, and lineage preservation are defined. |
| PH1-006 | `memory-promote` Governance Bridge Contract | done | Governance Enforcement Lead | Governance Policy Lead | Week 3 | 2026-03-14 | PH1-001,PH1-002,PH1-005 | `contracts/promotion_contract_schema_v0.json`;`specs/cortex_project_coach_spec_v0.md`;`docs/cortex-coach/commands.md` | Promotion output mapping, fail-closed bridge failure semantics, and non-governance separation are defined. |
| PH1-007 | Tactical Storage + Locking Determinism Contract | done | Runtime Reliability Lead | CI/Gate Owner | Week 4 | 2026-03-17 | PH1-002,PH1-005 | `specs/cortex_project_coach_spec_v0.md`;`docs/cortex-coach/quality-gate.md` | Lock acquisition/timeout/stale-lock behavior, concurrency expectations, idempotency semantics, and deterministic failure-recovery behavior are defined. |
| PH1-008 | Gate B Readiness Validation Pack (Design Exit) | todo | Conformance QA Lead | Maintainer Council | Week 4 | 2026-03-21 | PH1-001,PH1-002,PH1-003,PH1-004,PH1-005,PH1-006,PH1-007 | `tbd` | Contract test plan, docs plan, and implementation-ready checklist. |

## Tickets

### PH1-001: Tactical Memory Command Family Contract Baseline

Objective:
- Define one shared command contract baseline for tactical memory operations.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/commands.md`
- `contracts/` (new tactical memory contract files)

Acceptance criteria:
- Command list is explicit: `memory-record`, `memory-search`, `memory-prime`, `memory-diff`, `memory-prune`, `memory-promote`.
- Shared flags and behavior are explicit (`--project-dir`, `--format`, deterministic output and error semantics).
- JSON output contract requirements are documented for all non-interactive commands.
- Exit code semantics are documented for deterministic automation.

Evidence:
- `contracts/tactical_memory_command_family_contract_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/commands.md`

### PH1-002: `memory-record` Contract + Record Schema

Objective:
- Define normalized capture schema and invariants for tactical memory records.

Primary artifacts:
- `contracts/tactical_memory_record_schema_v0.json` (new)
- `specs/cortex_project_coach_spec_v0.md`
- `policies/tactical_data_policy_v0.md`

Acceptance criteria:
- Required fields are defined (record id, timestamp, source/provenance, content class, tags).
- Sanitization/redaction behavior is documented for disallowed content classes.
- Unknown/invalid fields are handled deterministically.
- Locking expectations for writes are explicit.

Evidence:
- `contracts/tactical_memory_record_schema_v0.json`
- `specs/cortex_project_coach_spec_v0.md`
- `policies/tactical_data_policy_v0.md`

### PH1-003: `memory-search` Contract + Ranking Determinism

Objective:
- Define deterministic retrieval semantics and ranking behavior for search.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `contracts/tactical_memory_search_result_schema_v0.json` (new)

Acceptance criteria:
- Query input and filter semantics are explicit.
- Ranking tie-breakers are deterministic and documented.
- Output fields include provenance and confidence.
- Empty/no-match behavior is deterministic and machine-readable.

Evidence:
- `contracts/tactical_memory_search_result_schema_v0.json`
- `specs/cortex_project_coach_spec_v0.md`

### PH1-004: `memory-prime` Contract + Budget Enforcement

Objective:
- Define bounded context priming behavior from tactical memory.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `contracts/tactical_memory_prime_bundle_schema_v0.json` (new)

Acceptance criteria:
- Inputs and output bundle shape are documented.
- Budget controls are explicit (record count, char budget, ordering policy).
- Truncation/overflow behavior is deterministic and auditable.
- Priming output references source records with provenance fields.

Evidence:
- `contracts/tactical_memory_prime_bundle_schema_v0.json`
- `specs/cortex_project_coach_spec_v0.md`

### PH1-005: `memory-diff` + `memory-prune` Mutation Safety Contract

Objective:
- Define safe mutation semantics for tactical memory maintenance.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `policies/tactical_data_policy_v0.md`
- `contracts/tactical_memory_diff_schema_v0.json` (new)
- `contracts/tactical_memory_prune_schema_v0.json` (new)

Acceptance criteria:
- Diff semantics define stable comparison keys and output structure.
- Prune policy defines eligibility rules (age/state/policy compliance) and dry-run behavior.
- Mutation outcomes are deterministic and machine-readable.
- Provenance lineage is retained across diff/prune operations.

Evidence:
- `contracts/tactical_memory_diff_schema_v0.json`
- `contracts/tactical_memory_prune_schema_v0.json`
- `specs/cortex_project_coach_spec_v0.md`
- `policies/tactical_data_policy_v0.md`

### PH1-006: `memory-promote` Governance Bridge Contract

Objective:
- Define bridge behavior from tactical memory evidence to canonical governance pathways.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `contracts/promotion_contract_schema_v0.json`
- `docs/cortex-coach/commands.md`

Acceptance criteria:
- `memory-promote` outputs map to decision/reflection/promotion-required fields.
- Governance-impacting promotions require explicit artifact linkage.
- Promotion failure modes are deterministic and fail closed for missing required evidence.
- Non-governance tactical outputs are clearly separated from promotion outputs.

Evidence:
- `contracts/promotion_contract_schema_v0.json`
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/commands.md`

### PH1-007: Tactical Storage + Locking Determinism Contract

Objective:
- Define storage and concurrency behavior before runtime implementation.

Primary artifacts:
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/quality-gate.md`

Acceptance criteria:
- Lock acquisition/timeout/stale-lock behavior is explicit.
- Concurrent read/write expectations are defined.
- Idempotency expectations for retries are explicit.
- Failure handling preserves integrity and deterministic recovery behavior.

Evidence:
- `specs/cortex_project_coach_spec_v0.md`
- `docs/cortex-coach/quality-gate.md`

### PH1-008: Gate B Readiness Validation Pack (Design Exit)

Objective:
- Produce the design-exit package required to begin implementation safely.

Primary artifacts:
- `.cortex/reports/project_state/` (new Phase 1 design closeout report)
- `playbooks/session_governance_hybrid_plan_v0.md`
- `docs/cortex-coach/commands.md`

Acceptance criteria:
- Each `PH1-001` to `PH1-007` ticket is marked `done` with evidence link.
- Gate B design checks are explicitly listed with pass/fail criteria.
- Test-plan skeleton exists for determinism, locking, and regression checks.
- Open risks/questions are owner-assigned and time-bounded.

Evidence:
- Published Phase 1 design closeout report under `.cortex/reports/project_state/`.

## Capacity Envelope (Phase 1, Option B)

Planning defaults (from synthesized proposal):
- `<= 3` five-hour windows/week
- `<= 8` cloud tasks/week
- `<= 6` code reviews/week

Adjustment rules:
- If weekly usage is `>= 80%` by Wednesday, cut to constrained mode for remaining sessions.
- If weekly lockout occurs, run stabilization-only week before new Phase 1 implementation starts.

## Definition of Done (Phase 1 Design Ticket Set)

This ticket set is complete when:

1. `PH1-001` through `PH1-008` are marked `done` with evidence links.
2. Gate B design readiness is documented with explicit pass/fail checks.
3. Command-contract artifacts are implementation-ready with no unresolved authority-boundary ambiguity.

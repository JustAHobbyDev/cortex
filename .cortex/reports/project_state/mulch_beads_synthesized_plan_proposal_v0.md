# Mulch + Beads Synthesized Plan Proposal v0

Date: 2026-02-21  
Status: Proposed  
Author: Cortex research synthesis

## Purpose

Define one actionable implementation proposal that synthesizes Mulch and Beads research into a coherent Cortex roadmap, while preserving Cortex’s governance-first architecture and ownership boundaries.

## Source Inputs

- `.cortex/reports/project_state/mulch_comparative_research_report_v0.md`
- `.cortex/reports/project_state/mulch_integration_strategy_report_v0.md`
- `.cortex/reports/project_state/beads_comparative_research_report_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`

## Strategic Thesis

- Keep Cortex as the canonical governance layer.
- Add a tactical execution/memory layer in `cortex-coach` for speed.
- Promote tactical signals into canonical artifacts through explicit governance gates.
- Integrate external work-graph state (for example Beads) through bounded read adapters first, not deep coupling.

## Target Operating Model

1. Governance Plane (authoritative)
- Canonical artifacts remain in `.cortex/` and existing governance dirs.
- Decision, reflection, audit, and contract checks remain release-gate authority.

2. Tactical Plane (non-authoritative until promoted)
- Fast capture/retrieval/priming workflows inspired by Mulch.
- Optional work-graph ingestion inspired by Beads for ready/blocked execution context.

3. Promotion Plane (bridge)
- Explicit promote path from tactical evidence into decisions/policies/specs.
- No governance-impacting closure without linked promoted decision/artifact coverage.

## Scope and Guardrails

1. Keep
- Governance-first philosophy from `README.md`.
- Runtime/governance ownership split from `policies/cortex_coach_final_ownership_boundary_v0.md`.
- Deterministic bounded context behavior.

2. Expand
- Explicitly allow tactical capture and retrieval in runtime.
- Add adapter-based ingestion for external work systems.
- Add promotion and evidence scoring workflows.

3. Do Not Do
- Do not turn Cortex into a general issue tracker.
- Do not let tactical state bypass decision/reflection/audit gates.
- Do not make external adapters mandatory in CI-critical governance paths.

## Capability Synthesis

1. Mulch-derived priorities
- Provider setup/onboarding recipes.
- Fast memory command set (`record/search/prime/diff/prune` equivalents).
- Ranked retrieval and budget-aware priming.

2. Beads-derived priorities
- Ready/blocked work-graph semantics via adapter.
- Session-close protocol output.
- Stronger performance and concurrency instrumentation discipline.

3. Shared insight
- Dual-loop workflow: fast execution during session, strict promotion + governance at closeout.

## Phased Plan Proposal

### Phase 0: Contract + Vision Update

Objective: formalize dual-plane model and boundaries before runtime changes.

Deliverables:
- Vision addendum for tactical plane + promotion rule.
- Coach spec delta for tactical scope and adapter interfaces.
- Policy language stating governance authority remains canonical.

Exit criteria:
- Updated spec/policy documents merged.
- No ambiguity on authoritative vs non-authoritative data.

### Phase 1: Tactical Memory Foundation (Mulch-first)

Objective: add fast tactical memory workflows in `cortex-coach`.

Deliverables:
- Experimental commands:
  - `memory-record`
  - `memory-search`
  - `memory-prime`
  - `memory-diff`
  - `memory-prune`
  - `memory-promote`
- Marker-based onboarding/setup recipes for agent environments.
- Command safety classes documented.

Exit criteria:
- Commands available behind experimental flag.
- Deterministic output contracts documented.
- Core tests added for determinism and locking behavior.

### Phase 2: Retrieval and Context Loader Upgrade

Objective: improve context quality without budget inflation.

Deliverables:
- Ranked retrieval in `context-load` (BM25-style + deterministic tie-breaks).
- Evidence/outcome weighting option.
- Compaction and stale-pruning policy for tactical records.

Exit criteria:
- Context utility improves in evaluation set.
- Budget regressions remain within target thresholds.

### Phase 3: Work-Graph Adapter (Beads-first, read-only)

Objective: enrich tactical context with execution-state signals.

Deliverables:
- Optional adapter to ingest bounded Beads signals (`ready`, `blocked`, top stale/high-priority).
- Timeout/circuit-breaker fallback to governance-only mode.
- Adapter result normalization into tactical context schema.

Exit criteria:
- No hard dependency on Beads for core coach operations.
- Adapter failure never blocks governance commands.

### Phase 4: Promotion and Enforcement Hardening

Objective: close the loop from tactical evidence to governance integrity.

Deliverables:
- Promotion assistant mapping tactical clusters to decision candidates.
- Rule: governance-impacting tactical closures require linked decision/artifact coverage.
- Reflection completeness integration with tactical promotion flow.

Exit criteria:
- Decision coverage and reflection completeness stable or improved.
- No increased governance regressions in CI.

### Phase 5: Performance Hardening and Rollout

Objective: default-on only after measured reliability and overhead targets are met.

Deliverables:
- Performance dashboards and thresholds.
- Rollout modes: `off`, `experimental`, `default`.
- Migration guide and operator playbook updates.

Exit criteria:
- SLO targets met for multiple cycles.
- Adoption metrics and gate reliability pass threshold.

## Phase Gates and Rollout Logic

1. Gate A (after Phase 0)
- Dual-plane governance language approved.
- Runtime boundary and schema versioning rules approved.

2. Gate B (after Phase 1)
- Experimental tactical commands pass determinism/locking tests.
- No regression in core governance command behavior.

3. Gate C (after Phase 2)
- Ranked retrieval shows measurable relevance gains.
- Context-size and latency budgets stay within target.

4. Gate D (after Phase 3)
- Adapter degradation paths verified (fail-open to governance-only mode).
- External dependency outages do not block mandatory governance workflows.

5. Gate E (after Phase 4)
- Promotion and decision/reflection link checks demonstrate stable coverage.
- Governance-impact tactical closures are correctly blocked when unlinked.

6. Gate F (after Phase 5)
- Two or more stable cycles with SLO compliance.
- Ready to move default mode from `experimental` to `default`.

## Codex Plus Capacity Model (Replaces Fixed Weekly Token Model)

There is no published fixed weekly token budget for Codex on ChatGPT Plus.  
Sequencing should be gated by the official 5-hour window limits, weekly code-review limits, and your live `/status` or dashboard usage.

1. Official planning constraints to use

| Metric | Official Limit Shape | Planning Baseline |
|---|---|---|
| Local messages | ~45-225 per 5-hour window | ~50-100 per 5-hour work window |
| Cloud tasks | ~10-60 per 5-hour window | ~15-30 per 5-hour work window |
| Code reviews | ~10-25 per week | Treat `10/week` as hard planning gate |

Notes:
- Local messages and cloud tasks share the same 5-hour window.
- Additional weekly limits may apply even when per-window usage looks safe.

2. Weekly capacity tiers for sequencing

| Tier | Weekly 5-hour Windows | Weekly Cloud Tasks (Large Repo) | Weekly Code Reviews |
|---|---:|---:|---:|
| Constrained | 2 | <= 5 | <= 4 |
| Balanced (Default) | 3 | <= 8 | <= 6 |
| Aggressive | 4 | <= 10 | <= 8 |

3. Dynamic gating rules
- If weekly usage is >= 80% by Wednesday, immediately drop to Constrained tier for the rest of that week.
- If weekly usage is <= 50% by Thursday, allow one additional focused implementation window.
- If weekly limit lockout occurs in any week, insert a stabilization week (testing/docs/gates only) before resuming normal phase progression.

4. Code-review hard gate
- Plan as if code reviews are capped at `10/week` even though the range may be higher.
- Do not schedule review-heavy milestones requiring >10 Codex reviews/week unless you explicitly plan paid overflow.

## Target Calendar (Capacity-Aware)

All calendars start Monday, February 23, 2026 and assume no emergency interruptions.

### Option A: Constrained Throughput (2 windows/week)

Target window: February 23, 2026 to July 12, 2026 (20 weeks)

| Weeks | Dates | Planned Focus |
|---|---|---|
| 1-2 | Feb 23-Mar 8 | Phase 0 |
| 3-7 | Mar 9-Apr 12 | Phase 1 |
| 8-11 | Apr 13-May 10 | Phase 2 |
| 12-15 | May 11-Jun 7 | Phase 3 |
| 16-18 | Jun 8-Jun 28 | Phase 4 |
| 19-20 | Jun 29-Jul 12 | Phase 5 + Gate F |

### Option B: Balanced Throughput (3 windows/week) (Recommended)

Target window: February 23, 2026 to May 31, 2026 (14 weeks)

| Weeks | Dates | Planned Focus |
|---|---|---|
| 1 | Feb 23-Mar 1 | Phase 0 |
| 2-4 | Mar 2-Mar 22 | Phase 1 |
| 5-7 | Mar 23-Apr 12 | Phase 2 |
| 8-10 | Apr 13-May 3 | Phase 3 |
| 11-12 | May 4-May 17 | Phase 4 |
| 13-14 | May 18-May 31 | Phase 5 + Gate F |

### Option C: Aggressive Throughput (4 windows/week)

Target window: February 23, 2026 to May 3, 2026 (10 weeks)

| Weeks | Dates | Planned Focus |
|---|---|---|
| 1 | Feb 23-Mar 1 | Phase 0 |
| 2-3 | Mar 2-Mar 15 | Phase 1 |
| 4-5 | Mar 16-Mar 29 | Phase 2 |
| 6-7 | Mar 30-Apr 12 | Phase 3 |
| 8-9 | Apr 13-Apr 26 | Phase 4 |
| 10 | Apr 27-May 3 | Phase 5 + Gate F |

### Calendar Selection Rule

1. Default to Option B for Week 1 and Week 2.
2. Promote to Option C only if both weeks finish with comfortable weekly headroom and no lockout signals.
3. Demote to Option A immediately if weekly usage pressure appears before mid-week.

## One-Page Operator Playbook (Preferred Tier: Option B)

This is the single operating playbook for execution unless you explicitly switch tiers.

Preferred tier:
- `Option B (Balanced)`
- Weekly default ceiling:
  - `<= 3` five-hour Codex work windows
  - `<= 8` cloud tasks touching large repos
  - `<= 6` Codex code reviews

| Phase | Calendar Weeks (Option B) | Weekly Window Cap | Weekly Cloud Task Cap | Weekly Code Review Cap | Primary Session Mix |
|---|---|---:|---:|---:|---|
| Phase 0 | Week 1 | <= 2 | <= 3 | <= 2 | Spec/policy drafting + boundary checks |
| Phase 1 | Weeks 2-4 | <= 3 | <= 8 | <= 6 | Implementation-heavy (memory commands + onboarding recipes) |
| Phase 2 | Weeks 5-7 | <= 3 | <= 7 | <= 5 | Retrieval/ranking implementation + eval loops |
| Phase 3 | Weeks 8-10 | <= 3 | <= 8 | <= 5 | Adapter implementation + fallback hardening |
| Phase 4 | Weeks 11-12 | <= 3 | <= 6 | <= 6 | Promotion/enforcement logic + governance validation |
| Phase 5 | Weeks 13-14 | <= 2 | <= 4 | <= 4 | Performance hardening, rollout checks, Gate F |

Execution guardrails:
1. If weekly usage reaches 80% before Thursday, cut that week to:
- `<= 2` windows, `<= 4` cloud tasks, `<= 3` reviews.
2. If any weekly lockout occurs, next week becomes stabilization-only:
- `<= 1` window, `<= 2` cloud tasks, `<= 2` reviews, no new phase starts.
3. Do not start the next phase until its prior gate (A-F) is passed.

## Weekly Capacity Allocation Guide

During active implementation weeks:
- 45% implementation sessions
- 20% test/fix sessions
- 20% design/spec/policy work
- 10% review/synthesis
- 5% contingency

During gate and stabilization weeks:
- 25% implementation
- 45% validation/testing
- 20% review/synthesis
- 10% contingency

## Performance Budget Proposal

1. Runtime latency
- `context-load` p95:
  - governance-only mode: <= 1.5s
  - with tactical plane only: <= 2.0s
  - with adapter enabled: <= 2.5s

2. CI overhead
- Mandatory governance pipeline runtime increase <= 10%.

3. Context size
- Tactical additions must remain inside explicit file/char budgets.
- Unrestricted fallback remains explicit and traceable.

4. Storage growth
- Tactical retention must include pruning/compaction policy.
- Canonical governance artifacts remain uncompacted source of truth.

## Ownership and Implementation Boundaries

1. `cortex` repo
- Owns policy/spec/contract updates and governance model evolution.

2. `cortex-coach` runtime
- Owns tactical commands, adapters, retrieval algorithms, and performance implementation.

3. Interface contract
- All tactical outputs consumed by governance checks must use versioned schemas.

## Success Metrics

1. Speed and usability
- Median commands per task decreases.
- Session-start overhead remains bounded.

2. Governance quality
- Decision-gap and reflection completeness pass rates stable or better.
- Unsynced decision failures do not increase.

3. Context quality
- Higher relevance scores from operator evaluations on context bundles.
- Lower stale/noise ratio in returned context.

4. Performance
- Meets latency and CI overhead budgets defined above.

## Immediate Next Actions

1. Execute Phase 0 ticket set in `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`.
2. Open a `cortex-coach` design ticket set for Phase 1 command contracts.
3. Define adapter interface spec for Phase 3 (read-only Beads integration).
4. Add a measurement plan doc before feature implementation begins.

## Recommendation

Proceed with Phase 0 immediately and treat this as an expansion of Cortex vision, not a pivot.  
Adopt Mulch-inspired tactical memory first, then Beads-inspired work-graph adapter, with promotion and governance enforcement as non-negotiable control gates.

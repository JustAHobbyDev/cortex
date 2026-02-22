# Mulch-Informed Cortex Integration Strategy Report v0

Date: 2026-02-21
Status: Proposed

## Purpose

Define how to incorporate high-value ideas identified in the Mulch comparison while preserving Cortex governance integrity, ownership boundaries, and performance posture.

## Source Artifact

- Primary source: `.cortex/reports/project_state/mulch_comparative_research_report_v0.md`

## Strategic Conclusion

- Keep Cortex vision core unchanged: governance-first, artifact-based operating memory.
- Expand the operating model to a two-plane design:
  - Governance Plane (canonical, enforced, durable)
  - Working Memory Plane (fast tactical capture/retrieval, promotion-driven)

This is an expansion of current vision, not a replacement.

## Alignment With Current Cortex Design

### Fits Well

- Vision already targets fast onboarding, low overhead, and durable cross-session learning.
- Agent-oriented preflight and workflow compression are already on roadmap.
- Ownership boundary already places runtime feature work in `cortex-coach`.

### Requires Explicit Contract Evolution

- Current coach spec constrains mutation to `.cortex/` and excludes multi-user conflict resolution as v0 concerns.
- Working memory and richer onboarding integrations should be added as explicit v1+ contract/scope evolution, not implicit behavior drift.

## Proposed Capability Additions

1. Working memory commands in `cortex-coach` runtime (experimental first):
- `memory-record`
- `memory-search`
- `memory-prime`
- `memory-diff`
- `memory-prune`
- `memory-promote`

2. Optional agent setup/onboarding support:
- Provider-aware snippet/hook install/check/remove.
- Marker-based idempotent updates for `AGENTS.md` / `CLAUDE.md`.

3. Retrieval improvements in context loading:
- Ranked retrieval (BM25-style) with deterministic tie-breakers.
- Budget-preserving prioritization and bounded output.

4. Memory safety/operability model:
- Explicit command safety classes in docs.
- Per-domain/file lock model for memory writes.
- Global lock retained for governance mutations.

## Optimal Usage Shift (Cortex Suite)

Current usage emphasizes periodic governance checks.
Target usage becomes dual-loop:

1. Session start:
- run preflight
- load governance-first context + ranked working-memory slice

2. During implementation:
- fast working-memory capture/search

3. Before merge/release:
- promote qualifying memory into governance artifacts
- run existing governance checks (decision/reflection/audit/gate)

Result:
- better in-session recall and speed
- unchanged governance strictness at release boundaries

## Vision Impact

### Keep

- Artifact-based governance authority
- Decision/reflection/audit enforceability
- Clear runtime vs governance ownership split

### Expand

Add explicit dual-plane statement to vision:
- tactical memory may be captured quickly
- canonical memory is governance artifacts, reached via promotion

Add guardrail:
- no tactical memory path may bypass decision/reflection governance gates when impact is governance-relevant

## Performance Implications and Controls

1. Retrieval cost growth
- Risk: BM25 ranking overhead as memory volume increases
- Control: index/cache with mtime invalidation and deterministic fallback ordering

2. Lock contention
- Risk: write throughput bottlenecks if all writes use one lock
- Control: per-domain/file locks for working-memory writes; preserve global governance lock

3. Context inflation
- Risk: larger payloads, reduced signal
- Control: strict budgets, classification/type priorities, stale-record pruning, compaction

4. CI/runtime overhead
- Risk: slower gates if memory checks enter critical path
- Control: keep governance checks mandatory; place deep memory-health checks in optional/nightly lanes unless flagged

5. Repository growth
- Risk: append-heavy memory artifacts increase repo weight
- Control: scheduled compaction, TTL for low-value tactical records, promotion/archive workflows

## Recommended Delivery Sequence

1. Contract and vision updates (spec/policy text only).
2. Experimental memory plane in `cortex-coach` runtime.
3. Promotion gates and governance linkage rules.
4. Performance instrumentation and thresholds.
5. Default-on only after reliability and overhead targets are met.

## Acceptance Signals

- Onboarding time decreases without reduced governance pass rates.
- Decision coverage and reflection completeness remain stable or improve.
- Median command burden per task decreases.
- Context bundle usefulness increases without budget regressions.
- CI duration remains within agreed threshold after rollout.

## Referenced Cortex Artifacts

- `playbooks/cortex_vision_master_roadmap_v1.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`
- `specs/cortex_project_coach_spec_v0.md`
- `specs/agent_context_loader_spec_v0.md`
- `playbooks/session_governance_hybrid_plan_v0.md`

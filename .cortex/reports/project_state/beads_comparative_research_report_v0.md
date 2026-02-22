# Beads vs Cortex Comparative Research Report v0

Date: 2026-02-21  
Author: Cortex research synthesis  
Status: Complete

## Scope

Deep comparative review of `steveyegge/beads` against current Cortex + installed `cortex-coach`, focusing on:

- What Beads does better
- What Cortex does better
- What ideas should be adopted into Cortex
- What new ideas Beads inspires for Cortex direction
- Alignment and performance implications

## Baseline Reviewed

- Beads repo: `https://github.com/steveyegge/beads`
  - Reviewed at commit `c210d421fad5074f129ef5418a997a963d940a4f` (2026-02-21)
- Cortex repo:
  - Reviewed at commit `e4d7604bee38433a7fd115fad5d1a99899749689` (2026-02-21)
- Installed standalone coach runtime:
  - `cortex-coach` version `0.1.0`
  - Source inspected under `/home/d/.local/share/uv/tools/cortex-coach/lib/python3.12/site-packages/cortex_coach/`

## Executive Summary

- Beads is materially stronger as an operational work graph and multi-agent execution substrate.
- Cortex is materially stronger as a governance operating layer with explicit decision/reflection/contract enforcement.
- Best strategic move is not to replicate Beads inside Cortex, but to add a bounded work-memory/work-graph bridge into `cortex-coach` with strict promotion rules into canonical Cortex artifacts.

## What Beads Does Better

1. Operational work graph and execution semantics
- Ready/blocked workflows are first-class (`bd ready`, `bd blocked`, dependencies, atomic claim).
- Atomic claim behavior is implemented with compare-and-swap semantics in storage (`internal/storage/dolt/issues.go`).
- Molecule/wisp/pour/squash/burn model supports persistent vs ephemeral execution workflows (`docs/MOLECULES.md`, `docs/CLI_REFERENCE.md`).

2. Multi-agent and distributed collaboration mechanics
- Hash-based IDs with adaptive length and collision math are explicit (`internal/idgen/hash.go`, `internal/storage/dolt/adaptive_length.go`, `docs/COLLISION_MATH.md`).
- Native Dolt commit/push/pull flows and batch commit mode are implemented (`internal/storage/dolt/store.go`, `cmd/bd/dolt_autocommit.go`).
- Multi-repo and workspace routing are deeply considered in MCP integration docs and tooling (`integrations/beads-mcp/README.md`).

3. Integration ergonomics for coding-agent environments
- Setup/onboarding is provider-oriented and operational (`cmd/bd/setup.go`, `cmd/bd/onboard.go`, `cmd/bd/prime.go`).
- The platform gives explicit “session-close protocol” behavior via `bd prime` and hooks.

4. Performance and concurrency engineering depth
- Large dedicated concurrency suite in storage layer (`internal/storage/dolt/concurrent_test.go`).
- Dedicated benchmark suite for cold/warm path and query/workflow behavior (`internal/storage/dolt/dolt_benchmark_test.go`, `BENCHMARKS.md`).
- Retry/lock behavior is explicit for transient DB/network conditions (`internal/storage/dolt/store.go`, `internal/storage/dolt/access_lock.go`).

5. Ecosystem scale and breadth
- CLI and feature surface is much broader (97 top-level command registrations in `cmd/bd/*.go`).
- Codebase has significantly larger runtime/test surface (Go-heavy implementation with deep domain modules and integrations).

## What Cortex Does Better

1. Governance enforceability and lifecycle control
- Explicit decision lifecycle: capture, promote, list, and gap checking (`cortex_coach/coach.py` decision commands).
- Reflection completeness enforcement exists as a dedicated integrity check (`reflection-completeness-check`).
- Contract conformance checks are explicit and artifact-contract driven (`contract-check`).

2. Governance-grade audit model
- Audit covers lifecycle artifact existence, schema validation, spec coverage, conformance, and unsynced decisions (`compute_audit_report` in `cortex_coach/coach.py`).
- Decision-gap checking ties dirty governance-impact files to explicit decision records (`compute_decision_gap_check`).

3. Deterministic bounded context strategy
- Control-plane-first context bundling with deterministic fallback ladder (restricted -> relaxed -> unrestricted) is implemented (`cortex_coach/agent_context_loader.py`).
- This directly aligns with Cortex’s anti-entropy philosophy and minimal-context discipline (`README.md`, `specs/agent_context_loader_spec_v0.md`).

4. Philosophy and scope clarity
- Cortex is explicit about being a high-signal governance layer, not a general work log (`README.md`).
- Ownership boundary is explicit (`policies/cortex_coach_final_ownership_boundary_v0.md`), reducing architectural ambiguity.

5. Lower cognitive load for governance tasks
- Command surface is much smaller and focused on governance lifecycle vs broad work-tracker operations.

## Key Comparative Insight

Beads and Cortex are not direct substitutes:

- Beads optimizes for execution throughput and distributed task memory.
- Cortex optimizes for governance integrity and durable reasoning artifacts.

The strongest combined model is complementary, not replacement.

## Notable Risks Observed in Beads (Relevant to Cortex Adoption Decisions)

1. Documentation/runtime drift risk
- Beads docs still describe older daemon/auto-flush internals (`docs/ARCHITECTURE.md`, `docs/INTERNALS.md`) while current code/release notes show significant architecture evolution (for example daemon removal paths in `cmd/bd/info.go` and sync behavior in `cmd/bd/sync.go`).
- This is manageable but increases operator model complexity.

2. Command-surface complexity
- Very large CLI surface area creates discoverability and consistency pressure (also acknowledged in Beads’ own agent guidelines around command sprawl).

3. Runtime complexity overhead
- Rich distributed behavior and sync modes increase maintenance and operational burden compared with Cortex’s current narrower governance contract.

## Ideas That Should Be Implemented into Cortex

1. Add a work-graph adapter plane (read-first, bounded)
- Add optional `cortex-coach` integration that can read current tactical work state from Beads (`bd ... --json`) without making Cortex itself a task tracker.
- Feed only bounded slices into `context-load` (for example top ready items + blockers + critical stale).

2. Add promotion bridge from tactical work to governance artifacts
- New helper path: create/augment decision candidates from selected tactical work items.
- Enforce that no governance-relevant work is “done” unless linked artifacts/decisions are present (Cortex already has primitives for this).

3. Add explicit session-close protocol command in `cortex-coach`
- Inspired by `bd prime`: one concise command emitting a deterministic closeout checklist tied to audit-needed + decision-gap + reflection completeness.

4. Add integration recipe system for agent environments
- Lightweight install/check/remove recipe framework similar to `bd setup` for injecting Cortex guidance into `AGENTS.md`, Copilot docs, and other IDE-specific locations.

5. Add benchmarked performance envelope for core governance paths
- Introduce explicit benchmark baselines for `audit`, `context-load`, and decision checks (latency and output-size budgets).

## New Ideas Beads Inspires for Cortex

1. Ephemeral-to-canonical lifecycle for governance signals
- Beads’ wisp/squash pattern suggests a Cortex pattern:
  - ephemeral reflection/work observations -> reviewed digest -> promoted decision/policy artifact.

2. Evidence-weighted promotion priority
- Use frequency/recurrence from tactical work history to prioritize which reflections/decisions should be promoted first.

3. Governance-aware work graph views
- Add derived governance views: “ready governance actions,” “blocked governance actions,” and “governance debt queue” by linking tactical work with missing policy/spec/decision artifacts.

4. Context compaction classes
- Borrow Beads’ compacting mindset for long-running Cortex reports: compress stale low-signal operational reports while preserving canonical governance artifacts.

## Alignment with Current Cortex Vision and Plan

Assessment against current artifacts (`playbooks/cortex_vision_master_roadmap_v1.md`, `specs/cortex_project_coach_spec_v0.md`, `policies/cortex_coach_final_ownership_boundary_v0.md`):

- Core vision should remain intact: governance-first, artifact-based memory.
- Vision should be expanded (not replaced) with a dual-plane model:
  - Governance Plane: canonical Cortex artifacts (authoritative)
  - Tactical Work Plane: fast operational memory/work graph (non-authoritative until promoted)
- Ownership boundary remains valid:
  - Any runtime integration should live in standalone `cortex-coach` runtime.
  - Cortex repo remains contract/policy/spec source of truth.

## Performance Implications for Cortex if These Ideas Are Adopted

1. Context-load cost growth
- Risk: pulling tactical work data inflates context bundles and compute cost.
- Control: strict caps, ranking, deterministic truncation, and opt-in flags.

2. External tool latency coupling
- Risk: `context-load` becomes dependent on external `bd` invocation timing/failures.
- Control: adapter timeouts, cached snapshots, graceful fallback to governance-only mode.

3. Lock/contention overhead
- Risk: additional mutable tactical stores can increase contention.
- Control: keep tactical store external (adapter first) and avoid broadening `.cortex` lock scope.

4. Audit runtime inflation
- Risk: blending tactical checks into mandatory governance audit slows CI.
- Control: keep governance checks mandatory; tactical-health checks advisory or separately staged.

## Recommended Implementation Sequence

1. Define dual-plane extension in Cortex vision/policy text without weakening governance authority.
2. Implement read-only Beads adapter in `cortex-coach` for `context-load` enrichment.
3. Add promotion bridge commands from tactical work -> decision candidate/reflection artifacts.
4. Add performance budgets and benchmark instrumentation.
5. Evaluate default-on only after bounded latency and signal-quality targets are met.

## Source References

- Beads:
  - `https://github.com/steveyegge/beads`
  - `/tmp/beads/README.md`
  - `/tmp/beads/docs/ARCHITECTURE.md`
  - `/tmp/beads/docs/CLI_REFERENCE.md`
  - `/tmp/beads/docs/MOLECULES.md`
  - `/tmp/beads/BENCHMARKS.md`
  - `/tmp/beads/cmd/bd/sync.go`
  - `/tmp/beads/cmd/bd/setup.go`
  - `/tmp/beads/cmd/bd/prime.go`
  - `/tmp/beads/internal/storage/dolt/store.go`
  - `/tmp/beads/internal/storage/dolt/issues.go`
  - `/tmp/beads/internal/storage/dolt/queries.go`
  - `/tmp/beads/internal/storage/dolt/adaptive_length.go`
  - `/tmp/beads/internal/idgen/hash.go`
  - `/tmp/beads/integrations/beads-mcp/README.md`
  - `/tmp/beads/cmd/bd/info.go`

- Cortex:
  - `/home/d/codex/cortex/README.md`
  - `/home/d/codex/cortex/playbooks/cortex_vision_master_roadmap_v1.md`
  - `/home/d/codex/cortex/policies/cortex_coach_final_ownership_boundary_v0.md`
  - `/home/d/codex/cortex/specs/cortex_project_coach_spec_v0.md`
  - `/home/d/codex/cortex/specs/agent_context_loader_spec_v0.md`
  - `/home/d/codex/cortex/playbooks/session_governance_hybrid_plan_v0.md`
  - `/home/d/codex/cortex/docs/cortex-coach/commands.md`
  - `/home/d/.local/share/uv/tools/cortex-coach/lib/python3.12/site-packages/cortex_coach/coach.py`
  - `/home/d/.local/share/uv/tools/cortex-coach/lib/python3.12/site-packages/cortex_coach/agent_context_loader.py`

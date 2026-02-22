# Mulch vs Cortex Comparative Research Report v0

Date: 2026-02-21
Author: Cortex research synthesis
Status: Complete

## Scope

Compare `jayminwest/mulch` against Cortex/Cortex Coach, identify relative strengths, and extract implementable ideas for Cortex.

## Baseline Reviewed

- Mulch repo: `https://github.com/jayminwest/mulch`
  - Reviewed at commit `dbff654a7fe771406d32e82ac6511a7aa7a4a057` (2026-02-20)
- Cortex Coach standalone repo: `https://github.com/JustAHobbyDev/cortex-coach`
  - Reviewed at commit `bc737f0462fbae5d1e568f5e6854c388f6eccf6c` (2026-02-20)
- This Cortex repo:
  - Reviewed at commit `749c5783bf41a37d979a87ef5d85dbb6871737b5` (2026-02-21)

## Executive Summary

- Mulch is stronger as an operational memory CLI for high-velocity capture, retrieval, and agent onboarding.
- Cortex is stronger as a governance and lifecycle operating system with explicit policy, audit, and decision traceability.
- Recommended direction: keep Cortex governance strict, add a Mulch-like fast memory plane that can be promoted into durable Cortex artifacts.

## What Mulch Does Better

1. Day-1 ergonomics and agent integration
- Broad provider integration (`claude`, `cursor`, `codex`, `gemini`, `windsurf`, `aider`) via `setup`.
- Marker-based onboarding snippets for `AGENTS.md`/`CLAUDE.md`, idempotent install/check/remove behavior.

2. Memory operations breadth
- Strong command surface for practical memory workflows:
  `record`, `edit`, `delete`, `query`, `search`, `prime`, `compact`, `prune`, `diff`, `learn`, `ready`, `sync`.

3. Retrieval quality for memory use-cases
- BM25 ranking for search relevance.
- Outcome-aware scoring and sort options for confirmation-frequency weighting.
- Token-budgeted priming output with deterministic prioritization.

4. Multi-agent memory concurrency posture
- File-level lock strategy with stale lock handling and retry.
- Atomic temp-write + rename to reduce corruption risk.
- `.gitattributes` union merge strategy for JSONL memory files.

5. Library usability
- Exposes a high-level programmatic API (`recordExpertise`, `searchExpertise`, `queryDomain`, `editRecord`) in addition to CLI.

## What Cortex Does Better

1. Governance discipline and traceability
- Decision lifecycle: capture, promote, list, and enforce linkage.
- Dedicated checks for governance gaps and reflection completeness.
- Explicit policy enablement and operating-model enforcement.

2. Audit and conformance depth
- Audits include spec coverage, artifact conformance, unsynced decisions, and schema checks.
- Contract-check command for compatibility against asset contract.

3. Safety posture for high-risk changes
- `audit-needed` with risk-tiered decisioning and fail-on-required CI behavior.
- Deterministic quality-gate framing around governance checks and test suite.

4. Control-plane context strategy
- Context loader prioritizes control-plane artifacts and active decisions before task slice.
- Fallback ladder (restricted -> relaxed -> unrestricted) for bounded context reliability.

5. Philosophy and boundary rigor
- Clear anti-entropy boundary: Cortex is a reasoning layer, not a raw note archive.
- Stronger long-horizon artifact curation standards than generic memory accumulation.

## Ideas To Implement Into Cortex

1. Add provider `setup` integrations in `cortex-coach`
- Install/check/remove hooks/snippets for agent environments and docs files.

2. Add marker-based `onboard` command
- Generate/update bounded, idempotent snippets in `AGENTS.md` and `CLAUDE.md`.

3. Add memory change workflow commands
- Mulch-inspired `learn`/`ready`/`diff` equivalents scoped to Cortex memory artifacts.

4. Add ranked retrieval for context loading
- BM25-style retrieval and optional outcome-weighting inside `context-load`.

5. Add explicit command safety classes in docs
- Document read-only vs locked-write vs setup-serialized commands for operator clarity.

## New Directions Inspired For Cortex

1. Two-plane architecture
- Governance Plane (existing strict Cortex artifacts/checks).
- Working Memory Plane (fast, tactical, agent-captured memory with stronger retrieval ergonomics).

2. Promotion pipeline
- Repeated/validated tactical memory can be promoted into decisions, policies, playbooks, and specs.

3. Confidence-aware governance
- Use evidence and outcomes to prioritize what is promoted, audited, or deprecated.

## Source Links

- Mulch:
  - `https://github.com/jayminwest/mulch`
  - `https://github.com/jayminwest/mulch/blob/main/README.md`
- Cortex Coach:
  - `https://github.com/JustAHobbyDev/cortex-coach`
  - `https://github.com/JustAHobbyDev/cortex-coach/blob/main/cortex_coach/coach.py`
  - `https://github.com/JustAHobbyDev/cortex-coach/blob/main/cortex_coach/agent_context_loader.py`
  - `https://github.com/JustAHobbyDev/cortex-coach/blob/main/docs/cortex-coach/commands.md`


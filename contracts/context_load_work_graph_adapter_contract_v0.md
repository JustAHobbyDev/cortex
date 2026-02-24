# Context-Load Work-Graph Adapter Contract v0

Canonical: true

Version: v0  
Status: Draft  
Scope: Phase 3 external work-graph adapter baseline contract for `context-load`

## Purpose

Define deterministic, read-only adapter ingestion semantics so `context-load` can enrich tactical context without introducing governance dependency on external systems.

## Contract Sources

- `playbooks/cortex_phase3_work_graph_adapter_ticket_breakdown_v0.md`
- `playbooks/cortex_phase3_measurement_plan_v0.md`
- `.cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json`
- `specs/agent_context_loader_spec_v0.md`

## Input Contract Baseline

Required:
- `task`
- `project_dir`

Optional (Phase 3 baseline):
- `adapter_mode` (`off`, `beads_file`; default: `off`)
- `adapter_file` (required when `adapter_mode=beads_file`)
- `adapter_max_items` (bounded integer, default contract baseline: `4`)
- `adapter_stale_seconds` (bounded integer threshold for freshness warnings)
- existing retrieval controls (`retrieval_profile`, `weighting_mode`, file/char budgets)

## Adapter Safety Requirements

- Adapter ingestion is opt-in and read-only.
- Adapter ingestion must not mutate governance artifacts.
- Adapter failures (missing file, decode error, stale metadata, timeout-equivalent failure) must fail open:
  - continue producing governance control-plane + task slice output.
- Mandatory governance commands (`audit`, `decision-gap-check`, reflection enforcement) must not depend on adapter health.

## Candidate Assembly and Ordering

- Adapter slice is appended after control-plane and task slices.
- Adapter candidate ordering must be deterministic with fixed tie-break chain:
  1. `combined_score_desc`
  2. `state_priority_asc`
  3. `priority_asc`
  4. `source_updated_at_desc`
  5. `path_asc`

No runtime-randomized ordering is allowed.

## Output Contract Baseline

`context-load` JSON payload must include:
- top-level `adapter` metadata object:
  - `mode`
  - `status` (`disabled`, `loaded`, `degraded`)
  - `adapter_id` (when available)
  - `candidate_count`
  - `selected_count`
  - `max_items`
  - `stale_threshold_seconds`
- per adapter-selected entry:
  - `selected_by` prefixed with `adapter:`
  - provenance with `source_kind=adapter_signal`
  - normalized adapter metadata (`adapter_id`, `item_id`, `state`, freshness fields when available)
  - bounded confidence and deterministic score breakdown fields

## Freshness and Warning Semantics

- Adapter metadata should include `adapter_fetched_at` and `source_updated_at` when available.
- Runtime should derive `staleness_seconds` when both timestamps are parseable.
- Missing/invalid freshness fields must emit deterministic warning classes.
- Staleness above `adapter_stale_seconds` threshold must emit deterministic stale-warning classes.

## Budget and Fallback Requirements

- Adapter slice must respect configured context budgets before output emission.
- Adapter failures must not force unrestricted fallback when governance+task slices already satisfy bundle success.
- Fallback metadata remains deterministic (`restricted -> relaxed -> unrestricted` when enabled).

## Fixture Freeze Binding

Gate D evaluation must use:
- `.cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json`

Any fixture profile/scenario change requires:
1. fixture version bump, and
2. explicit baseline reset note in Gate D closeout artifact.

# Context-Load Retrieval Contract v0

Canonical: true

Version: v0
Status: Draft
Scope: Phase 2 retrieval and context quality baseline contract for `context-load`

## Purpose

Define deterministic retrieval/ranking semantics for `context-load` so context quality can improve without budget inflation or governance ambiguity.

## Contract Sources

- `playbooks/cortex_phase2_retrieval_context_ticket_breakdown_v0.md`
- `playbooks/cortex_phase2_measurement_plan_v0.md`
- `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`

## Input Contract Baseline

Required:
- `task` (non-empty context objective string)
- `project_dir`

Optional (Phase 2 baseline):
- `retrieval_profile` (`small`, `medium`, `large`; default: `medium`)
- `weighting_mode` (`uniform`, `evidence_outcome_bias`; default: `uniform`)
- existing context budget controls (`max_files`, `max_chars_per_file`, fallback settings)

## Candidate Assembly

Candidate pool may include:
- canonical governance context files
- tactical memory retrieval candidates

Candidate assembly must be deterministic for identical repository state and inputs.

## Scoring Model Baseline

Each candidate exposes normalized component scores in `[0.0, 1.0]`:
- `lexical_score`
- `evidence_score`
- `outcome_score`
- `freshness_score`

Combined score:
- `combined_score = (w_lexical * lexical_score) + (w_evidence * evidence_score) + (w_outcome * outcome_score) + (w_freshness * freshness_score)`
- weight values must be deterministic per `weighting_mode`

Default weighting presets:
- `uniform`: `w_lexical=0.55`, `w_evidence=0.20`, `w_outcome=0.15`, `w_freshness=0.10`
- `evidence_outcome_bias`: `w_lexical=0.40`, `w_evidence=0.30`, `w_outcome=0.20`, `w_freshness=0.10`

## Deterministic Ordering and Tie-Break Rules

Ranking order must be deterministic with fixed tie-break chain:
1. `combined_score_desc`
2. `evidence_score_desc`
3. `captured_at_desc`
4. `source_path_asc`
5. `record_id_asc`

No runtime-randomized ordering is allowed.

## Budget and Fallback Requirements

- Ranked selection must honor configured budget controls before emitting bundle output.
- Fallback sequence remains deterministic and traceable (`restricted -> relaxed -> unrestricted` when enabled).
- Overflow/truncation must include machine-readable metadata for dropped candidates.

## Output Contract Baseline

`context-load` JSON result payload must include:
- `ranking_contract_version` (`v0`)
- `retrieval_profile`
- `weighting_mode`
- `selected_count`
- per-entry `score_breakdown` (`lexical_score`, `evidence_score`, `outcome_score`, `freshness_score`, `combined_score`)
- per-entry provenance references and bounded confidence metadata

No-match output must preserve stable shape with explicit reason fields.

## Safety and Authority Constraints

- Retrieval output is tactical and non-authoritative until promoted.
- `context-load` retrieval must not mutate canonical governance artifacts.
- Missing required ranking metadata in JSON mode is contract-invalid.

## Fixture Freeze Binding

Gate C evaluation must use the frozen fixture artifact:
- `.cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json`

Any fixture profile/query change requires:
1. a version bump to fixture artifact id, and
2. explicit baseline reset note in Gate C measurement closeout.

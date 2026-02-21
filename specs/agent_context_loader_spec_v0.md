# Agent Context Loader Spec

Version: v0  
Status: Experimental (Governance-Amended)  
Inputs:
- `.cortex/manifest_v0.json` lifecycle control artifact
- `.cortex/reports/lifecycle_audit_v0.json` latest health status
- `.cortex/reports/audit_needed_v0.json` optional dirty-state risk signal
- `.cortex/reports/decision_candidates_v0.json` decision linkage state
- `specs/spec_spec_v0.md` repository spec governance contract
- `philosophy/ontology_architecture_map_v0.md` layered architecture alignment
- `scripts/agent_context_loader_v0.py` deterministic loader implementation

## Purpose

Define a deterministic retrieval policy so agents unfamiliar with both project and Cortex can consume only necessary artifacts while staying within strict context budgets, while safely incorporating optional tactical and adapter-derived signals.

## Scope

- In scope:
  - staged loading order (governance control-plane first, then task slice)
  - deterministic file selection and truncation
  - bounded output contract for downstream agent prompts
  - optional tactical/context adapter ingestion under bounded budgets
- Out of scope:
  - semantic correctness of project code
  - domain-specific reasoning quality beyond retrieval policy
  - making tactical/adapter data authoritative over governance artifacts

## Core Definitions

- `Control Plane`: minimal governance artifacts needed to ground agent state (`manifest`, audit reports, decision state).
- `Task Slice`: additional files selected by task intent (for example direction/governance/design/spec).
- `Tactical Slice`: optional tactical memory/work signals, non-authoritative by default.
- `Adapter Slice`: optional external adapter payloads (for example read-only work-graph summaries).
- `Context Budget`: max files/chars the loader may emit.
- `Budget Partition`: explicit per-slice allocation so control-plane precedence is preserved.
- `Bundle`: machine-readable output containing selected files/excerpts plus selection provenance.

## Determinism and Drift Tests

- Ordering determinism: control-plane files are always listed first in fixed order.
- Selection determinism: task keywords map to fixed include patterns.
- Fallback determinism: fallback levels and attempt metadata are stable for identical inputs.
- Truncation determinism: excerpts are hard-limited by `max_chars_per_file`.
- Repeat-run drift test: same repo state + same args => byte-identical normalized JSON output.
- Source merge determinism: when tactical/adapter slices are enabled, tie-breakers are deterministic.

## Governance Rules

### Canonical-First Rule

- Governance control-plane selection always precedes tactical/adapter slices.
- Tactical/adapter slices cannot suppress or overwrite governance selections.

### Budget-First Rule

- Loader must stop adding files when configured limits are reached.
- Tactical/adapter slices consume only their allocated partitions unless unrestricted fallback is explicitly triggered.

### Minimal Context Rule

- No recursive bulk ingestion outside selected patterns and configured adapters.
- No implicit historical sweeps by default.

### Provenance Rule

- Output must include `selected_by` and source class (`control_plane`, `task`, `tactical`, `adapter`).
- Adapter-derived fields must include adapter identifier and freshness metadata.

### Safety Rule

- Tactical/adapter payloads must be sanitized for prohibited content classes before inclusion.
- On sanitization failure, drop unsafe entries and emit warnings.

### Degradation Rule

- Adapter failures/timeouts must degrade to governance-only + task slices.
- Degradation must be explicit in warnings and fallback metadata.

## Failure Modes

- Over-selection causing token overflow.
- Under-selection causing missing task-critical artifacts.
- Non-deterministic ordering due to unsorted enumeration.
- Adapter stall inflates latency and blocks context generation.
- Tactical/adapter payload introduces unsafe content.
- Excessive tactical inclusion dilutes governance signal.

## Success Criteria (v0)

- Loader exists at `scripts/agent_context_loader_v0.py`.
- Output JSON includes:
  - control-plane status
  - selected file list
  - bounded excerpts
  - warnings and truncation markers
  - fallback metadata
  - source provenance metadata
- Task-focused selection works for `direction`, `governance`, `design`, `spec` keyword intents.
- Governance-only degradation works when tactical/adapter inputs are unavailable or disabled.

## Immediate Next Step

Add explicit budget partition fields and source-class provenance to emitted bundles, then wire adapter/tactical slices behind opt-in runtime flags.

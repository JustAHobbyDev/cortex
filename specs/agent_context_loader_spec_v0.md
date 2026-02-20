# Agent Context Loader Spec

Version: v0
Status: Experimental
Inputs:
- `.cortex/manifest_v0.json` lifecycle control artifact
- `.cortex/reports/lifecycle_audit_v0.json` latest health status
- `.cortex/reports/audit_needed_v0.json` optional dirty-state risk signal
- `specs/spec_spec_v0.md` repository spec governance contract
- `philosophy/ontology_architecture_map_v0.md` layered architecture alignment
- `scripts/agent_context_loader_v0.py` deterministic loader implementation

## Purpose
Define a deterministic retrieval policy so agents unfamiliar with both project and Cortex can consume only necessary artifacts while staying within strict context budgets.

## Scope
- In scope:
  - staged loading order (control-plane first, then task slice)
  - deterministic file selection and truncation
  - bounded output contract for downstream agent prompts
- Out of scope:
  - semantic correctness of project code
  - domain-specific reasoning quality beyond retrieval policy

## Core Definitions
- `Control Plane`: minimal lifecycle artifacts needed to ground agent state (`manifest`, latest audit reports).
- `Task Slice`: additional files selected by task intent (for example direction/governance/design/spec).
- `Context Budget`: max files and max characters the loader may emit.
- `Bundle`: machine-readable output containing selected files and truncated excerpts.

## Determinism and Drift Tests
- Ordering determinism: control-plane files are always listed first in fixed order.
- Selection determinism: task keywords map to fixed include patterns.
- Truncation determinism: excerpts are hard-limited by `max_chars_per_file`.
- Repeat-run drift test: same repo state + same args => byte-identical normalized JSON output.

## Governance Rules
- Fail closed:
  - missing control-plane files are recorded as explicit warnings; no silent assumptions.
- Budget first:
  - loader must stop adding task files when `max_files` limit is reached.
- Minimal context:
  - no recursive bulk file ingestion outside selected patterns.
- Explicit signal:
  - output must include why each file was selected (`selected_by`).

## Failure Modes
- Over-selection causing token overflow.
- Under-selection causing missing task-critical artifacts.
- Non-deterministic file ordering due to unsorted path enumeration.
- Pulling historical artifacts by default and inflating context.

## Success Criteria (v0)
- Loader exists at `scripts/agent_context_loader_v0.py`.
- Output JSON includes:
  - control-plane status
  - selected file list
  - bounded excerpts
  - warnings and truncation markers
- Task-focused selection works for `direction`, `governance`, `design`, `spec` keyword intents.

## Immediate Next Step
Integrate loader invocation into `cortex-coach coach` outputs so each cycle can emit a ready-to-use context bundle for downstream agents.

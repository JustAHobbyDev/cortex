# Project Manager Recurring Cycle Runbook v0

Status: Draft
Source: distilled from `pm-recurring-cycle` skill candidate.
Scope: deterministic PM consultation cycles across any compatible project runtime.

## Outcome

Run one PM loop that keeps stage visibility current, asks or resolves exactly one consultation decision, and records all mutations in scene artifacts and the mutation ledger.

## Portability Contract

This runbook is interface-first, not storage-path-first.

Any implementation is valid if it can:
- Read and write the interfaces listed below.
- Apply one bounded mutation set atomically per cycle.
- Append one immutable mutation record per cycle.
- Produce deterministic, machine-checkable execution status.

## Required Interfaces

- `pm_status`: stage summary, active signals, and `next_consultation_due`.
- `pm_ideas`: current option/idea list that PM may advance or defer.
- `pm_consultation_queue`: queue of pending/resolved consultations.
- `task_queue`: task rows relevant to PM orchestration.
- `authority_registry`: current delegation/execution authority records.
- `mutation_ledger`: append-only record of cycle mutations.

## Adapter Mapping

Define one adapter mapping from interface names to local resources before running cycles.

Example mapping (reference implementation only):
- `pm_status` -> `scene/agent/project_manager/status_v0.json`
- `pm_ideas` -> `scene/agent/project_manager/ideas_v0.json`
- `pm_consultation_queue` -> `scene/agent/project_manager/consultation_queue_v0.json`
- `task_queue` -> `scene/task_queue/v0.json`
- `authority_registry` -> `scene/authority/registry_v0.json`
- `mutation_ledger` -> `scene/ledger/mutations_v0.jsonl`

## Trigger Boundaries

- Trigger on explicit PM governance-cycle requests.
- Trigger when the user asks to resolve numbered PM consultation choices.
- Skip when the user asks for implementation work outside PM state orchestration.
- Use `templates/project_manager_cycle_branch_templates_v0.md` for deterministic branch updates.

## Cycle Workflow

1) Read a snapshot from all required interfaces.

- Inspect stage summary, signals, and next consultation due from `pm_status`.
- Inspect pending consultation items from `pm_consultation_queue`.
- Inspect PM-owned rows from `task_queue`.

2) Select exactly one branch:
- `consult`: resolve one pending consultation from an explicit user choice.
- `kickoff`: if none pending, add one next consultation and update stage focus.
- `status-only`: refresh stage signals with no new consultation.

3) Build a single-cycle mutation plan.

- Use a deterministic mutator (script or function).
- Limit writes to mapped PM target interfaces only.
- Resolve exactly one consultation decision unless the user explicitly requests batching.

4) Execute via a cycle runner abstraction (never bypass it for tracked artifacts).

Generic contract:

```bash
<cycle-runner> \
  --agent-id <agent-id> \
  --targets <mapped-target-list> \
  --reason "<cycle reason>" \
  --task-id <task-id> \
  --phase <phase-slug> \
  --mutation-type UPDATE \
  --inputs <provenance-input-list> \
  --exec-cmd "<deterministic mutator command>"
```

Required behavior:
- Acquire any required claims/locks for target resources.
- Execute mutator exactly once.
- Apply and persist updates atomically.
- Append one mutation entry to `mutation_ledger`.
- Return a clear success/failure status with changed targets.

5) Verify and report.

- Confirm pending consultation state is valid.
- Confirm stage summary/signals are coherent post-update.
- Confirm PM task rows show updated progress timestamps/state.
- Confirm one new ledger entry exists for this cycle.

## Decision Contract

- Keep PM in delegator/planner mode by default.
- Consult the human before high-impact changes.
- Resolve only one consultation per cycle unless user asks for batching.
- Keep mutations scoped to PM scene surfaces and assigned task rows.

## Output Contract

- Return:
  - what decision was processed,
  - which files changed,
  - resulting task/stage state,
  - the next explicit choice for the human.

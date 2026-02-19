# PM Cycle Branch Templates

Use one branch per cycle. Keep mutations scoped to mapped PM interfaces:

- `pm_status`
- `pm_ideas`
- `pm_consultation_queue`
- `task_queue`

## consult

Use when a pending consultation exists and user gave an explicit choice.

Minimum updates:

- Resolve selected consultation (`state: resolved`, set `resolution`)
- Update `pm_status.stage_summary` for the affected stream
- Append one `decision_log` entry in `pm_status`
- Update mapped task row state + `last_progress_at`
- Set next human choice if another decision is needed

Recommended phase label: `consultation_resolved`

## kickoff

Use when no pending consultations exist and PM should advance stage planning.

Minimum updates:

- Refresh `pm_status.stage_summary.next_focus`
- Add one new pending consultation item
- Optionally update one idea `stage` and `deliverable_focus`
- Keep tasks unchanged unless kickoff explicitly opens a task transition

Recommended phase label: `cycle_kickoff`

## status-only

Use when user requests a state refresh with no new consultation decision.

Minimum updates:

- Refresh non-decision status signals only (`signals`, timestamps)
- Do not append decision log entries
- Do not create or resolve consultations
- Do not change task state

Recommended phase label: `status_refresh`

## Guardrails

- Resolve exactly one consultation per cycle unless user requested batching.
- Keep PM in `delegator_planner_non_executor` mode.
- Do not mutate resources outside declared PM interfaces.
- Always run through a cycle-runner abstraction to preserve claims and ledger semantics.

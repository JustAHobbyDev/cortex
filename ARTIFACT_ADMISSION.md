Cortex Artifact Admission Rules
Rule 1 — Reusability Test

An artifact must be reusable across at least two distinct projects or contexts.

If it is specific to one project instance, it does not belong in Cortex.

Rule 2 — Leverage Test

An artifact must meaningfully increase at least one of:

Structured reasoning clarity

Agent reliability

Execution speed

Decision consistency

If it does not measurably improve future cognition, it is rejected.

Rule 3 — Distillation Requirement

Artifacts must be distilled.

Raw inputs are not allowed:

No session logs

No chat transcripts

No brainstorming dumps

No telemetry

No unstructured notes

Only refined, structured output is permitted.

Rule 4 — Stability Threshold

Artifacts should represent stabilized insight, not active exploration.

If the idea is still evolving rapidly, it belongs in a project repo — not Cortex.

Rule 5 — Minimal Surface Area

Artifacts should be minimal and composable.

Prefer:

Clear invariants

Explicit constraints

Concise patterns

Structured templates

Avoid:

Narrative sprawl

Redundant explanation

Context-heavy storytelling

Rule 6 — No Operational State

Cortex does not store:

Live project state

Experimental results

Registry state

Checkpoints

Migration logs

Git history is the only provenance mechanism.

Rule 7 — Compounding Standard

Before adding an artifact, ask:

Will this make future thinking faster, cleaner, or more reliable?

If the answer is unclear, do not admit it.

Optional Enforcement Layer

You can add a simple pre-commit checklist:

Before committing a new artifact:

 Is it reusable?

 Is it distilled?

 Is it stable?

 Does it increase leverage?

 Is it free of raw logs?

If any answer is no → stop.

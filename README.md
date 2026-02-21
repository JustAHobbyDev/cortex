# Cortex

Cortex is a structured cognitive operating layer for high-leverage AI collaboration.

It is not a note system.
It is not a knowledge dump.
It is not a session archive.

Cortex stores distilled cognitive leverage — reusable structures that improve clarity, reliability, and execution speed across projects.

---

## What Cortex Contains

Cortex contains only high-signal, reusable artifacts:

* Principles
* Patterns
* Contracts
* Specs
* Templates
* Canonical Prompts
* Playbooks
* Policies
* Philosophical Positions
* Operating Model Definitions

Every artifact must:

* Increase structured thinking
* Improve agent reliability
* Be reusable across projects
* Reduce cognitive entropy

If it does not compound reasoning power over time, it does not belong here.

---

## What Cortex Does Not Contain

Cortex does not store:

* Raw sessions
* Chat logs
* Telemetry
* Checkpoints
* Project state
* Experimental exhaust
* Brainstorm dumps

Git history is sufficient provenance.

Cortex is a reasoning layer, not an activity log.

---

## Design Philosophy

Cortex exists to compound structured thinking.

It is optimized for:

* Clarity over accumulation
* Reusability over novelty
* Discipline over volume
* Architecture over tools

Cortex is a long-term cognitive multiplier.

---

## Tech Stack

Cortex standardizes on:

* `uv` for Python environment + command execution
* `just` for task orchestration

Primary operational entrypoints should be callable through `just` recipes that shell out via `uv`.

---

## User Documentation

- Cortex Coach docs: `docs/cortex-coach/README.md`
- Maintainer gate: `just quality-gate` (fallback: `./scripts/quality_gate_v0.sh`)
- CI gate: `just quality-gate-ci` (fallback: `./scripts/quality_gate_ci_v0.sh`)

---

Artifact Admission Rules: [ARTIFACT_ADMISSION.md]

---

## Footnotes

[1] Reflection-loop pattern inspiration: [`aviadr1/claude-meta`](https://github.com/aviadr1/claude-meta)
[2] Comparative research reference and credited project: [`jayminwest/mulch`](https://github.com/jayminwest/mulch) (report: `reports/mulch_comparative_research_report_v0.md`)

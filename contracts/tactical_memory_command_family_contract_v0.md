# Tactical Memory Command Family Contract v0

Canonical: true

Version: v0
Status: Draft
Scope: Phase 1 tactical memory command contract baseline for `cortex-coach`

## Purpose

Define the shared contract for Phase 1 tactical memory commands before runtime implementation.

This contract is design-authoritative for command surface and behavior expectations.

## Command Set (Required)

| Command | Operation Class | Mutation Class | Governance Authority |
|---|---|---|---|
| `memory-record` | capture tactical record | write tactical | non-authoritative until promoted |
| `memory-search` | retrieve tactical records | read-only | non-authoritative until promoted |
| `memory-prime` | build bounded context bundle | read-only | non-authoritative until promoted |
| `memory-diff` | compare tactical snapshots/sets | read-only | non-authoritative until promoted |
| `memory-prune` | policy-bounded tactical cleanup | write tactical | non-authoritative until promoted |
| `memory-promote` | bridge tactical evidence to governance pathways | write tactical bridge artifacts | canonical effect only through existing promotion flow |

## Shared CLI Contract

Required shared behavior across all command entries:

- `--project-dir` is required.
- `--format text|json` is supported for non-interactive execution.
- Omitted `--format` defaults to `text` for backward-compatible behavior.
- JSON mode must return parseable JSON objects suitable for automation.

Shared lock-safety controls for mutation commands (`memory-record`, `memory-prune`, `memory-promote`):

- `--lock-timeout-seconds`
- `--lock-stale-seconds`
- `--force-unlock`

## Output Contract Baseline

All commands must emit:

- stable `command` identifier
- normalized `status` field
- deterministic `result` payload shape

JSON output must include:

- `version` (`v0`)
- `command` (invoked command name)
- `status` (`pass` or `fail`)
- `project_dir`
- `run_at` (RFC3339 UTC timestamp)
- `result` (command-specific payload)

Failure output in JSON mode must include:

- `error.code` (stable error class)
- `error.message` (human-readable summary)
- `error.details` (optional structured diagnostics)

## Exit Code Semantics

| Exit Code | Meaning | Class |
|---|---|---|
| `0` | successful completion | success |
| `2` | invalid arguments or contract-shape violation | caller/input error |
| `3` | policy violation (for example prohibited tactical content class) | policy enforcement |
| `4` | lock timeout/conflict/stale-lock blocking condition | concurrency/state gate |
| `5` | unexpected runtime failure | internal error |

## Determinism Requirements

- Identical inputs and repository state must produce identical normalized JSON outputs except `run_at`.
- Ordering of returned records/results must be deterministic when scores tie.
- Error code assignment must be deterministic for the same failure class.

## Safety Boundaries

- Tactical memory commands must not mutate canonical governance artifacts directly.
- Any governance-impacting outcome must flow through existing decision/reflection/promotion requirements.
- Project-state writes must remain within configured project-state boundary root (default `.cortex/`).

# Cortex Coach CLI Output Contract Policy v0

Version: v0  
Status: Active  
Scope: `cortex` integration boundary for `cortex-coach` command usage

## Purpose

Guarantee deterministic machine-readable CLI outputs for automation, CI, and governance evidence collection while preserving backward compatibility for existing text-mode workflows.

## Policy Rules

1. Non-interactive `cortex-coach` commands MUST support `--format` with values `text` and `json`.
2. Default behavior MUST remain backward-compatible:
   - when `--format` is omitted, existing text/output semantics remain unchanged.
3. JSON mode MUST emit one parseable JSON payload on stdout for each command invocation.
4. Exit codes MUST remain semantically equivalent between text and json modes.
5. Output-contract upgrades MUST be tracked with decision/reflection artifacts when they affect governance/CI workflows.

## Integration Boundary Rule

Until standalone runtime parity is complete across all commands, this repository's delegator entrypoint:

- `python3 scripts/cortex_project_coach_v0.py`

is authorized to provide a compatibility shim for missing native `--format` support.

Boundary constraints:

- Shim behavior may normalize output format only.
- Shim behavior MUST NOT bypass or redefine runtime governance logic.
- Native runtime parity remains the long-term target.

## Current Coverage Contract (v0)

Native `--format` in standalone runtime (as currently observed):

- `audit-needed`
- `context-policy`
- `decision-capture`
- `reflection-scaffold`
- `decision-list`
- `decision-gap-check`
- `reflection-completeness-check`
- `decision-promote`
- `contract-check`

Compatibility-shim coverage via delegator:

- `init`
- `audit`
- `context-load`
- `policy-enable`
- `coach`

## Enforcement

- Test coverage must include JSON-mode checks for shim-covered commands.
- Session/release governance checks should prefer JSON mode for machine-evaluated flows.
- Any change to this contract requires maintainer-reviewed policy/spec updates.

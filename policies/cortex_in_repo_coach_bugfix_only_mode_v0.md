# Cortex In-Repo Coach Bugfix-Only Mode v0

Version: v0
Status: Active
Scope: `cortex` repository in-repo coach runtime paths

## Purpose

Freeze new feature development in in-repo coach runtime during Phase 3+ and route feature evolution to standalone `cortex-coach`.

## Rule

- In `cortex`, changes under in-repo coach runtime paths are limited to:
  - bug fixes
  - compatibility fixes
  - wrapper/migration support for standalone coach
- New runtime features must be implemented in `cortex-coach` first.

## In-Repo Paths Covered

- `scripts/cortex_project_coach_v0.py`
- `scripts/agent_context_loader_v0.py`
- `scripts/cortex_coach_wrapper_v0.sh`

## Exception Process

Any exception must include:

- explicit justification in PR description
- linked decision artifact
- paired issue/PR reference in standalone `cortex-coach`

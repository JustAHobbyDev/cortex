# Cortex Coach Concurrency Hardening Plan v0

## Purpose

Capture the agreed implementation plan for race-condition prevention in `cortex-coach` before execution begins.

## Planned Steps

1. Implement concurrency safety in `cortex-coach`
- Add lock file around mutating commands (`init`, `coach`, `coach --apply`, manifest/report writes).
- Add atomic write helper for JSON/MD outputs (`write temp -> fsync -> os.replace`).
- Add stale-lock handling (`timestamp`, `pid`, timeout, optional `--force-unlock`).

2. Continue maintainer-mode operation with current guardrails
- Use sequential command flow only.
- Avoid parallel invocations in local/CI until lock feature is merged.

3. Update operational entrypoints
- Add `just` recipe that runs `init -> coach -> audit` as one fail-fast chain.
- Document single-runner mode and lock behavior in runbook.

4. Validate behavior explicitly
- Normal flow test: `init -> coach -> audit`.
- Concurrency test: second run blocks/fails with clear lock message while first run is active.
- Crash/interrupt test: atomic writes keep manifest/reports valid JSON.

5. Commit and push in scoped commits
- Commit 1: lock + atomic write code changes.
- Commit 2: docs/runbook/just updates + test evidence artifacts.

6. Optional follow-up after stability
- Promote to installable `cortex-coach` package flow (`uv`/`pipx`) after concurrency safeguards are in place.

## Execution Status

Status: Saved, not yet executed.

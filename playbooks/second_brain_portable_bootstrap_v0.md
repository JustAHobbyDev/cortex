# Second Brain Portable Bootstrap v0

Canonical: false

## Purpose

Make `project/second-brain` runnable from any machine with deterministic startup checks.

## Scope

- Install repo-local skills into Codex skill discovery path.
- Verify local command/file/runtime prerequisites.
- Keep process local-only (no network calls, no remote state mutation).

## One-Command Startup

From repo root:

```bash
<bootstrap-runner>
```

Or with `just`:

```bash
just sb-up
```

## Startup Sequence (deterministic)

1) skill-bootstrap runner

- Discovers local skills under `skills/*/SKILL.md`.
- Installs to `${CODEX_HOME:-~/.codex}/skills/local/second-brain` (or override path).
- Supports `--mode symlink` (default) and `--mode copy`.

2) environment doctor runner

- Checks required commands: `bash`, `git`, `jq`, and a Python runtime (and warns on missing `just`).
- Checks core repo files required for agent workflows.
- Checks whether local skills are installed.
- Checks `git config core.hooksPath` status.

## Common Flags

```bash
<bootstrap-runner> --dry-run
<bootstrap-runner> --mode copy --force
<bootstrap-runner> --strict
<environment-doctor-runner> --json
```

## Recommended First-Time Setup

```bash
git config core.hooksPath .githooks
<bootstrap-runner> --mode symlink
```

## Notes

- `--mode symlink` keeps installed skills synced to repo edits.
- `--mode copy` is useful when symlinks are constrained by environment policy.
- `--force` replaces existing installed skill paths under the configured install root only.

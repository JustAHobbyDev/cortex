# Migration to Standalone `cortex-coach` v0

## Goal

Move usage from in-repo script mode to installed standalone `cortex-coach`.

## Recommended Path

Install standalone CLI:

```bash
uv tool install git+https://github.com/JustAHobbyDev/cortex-coach.git
```

Use:

```bash
cortex-coach <command> ...
```

## Temporary Compatibility in `cortex`

- `just coach-*` recipes route through `scripts/cortex_coach_wrapper_v0.sh`.
- Wrapper behavior:
  - prefers installed `cortex-coach`
  - falls back to in-repo script runtime
- For parity testing only: `CORTEX_COACH_FORCE_INTERNAL=1`.

## Deprecation Direction

- In-repo script fallback is transitional.
- Full decoupling will remove runtime feature development in `cortex` script paths.

## Verification Checklist

1. `cortex-coach --help` works from shell.
2. `just coach-audit-needed .` runs through wrapper successfully.
3. `just phase3-parity-check` passes.

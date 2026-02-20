# Quality Gate

Use one deterministic command for local pre-merge and pre-release checks.

## Run

Preferred:

```bash
just quality-gate
```

Fallback without `just`:

```bash
./scripts/quality_gate_v0.sh
```

## What It Checks

1. `audit-needed` with fail-on-required behavior
2. `cortex-coach` smoke commands
3. docs local-link + JSON integrity
4. focused `cortex-coach` pytest suite

## When to Run

- Before opening or updating a PR to `main`
- Before release-tagging or handoff

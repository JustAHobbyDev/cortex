---
name: cortex-training-handoff
description: "Execute governed transfer of Cortex training assets into the standalone training repository with approval linkage, pinned handoff manifest generation, and quality-gated closeout. Use when migrating or re-running training handoff between `cortex` and `cortex-training`."
---

# Cortex Training Handoff

## Overview

Run the training transfer through the governed wrapper so file transfer, pinning, and evidence artifacts stay consistent.

## Workflow

1. Verify both repos are present and clean enough for transfer:
   - source repo: `cortex`
   - target repo: `cortex-training`
2. Run dry-run first.
3. Run live transfer with `--approval-ref`.
4. Confirm:
   - target commit exists
   - handoff manifest generated
   - transfer execution report generated
   - pointer doc updated with active pin
5. Push target repo and source repo commits.

Use `references/transfer-runbook.md` for command templates.

## Required inputs

1. `--target-repo-dir`
2. at least one `--approval-ref` (promoted decision id preferred)
3. transfer mode:
   - default copy
   - move only when bundle source pruning is intended

## Safety rules

1. Always dry-run first when rerunning after script or contract changes.
2. Never treat dry-run report as final evidence.
3. Only use `--move` when transfer is already verified and you intend to consume the source bundle.

## References

- `references/transfer-runbook.md`: dry-run/live-run command templates and verification commands

---
name: cortex-gate-remediation
description: "Diagnose and remediate failed Cortex quality-gate runs by reproducing the first failing step, applying minimal fixes, re-validating narrowly, and then re-running full required gates. Use when `quality_gate_ci` or related governance checks fail locally or in CI."
---

# Cortex Gate Remediation

## Overview

Use deterministic gate remediation order. Always fix the first failing step and avoid parallel speculative fixes.

## Workflow

1. Capture the failing gate log and identify the first failing step.
2. Map the failing step to the exact command in `references/ci-step-map.md`.
3. Run only that command until it passes.
4. Apply minimal code/doc/policy fixes for that failure class.
5. Re-run the same failing step.
6. Re-run full `./scripts/quality_gate_ci_v0.sh`.
7. Remove incidental generated timestamp-only artifacts from the diff.
8. If enforcement semantics changed, run decision/reflection capture before closeout.

## Remediation Rules

1. Do not skip directly to full-gate reruns before reproducing the failing step.
2. Do not widen scope until the initial failure is closed.
3. Do not commit generated report timestamp churn unless explicitly required as evidence.

## Typical failure classes

- Decision gap uncovered files: run reflection scaffold + decision capture/promote.
- Reflection enforcement mismatch: ensure promoted decisions are linked and scaffold exists.
- Project boundary violations: relocate artifacts under `.cortex/` or add temporary waiver.
- Docs/json integrity: fix broken links and invalid JSON payloads.

## References

- `references/ci-step-map.md`: step-to-command map and first-response actions

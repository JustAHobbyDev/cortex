---
name: cortex-policy-change
description: "Implement Cortex policy changes with correct boundary classification and governance linkage. Use when adding or changing policy rules, enforcement expectations, or governance contracts, and when deciding whether content should live in policy, playbook, spec, or skill."
---

# Cortex Policy Change

## Overview

Apply policy edits without mixing governance invariants with temporary implementation choices.

## Workflow

1. Classify requested change using `references/policy-boundary-matrix.md`.
2. Place content in the right layer:
   - policy for durable invariant
   - playbook for operational sequence
   - skill for tool-specific execution workflow
   - spec/contract for machine-checkable behavior
3. Keep policy statements stable, testable, and outcome-oriented.
4. Avoid encoding tool preference unless it is risk/compliance-critical.
5. Update linked enforcement scripts/tests/contracts when policy changes imply runtime checks.
6. Run governance checks and capture decision/reflection linkage.

## Mandatory validation sequence

1. `python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir . --format json`
2. `python3 scripts/cortex_project_coach_v0.py reflection-completeness-check --project-dir . --format json`
3. `./scripts/quality_gate_ci_v0.sh`

## Policy drafting constraints

1. Specify required outcome and failure mode.
2. Specify scope and exceptions explicitly.
3. Avoid embedding one-off operational commands unless the policy governs command contract behavior itself.
4. Keep implementation-level command recipes in skills/playbooks.

## References

- `references/policy-boundary-matrix.md`: policy vs playbook vs skill vs spec rubric

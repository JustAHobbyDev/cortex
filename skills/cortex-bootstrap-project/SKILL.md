---
name: cortex-bootstrap-project
description: "Bootstrap a new Cortex-governed project with deterministic scaffold and first-green-gate verification. Use when initializing governance artifacts, boundary defaults, and required gate readiness in a fresh or external project repository."
---

# Cortex Bootstrap Project

## Overview

Initialize new project governance surfaces with the `bootstrap-scaffold` flow, then verify first-green-gate readiness.

## Workflow

1. Collect inputs:
   - project directory
   - project id
   - project name
   - optional cortex root
2. Run `bootstrap-scaffold`.
3. Inspect scaffold output and report path for missing required artifacts.
4. Run first-green-gate sequence from scaffold output.
5. Confirm required gate is green.
6. Commit baseline bootstrap artifacts.

Use `references/bootstrap-sequence.md` for exact command templates.

## Validation targets

1. `.cortex/templates/bootstrap_first_green_gate_checklist_v0.md` exists.
2. `.cortex/reports/project_state/phase6_bootstrap_scaffold_report_v0.json` status is pass.
3. Required gate command bundle passes.

## Failure handling

1. If scaffold report status is fail, fix missing required paths before running full gates.
2. If portability bundle entries are missing, treat bootstrap as incomplete and do not close out.

## References

- `references/bootstrap-sequence.md`: canonical commands and expected artifacts

# Cortex Coach Usage Decision Policy

Version: v0
Status: Active
Scope: This repository (`/home/d/codex/cortex`)

## Purpose

Ensure `cortex-coach` is consistently considered before next-step execution so lifecycle governance is not skipped due to operator memory gaps.

## Rule

Before substantial next-step work, the operator/agent must make an explicit decision:

1. `Use coach now`, or
2. `Coach not needed yet` (with concrete reason).

## Default Decision Procedure

1. Run:
   ```bash
   cortex-coach audit-needed --project-dir . --format json
   ```
2. If `audit_required=true`:
   - run `cortex-coach coach --project-dir .`
   - run `cortex-coach audit --project-dir .`
   - proceed only after handling blocking findings
3. If `audit_required=false`:
   - proceed with work
   - run audit at the next milestone boundary (before merge/release)

## High-Risk Trigger Guidance

Treat changes as high-risk (likely requiring coach/audit) when they touch:

- `specs/`
- `policies/`
- `.cortex/manifest_v0.json`
- `.cortex/artifacts/`
- `scripts/cortex_project_coach_v0.py`

## Exceptions

Skip immediate coach usage only for tiny, non-governance edits (for example simple typo-only changes), but still run audit before merge/release.

## Enforcement Style

This policy is enforced as an operating discipline (human + agent behavior), and may later be promoted to CI gating.

# Cortex / cortex-coach Decoupling Closeout v1

Date: 2026-02-20
Status: Closed

## Summary

Decoupling objective is complete:
- standalone `cortex-coach` runtime is active in its own repository
- `cortex` runtime entrypoints delegate to installed standalone coach
- in-repo legacy runtime implementation has been removed
- parity and governance gates were run during migration

## Repository References

### `cortex`

- `61733c6` Start phase 3 with coach wrapper dual-path routing
- `ceade05` Add phase 3 parity check runner and update plan progress
- `4d591e9` Close phase 3 with parity evidence and bugfix-only policy
- `0912ce7` Default docs to standalone cortex-coach and add migration guide
- `fec377f` Make cortex_project_coach entrypoint a thin external-first delegator
- `c5849d2` Complete phase 4 decoupling with external-only coach delegation

### `cortex-coach`

- `1982d2c` Bootstrap standalone cortex-coach repository
- `cf92d9f` Remove generated artifacts and add gitignore
- `f12690a` Trim bootstrap to coach-owned runtime and add migration matrix
- `ffb7e5a` Record decision-gap recursive failure known issue and proposed fix

## Evidence Artifacts

- `playbooks/cortex_coach_decoupling_plan_v0.md`
- `reports/phase3_parity_check_report_v0.md`
- `docs/cortex-coach/migration_to_standalone_v0.md`
- `policies/cortex_coach_final_ownership_boundary_v0.md`

## Open Follow-Up (Non-Blocking)

- external repo release workflow/version tagging polish
- resolve known issue: `https://github.com/JustAHobbyDev/cortex-coach/issues/1`

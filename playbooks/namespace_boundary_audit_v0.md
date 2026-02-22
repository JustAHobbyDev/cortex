# Namespace Boundary Audit Operation

Version: v0
Status: Track-only
Inputs:
- shell-runner files
- audit/automation runner files
- `policies/scene_namespace_boundary_v0.md` (policy context)

## Purpose

Detect mutating tools that are missing required namespace-boundary declarations:

- `TARGET_NAMESPACE`
- `ALLOWED_PATH_PREFIXES`
- `BOUNDARY_JUSTIFICATION` (required only for `TARGET_NAMESPACE=mixed`)

## Operation Signature

`run_namespace_boundary_audit(repo_root?, out_file?)`

## Parameters

- `repo_root` (optional, default repo root): repository root path.
- `out_file` (optional, default .cortex/reports/namespace_boundary_audit_v0.json): JSON output path.

## Metrics (v0)

- `scripts_scanned`
- `mutating_tool_candidates`
- `declarations_complete`
- `missing_declaration_count`

## Advisory Threshold (track-only)

- `missing_declaration_warn_gt`: `0`

## Procedure

1. Run:
   ```bash
   <audit-runner> --audit namespace-boundary
   ```
2. Inspect `reports/namespace_boundary_audit_v0.json`.
3. Prioritize missing declaration remediation on high-change mutating tools first.
4. Re-run until missing count trends toward zero.

## Definition of Done

- [ ] Report JSON generated.
- [ ] Missing declaration offenders listed with missing fields.
- [ ] Track-only warning status emitted when missing declarations are present.
- [ ] No automatic mutation performed by this audit run.

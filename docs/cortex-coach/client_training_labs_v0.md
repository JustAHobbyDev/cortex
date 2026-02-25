# Client Training Labs v0

Version: v0  
Status: Active  
Scope: Deterministic lab pack for onboarding modules `M2` through `M5`

## Purpose

Provide reproducible, command-driven labs that validate operational readiness for Cortex client teams.

## Lab Conventions

1. Run all commands from the client project root.
2. Prefer JSON output for machine-readable verification.
3. Record command outputs and generated artifact paths in the onboarding completion report.
4. Treat any required-gate failure as a blocking result for the lab.

## Prerequisites

1. `cortex-coach` installed and available on `PATH`.
2. Project initialized with `.cortex/`.
3. Governance baseline artifacts present and repository clean before each lab.
4. Command-surface preflight passes before starting `M2` and before starting `M4`.

## Command Surface Preflight (Required)

### Objective

Fail early when the installed `cortex-coach` build cannot satisfy onboarding lab command requirements.

### Command Checklist

1. `python3 scripts/client_onboarding_command_preflight_v0.py --project-dir . --format json --out-file .cortex/reports/project_state/client_onboarding_command_preflight_v0.json`

### Expected Results

1. Preflight exits with code `0`.
2. JSON payload has `status=pass`.
3. `summary.required_check_fail_count=0`.

### Exit Evidence

1. `.cortex/reports/project_state/client_onboarding_command_preflight_v0.json`
2. Command transcript proving pass status.

If preflight fails:

1. Stop onboarding labs and remediate capability gaps first.
2. Use delegator compatibility path for universal JSON command support:
   - `python3 scripts/cortex_project_coach_v0.py <command> ... --format json`
3. Upgrade standalone `cortex-coach` when delegator preflight still reports rollout capability failures.

## M2 Lab: Operator Workflow

### Objective

Demonstrate daily operator flow and pre-merge closeout sequence without governance bypass.

### Command Checklist

1. `cortex-coach audit-needed --project-dir . --format json`
2. `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope cortex-only --format json`
3. `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all --format json`
4. `cortex-coach decision-gap-check --project-dir . --format json`
5. `cortex-coach reflection-completeness-check --project-dir . --required-decision-status promoted --format json`
6. `python3 scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`
7. `python3 scripts/project_state_boundary_gate_v0.py --project-dir . --format json`
8. `./scripts/quality_gate_ci_v0.sh`

### Expected Results

1. Commands 1-7 return JSON payload with `status=pass`.
2. Command 8 ends with `[quality-gate-ci] PASS`.
3. No unmanaged or out-of-boundary artifacts are introduced.

### Exit Evidence

1. `.cortex/reports/lifecycle_audit_v0.json`
2. Terminal transcript or CI log snippet proving required gate pass.

## M3 Lab: Governance Enforcement

### Objective

Demonstrate decision/reflection linkage from capture through promotion with enforced completeness.

### Command Checklist

1. Create reflection scaffold:
- `cortex-coach reflection-scaffold --project-dir . --title "<title>" --mistake "<mistake>" --pattern "<pattern>" --rule "<rule>" --format json`
2. Capture linked decision (use scaffold outputs for `--reflection-id` and `--reflection-report`):
- `cortex-coach decision-capture --project-dir . --title "<title>" --decision "<decision>" --rationale "<rationale>" --impact-scope governance,docs --linked-artifacts <comma_paths> --reflection-id <reflection_id> --reflection-report <reflection_report> --format json`
3. Promote decision:
- `cortex-coach decision-promote --project-dir . --decision-id <decision_id> --format json`
4. Validate linkage gates:
- `cortex-coach decision-gap-check --project-dir . --format json`
- `python3 scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`

### Expected Results

1. Promoted decision artifact exists under `.cortex/artifacts/decisions/`.
2. Reflection scaffold exists under `.cortex/reports/`.
3. Post-promotion linkage checks pass with no findings.

### Exit Evidence

1. `.cortex/reports/decision_candidates_v0.json`
2. `.cortex/artifacts/decisions/<decision_file>.md`
3. `.cortex/reports/reflection_scaffold_<...>_v0.json`

## M4 Lab: Rollout and Recovery

### Objective

Demonstrate safe rollout-mode transitions, rollback drill execution, and transition-audit completeness.

### Command Checklist

1. Rerun required preflight:
- `python3 scripts/client_onboarding_command_preflight_v0.py --project-dir . --format json`
2. Read mode:
- `python3 scripts/cortex_project_coach_v0.py rollout-mode --project-dir . --format json`
3. Drill transition to `off`:
- `python3 scripts/cortex_project_coach_v0.py rollout-mode --project-dir . --set-mode off --changed-by <actor> --reason "<reason>" --format json`
4. Restore to `experimental`:
- `python3 scripts/cortex_project_coach_v0.py rollout-mode --project-dir . --set-mode experimental --changed-by <actor> --reason "<reason>" --incident-ref <incident_ref> --format json`
5. Audit transitions:
- `python3 scripts/cortex_project_coach_v0.py rollout-mode-audit --project-dir . --format json`
6. (Instructor-supervised only) transition to `default` with full linkage:
- `python3 scripts/cortex_project_coach_v0.py rollout-mode --project-dir . --set-mode default --changed-by <actor> --reason "<reason>" --decision-refs <decision_refs> --reflection-refs <reflection_refs> --audit-refs <audit_refs> --format json`

### Expected Results

1. Every transition command returns `status=pass`.
2. Audit reports `transition_completeness_rate=1.0` and `finding_count=0`.
3. Rollback path remains available (`default -> experimental -> off`).

### Exit Evidence

1. `.cortex/state/rollout_mode_state_v0.json`
2. `.cortex/state/rollout_mode_transitions_v0.jsonl`
3. `.cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json`

## M5 Lab: Project Integration

### Objective

Demonstrate client-repo operational readiness with CI-quality gates and onboarding closeout artifacts.

### Command Checklist

1. Run release-boundary gate bundle:
- `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all --format json`
- `cortex-coach decision-gap-check --project-dir . --format json`
- `cortex-coach reflection-completeness-check --project-dir . --required-decision-status promoted --format json`
- `python3 scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`
- `python3 scripts/project_state_boundary_gate_v0.py --project-dir . --format json`
2. Run CI gate:
- `./scripts/quality_gate_ci_v0.sh`
3. Produce onboarding closeout package:
- Fill `.cortex/templates/client_onboarding_completion_report_template_v0.md`
- Produce certification scorecard JSON matching `contracts/client_onboarding_certification_scorecard_schema_v0.json`
- Generate certification/cadence pack:
  - `python3 scripts/client_onboarding_certification_pack_v0.py --project-dir . --run-quality-gate --format json --out-file .cortex/reports/project_state/client_onboarding_certification_pack_v0.json`

### Expected Results

1. Required gate bundle and CI gate pass.
2. Completion report is fully populated and signed.
3. Certification scorecard validates against schema and yields `status=pass`.
4. Certification pack reports `status=pass` with cadence schedule populated.

### Exit Evidence

1. Client CI run link or log snippet with green result.
2. Completed onboarding report artifact.
3. Certification scorecard artifact.
4. `.cortex/reports/project_state/client_onboarding_certification_pack_v0.json`

## Instructor Notes

1. Run labs in order (`M2 -> M5`) because each lab builds required artifacts for the next.
2. Do not permit `default` activation in M4 without promoted decision/reflection/audit linkage.
3. When client environments differ from this repository, preserve the same required gate semantics and evidence expectations.

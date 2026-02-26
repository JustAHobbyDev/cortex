# Bootstrap Sequence

## Scaffold command

```bash
python3 scripts/cortex_project_coach_v0.py bootstrap-scaffold \
  --project-dir <target_project_dir> \
  --project-id <project_id> \
  --project-name "<project_name>" \
  --format json
```

## First-green-gate flow

```bash
python3 scripts/cortex_project_coach_v0.py audit-needed --project-dir <target_project_dir> --format json
python3 scripts/cortex_project_coach_v0.py coach --project-dir <target_project_dir>
python3 scripts/cortex_project_coach_v0.py audit --project-dir <target_project_dir>
```

In this repository:

```bash
./scripts/quality_gate_ci_v0.sh
```

## Expected bootstrap artifacts

- `.cortex/templates/bootstrap_first_green_gate_checklist_v0.md`
- `.cortex/reports/project_state/phase6_bootstrap_scaffold_report_v0.json`

## Baseline commit

```bash
git add .
git commit -m "Bootstrap cortex governance baseline"
```

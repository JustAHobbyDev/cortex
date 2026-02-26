# Training Handoff Runbook

## Dry run

```bash
./scripts/move_training_files_to_repo_v0.sh \
  --target-repo-dir /path/to/cortex-training \
  --approval-ref dec_20260225T175933Z_execute_training_materia \
  --dry-run --skip-quality-gate --format json
```

## Live run (copy mode)

```bash
./scripts/move_training_files_to_repo_v0.sh \
  --target-repo-dir /path/to/cortex-training \
  --approval-ref dec_20260225T175933Z_execute_training_materia \
  --format json
```

## Live run (move mode)

```bash
./scripts/move_training_files_to_repo_v0.sh \
  --target-repo-dir /path/to/cortex-training \
  --approval-ref dec_20260225T175933Z_execute_training_materia \
  --move \
  --format json
```

## Verify target pin

```bash
git -C /path/to/cortex-training show -s --oneline <target_pin_ref>
```

## Commit surfaces in source repo (`cortex`)

- `.cortex/reports/project_state/client_training_project_handoff_manifest_v0.json`
- `.cortex/reports/project_state/client_training_transfer_execution_report_v0.json`
- `docs/cortex-coach/client_training_external_repo_v0.md`

# Cortex Governed Cycle Commands

## Preflight

```bash
python3 scripts/cortex_project_coach_v0.py audit-needed --project-dir . --format json
```

If `audit_required=true`:

```bash
python3 scripts/cortex_project_coach_v0.py coach --project-dir .
python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope cortex-only
python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all
```

## Decision and Reflection (when governance-impacting)

```bash
python3 scripts/cortex_project_coach_v0.py reflection-scaffold \
  --project-dir . \
  --title "<title>" \
  --mistake "<mistake>" \
  --pattern "<pattern>" \
  --rule "<rule>" \
  --impact-scope governance,docs,operations \
  --format json
```

Use scaffold output to run:

```bash
python3 scripts/cortex_project_coach_v0.py decision-capture ...
python3 scripts/cortex_project_coach_v0.py decision-promote ...
```

## Required Gate

```bash
./scripts/quality_gate_ci_v0.sh
```

## Common cleanup for incidental timestamp drift

```bash
git restore .cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json
```

## Final state check

```bash
git status --short --branch
```

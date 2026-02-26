# AGENTS Instructions for Cortex

## Skills

This repository includes local skills under `skills/` that should be used for recurring Cortex workflows.

### Available skills

- `cortex-governed-cycle`: Run the default governance cycle for substantial work (audit-needed, coach/audit, decision/reflection, quality gate, closeout hygiene). Path: `skills/cortex-governed-cycle/SKILL.md`
- `cortex-gate-remediation`: Diagnose and remediate failed `quality_gate_ci` / governance gate runs deterministically. Path: `skills/cortex-gate-remediation/SKILL.md`
- `cortex-policy-change`: Apply policy changes with correct boundary classification (policy vs playbook vs skill vs spec) and governance linkage. Path: `skills/cortex-policy-change/SKILL.md`
- `cortex-bootstrap-project`: Bootstrap a new governed project with `bootstrap-scaffold` and first-green-gate sequence. Path: `skills/cortex-bootstrap-project/SKILL.md`
- `cortex-training-handoff`: Execute governed training transfer from `cortex` to `cortex-training` with approval refs and pinned handoff artifacts. Path: `skills/cortex-training-handoff/SKILL.md`

## Trigger rules

1. Use a listed skill whenever the user request clearly matches its workflow.
2. Use multiple skills only when needed; prefer the minimal set.
3. For non-trivial implementation work in this repo, default to `cortex-governed-cycle`.
4. For any failed gate workflow, use `cortex-gate-remediation` first before ad-hoc debugging.

## Skill bootstrap

Install local skills into Codex skill discovery with:

```bash
python3 scripts/skills_bootstrap_v0.py --project-dir . --mode symlink
```

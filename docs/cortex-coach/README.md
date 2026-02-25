# Cortex Coach User Docs

This documentation is for users running `cortex-coach` in their own projects.

## Start Here

1. [Install](install.md)
2. [Quickstart](quickstart.md)
   - Includes Minimal Workflow and Complete Workflow paths
3. [AI Governance Fundamentals (M0)](client_ai_governance_fundamentals_v0.md)
4. [Client Training Labs](client_training_labs_v0.md)
   - Includes required command-surface preflight before `M2` and `M4`
5. [Training Project Boundary + Handoff](client_training_project_boundary_and_handoff_v0.md)
6. [Commands](commands.md)
7. [Maintainer Mode](maintainer-mode.md)
8. [Agent Context Loader](agent-context-loader.md)
9. [Quality Gate](quality-gate.md)
10. [FAQ](faq.md)
11. [Troubleshooting](troubleshooting.md)
12. [Migration to Standalone](migration_to_standalone_v0.md)
13. [GDD Role + Capability Pack](../../playbooks/cortex_phase0_role_charters_v0.md)

## What Cortex Coach Does

`cortex-coach` creates and maintains a project-local `.cortex/` lifecycle layer:

- bootstrap project artifacts (`init`)
- audit artifact health (`audit`)
- run guidance cycles (`coach`)
- optionally draft next-version artifacts (`coach --apply`)

It is designed to keep lifecycle artifacts deterministic, versioned, and auditable.

## Multi-Agent Governance Baseline

For bootstrap and governed multi-agent delivery, use the minimum role/capability matrix and escalation rules in:

- `playbooks/cortex_phase0_role_charters_v0.md` (section: `Phase 6 GDD Minimum Role + Capability Pack (PH6-005)`)

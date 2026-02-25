# Cortex Coach User Docs

This documentation is for users running `cortex-coach` in their own projects.

## Start Here

1. [Install](install.md)
2. [Quickstart](quickstart.md)
   - Includes Minimal Workflow and Complete Workflow paths
3. [Client Training Labs](client_training_labs_v0.md)
   - Includes required command-surface preflight before `M2` and `M4`
4. [Commands](commands.md)
5. [Maintainer Mode](maintainer-mode.md)
6. [Agent Context Loader](agent-context-loader.md)
7. [Quality Gate](quality-gate.md)
8. [FAQ](faq.md)
9. [Troubleshooting](troubleshooting.md)
10. [Migration to Standalone](migration_to_standalone_v0.md)

## What Cortex Coach Does

`cortex-coach` creates and maintains a project-local `.cortex/` lifecycle layer:

- bootstrap project artifacts (`init`)
- audit artifact health (`audit`)
- run guidance cycles (`coach`)
- optionally draft next-version artifacts (`coach --apply`)

It is designed to keep lifecycle artifacts deterministic, versioned, and auditable.

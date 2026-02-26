# Client Training External Repo Reference v0

Version: v0  
Status: Active  
Scope: Canonical pointer for training assets that were split out of the core `cortex` repository.

## Canonical Source

Training materials are now maintained in a standalone training project.

- Canonical repo slug: `JustAHobbyDev/cortex-training`
- Canonical training pack: `client-onboarding-pack`
- Version pin policy: use immutable `commit_sha` (preferred) or signed tag for release-boundary usage.

## What Moved Out of This Repo

1. AI governance fundamentals curriculum content.
2. Client training labs and instructor delivery material.
3. Training execution board and delivery plan details.
4. Onboarding completion template and certification scorecard schema ownership.
5. Training automation scripts for certification and preflight.

## What Stays in This Repo

1. Governance/runtime authority and enforcement gates.
2. Training-project boundary and handoff contract:
- `docs/cortex-coach/client_training_project_boundary_and_handoff_v0.md`
- `contracts/client_training_project_handoff_schema_v0.json`
- `.cortex/templates/client_training_project_handoff_manifest_template_v0.json`
3. Compatibility stubs and migration guidance for previously in-repo training paths.

Legacy training scripts in `scripts/` now act as compatibility shims that emit `status=moved`.

## Migration Notes

1. If you need full training content, use the standalone training project.
2. If you are auditing historical references in this repo, legacy paths remain as compatibility stubs.
3. Update local onboarding runbooks to pin the training repo ref explicitly in handoff manifests.

## Active Pin

- Pin type: `commit_sha`
- Pin ref: `3f558891d6a805b9d576323495de82b03949ec41`
- Updated at: `2026-02-26T09:10:23Z`
- Source bundle: `.cortex/artifacts/training_migration_bundle_v0/manifest_v0.json`

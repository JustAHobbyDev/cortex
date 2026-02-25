# Client Training Project Boundary and Handoff v0

Version: v0  
Status: Active (split executed)  
Scope: Define how training content operates as a standalone project while keeping Cortex governance and runtime contracts stable.

## Purpose

Establish a clear separation between:

1. Core Cortex runtime/governance system of record.
2. Training and enablement content lifecycle.

And define a deterministic handoff contract between the two.

## Why Split into a Separate Project

1. Independent release cadence:
- Training content should evolve faster than core runtime/policy contracts.
2. Cleaner release surface:
- Cortex base OS/repo should not be overloaded with all training delivery artifacts.
3. Clear ownership:
- Education/enablement owners can iterate without altering core enforcement logic.
4. Better QA targeting:
- Training-specific quality checks can run in a dedicated training repository.

## Repository Boundary

### Cortex Repository (canonical governance/runtime)

Owns and remains authoritative for:

1. Governance policies, contracts, and enforcement gates.
2. Runtime command semantics and release-boundary checks.
3. Integration interface contracts consumed by training project.
4. Compatibility expectations for training outputs used in governance workflows.

### Training Repository (standalone enablement project)

Owns:

1. Curriculum assets (decks, workbooks, role-specific tracks).
2. Scenario libraries and exercises.
3. Instructor operations runbooks.
4. Cohort-level analytics and delivery tooling.

Must not override:

1. Core governance authority model.
2. Required release-boundary gate semantics.
3. Canonical contract versions without coordinated change and approval.

## Handoff Contract (Machine-Checkable)

Use:

1. `contracts/client_training_project_handoff_schema_v0.json`
2. `.cortex/templates/client_training_project_handoff_manifest_template_v0.json`

The handoff manifest records:

1. Source and target repos.
2. Version pin for training project (`commit_sha` or `tag` preferred for release boundaries).
3. Compatibility declarations (`cortex` contract min version, `cortex-coach` min version, scorecard schema version).
4. Required interface coverage (fundamentals module, labs, completion template, scorecard schema compatibility, FAQ/triage material).
5. Governance approvals and status (`draft`, `ready_for_handoff`, `accepted`).

## Version Pinning Policy

1. Release-boundary usage must pin training project by immutable ref:
- preferred: `commit_sha`
- acceptable: signed `tag`
2. Floating branch pins (`main`) are advisory only and not release-authoritative.
3. Any `breaking_changes=true` manifest requires:
- explicit migration notes
- maintainer/governance approval linkage
- synchronized compatibility update in Cortex docs/contracts.

## Recommended Handoff Flow

1. Prepare manifest from template and fill required interfaces.
2. Validate manifest against schema.
3. Confirm boundary/coverage/pin checklist fields.
4. Link governance approvals.
5. Mark manifest `ready_for_handoff`.
6. Final reviewer marks `accepted`.

## Minimum Integration Surface Kept in Cortex

Even after full training split, Cortex should retain:

1. Pointer docs to approved training project entry points.
2. The handoff schema contract and manifest template.
3. Any runtime-critical templates/contracts still required by quality gates.

## Current Status

Training content ownership has been split out of `cortex`.

`cortex` now retains:

1. Boundary/handoff contract artifacts.
2. Compatibility stubs at legacy training paths for historical reference stability.
3. External training repo pointer documentation.

# Cortex Project Coach Spec

Version: v0
Status: Experimental
Inputs:
- `README.md` repository purpose and admission criteria
- `philosophy/ontology_architecture_map_v0.md` layer model
- `specs/spec_spec_v0.md` governance and spec structure
- `specs/design_ontology_schema_spec_v0.md` design ontology baseline
- `scripts/design_prompt_dsl_compile_v0.py` DSL compiler
- `scripts/design_ontology_validate_v0.py` ontology validator

## Purpose
Define an application that guides project creation with AI assistance and maintains required Cortex artifacts across the project lifecycle.

## Scope
- In scope:
  - Bootstrap of required lifecycle artifacts for a new project.
  - Ongoing artifact audit/status reporting across lifecycle phases.
  - Deterministic output files for automation and AI prompt handoff.
- Out of scope:
  - Hosting or UI framework decisions (CLI-first in v0).
  - Remote synchronization and multi-user conflict resolution.

## Core Definitions
- `Project Coach`: CLI application that initializes and audits `.cortex/` artifacts in a target project.
- `Lifecycle Manifest`: machine-readable contract for project metadata and phase completion.
- `Bootstrap`: first-run operation creating required artifact skeletons and starter prompts.
- `Audit`: repeated operation validating artifact existence and schema conformance.

## Determinism and Drift Tests
- Bootstrap determinism: running `init` twice without changes must not rewrite existing files unless `--force` is used.
- Audit determinism: identical project state must produce identical normalized audit status except timestamp fields.
- Schema drift test: design ontology JSON in target project must validate against the canonical schema.

## Governance Rules
- Versioning:
  - New behavior requires a new script/spec version (`vN`).
- Fail closed:
  - Missing required files or invalid schema status is reported as `fail`.
- Boundary discipline:
  - Project Coach mutates only `.cortex/` paths in target projects.
  - Existing user files outside `.cortex/` are never rewritten.

## Failure Modes
- Target project lacks write permissions for `.cortex/`.
- Design DSL compiles but generated JSON fails schema constraints.
- Lifecycle manifest exists but version mismatches required format.

## Success Criteria (v0)
- CLI exists at `scripts/cortex_project_coach_v0.py`.
- `init` command scaffolds `.cortex/` with required files.
- `audit` command emits `.cortex/reports/lifecycle_audit_v0.json`.
- Audit includes design ontology schema validation result.
- `coach` command emits cycle action artifacts (`.json`, `.md`, AI prompt) for iterative maintenance.
- `coach --apply` generates deterministic draft `vN+1` artifacts for eligible action targets under `.cortex/artifacts/` and logs applied/skipped outcomes.
- `coach --apply-scope` constrains draft generation by artifact class (`direction`, `governance`, `design`) with fail-closed validation on unknown scopes.

## Immediate Next Step
Add an optional service wrapper (HTTP or TUI) that calls the same `init` and `audit` operations for non-CLI workflows.

# Design Prompt DSL Spec

Version: v0
Status: Experimental
Inputs:
- `specs/design_ontology_schema_spec_v0.md` core design ontology semantics and constraints
- `templates/design_ontology_v0.schema.json` canonical target schema
- `templates/modern_web_design_vocabulary_v0.json` mapped design token registry
- `scripts/design_prompt_dsl_compile_v0.py` reference compiler
- `templates/design_prompt_dsl_example_v0.dsl` canonical DSL example

## Purpose
Define a compact, high-signal DSL that compiles into design ontology JSON artifacts, enabling rapid authoring while preserving strict structure and token-to-field correctness.

## Scope
- In scope:
  - DSL directives and parse rules for authoring design specs
  - Compilation contract into design ontology JSON
  - Vocabulary token mapping enforcement
- Out of scope:
  - Runtime rendering engines or direct HTML/CSS generation
  - Non-design domains outside the design ontology

## Core Definitions
- `Design Prompt DSL`: Line-oriented authoring format for design ontology artifacts.
- `Directive`: One DSL command (`id`, `version`, `name`, `token`, `set`, `add`, `score`).
- `Token Binding`: A `token` directive whose text must exist in vocabulary and map to the same schema field.
- `Compiled Artifact`: Deterministically serialized JSON output from the DSL compiler.

## Determinism and Drift Tests
- Parse determinism: identical DSL input must produce byte-identical JSON output (stable key ordering).
- Token mapping determinism: token text must resolve to exactly one `maps_to` path.
- Required-path drift test: compiler must fail when required ontology paths are missing.
- Unsupported directive test: unknown directives must fail closed with line-level error.

## Governance Rules
- DSL versioning:
  - Semantic directive changes require `vN -> vN+1` spec and compiler update.
- Fail closed:
  - Unknown tokens, path mismatches, invalid score ranges, and missing required paths are hard failures.
- Vocabulary discipline:
  - `token` directives must bind only through `templates/modern_web_design_vocabulary_v0.json`.
- Output discipline:
  - Compiler output must be valid JSON and schema-targeted for `templates/design_ontology_v0.schema.json`.

## Failure Modes
- Token text exists but maps to a different field than declared in DSL.
- Freeform `set` values degrade quality despite structural validity.
- DSL files drift from schema evolution without coordinated compiler updates.

## Success Criteria (v0)
- Compiler exists and runs: `scripts/design_prompt_dsl_compile_v0.py`.
- Example DSL compiles to JSON successfully.
- Compiled JSON validates against the design ontology schema.
- Token-path mismatch produces explicit error with line reference.

## Immediate Next Step
Add a validation runner that compiles all DSL files under `templates/`, validates compiled outputs against schema, and emits a consolidated report artifact.

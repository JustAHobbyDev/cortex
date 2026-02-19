# Design Ontology Schema Spec

Version: v0
Status: Experimental
Inputs:
- `README.md` repository purpose and admission criteria
- `philosophy/ontology_architecture_map_v0.md` layer model and ontology/schema boundary
- `specs/spec_spec_v0.md` required spec structure and governance inheritance
- `templates/design_ontology_v0.schema.json` L4 validation contract
- `templates/design_ontology_example_v0.json` canonical example instance
- `templates/modern_web_design_vocabulary_v0.json` reusable high-signal token glossary mapped to schema fields

## Purpose
Define a reusable ontology-aligned representation for visual design intent so visual references can be translated into precise language and then into machine-checkable specs for downstream AI generation.

## Scope
- In scope:
  - L3/L4 contract for design artifacts centered on layout, typography, surface, motion, and influence
  - Required and optional fields for composable design specs
  - Validation constraints for deterministic interchange and quality scoring metadata
- Out of scope:
  - Runtime rendering implementation details (CSS, JS, framework-specific code)
  - Evaluation policy for model output quality beyond declared target fields
  - Design asset binaries (images, videos, source Figma files)

## Core Definitions
- `Design Spec Artifact`: A structured description of visual intent with constrained language suitable for AI consumption.
- `Design Ontology`: The semantic model of design dimensions (`layout`, `typography`, `surface`, `motion`, `influence`) and cross-cutting metadata.
- `Schema Contract`: JSON Schema that validates representation integrity for design artifacts.
- `Composition`: Inheritance and override references enabling reuse across related design specs.
- Layer alignment:
  - L3: design semantics, relations, and meaning categories.
  - L4: JSON serialization and validation rules in `templates/design_ontology_v0.schema.json`.
  - L5: concrete instances such as `templates/design_ontology_example_v0.json`.

## Determinism and Drift Tests
- Validation determinism: any compliant instance must pass schema validation identically across repeat runs.
- Key-set determinism: no undeclared keys are allowed (`additionalProperties: false`) across top-level and constrained nested objects.
- Required-field drift test: missing core sections (`layout`, `typography`, `surface`, `motion`, `influence`) must fail closed.
- Enumeration drift test: constrained categorical fields (`density`, `depth_model`, override list) must reject unknown values unless version-bumped.
- Composition drift test: inherited references must preserve stable ID format and bounded cardinality.

## Governance Rules
- Versioning:
  - Semantic schema changes require monotonic version increments (`vN -> vN+1`) and a new schema file.
  - Example instances must declare matching `version`.
- Boundary discipline:
  - L3 meaning changes (new dimensions, altered semantics) require coordinated update of both this spec and the schema artifact.
  - L4 representation changes must not silently redefine existing fields.
- Fail-closed posture:
  - Unknown keys or invalid enums are invalid by default.
  - Missing required sections block ingestion.
- Reuse constraints:
  - Composition links (`inherits_from`) are ID references only; no implicit merge semantics are assumed outside consuming tools.
- Language quality:
  - Field content should be concrete, observable design language rather than vague adjectives.

## Failure Modes
- Artifacts using ambiguous terms without system-level fields (e.g., only "modern and clean" descriptors).
- Schema-compliant but semantically weak artifacts with non-observable language.
- Unversioned semantic expansion of enum fields causing downstream parser mismatch.
- Composition references that point to non-existent IDs in a managed registry.

## Success Criteria (v0)
- A stable L4 JSON Schema exists at `templates/design_ontology_v0.schema.json`.
- At least one canonical artifact validates against the schema (`templates/design_ontology_example_v0.json`).
- The five primary design dimensions are mandatory and explicitly modeled.
- Composition and quality targets are represented without weakening core required dimensions.

## Immediate Next Step
Add an index/registry artifact for design spec IDs and wire a validation playbook that checks schema compliance plus a minimum language-quality lint over required descriptive fields.

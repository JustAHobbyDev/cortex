# Design Ontology Validation Runbook v0

## Purpose

Provide a deterministic validation loop for design ontology artifacts so new specs are structurally valid, schema-compatible, and minimally high-signal before downstream AI usage.

## Scope

- Validate JSON syntax for design ontology instances.
- Validate schema conformance against `templates/design_ontology_v0.schema.json`.
- Enforce lightweight language-quality checks on required descriptive fields.
- Produce auditable run outputs for repeated checks.

## Inputs

- `templates/design_ontology_v0.schema.json`
- One or more instance files matching pattern:
  - .cortex/templates/design_ontology_*.json
  - Excluding `templates/design_ontology_v0.schema.json`

## Output Artifacts

- .cortex/reports/design_ontology_validation_v0.json
- .cortex/reports/design_ontology_validation_v0.md

## Preconditions

1. `jq` is installed.
2. Python 3 with `jsonschema` package is available for automated validation.
3. Repository root is current working directory.

## Validation Criteria (v0)

1. JSON syntax validity:
   - Every instance must parse with `jq`.
2. Schema validity:
   - Every instance must validate against `templates/design_ontology_v0.schema.json`.
3. Required language quality:
   - Required fields must be non-empty and not vague-only phrases.
   - Required paths:
     - `layout.grid`
     - `layout.spacing`
     - `layout.structure`
     - `typography.hero`
     - `typography.body`
     - `surface.base`
     - `surface.accent`
     - `motion.scroll`
     - `motion.hover`
     - `influence.primary`
4. Fail-closed behavior:
   - Any syntax, schema, or quality failure marks run status `fail`.

## Execution Flow

1. Run the automated validator:
   ```bash
   python3 scripts/design_ontology_validate_v0.py
   ```
2. Create report directory (only needed for manual flow):
   ```bash
   mkdir -p reports
   ```
3. List candidate instances:
   ```bash
   rg --files templates | rg '^templates/design_ontology_.*\.json$' | rg -v 'design_ontology_v0\.schema\.json$'
   ```
4. Syntax check each instance:
   ```bash
   jq empty templates/design_ontology_example_v0.json
   ```
5. Schema check each instance:
   ```bash
   python3 -c 'import json, jsonschema; s=json.load(open("templates/design_ontology_v0.schema.json")); i=json.load(open("templates/design_ontology_example_v0.json")); jsonschema.validate(instance=i, schema=s)'
   ```
6. Language-quality lint (manual or scripted):
   - Reject placeholder-style strings like:
     - `modern`, `clean`, `nice`, `good`, `cool`
   - Accept only observable design language (for example: grid size, spacing rhythm, concrete motion behavior, specific typographic treatment).
7. Write machine report:
   - Include timestamp, checked files, pass/fail per gate, and failure reasons.
8. Write human summary:
   - Include concise findings and corrective actions.

## Recommended Report JSON Shape

```json
{
  "version": "v0",
  "run_at": "2026-02-19T00:00:00Z",
  "schema_path": "templates/design_ontology_v0.schema.json",
  "instances_checked": [
    "templates/design_ontology_example_v0.json"
  ],
  "results": [
    {
      "instance": "templates/design_ontology_example_v0.json",
      "syntax": "pass",
      "schema": "pass",
      "language_quality": "pass",
      "notes": []
    }
  ],
  "status": "pass"
}
```

## Determinism Rules

- Always sort instance paths lexicographically before validation.
- Always use UTC ISO-8601 timestamps in reports.
- Keep stable key ordering in report JSON for diff readability.
- Never skip failed files; include explicit failure records.

## Failure Modes

- JSON parses but schema rejects unknown keys.
- Schema passes but required language fields use vague adjectives only.
- New instance files are added outside naming pattern and not checked.
- Reports are overwritten without retaining git diff trace.

## Definition of Done

- [ ] All target instances parsed by `jq`.
- [ ] All target instances validated against schema.
- [ ] Required descriptive fields passed quality lint.
- [ ] Both report files generated under `.cortex/reports/`.
- [ ] Any failures include actionable field-level reasons.

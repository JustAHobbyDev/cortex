# Cortex Coach Stage 1 Steering Quality Plan v0

## Purpose

Define a guided Stage 1 flow so users can provide higher-quality steering inputs (outcomes, constraints, priorities, success signals) before downstream agent execution.

## Problem

Current Stage 1 is scaffolded through templates, but lacks interactive quality guidance and enforcement thresholds.

## Scope

- In scope:
  - structured Stage 1 intake prompts
  - quality scoring for steering artifacts
  - coach feedback loops for weak inputs
  - gating options before progression
- Out of scope:
  - replacing human intent with automatic goal selection
  - domain-specific strategic advising beyond quality guardrails (v0)

## Planned Deliverables

1. Stage 1 intake contract
- Machine-readable file in `.cortex/artifacts/` for:
  - outcome statements
  - constraints
  - priority ranking
  - measurable success signals

2. Quality rubric
- Score dimensions:
  - clarity
  - measurability
  - constraint completeness
  - priority explicitness
- Emit score summary and improvement prompts.

3. Coach guidance mode
- New `coach` output section for Stage 1 refinement actions.
- Suggest concrete edits when rubric scores are below threshold.

4. Optional progression gate
- Configurable rule: block certain actions (for example `--apply`) when Stage 1 quality is below threshold.

## Execution Steps

1. Add Stage 1 intake artifact template.
2. Implement rubric evaluator in `coach`.
3. Add Stage 1 findings/actions to cycle report.
4. Add optional gating flag and enforcement logic.
5. Update user docs with Stage 1 quality workflow.

## Validation Plan

- High-quality input set => pass with no blocking findings.
- Ambiguous input set => low scores and targeted improvement actions.
- Missing success signals => gating behavior verified when enabled.

## Commit Plan

1. Intake/rubric contracts + evaluator.
2. Coach integration + optional gate.
3. Docs and examples.

## Status

Saved, not yet executed.

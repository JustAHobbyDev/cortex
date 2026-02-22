# Project State Boundary Migration v0

Version: v0  
Status: Complete  
Scope: repository project-state artifact relocation into `.cortex/`

## Summary

Moved legacy project-state reports from top-level `reports/` into `.cortex/reports/` so boundary enforcement can fail closed.

## Relocated Artifacts

- `reports/beads_comparative_research_report_v0.md` -> `.cortex/reports/project_state/beads_comparative_research_report_v0.md`
- `reports/cortex_coach_decoupling_closeout_v1.md` -> `.cortex/reports/project_state/cortex_coach_decoupling_closeout_v1.md`
- `reports/mulch_beads_synthesized_plan_proposal_v0.md` -> `.cortex/reports/project_state/mulch_beads_synthesized_plan_proposal_v0.md`
- `reports/mulch_comparative_research_report_v0.md` -> `.cortex/reports/project_state/mulch_comparative_research_report_v0.md`
- `reports/mulch_integration_strategy_report_v0.md` -> `.cortex/reports/project_state/mulch_integration_strategy_report_v0.md`
- `reports/ph0_004_adapter_safety_reviewer_pass_v0.md` -> `.cortex/reports/project_state/ph0_004_adapter_safety_reviewer_pass_v0.md`
- `reports/ph0_005_enforcement_ladder_mapping_evidence_v0.md` -> `.cortex/reports/project_state/ph0_005_enforcement_ladder_mapping_evidence_v0.md`
- `reports/phase3_parity_check_report_v0.md` -> `.cortex/reports/project_state/phase3_parity_check_report_v0.md`
- `reports/design_ontology_validation_v0.json` -> `.cortex/reports/design_ontology_validation_v0.json`
- `reports/design_ontology_validation_v0.md` -> `.cortex/reports/design_ontology_validation_v0.md`

## Follow-up

- Boundary gate is now mandatory in local/CI quality gates.
- New exceptions require explicit waiver records in `.cortex/policies/project_state_boundary_waivers_v0.json`.

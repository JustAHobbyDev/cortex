# Decision: Formalize Swarm-GDD baseline gates and adoption stop-rule

DecisionID: dec_20260223T051831Z_formalize_swarm_gdd_base
Status: Active
Scope: project/cortex_repo
CapturedAt: 2026-02-23T05:18:31Z
PromotedAt: 2026-02-23T05:18:33Z
ImpactScope: governance, workflow, runtime
LinkedArtifacts:
- `.cortex/reports/project_state/ph0_011_swarm_gdd_baseline_closeout_v0.md`
- `.cortex/reports/project_state/ph0_011_swarm_gdd_gate_sequence_verification_note_v0.md`
- `playbooks/cortex_vision_master_roadmap_v1.md`
- `playbooks/cortex_phase0_governance_ticket_breakdown_v0.md`
- `scripts/quality_gate_ci_v0.sh`
- `scripts/reflection_enforcement_gate_v0.py`

## Context
- Captured via `cortex-coach decision-capture`.

## Decision
Define PH0-011 Swarm-GDD baseline with normative swarm governance rules, explicit local/CI gate mapping, adoption stop-rule, and a verified end-to-end closeout sequence artifact.

## Rationale
This makes swarm adoption fail-closed, preserves governance-plane authority, and prevents premature default-on swarm rollout.

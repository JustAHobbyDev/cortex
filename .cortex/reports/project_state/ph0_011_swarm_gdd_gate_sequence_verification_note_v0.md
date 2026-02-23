# PH0-011 Swarm-GDD Gate Sequence Verification Note v0

Version: v0  
Status: Accepted  
Date: 2026-02-23  
Scope: End-to-end intended gate sequence for swarm-governed closeout

## Purpose

Capture a concrete, deterministic closeout sequence for governance-impacting work performed in swarm mode, proving the required gate order and non-bypass rules.

## Sequence (Normative)

1. Capture and promote governance decision with linked reflection artifact.
2. Run `python3 scripts/cortex_project_coach_v0.py decision-gap-check --project-dir . --format json`.
3. Run `python3 scripts/reflection_enforcement_gate_v0.py --project-dir . --required-decision-status promoted --min-scaffold-reports 1 --min-required-status-mappings 1 --format json`.
4. Run `python3 scripts/cortex_project_coach_v0.py audit --project-dir . --audit-scope all --format json`.
5. Run `./scripts/quality_gate_v0.sh` locally before push when possible.
6. Run `./scripts/quality_gate_ci_v0.sh` in CI/release boundary.

## Local and CI Mapping

- Local gate bundle source: `scripts/quality_gate_v0.sh`
- CI gate bundle source: `scripts/quality_gate_ci_v0.sh`
- Mapping contract source: `playbooks/cortex_vision_master_roadmap_v1.md` (`Swarm Gate Execution Mapping (PH0-011)`)

## Expected Outcomes

1. Decision/reflection linkage is complete for governance-impact files.
2. No governance-impact closure is accepted from swarm outputs alone without promotion.
3. Kill-switch degradation path (`swarm -> single-agent -> governance-only`) remains valid and non-bypassing.
4. Merge/release remains blocked if any required swarm gate fails.

## Verification Summary

PH0-011 verifies that swarm execution remains tactical acceleration only; canonical closure authority remains in governance plane artifacts and required gate passes.

from __future__ import annotations

import json
import sys
from pathlib import Path

from conftest import REPO_ROOT, run_cmd


MISTAKE_GATE_SCRIPT = REPO_ROOT / "scripts" / "mistake_candidate_gate_v0.py"
MISTAKE_CONTRACT_FILE = REPO_ROOT / "contracts" / "mistake_candidate_schema_v0.json"


def run_mistake_gate(project_dir: Path, expect_code: int = 0) -> dict:
    proc = run_cmd(
        [
            sys.executable,
            str(MISTAKE_GATE_SCRIPT),
            "--project-dir",
            str(project_dir),
            "--contract-file",
            str(MISTAKE_CONTRACT_FILE),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expect_code=expect_code,
    )
    return json.loads(proc.stdout)


def write_candidate_file(project_dir: Path, candidates: list[dict]) -> None:
    candidate_file = project_dir / ".cortex" / "reports" / "mistake_candidates_v0.json"
    candidate_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "v0",
        "candidates": candidates,
    }
    candidate_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def machine_candidate(**overrides: object) -> dict:
    base: dict[str, object] = {
        "candidate_id": "mc_001",
        "summary": "Machine detected a policy violation during automated checks.",
        "detected_by": "machine",
        "detector": {
            "name": "reflection_enforcement_gate_v0.py",
            "version": "v0",
            "run_ref": "run_20260223T000000Z",
        },
        "evidence_refs": [".cortex/reports/reflection_scaffold_ph0_011_swarm_gdd_baseline_v0.json"],
        "rule_violated": "decision_reflection_linkage_required",
        "confidence": "high",
        "status": "candidate",
    }
    base.update(overrides)
    return base


def test_mistake_candidate_gate_passes_for_valid_machine_claim(initialized_project: Path) -> None:
    write_candidate_file(initialized_project, [machine_candidate()])
    payload = run_mistake_gate(initialized_project)

    assert payload["status"] == "pass"
    assert payload["finding_count"] == 0
    assert payload["machine_claim_count"] == 1


def test_mistake_candidate_gate_fails_for_machine_claim_missing_evidence(initialized_project: Path) -> None:
    write_candidate_file(initialized_project, [machine_candidate(evidence_refs=[])])
    payload = run_mistake_gate(initialized_project, expect_code=1)
    checks = {finding["check"] for finding in payload["findings"]}

    assert payload["status"] == "fail"
    assert "machine_claim_missing_evidence" in checks


def test_mistake_candidate_gate_fails_for_unsupported_confidence_and_status(initialized_project: Path) -> None:
    write_candidate_file(initialized_project, [machine_candidate(confidence="certain", status="new")])
    payload = run_mistake_gate(initialized_project, expect_code=1)
    checks = {finding["check"] for finding in payload["findings"]}

    assert payload["status"] == "fail"
    assert "unsupported_confidence_value" in checks
    assert "unsupported_status_value" in checks

from __future__ import annotations

import json
import sys
from pathlib import Path

from conftest import REPO_ROOT, run_cmd, run_coach


REFLECTION_GATE_SCRIPT = REPO_ROOT / "scripts" / "reflection_enforcement_gate_v0.py"


def run_reflection_gate(project_dir: Path, *args: str, expect_code: int = 0) -> dict:
    proc = run_cmd(
        [
            sys.executable,
            str(REFLECTION_GATE_SCRIPT),
            "--project-dir",
            str(project_dir),
            "--format",
            "json",
            *args,
        ],
        cwd=REPO_ROOT,
        expect_code=expect_code,
    )
    return json.loads(proc.stdout)


def test_reflection_enforcement_fails_for_promoted_decision_without_reflection(initialized_project: Path) -> None:
    capture = run_coach(
        initialized_project,
        "decision-capture",
        "--title",
        "Promoted decision missing reflection",
        "--decision",
        "Use promoted decisions for governance checks.",
        "--impact-scope",
        "governance",
        "--linked-artifacts",
        ".cortex/manifest_v0.json",
        "--format",
        "json",
    )
    decision_id = json.loads(capture.stdout)["decision_id"]
    run_coach(initialized_project, "decision-promote", "--decision-id", decision_id, "--format", "json")

    payload = run_reflection_gate(initialized_project, expect_code=1)
    checks = {f["check"] for f in payload["findings"]}

    assert payload["status"] == "fail"
    assert "missing_reflection_id" in checks
    assert "missing_reflection_report" in checks
    assert "insufficient_scaffold_reports" in checks
    assert "insufficient_required_status_mappings" in checks


def test_reflection_enforcement_fails_when_matched_governance_decision_lacks_reflection(
    initialized_project: Path,
) -> None:
    manifest = initialized_project / ".cortex" / "manifest_v0.json"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    run_coach(
        initialized_project,
        "decision-capture",
        "--title",
        "Match manifest change",
        "--decision",
        "Manifest changes are intentional.",
        "--impact-scope",
        "governance",
        "--linked-artifacts",
        ".cortex/manifest_v0.json",
        "--format",
        "json",
    )

    payload = run_reflection_gate(
        initialized_project,
        "--required-decision-status",
        "candidate",
        "--min-scaffold-reports",
        "0",
        "--min-required-status-mappings",
        "0",
        expect_code=1,
    )
    matched_missing = [
        f
        for f in payload["findings"]
        if f.get("check") == "missing_reflection_id" and f.get("context") == "matched_governance_change"
    ]

    assert payload["status"] == "fail"
    assert matched_missing


def test_reflection_enforcement_passes_with_scaffold_and_promoted_reflection_linkage(
    initialized_project: Path,
) -> None:
    report_path = ".cortex/reports/reflection_scaffold_manifest_guard_v0.json"
    scaffold = run_coach(
        initialized_project,
        "reflection-scaffold",
        "--title",
        "Backfill reflection linkage",
        "--mistake",
        "Governance decision had no reflection linkage.",
        "--pattern",
        "Operating decisions were promoted without reflection metadata.",
        "--rule",
        "Every governance-impacting promoted decision must include reflection metadata.",
        "--linked-artifacts",
        ".cortex/manifest_v0.json",
        "--no-auto-link-governance-dirty",
        "--out-file",
        report_path,
        "--format",
        "json",
    )
    reflection = json.loads(scaffold.stdout)

    manifest = initialized_project / ".cortex" / "manifest_v0.json"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    capture = run_coach(
        initialized_project,
        "decision-capture",
        "--title",
        "Track manifest change with reflection",
        "--decision",
        "Manifest changes require explicit governance traceability.",
        "--impact-scope",
        "governance",
        "--linked-artifacts",
        ".cortex/manifest_v0.json",
        "--reflection-id",
        reflection["reflection_id"],
        "--reflection-report",
        report_path,
        "--format",
        "json",
    )
    decision_id = json.loads(capture.stdout)["decision_id"]
    run_coach(initialized_project, "decision-promote", "--decision-id", decision_id, "--format", "json")

    payload = run_reflection_gate(initialized_project)
    assert payload["status"] == "pass"
    assert payload["findings"] == []

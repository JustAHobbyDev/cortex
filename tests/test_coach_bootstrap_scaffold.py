from __future__ import annotations

import json
import sys
from pathlib import Path

from conftest import COACH_SCRIPT, REPO_ROOT, init_git_repo, run_cmd, run_coach


def test_bootstrap_scaffold_creates_checklist_and_report(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_bootstrap_scaffold"
    project_dir.mkdir(parents=True, exist_ok=True)
    init_git_repo(project_dir)

    proc = run_cmd(
        [
            sys.executable,
            str(COACH_SCRIPT),
            "bootstrap-scaffold",
            "--project-dir",
            str(project_dir),
            "--project-id",
            "demo_bootstrap",
            "--project-name",
            "Demo Bootstrap",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )

    payload = json.loads(proc.stdout)
    assert payload["status"] == "pass"
    assert payload["command"] == "bootstrap-scaffold"
    assert payload["format_source"] == "delegator_bootstrap_scaffolder_v0"

    result = payload["result"]
    checklist = project_dir / result["checklist_path"]
    report = project_dir / result["report_path"]
    assert checklist.exists()
    assert report.exists()
    assert any("quality_gate_ci_v0.sh" in cmd for cmd in result["first_green_gate_commands"])
    assert (project_dir / "contracts/context_hydration_receipt_schema_v0.json").exists()
    assert (project_dir / "contracts/project_state_boundary_contract_v0.json").exists()
    assert (project_dir / ".cortex/reports/lifecycle_audit_v0.json").exists()
    assert (project_dir / ".cortex/reports/decision_candidates_v0.json").exists()
    assert (project_dir / "policies/cortex_coach_final_ownership_boundary_v0.md").exists()
    assert (project_dir / "policies/project_state_boundary_policy_v0.md").exists()
    assert (project_dir / "playbooks/cortex_vision_master_roadmap_v1.md").exists()

    report_payload = json.loads(report.read_text(encoding="utf-8"))
    assert report_payload["status"] == "pass"
    assert report_payload["missing_required_paths"] == []


def test_bootstrap_scaffold_skip_init_fails_when_required_paths_missing(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_bootstrap_skip_init_fail"
    project_dir.mkdir(parents=True, exist_ok=True)
    init_git_repo(project_dir)

    proc = run_cmd(
        [
            sys.executable,
            str(COACH_SCRIPT),
            "bootstrap-scaffold",
            "--project-dir",
            str(project_dir),
            "--project-id",
            "demo_bootstrap",
            "--project-name",
            "Demo Bootstrap",
            "--skip-init",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expect_code=3,
    )

    payload = json.loads(proc.stdout)
    assert payload["status"] == "fail"
    assert ".cortex/manifest_v0.json" in payload["result"]["missing_required_paths"]


def test_bootstrap_scaffold_skip_init_passes_for_initialized_project(initialized_project: Path) -> None:
    proc = run_coach(
        initialized_project,
        "bootstrap-scaffold",
        "--project-id",
        "demo",
        "--project-name",
        "Demo",
        "--skip-init",
        "--format",
        "json",
    )
    payload = json.loads(proc.stdout)
    assert payload["status"] == "pass"

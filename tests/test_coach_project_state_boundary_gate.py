from __future__ import annotations

import json
import sys
from pathlib import Path

from conftest import REPO_ROOT, run_cmd


BOUNDARY_GATE_SCRIPT = REPO_ROOT / "scripts" / "project_state_boundary_gate_v0.py"
BOUNDARY_CONTRACT_FILE = REPO_ROOT / "contracts" / "project_state_boundary_contract_v0.json"


def run_boundary_gate(project_dir: Path, expect_code: int = 0) -> dict:
    proc = run_cmd(
        [
            sys.executable,
            str(BOUNDARY_GATE_SCRIPT),
            "--project-dir",
            str(project_dir),
            "--contract-file",
            str(BOUNDARY_CONTRACT_FILE),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expect_code=expect_code,
    )
    return json.loads(proc.stdout)


def test_boundary_gate_fails_for_tracked_reports_file_outside_cortex(initialized_project: Path) -> None:
    reports_dir = initialized_project / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "bad_report.md").write_text("bad", encoding="utf-8")

    run_cmd(["git", "add", "reports/bad_report.md"], cwd=initialized_project)
    run_cmd(["git", "commit", "-m", "add bad report"], cwd=initialized_project)

    payload = run_boundary_gate(initialized_project, expect_code=1)
    violating_paths = [v["path"] for v in payload["violations"]]

    assert payload["status"] == "fail"
    assert "reports/bad_report.md" in violating_paths


def test_boundary_gate_passes_for_project_state_inside_cortex(initialized_project: Path) -> None:
    path = initialized_project / ".cortex" / "reports" / "project_state" / "ok_report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("ok", encoding="utf-8")

    payload = run_boundary_gate(initialized_project)
    assert payload["status"] == "pass"
    assert payload["violation_count"] == 0


def test_boundary_gate_fails_for_expired_active_waiver(initialized_project: Path) -> None:
    reports_dir = initialized_project / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "legacy.md").write_text("legacy", encoding="utf-8")

    waiver_file = initialized_project / ".cortex" / "policies" / "project_state_boundary_waivers_v0.json"
    waiver_file.parent.mkdir(parents=True, exist_ok=True)
    waiver_file.write_text(
        json.dumps(
            {
                "version": "v0",
                "waivers": [
                    {
                        "path": "reports/legacy.md",
                        "reason": "temporary migration",
                        "decision_id": "dec_test",
                        "owner": "test",
                        "expires_on": "2026-01-01",
                        "status": "active",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    payload = run_boundary_gate(initialized_project, expect_code=1)
    checks = [f["check"] for f in payload["findings"]]
    assert payload["status"] == "fail"
    assert "expired_active_waiver" in checks

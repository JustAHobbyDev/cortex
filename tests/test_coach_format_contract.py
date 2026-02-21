from __future__ import annotations

import json
import sys
from pathlib import Path

from conftest import COACH_SCRIPT, REPO_ROOT, init_git_repo, run_cmd, run_coach


def test_init_supports_json_format_via_delegator(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_init_json_format"
    project_dir.mkdir(parents=True, exist_ok=True)
    init_git_repo(project_dir)

    proc = run_cmd(
        [
            sys.executable,
            str(COACH_SCRIPT),
            "init",
            "--project-dir",
            str(project_dir),
            "--project-id",
            "demo",
            "--project-name",
            "Demo",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )

    payload = json.loads(proc.stdout)
    assert payload["status"] == "pass"
    assert payload["command"] == "init"
    assert payload["created_or_updated_files"] >= 1
    assert payload["format_source"] == "delegator_compat_shim_v0"


def test_audit_supports_json_format_via_delegator(initialized_project: Path) -> None:
    proc = run_coach(initialized_project, "audit", "--format", "json")
    payload = json.loads(proc.stdout)

    assert payload["status"] == "pass"
    assert payload["audit_scope"] == "cortex-only"
    assert payload["format_source"] == "delegator_compat_shim_v0"


def test_audit_text_format_is_backward_compatible(initialized_project: Path) -> None:
    proc = run_coach(initialized_project, "audit", "--format", "text")
    assert ".cortex/reports/lifecycle_audit_v0.json" in proc.stdout


def test_policy_enable_supports_json_format_via_delegator(initialized_project: Path) -> None:
    proc = run_coach(
        initialized_project,
        "policy-enable",
        "--policy",
        "usage-decision",
        "--force",
        "--format",
        "json",
    )
    payload = json.loads(proc.stdout)

    assert payload["status"] == "pass"
    assert payload["command"] == "policy-enable"
    policy_path = payload["policy_path"]
    assert policy_path.endswith(".cortex/policies/cortex_coach_usage_decision_policy_v0.md")
    assert Path(policy_path).exists()


def test_context_load_supports_explicit_json_format_via_delegator(initialized_project: Path) -> None:
    proc = run_coach(
        initialized_project,
        "context-load",
        "--task",
        "governance",
        "--max-files",
        "2",
        "--max-chars-per-file",
        "200",
        "--fallback-mode",
        "priority",
        "--format",
        "json",
    )
    payload = json.loads(proc.stdout)

    assert payload["version"] == "v0"
    assert payload["selected_file_count"] >= 1
    assert any(file_entry["selected_by"] == "control_plane" for file_entry in payload["files"])

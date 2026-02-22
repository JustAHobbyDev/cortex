from __future__ import annotations

import json
import sys
from pathlib import Path

from conftest import REPO_ROOT, run_cmd


SYNC_CHECK_SCRIPT = REPO_ROOT / "scripts" / "quality_gate_sync_check_v0.py"
CI_GATE_SCRIPT = REPO_ROOT / "scripts" / "quality_gate_ci_v0.sh"
LOCAL_GATE_SCRIPT = REPO_ROOT / "scripts" / "quality_gate_v0.sh"


def run_sync_check(ci_script: Path, local_script: Path, expect_code: int = 0) -> dict:
    proc = run_cmd(
        [
            sys.executable,
            str(SYNC_CHECK_SCRIPT),
            "--ci-script",
            str(ci_script),
            "--local-script",
            str(local_script),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        expect_code=expect_code,
    )
    return json.loads(proc.stdout)


def test_quality_gate_sync_check_passes_for_repo_scripts() -> None:
    payload = run_sync_check(CI_GATE_SCRIPT, LOCAL_GATE_SCRIPT)
    assert payload["status"] == "pass"
    assert payload["findings"] == []


def test_quality_gate_sync_check_fails_when_shared_command_drifts(tmp_path: Path) -> None:
    ci_copy = tmp_path / "quality_gate_ci_v0.sh"
    local_copy = tmp_path / "quality_gate_v0.sh"
    ci_copy.write_text(CI_GATE_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    local_copy.write_text(LOCAL_GATE_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")

    local_text = local_copy.read_text(encoding="utf-8")
    local_copy.write_text(
        local_text.replace(
            "python3 scripts/temporal_playbook_release_gate_v0.py",
            "python3 scripts/temporal_playbook_release_gate_v1.py",
            1,
        ),
        encoding="utf-8",
    )

    payload = run_sync_check(ci_copy, local_copy, expect_code=1)
    checks = {finding["check"] for finding in payload["findings"]}
    assert payload["status"] == "fail"
    assert "shared_command_mismatch" in checks


def test_quality_gate_sync_check_fails_when_local_precheck_drifted(tmp_path: Path) -> None:
    ci_copy = tmp_path / "quality_gate_ci_v0.sh"
    local_copy = tmp_path / "quality_gate_v0.sh"
    ci_copy.write_text(CI_GATE_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    local_copy.write_text(LOCAL_GATE_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")

    local_text = local_copy.read_text(encoding="utf-8")
    local_copy.write_text(
        local_text.replace(
            "audit-needed --fail-on-required",
            "audit-needed",
            1,
        ),
        encoding="utf-8",
    )

    payload = run_sync_check(ci_copy, local_copy, expect_code=1)
    checks = {finding["check"] for finding in payload["findings"]}
    assert payload["status"] == "fail"
    assert "local_precheck_label_mismatch" in checks

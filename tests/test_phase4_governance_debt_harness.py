from __future__ import annotations

import json
import sys
from pathlib import Path

from conftest import REPO_ROOT, run_cmd


DEBT_HARNESS_SCRIPT = REPO_ROOT / "scripts" / "phase4_governance_debt_harness_v0.py"


def test_phase4_governance_debt_harness_generates_visibility_report(tmp_path: Path) -> None:
    out_file = tmp_path / "phase4_governance_debt_visibility_report_v0.json"
    proc = run_cmd(
        [
            sys.executable,
            str(DEBT_HARNESS_SCRIPT),
            "--project-dir",
            str(REPO_ROOT),
            "--out-file",
            str(out_file),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    payload = json.loads(proc.stdout)

    assert payload["status"] == "pass"
    assert out_file.exists()
    written = json.loads(out_file.read_text(encoding="utf-8"))
    assert written["artifact"] == "phase4_governance_debt_visibility_report_v0"
    assert written["summary"]["owner_coverage_rate"] == 1.0
    assert written["summary"]["next_action_coverage_rate"] == 1.0
    assert written["summary"]["required_visibility_coverage_rate"] == 1.0

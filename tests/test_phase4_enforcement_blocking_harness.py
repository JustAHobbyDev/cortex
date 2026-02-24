from __future__ import annotations

import json
import sys
from pathlib import Path

from conftest import REPO_ROOT, run_cmd


ENFORCEMENT_HARNESS_SCRIPT = REPO_ROOT / "scripts" / "phase4_enforcement_blocking_harness_v0.py"


def test_phase4_enforcement_blocking_harness_generates_pass_report(tmp_path: Path) -> None:
    out_file = tmp_path / "phase4_enforcement_blocking_report_v0.json"
    proc = run_cmd(
        [
            sys.executable,
            str(ENFORCEMENT_HARNESS_SCRIPT),
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
    assert written["artifact"] == "phase4_enforcement_blocking_report_v0"
    assert written["summary"]["unlinked_closure_block_rate"] == 1.0
    assert written["summary"]["linked_closure_false_block_rate"] <= 0.05

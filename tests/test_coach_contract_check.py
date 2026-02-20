from __future__ import annotations

import json
from pathlib import Path

from conftest import run_coach


def test_contract_check_passes_for_initialized_project(initialized_project: Path) -> None:
    proc = run_coach(initialized_project, "contract-check", "--format", "json")
    payload = json.loads(proc.stdout)
    assert payload["status"] == "pass"
    assert payload["checks"]
    assert all(item["status"] == "pass" for item in payload["checks"])


def test_contract_check_fails_when_required_path_missing(initialized_project: Path) -> None:
    registry = initialized_project / ".cortex" / "spec_registry_v0.json"
    registry.unlink()
    proc = run_coach(initialized_project, "contract-check", "--format", "json", expect_code=1)
    payload = json.loads(proc.stdout)
    assert payload["status"] == "fail"
    assert any(item["check"] == "required_path:.cortex/spec_registry_v0.json" for item in payload["checks"])

#!/usr/bin/env python3
"""Generate Phase 6 boundary conformance evidence for configurable project boundary."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_rel_path(project_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def _run_json_command(cmd: list[str], cwd: Path) -> tuple[dict[str, Any], int, str]:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=False)
    stderr = proc.stderr.strip()
    payload: dict[str, Any] = {}
    stdout = proc.stdout.strip()
    if stdout:
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            payload = {}
    return payload, proc.returncode, stderr


def _run_gate(
    python_bin: str,
    gate_script: Path,
    project_dir: Path,
    contract_file: Path,
) -> dict[str, Any]:
    payload, returncode, stderr = _run_json_command(
        [
            python_bin,
            str(gate_script),
            "--project-dir",
            str(project_dir),
            "--contract-file",
            str(contract_file),
            "--format",
            "json",
        ],
        cwd=project_dir,
    )
    status = str(payload.get("status", "unknown")) if payload else "unknown"
    return {
        "command": [
            python_bin,
            str(gate_script),
            "--project-dir",
            str(project_dir),
            "--contract-file",
            str(contract_file),
            "--format",
            "json",
        ],
        "returncode": returncode,
        "status": status,
        "stderr": stderr,
        "summary": payload.get("violation_count") if isinstance(payload, dict) else None,
        "payload": payload,
    }


def _write_contract(path: Path, project_state_root: str, forbidden_roots: list[str], waiver_file: str) -> None:
    payload = {
        "version": "v0",
        "project_state_root": project_state_root,
        "forbidden_outside_project_state_roots": forbidden_roots,
        "waiver_file": waiver_file,
    }
    _write_json(path, payload)


def _init_fixture_repo(base_dir: Path) -> Path:
    fixture = base_dir / "fixture_repo"
    fixture.mkdir(parents=True, exist_ok=True)
    (fixture / "reports").mkdir(parents=True, exist_ok=True)
    (fixture / ".cortex" / "policies").mkdir(parents=True, exist_ok=True)
    (fixture / "reports" / "synthetic_project_state.json").write_text("{\"ok\": true}\n", encoding="utf-8")
    _write_json(fixture / ".cortex" / "policies" / "project_state_boundary_waivers_v0.json", {"waivers": []})

    subprocess.run(["git", "init"], cwd=str(fixture), check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "phase6-boundary@example.com"], cwd=str(fixture), check=True)
    subprocess.run(["git", "config", "user.name", "Phase6 Boundary"], cwd=str(fixture), check=True)
    subprocess.run(["git", "add", "."], cwd=str(fixture), check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "phase6 boundary fixture"], cwd=str(fixture), check=True, capture_output=True)
    return fixture


def _render_text(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
        (
            "targets: "
            f"default_contract_pass={payload.get('target_results', {}).get('default_contract_pass_met', False)} "
            f"default_root_blocks_reports={payload.get('target_results', {}).get('default_root_blocks_reports_outside_boundary_met', False)} "
            f"override_root_allows_reports={payload.get('target_results', {}).get('override_root_allows_reports_boundary_met', False)}"
        ),
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument(
        "--out-file",
        default=".cortex/reports/project_state/phase6_boundary_conformance_report_v0.json",
    )
    parser.add_argument("--format", default="text", choices=("text", "json"))
    parser.add_argument("--fail-on-target-miss", action="store_true")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    gate_script = (project_dir / "scripts" / "project_state_boundary_gate_v0.py").resolve()
    default_contract = (project_dir / "contracts" / "project_state_boundary_contract_v0.json").resolve()

    default_repo_result = _run_gate(args.python_bin, gate_script, project_dir, default_contract)

    with tempfile.TemporaryDirectory(prefix="phase6_boundary_conformance_") as tmp_dir_text:
        tmp_dir = Path(tmp_dir_text)
        fixture_repo = _init_fixture_repo(tmp_dir)

        default_fixture_contract = fixture_repo / "contract_default.json"
        override_fixture_contract = fixture_repo / "contract_override.json"
        waiver_file = ".cortex/policies/project_state_boundary_waivers_v0.json"

        _write_contract(default_fixture_contract, ".cortex", ["reports"], waiver_file)
        default_fixture_result = _run_gate(args.python_bin, gate_script, fixture_repo, default_fixture_contract)

        _write_contract(override_fixture_contract, "reports", ["reports"], waiver_file)
        override_fixture_result = _run_gate(args.python_bin, gate_script, fixture_repo, override_fixture_contract)

    target_results = {
        "default_contract_pass_met": default_repo_result["status"] == "pass",
        "default_root_blocks_reports_outside_boundary_met": default_fixture_result["status"] == "fail",
        "override_root_allows_reports_boundary_met": override_fixture_result["status"] == "pass",
    }
    status = "pass" if all(target_results.values()) else "fail"

    payload: dict[str, Any] = {
        "artifact": "phase6_boundary_conformance_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "measurement_mode": "phase6_boundary_conformance_harness",
        "contract_sources": {
            "json_contract": _safe_rel_path(project_dir, default_contract),
            "markdown_contract": "contracts/project_state_boundary_contract_v0.md",
            "policy": "policies/project_state_boundary_policy_v0.md",
        },
        "checks": {
            "default_repo_contract": default_repo_result,
            "fixture_default_root": default_fixture_result,
            "fixture_override_root": override_fixture_result,
        },
        "targets": {
            "default_contract_pass": True,
            "default_root_blocks_reports_outside_boundary": True,
            "override_root_allows_reports_boundary": True,
        },
        "target_results": target_results,
        "status": status,
    }

    out_file = Path(args.out_file)
    if not out_file.is_absolute():
        out_file = (project_dir / out_file).resolve()
    _write_json(out_file, payload)
    payload["out_file"] = str(out_file)

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_render_text(payload))

    if args.fail_on_target_miss and status != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

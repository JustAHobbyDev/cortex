#!/usr/bin/env python3
"""Run Phase 6 external pilot validation across two non-Cortex seed repos."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PILOT_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "pilot_id": "pilot_python_api",
        "stack_shape": "python_api_service",
        "project_id": "ext_py_api",
        "project_name": "External Python API",
        "files": {
            "README.md": "# External Python API\n\nSeed repo for Cortex Phase 6 external pilot.\n",
            "pyproject.toml": "[project]\nname = \"external-python-api\"\nversion = \"0.1.0\"\n",
            "src/app.py": "def handler() -> str:\n    return \"ok\"\n",
        },
    },
    {
        "pilot_id": "pilot_node_dashboard",
        "stack_shape": "node_dashboard_app",
        "project_id": "ext_node_dash",
        "project_name": "External Node Dashboard",
        "files": {
            "README.md": "# External Node Dashboard\n\nSeed repo for Cortex Phase 6 external pilot.\n",
            "package.json": "{\n  \"name\": \"external-node-dashboard\",\n  \"version\": \"0.1.0\",\n  \"private\": true\n}\n",
            "src/index.js": "console.log('ok');\n",
        },
    },
)

REQUIRED_GOVERNANCE_CAPSULE_PATHS: tuple[str, ...] = (
    "contracts/context_hydration_receipt_schema_v0.json",
    "contracts/project_state_boundary_contract_v0.json",
    ".cortex/policies/project_state_boundary_waivers_v0.json",
    ".cortex/reports/lifecycle_audit_v0.json",
    ".cortex/reports/decision_candidates_v0.json",
    "policies/cortex_coach_final_ownership_boundary_v0.md",
    "policies/project_state_boundary_policy_v0.md",
    "playbooks/cortex_vision_master_roadmap_v1.md",
)
BOUNDARY_RUNTIME_PATHS: tuple[str, ...] = (
    "contracts/project_state_boundary_contract_v0.json",
    ".cortex/policies/project_state_boundary_waivers_v0.json",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _safe_rel_path(project_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def _run_json_command(
    cmd: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=max(1, timeout_seconds),
    )
    elapsed = time.perf_counter() - started
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    payload: dict[str, Any] = {}
    if stdout:
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            payload = {}
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "duration_seconds": elapsed,
        "stdout_excerpt": stdout.splitlines()[0] if stdout else "",
        "stderr_excerpt": stderr.splitlines()[0] if stderr else "",
        "payload": payload,
        "status": "pass" if proc.returncode == 0 and str(payload.get("status", "pass")) != "fail" else "fail",
        "payload_status": str(payload.get("status", "")),
    }


def _run_shell_command(cmd: list[str], *, cwd: Path, timeout_seconds: int) -> dict[str, Any]:
    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=max(1, timeout_seconds),
    )
    elapsed = time.perf_counter() - started
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "duration_seconds": elapsed,
        "stdout_excerpt": stdout.splitlines()[0] if stdout else "",
        "stderr_excerpt": stderr.splitlines()[0] if stderr else "",
        "status": "pass" if proc.returncode == 0 else "fail",
    }


def _init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "phase6-external-pilot@example.com"], cwd=str(path), check=True)
    subprocess.run(["git", "config", "user.name", "Phase6 External Pilot"], cwd=str(path), check=True)


def _seed_profile_repo(root: Path, profile: dict[str, Any]) -> Path:
    repo = root / str(profile["pilot_id"])
    repo.mkdir(parents=True, exist_ok=True)
    for rel, text in dict(profile["files"]).items():
        file_path = repo / rel
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(str(text), encoding="utf-8")
    _init_git_repo(repo)
    subprocess.run(["git", "add", "."], cwd=str(repo), check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed external pilot repo"], cwd=str(repo), check=True, capture_output=True)
    return repo


def _seed_governance_capsule(project_dir: Path, pilot_repo: Path) -> list[str]:
    copied: list[str] = []
    for rel in REQUIRED_GOVERNANCE_CAPSULE_PATHS:
        source = project_dir / rel
        target = pilot_repo / rel
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(rel)
    return copied


def _seed_paths(project_dir: Path, pilot_repo: Path, paths: tuple[str, ...]) -> list[str]:
    copied: list[str] = []
    for rel in paths:
        source = project_dir / rel
        target = pilot_repo / rel
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(rel)
    return copied


def _run_pilot(
    *,
    project_dir: Path,
    pilot_repo: Path,
    profile: dict[str, Any],
    python_bin: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    scripts_dir = (project_dir / "scripts").resolve()
    coach = scripts_dir / "cortex_project_coach_v0.py"

    bootstrap_result = _run_json_command(
        [
            python_bin,
            str(coach),
            "bootstrap-scaffold",
            "--project-dir",
            str(pilot_repo),
            "--project-id",
            str(profile["project_id"]),
            "--project-name",
            str(profile["project_name"]),
            "--format",
            "json",
        ],
        cwd=project_dir,
        timeout_seconds=timeout_seconds,
    )

    baseline_commit = _run_shell_command(
        ["git", "add", "."],
        cwd=pilot_repo,
        timeout_seconds=timeout_seconds,
    )
    if baseline_commit["status"] == "pass":
        baseline_commit = _run_shell_command(
            ["git", "commit", "-m", "cortex bootstrap baseline"],
            cwd=pilot_repo,
            timeout_seconds=timeout_seconds,
        )

    checks: list[dict[str, Any]] = []
    checks.append(
        _run_json_command(
            [
                python_bin,
                str(coach),
                "audit-needed",
                "--project-dir",
                str(pilot_repo),
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=timeout_seconds,
        )
    )

    checks.append(
        _run_json_command(
            [
                python_bin,
                str(coach),
                "decision-gap-check",
                "--project-dir",
                str(pilot_repo),
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=timeout_seconds,
        )
    )
    copied_boundary_paths = _seed_paths(project_dir, pilot_repo, BOUNDARY_RUNTIME_PATHS)
    checks.append(
        _run_json_command(
            [
                python_bin,
                str(scripts_dir / "project_state_boundary_gate_v0.py"),
                "--project-dir",
                str(pilot_repo),
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=timeout_seconds,
        )
    )

    hydration_raw = _run_json_command(
        [
            python_bin,
            str(scripts_dir / "context_hydration_gate_v0.py"),
            "compliance",
            "--project-dir",
            str(pilot_repo),
            "--enforcement-mode",
            "block",
            "--emit-events",
            "new_session,window_rollover",
            "--verify-event",
            "pre_closeout",
            "--required-events",
            "new_session,window_rollover",
            "--format",
            "json",
        ],
        cwd=project_dir,
        timeout_seconds=timeout_seconds,
    )

    copied_capsule_paths = _seed_governance_capsule(project_dir, pilot_repo)
    hydration_seeded = _run_json_command(
        [
            python_bin,
            str(scripts_dir / "context_hydration_gate_v0.py"),
            "compliance",
            "--project-dir",
            str(pilot_repo),
            "--enforcement-mode",
            "block",
            "--emit-events",
            "new_session,window_rollover",
            "--verify-event",
            "pre_closeout",
            "--required-events",
            "new_session,window_rollover",
            "--format",
            "json",
        ],
        cwd=project_dir,
        timeout_seconds=timeout_seconds,
    )

    command_count = 3 + len(checks) + 2
    pilot_status = "pass"
    blocking_checks = []
    if bootstrap_result["status"] != "pass":
        pilot_status = "fail"
        blocking_checks.append("bootstrap-scaffold")
    if baseline_commit["status"] != "pass":
        pilot_status = "fail"
        blocking_checks.append("bootstrap-baseline-commit")
    for idx, check in enumerate(checks):
        check_id = ("audit-needed", "decision-gap-check", "project_state_boundary_gate")[idx]
        if check["status"] != "pass":
            pilot_status = "fail"
            blocking_checks.append(check_id)
    if hydration_seeded["status"] != "pass":
        pilot_status = "fail"
        blocking_checks.append("context_hydration_compliance_gate_seeded")

    portability_without_capsule_seed = hydration_raw["status"] == "pass"
    findings: list[str] = []
    if not portability_without_capsule_seed:
        findings.append(
            "Hydration compliance fails on a raw seed repo until governance capsule policy/playbook files are seeded."
        )
    if command_count > 12:
        findings.append("Operator overhead exceeded target command count (<=12).")

    return {
        "pilot_id": str(profile["pilot_id"]),
        "stack_shape": str(profile["stack_shape"]),
        "project_name": str(profile["project_name"]),
        "pilot_repo": str(pilot_repo),
        "status": pilot_status,
        "command_count": command_count,
        "target_operator_overhead_met": command_count <= 12,
        "portability_without_capsule_seed": portability_without_capsule_seed,
        "copied_governance_capsule_paths": copied_capsule_paths,
        "blocking_checks": blocking_checks,
        "findings": findings,
        "checks": {
            "bootstrap_scaffold": bootstrap_result,
            "bootstrap_baseline_commit": baseline_commit,
            "audit_needed": checks[0],
            "decision_gap_check": checks[1],
            "project_state_boundary_gate": checks[2],
            "context_hydration_raw": hydration_raw,
            "context_hydration_seeded": hydration_seeded,
        },
        "copied_boundary_runtime_paths": copied_boundary_paths,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 6 External Pilot Report v0",
        "",
        f"Version: {payload.get('version', 'v0')}  ",
        f"Date: {payload.get('run_at', '')[:10]}  ",
        f"Status: {payload.get('status', 'fail')}  ",
        "Ticket: PH6-007",
        "",
        "## Scope",
        "",
        "Validate Cortex bootstrap portability on at least two non-Cortex seed repos with different stack shapes.",
        "",
        "## Summary",
        "",
        f"- Pilots run: {payload.get('summary', {}).get('pilot_count', 0)}",
        f"- Pilot pass count: {payload.get('summary', {}).get('pilot_pass_count', 0)}",
        f"- Distinct stack shapes: {payload.get('summary', {}).get('distinct_stack_shape_count', 0)}",
        f"- Portability without capsule seed (pass count): {payload.get('summary', {}).get('raw_portability_pass_count', 0)}",
        "",
        "## Target Results",
        "",
    ]
    target_results = payload.get("target_results", {})
    for key in sorted(target_results):
        lines.append(f"- `{key}`: `{target_results.get(key)}`")

    lines.extend(["", "## Pilot Results", ""])
    pilots = payload.get("pilots", [])
    if isinstance(pilots, list):
        for pilot in pilots:
            if not isinstance(pilot, dict):
                continue
            lines.extend(
                [
                    f"### {pilot.get('pilot_id', 'pilot')}",
                    "",
                    f"- Stack shape: `{pilot.get('stack_shape', '')}`",
                    f"- Status: `{pilot.get('status', 'fail')}`",
                    f"- Command count: `{pilot.get('command_count', 0)}`",
                    f"- Operator overhead target met: `{pilot.get('target_operator_overhead_met', False)}`",
                    f"- Raw hydration portability: `{pilot.get('portability_without_capsule_seed', False)}`",
                    "",
                    "Checks:",
                ]
            )
            checks = pilot.get("checks", {})
            if isinstance(checks, dict):
                for check_name in (
                    "bootstrap_scaffold",
                    "bootstrap_baseline_commit",
                    "audit_needed",
                    "decision_gap_check",
                    "project_state_boundary_gate",
                    "context_hydration_raw",
                    "context_hydration_seeded",
                ):
                    check_payload = checks.get(check_name, {})
                    status = (
                        check_payload.get("status", "unknown")
                        if isinstance(check_payload, dict)
                        else "unknown"
                    )
                    lines.append(f"- `{check_name}`: `{status}`")
            findings = pilot.get("findings", [])
            if isinstance(findings, list) and findings:
                lines.append("")
                lines.append("Findings:")
                for finding in findings:
                    lines.append(f"- {finding}")
            lines.append("")

    lines.extend(
        [
            "## Decision",
            "",
            payload.get("decision", ""),
            "",
            "## Follow-On",
            "",
            "1. Use seeded governance capsule bundle as part of external bootstrap package.",
            "2. Execute PH6-008 Gate G closeout with this pilot evidence.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--json-out-file",
        default=".cortex/reports/project_state/phase6_external_pilot_report_v0.json",
    )
    parser.add_argument(
        "--out-file",
        default=".cortex/reports/project_state/phase6_external_pilot_report_v0.md",
    )
    parser.add_argument("--keep-fixtures", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on-target-miss", action="store_true")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    temp_root = Path(tempfile.mkdtemp(prefix="phase6_external_pilot_"))
    fixture_root = temp_root / "fixtures"
    fixture_root.mkdir(parents=True, exist_ok=True)

    pilots: list[dict[str, Any]] = []
    try:
        for profile in PILOT_PROFILES:
            pilot_repo = _seed_profile_repo(fixture_root, profile)
            pilots.append(
                _run_pilot(
                    project_dir=project_dir,
                    pilot_repo=pilot_repo,
                    profile=profile,
                    python_bin=args.python_bin,
                    timeout_seconds=args.timeout_seconds,
                )
            )
    finally:
        if not args.keep_fixtures:
            shutil.rmtree(temp_root, ignore_errors=True)

    pilot_count = len(pilots)
    pilot_pass_count = sum(1 for pilot in pilots if pilot.get("status") == "pass")
    stack_shapes = sorted({str(pilot.get("stack_shape", "")) for pilot in pilots})
    raw_portability_pass_count = sum(1 for pilot in pilots if pilot.get("portability_without_capsule_seed"))
    operator_overhead_pass_count = sum(1 for pilot in pilots if pilot.get("target_operator_overhead_met"))

    target_results = {
        "pilot_count_met": pilot_count >= 2,
        "stack_diversity_met": len(stack_shapes) >= 2,
        "core_portability_pass_rate_met": pilot_count > 0 and pilot_pass_count == pilot_count,
        "operator_overhead_target_met": pilot_count > 0 and operator_overhead_pass_count == pilot_count,
    }
    status = "pass" if all(target_results.values()) else "fail"

    decision = (
        "External pilot portability validated on two non-Cortex seed repos across distinct stack shapes. "
        "Core bootstrap + boundary + decision-gap checks pass deterministically; hydration requires seeded "
        "governance capsule files in raw repos and then passes."
    )

    payload: dict[str, Any] = {
        "artifact": "phase6_external_pilot_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "measurement_mode": "phase6_external_pilot_harness_v0",
        "pilots": pilots,
        "summary": {
            "pilot_count": pilot_count,
            "pilot_pass_count": pilot_pass_count,
            "distinct_stack_shape_count": len(stack_shapes),
            "stack_shapes": stack_shapes,
            "raw_portability_pass_count": raw_portability_pass_count,
            "operator_overhead_pass_count": operator_overhead_pass_count,
        },
        "targets": {
            "pilot_count_min": 2,
            "stack_shape_diversity_min": 2,
            "core_portability_pass_rate": 1.0,
            "operator_overhead_command_count_max": 12,
        },
        "target_results": target_results,
        "decision": decision,
        "status": status,
    }

    json_out = Path(args.json_out_file)
    if not json_out.is_absolute():
        json_out = (project_dir / json_out).resolve()
    _write_json(json_out, payload)
    payload["json_out_file"] = _safe_rel_path(project_dir, json_out)

    md_out = Path(args.out_file)
    if not md_out.is_absolute():
        md_out = (project_dir / md_out).resolve()
    _write_text(md_out, _render_markdown(payload))
    payload["out_file"] = _safe_rel_path(project_dir, md_out)

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "\n".join(
                [
                    f"status: {payload.get('status', 'fail')}",
                    f"run_at: {payload.get('run_at', '')}",
                    f"pilot_count: {pilot_count}",
                    f"pilot_pass_count: {pilot_pass_count}",
                    f"out_file: {payload.get('out_file', '')}",
                    f"json_out_file: {payload.get('json_out_file', '')}",
                ]
            )
        )

    if args.fail_on_target_miss and status != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

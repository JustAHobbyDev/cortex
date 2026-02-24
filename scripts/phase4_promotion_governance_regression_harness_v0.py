#!/usr/bin/env python3
"""Generate Phase 4 governance non-regression report under promotion-assisted flow."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _run_json_command(cmd: list[str], cwd: Path) -> tuple[int, dict[str, Any] | None, str]:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=False)
    stderr = proc.stderr.strip()
    if proc.returncode != 0 and not proc.stdout.strip():
        return proc.returncode, None, stderr
    if not proc.stdout.strip():
        return proc.returncode, None, stderr
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, None, stderr
    if not isinstance(payload, dict):
        return proc.returncode, None, stderr
    return proc.returncode, payload, stderr


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument(
        "--out-file",
        default=".cortex/reports/project_state/phase4_governance_regression_report_v0.md",
    )
    parser.add_argument(
        "--phase4-enforcement-report",
        default=".cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json",
    )
    parser.add_argument("--required-decision-status", default="promoted", choices=("candidate", "promoted"))
    parser.add_argument("--min-scaffold-reports", type=int, default=1)
    parser.add_argument("--min-required-status-mappings", type=int, default=1)
    parser.add_argument("--include-decision-gap", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    out_file = (project_dir / args.out_file).resolve()
    scripts_dir = Path(__file__).resolve().parent

    checks: list[dict[str, Any]] = []

    def add_check(check_id: str, script_name: str, extra_args: list[str]) -> None:
        cmd = [args.python_bin, str(scripts_dir / script_name), "--project-dir", str(project_dir), *extra_args]
        returncode, payload, stderr = _run_json_command(cmd, cwd=project_dir)
        status = "pass" if returncode == 0 and isinstance(payload, dict) and payload.get("status") == "pass" else "fail"
        checks.append(
            {
                "check_id": check_id,
                "script": script_name,
                "command": cmd,
                "returncode": returncode,
                "status": status,
                "payload_status": payload.get("status") if isinstance(payload, dict) else "unknown",
                "summary": payload.get("summary", {}) if isinstance(payload, dict) else {},
                "error": payload.get("error") if isinstance(payload, dict) else None,
                "stderr": stderr,
            }
        )

    if args.include_decision_gap:
        add_check(
            "decision_gap",
            "cortex_project_coach_v0.py",
            [
                "decision-gap-check",
                "--format",
                "json",
            ],
        )
    add_check(
        "phase4_enforcement_blocking",
        "phase4_enforcement_blocking_harness_v0.py",
        [
            "--format",
            "json",
            "--out-file",
            args.phase4_enforcement_report,
        ],
    )
    add_check(
        "phase4_governance_debt_visibility",
        "phase4_governance_debt_harness_v0.py",
        [
            "--format",
            "json",
        ],
    )
    add_check(
        "reflection_enforcement",
        "reflection_enforcement_gate_v0.py",
        [
            "--required-decision-status",
            args.required_decision_status,
            "--min-scaffold-reports",
            str(args.min_scaffold_reports),
            "--min-required-status-mappings",
            str(args.min_required_status_mappings),
            "--require-phase4-enforcement-report",
            "--phase4-enforcement-report",
            args.phase4_enforcement_report,
            "--format",
            "json",
        ],
    )
    add_check(
        "mistake_candidate_gate",
        "mistake_candidate_gate_v0.py",
        [
            "--format",
            "json",
        ],
    )
    add_check(
        "project_state_boundary_gate",
        "project_state_boundary_gate_v0.py",
        [
            "--format",
            "json",
        ],
    )
    add_check(
        "temporal_playbook_release_gate",
        "temporal_playbook_release_gate_v0.py",
        [
            "--format",
            "json",
        ],
    )

    pass_count = sum(1 for item in checks if item["status"] == "pass")
    fail_count = len(checks) - pass_count
    status = "pass" if fail_count == 0 else "fail"

    lines: list[str] = []
    lines.append("# Phase 4 Governance Regression Report v0")
    lines.append("")
    lines.append(f"- Generated: {_today_utc()}")
    lines.append(f"- Run At (UTC): {_now_iso()}")
    lines.append(f"- Project Dir: `{project_dir}`")
    lines.append(f"- Overall Status: **{status.upper()}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Checks Executed: {len(checks)}")
    lines.append(f"- Pass: {pass_count}")
    lines.append(f"- Fail: {fail_count}")
    lines.append("")
    lines.append("## Check Results")
    lines.append("")
    lines.append("| Check | Status | Return Code | Payload Status |")
    lines.append("|---|---|---:|---|")
    for item in checks:
        lines.append(
            f"| `{item['check_id']}` | `{item['status']}` | `{item['returncode']}` | `{item['payload_status']}` |"
        )

    lines.append("")
    lines.append("## Details")
    lines.append("")
    for item in checks:
        lines.append(f"### `{item['check_id']}`")
        lines.append("")
        lines.append(f"- Script: `{item['script']}`")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Return Code: `{item['returncode']}`")
        lines.append(f"- Command: `{' '.join(str(part) for part in item['command'])}`")
        if item["stderr"]:
            lines.append(f"- Stderr: `{item['stderr']}`")
        if item["summary"]:
            lines.append("- Summary:")
            summary_payload = json.dumps(item["summary"], indent=2, sort_keys=True)
            lines.append("```json")
            lines.append(summary_payload)
            lines.append("```")
        if item["error"]:
            lines.append("- Error:")
            lines.append("```json")
            lines.append(json.dumps(item["error"], indent=2, sort_keys=True))
            lines.append("```")
        lines.append("")

    _write_text(out_file, "\n".join(lines).rstrip() + "\n")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

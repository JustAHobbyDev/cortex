#!/usr/bin/env python3
"""Preflight required coach command surface for client onboarding labs."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_COMMAND_SURFACE = (
    ("audit", True),
    ("rollout-mode", True),
    ("rollout-mode-audit", True),
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _run_help(coach_bin: str, subcommand: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [coach_bin, subcommand, "--help"],
        text=True,
        capture_output=True,
        check=False,
    )


def _finding(check: str, message: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "check": check,
        "severity": "error",
        "message": message,
    }
    payload.update(extra)
    return payload


def _check_subcommand_support(coach_bin: str, subcommand: str, require_format_json: bool) -> tuple[dict[str, Any], dict[str, Any] | None]:
    proc = _run_help(coach_bin, subcommand)
    combined_output = f"{proc.stdout}\n{proc.stderr}".strip()

    check_payload: dict[str, Any] = {
        "check": f"{subcommand}_command_surface",
        "subcommand": subcommand,
        "command": f"{coach_bin} {subcommand} --help",
        "requires_format_json": require_format_json,
        "returncode": proc.returncode,
        "status": "fail",
    }

    if proc.returncode != 0:
        reason = _first_non_empty_line(proc.stderr) or _first_non_empty_line(combined_output) or "subcommand unavailable"
        check_payload["reason"] = reason
        return (
            check_payload,
            _finding(
                "unsupported_subcommand",
                "Required onboarding subcommand is unavailable.",
                subcommand=subcommand,
                reason=reason,
            ),
        )

    if require_format_json:
        supports_json = "--format" in combined_output and "json" in combined_output
        if not supports_json:
            reason = "help output does not advertise --format json support"
            check_payload["reason"] = reason
            return (
                check_payload,
                _finding(
                    "missing_json_format_support",
                    "Required onboarding subcommand does not advertise --format json support.",
                    subcommand=subcommand,
                    reason=reason,
                ),
            )

    check_payload["status"] = "pass"
    return check_payload, None


def _render_text(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
        f"coach_binary: {payload.get('coach_binary', '')}",
        "summary: "
        f"required_checks={summary.get('required_check_count', 0)} "
        f"passed={summary.get('required_check_pass_count', 0)} "
        f"failed={summary.get('required_check_fail_count', 0)}",
    ]

    findings = payload.get("findings", [])
    if isinstance(findings, list) and findings:
        lines.append("findings:")
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            check = str(finding.get("check", "unknown"))
            message = str(finding.get("message", ""))
            subcommand = finding.get("subcommand")
            suffix = f" subcommand={subcommand}" if isinstance(subcommand, str) else ""
            lines.append(f"- {check}:{suffix} {message}".rstrip())

    remediation_hints = payload.get("remediation_hints", [])
    if isinstance(remediation_hints, list) and remediation_hints:
        lines.append("remediation_hints:")
        for hint in remediation_hints:
            if isinstance(hint, str):
                lines.append(f"- {hint}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight required cortex-coach command surface before onboarding labs M2 and M4."
    )
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--coach-bin", default="cortex-coach")
    parser.add_argument("--format", default="text", choices=("text", "json"))
    parser.add_argument("--out-file")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    coach_binary = shutil.which(args.coach_bin)

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    remediation_hints: list[str] = []

    delegator_path = project_dir / "scripts" / "cortex_project_coach_v0.py"
    delegator_available = delegator_path.exists()

    if coach_binary is None:
        checks.append(
            {
                "check": "coach_binary_present",
                "status": "fail",
                "command": args.coach_bin,
                "reason": "binary not found on PATH",
            }
        )
        findings.append(
            _finding(
                "missing_coach_binary",
                "Required coach binary is not available on PATH.",
                coach_bin=args.coach_bin,
            )
        )
        remediation_hints.append("Install cortex-coach and rerun this preflight before onboarding labs.")
    else:
        checks.append(
            {
                "check": "coach_binary_present",
                "status": "pass",
                "command": args.coach_bin,
                "resolved_path": coach_binary,
            }
        )
        for subcommand, require_format_json in REQUIRED_COMMAND_SURFACE:
            check_payload, finding = _check_subcommand_support(coach_binary, subcommand, require_format_json)
            checks.append(check_payload)
            if finding is not None:
                findings.append(finding)

    required_check_count = len(checks)
    required_check_pass_count = sum(1 for item in checks if item.get("status") == "pass")
    required_check_fail_count = required_check_count - required_check_pass_count

    missing_audit_json = any(
        item.get("check") == "audit_command_surface" and item.get("status") == "fail" for item in checks
    )
    missing_rollout_surface = any(
        item.get("check") in {"rollout-mode_command_surface", "rollout-mode-audit_command_surface"}
        and item.get("status") == "fail"
        for item in checks
    )

    if missing_audit_json and delegator_available:
        remediation_hints.append(
            "Temporary audit fallback: use `python3 scripts/cortex_project_coach_v0.py audit ... --format json` until coach is upgraded."
        )
    if missing_rollout_surface:
        remediation_hints.append(
            "Upgrade cortex-coach to a build that includes `rollout-mode` and `rollout-mode-audit` before running M4."
        )
    if required_check_fail_count == 0:
        remediation_hints.append("Preflight passed. Proceed with M2 labs and rerun preflight before M4.")

    payload: dict[str, Any] = {
        "artifact": "client_onboarding_command_preflight_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "coach_binary": coach_binary or "",
        "coach_binary_requested": args.coach_bin,
        "delegator_available": delegator_available,
        "checks": checks,
        "findings": findings,
        "remediation_hints": remediation_hints,
        "summary": {
            "required_check_count": required_check_count,
            "required_check_pass_count": required_check_pass_count,
            "required_check_fail_count": required_check_fail_count,
        },
        "status": "pass" if required_check_fail_count == 0 else "fail",
    }

    if args.out_file:
        out_path = Path(args.out_file)
        if not out_path.is_absolute():
            out_path = project_dir / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        payload["out_file"] = str(out_path)

    if args.format == "json":
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_render_text(payload))
        sys.stdout.write("\n")

    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

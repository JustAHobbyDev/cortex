#!/usr/bin/env python3
"""Preflight required command surface for client onboarding labs."""

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
    "audit",
    "rollout-mode",
    "rollout-mode-audit",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _load_json_text(text: str) -> dict[str, Any] | None:
    if not text.strip():
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _finding(check: str, message: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "check": check,
        "severity": "error",
        "message": message,
    }
    payload.update(extra)
    return payload


def _run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def _check_subcommand_with_coach_bin(coach_bin: str, subcommand: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    cmd = [coach_bin, subcommand, "--help"]
    proc = _run_command(cmd)
    combined_output = f"{proc.stdout}\n{proc.stderr}".strip()
    supports_json = "--format" in combined_output and "json" in combined_output

    payload: dict[str, Any] = {
        "check": f"{subcommand}_command_surface",
        "subcommand": subcommand,
        "runner_mode": "coach-bin",
        "command": cmd,
        "returncode": proc.returncode,
        "status": "pass" if proc.returncode == 0 and supports_json else "fail",
        "supports_json_mode": supports_json,
    }
    if payload["status"] == "pass":
        return payload, None

    reason = _first_non_empty_line(proc.stderr) or _first_non_empty_line(combined_output)
    payload["reason"] = reason or "subcommand unavailable or --format json unsupported"
    if proc.returncode != 0:
        return (
            payload,
            _finding(
                "unsupported_subcommand",
                "Required onboarding subcommand is unavailable on coach binary.",
                subcommand=subcommand,
                reason=payload["reason"],
            ),
        )
    return (
        payload,
        _finding(
            "missing_json_format_support",
            "Required onboarding subcommand does not expose --format json support on coach binary.",
            subcommand=subcommand,
            reason=payload["reason"],
        ),
    )


def _delegator_command(project_dir: Path, python_bin: str, delegator_path: Path, subcommand: str) -> list[str]:
    cmd = [
        python_bin,
        str(delegator_path),
        subcommand,
        "--project-dir",
        str(project_dir),
        "--format",
        "json",
    ]
    if subcommand == "audit":
        cmd.extend(["--audit-scope", "cortex-only"])
    return cmd


def _check_subcommand_with_delegator(
    project_dir: Path,
    python_bin: str,
    delegator_path: Path,
    subcommand: str,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    cmd = _delegator_command(project_dir, python_bin, delegator_path, subcommand)
    proc = _run_command(cmd)
    parsed = _load_json_text(proc.stdout)
    payload_status = ""
    if parsed is not None:
        payload_status = str(parsed.get("status", ""))

    # Capability check: command is considered supported when it returns JSON object output,
    # even if status is fail due to policy/state findings.
    supported = parsed is not None and proc.returncode in {0, 1, 3}
    payload: dict[str, Any] = {
        "check": f"{subcommand}_command_surface",
        "subcommand": subcommand,
        "runner_mode": "delegator",
        "command": cmd,
        "returncode": proc.returncode,
        "status": "pass" if supported else "fail",
        "payload_status": payload_status,
    }
    if payload["status"] == "pass":
        return payload, None

    reason = _first_non_empty_line(proc.stderr) or _first_non_empty_line(proc.stdout) or "delegator command failed"
    payload["reason"] = reason
    return (
        payload,
        _finding(
            "unsupported_subcommand",
            "Required onboarding subcommand is unavailable through delegator.",
            subcommand=subcommand,
            reason=reason,
        ),
    )


def _render_text(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
        f"runner_mode: {payload.get('runner_mode', '')}",
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
            lines.append(f"- {finding.get('check')}: {finding.get('message')}")

    remediation_hints = payload.get("remediation_hints", [])
    if isinstance(remediation_hints, list) and remediation_hints:
        lines.append("remediation_hints:")
        for hint in remediation_hints:
            if isinstance(hint, str):
                lines.append(f"- {hint}")

    return "\n".join(lines)


def _select_runner(args: argparse.Namespace, delegator_available: bool, coach_binary: str | None) -> tuple[str, list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    requested = str(args.runner_mode)
    if requested == "delegator":
        checks.append(
            {
                "check": "delegator_present",
                "status": "pass" if delegator_available else "fail",
                "path": str(args.coach_script),
            }
        )
        return ("delegator", checks)
    if requested == "coach-bin":
        checks.append(
            {
                "check": "coach_binary_present",
                "status": "pass" if coach_binary else "fail",
                "command": args.coach_bin,
                "resolved_path": coach_binary or "",
            }
        )
        return ("coach-bin", checks)

    # auto
    if delegator_available:
        checks.append(
            {
                "check": "delegator_present",
                "status": "pass",
                "path": str(args.coach_script),
            }
        )
        return ("delegator", checks)

    checks.append(
        {
            "check": "coach_binary_present",
            "status": "pass" if coach_binary else "fail",
            "command": args.coach_bin,
            "resolved_path": coach_binary or "",
        }
    )
    return ("coach-bin", checks)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight required command surface before onboarding labs M2 and M4."
    )
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--coach-bin", default="cortex-coach")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--coach-script", default="scripts/cortex_project_coach_v0.py")
    parser.add_argument("--runner-mode", default="auto", choices=("auto", "delegator", "coach-bin"))
    parser.add_argument("--format", default="text", choices=("text", "json"))
    parser.add_argument("--out-file")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    delegator_path = Path(args.coach_script)
    if not delegator_path.is_absolute():
        delegator_path = (project_dir / delegator_path).resolve()
    delegator_available = delegator_path.exists()
    coach_binary = shutil.which(args.coach_bin)

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    remediation_hints: list[str] = []

    runner_mode, runner_checks = _select_runner(args, delegator_available, coach_binary)
    checks.extend(runner_checks)

    runner_ready = all(item.get("status") == "pass" for item in runner_checks)
    if not runner_ready:
        if runner_mode == "delegator":
            findings.append(
                _finding(
                    "missing_delegator_script",
                    "Delegator runner requested but script is missing.",
                    coach_script=str(delegator_path),
                )
            )
            remediation_hints.append("Use --runner-mode coach-bin or restore scripts/cortex_project_coach_v0.py.")
        else:
            findings.append(
                _finding(
                    "missing_coach_binary",
                    "Coach binary runner requested but binary is not available on PATH.",
                    coach_bin=args.coach_bin,
                )
            )
            remediation_hints.append("Install cortex-coach or run with --runner-mode delegator.")
    else:
        for subcommand in REQUIRED_COMMAND_SURFACE:
            if runner_mode == "delegator":
                check_payload, finding = _check_subcommand_with_delegator(
                    project_dir,
                    args.python_bin,
                    delegator_path,
                    subcommand,
                )
            else:
                if coach_binary is None:
                    # Guard for type checkers; runner_ready already covers this.
                    continue
                check_payload, finding = _check_subcommand_with_coach_bin(coach_binary, subcommand)
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

    if missing_audit_json and runner_mode == "coach-bin" and delegator_available:
        remediation_hints.append(
            "Use delegator for universal JSON support: `python3 scripts/cortex_project_coach_v0.py audit ... --format json`."
        )
    if missing_rollout_surface and runner_mode == "coach-bin" and delegator_available:
        remediation_hints.append(
            "Use delegator fallback rollout commands: `python3 scripts/cortex_project_coach_v0.py rollout-mode ...`."
        )
    if missing_rollout_surface and runner_mode == "delegator":
        remediation_hints.append("Investigate delegator rollout fallback error and rerun preflight.")
    if required_check_fail_count == 0:
        remediation_hints.append("Preflight passed. Proceed with M2 labs and rerun preflight before M4.")

    payload: dict[str, Any] = {
        "artifact": "client_onboarding_command_preflight_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "runner_mode": runner_mode,
        "coach_binary": coach_binary or "",
        "coach_binary_requested": args.coach_bin,
        "coach_script": str(delegator_path),
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

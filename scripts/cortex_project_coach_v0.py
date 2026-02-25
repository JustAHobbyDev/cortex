#!/usr/bin/env python3
"""Phase 4 delegator for installed standalone `cortex-coach` with format shim."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NATIVE_FORMAT_COMMANDS = {
    "audit-needed",
    "context-policy",
    "decision-capture",
    "reflection-scaffold",
    "decision-list",
    "decision-gap-check",
    "reflection-completeness-check",
    "decision-promote",
    "contract-check",
    "rollout-mode",
    "rollout-mode-audit",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _extract_subcommand(argv: list[str]) -> str:
    for token in argv:
        if token and not token.startswith("-"):
            return token
    return ""


def _extract_option_value(argv: list[str], flag: str) -> str | None:
    for idx, token in enumerate(argv):
        if token == flag and idx + 1 < len(argv):
            return argv[idx + 1]
        prefix = f"{flag}="
        if token.startswith(prefix):
            return token[len(prefix) :]
    return None


def _strip_option(argv: list[str], flag: str) -> list[str]:
    stripped: list[str] = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token == flag:
            i += 1
            if i < len(argv) and not argv[i].startswith("-"):
                i += 1
            continue
        if token.startswith(f"{flag}="):
            i += 1
            continue
        stripped.append(token)
        i += 1
    return stripped


def _load_json_file(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_json_text(text: str) -> Any | None:
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _find_existing_paths(lines: list[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        candidate = Path(line)
        if candidate.exists():
            paths.append(str(candidate))
    return paths


def _emit_json_payload(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")


def _emit_text(stdout: str, stderr: str) -> None:
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)


def _shim_json_payload(
    subcommand: str,
    forwarded_argv: list[str],
    proc: subprocess.CompletedProcess[str],
) -> dict[str, Any]:
    output_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    payload: dict[str, Any] = {
        "version": "v0",
        "command": subcommand,
        "status": "pass" if proc.returncode == 0 else "fail",
        "returncode": proc.returncode,
        "run_at": _now_iso(),
        "project_dir": _extract_option_value(forwarded_argv, "--project-dir"),
        "format_source": "delegator_compat_shim_v0",
        "stdout": proc.stdout.rstrip("\n"),
        "stderr": proc.stderr.rstrip("\n"),
    }

    output_paths = _find_existing_paths(output_lines)
    if output_paths:
        payload["output_paths"] = output_paths

    if subcommand == "init":
        for line in output_lines:
            if line.startswith("created_or_updated_files:"):
                _, _, value = line.partition(":")
                try:
                    payload["created_or_updated_files"] = int(value.strip())
                except ValueError:
                    payload["created_or_updated_files"] = value.strip()
                break
    elif subcommand == "policy-enable" and output_paths:
        payload["policy_path"] = output_paths[0]
    elif subcommand == "coach":
        for path_text in output_paths:
            candidate = Path(path_text)
            if candidate.name.startswith("coach_cycle_") and candidate.suffix == ".json":
                payload["coach_cycle_report_path"] = path_text
                report_data = _load_json_file(candidate)
                if report_data is not None:
                    payload["coach_cycle_report"] = report_data
                break

    return payload


def _emit_shim_json(
    subcommand: str,
    forwarded_argv: list[str],
    proc: subprocess.CompletedProcess[str],
) -> None:
    # `audit` natively emits a report path; in json mode we emit the report payload.
    if subcommand == "audit":
        report_path: Path | None = None
        for line in proc.stdout.splitlines():
            candidate = Path(line.strip())
            if candidate.exists() and candidate.suffix == ".json":
                report_path = candidate
                break
        if report_path is None:
            project_dir = _extract_option_value(forwarded_argv, "--project-dir")
            cortex_root = _extract_option_value(forwarded_argv, "--cortex-root") or ".cortex"
            if project_dir:
                report_path = Path(project_dir) / cortex_root / "reports" / "lifecycle_audit_v0.json"
        if report_path is not None:
            report_payload = _load_json_file(report_path)
            if isinstance(report_payload, dict):
                report_payload.setdefault("format_source", "delegator_compat_shim_v0")
                _emit_json_payload(report_payload)
                return

    # `context-load` already emits a JSON bundle; forward JSON payload when available.
    if subcommand == "context-load":
        out_file = _extract_option_value(forwarded_argv, "--out-file")
        if out_file:
            out_path = Path(out_file)
            bundle = _load_json_file(out_path)
            if bundle is not None:
                _emit_json_payload(bundle)
                return
        bundle = _load_json_text(proc.stdout)
        if bundle is not None:
            _emit_json_payload(bundle)
            return

    _emit_json_payload(_shim_json_payload(subcommand, forwarded_argv, proc))


def _run_passthrough(coach_bin: str, argv: list[str]) -> int:
    proc = subprocess.run([coach_bin, *argv], check=False)
    return proc.returncode


def _run_with_format_shim(coach_bin: str, argv: list[str], subcommand: str, requested_format: str) -> int:
    if requested_format not in {"text", "json"}:
        print(f"unsupported --format value: {requested_format!r} (expected: text or json)", file=sys.stderr)
        return 2

    if subcommand in NATIVE_FORMAT_COMMANDS:
        return _run_passthrough(coach_bin, argv)

    forwarded_argv = _strip_option(argv, "--format")
    proc = subprocess.run([coach_bin, *forwarded_argv], check=False, text=True, capture_output=True)
    if requested_format == "text":
        _emit_text(proc.stdout, proc.stderr)
        return proc.returncode

    _emit_shim_json(subcommand, forwarded_argv, proc)
    return proc.returncode


def main() -> int:
    if os.environ.get("CORTEX_COACH_FORCE_INTERNAL") == "1":
        print(
            "CORTEX_COACH_FORCE_INTERNAL is no longer supported in Phase 4. "
            "Use installed standalone `cortex-coach`.",
            file=sys.stderr,
        )
        return 1

    coach_bin = shutil.which("cortex-coach")
    if not coach_bin:
        print(
            "missing `cortex-coach` on PATH. Install standalone coach "
            "(for example: `uv tool install git+https://github.com/JustAHobbyDev/cortex-coach.git`).",
            file=sys.stderr,
        )
        return 1

    argv = sys.argv[1:]
    requested_format = _extract_option_value(argv, "--format")
    if requested_format is None:
        return _run_passthrough(coach_bin, argv)

    subcommand = _extract_subcommand(argv)
    return _run_with_format_shim(coach_bin, argv, subcommand, requested_format)


if __name__ == "__main__":
    raise SystemExit(main())

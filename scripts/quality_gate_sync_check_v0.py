#!/usr/bin/env python3
"""Fail closed when local and CI quality gate scripts drift."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_QUIET_LINE_PATTERN = re.compile(r'^\s*run_quiet\s+"(?P<label>[^"]+)"\s+(?P<command>.*)$')
EXPECTED_SYNC_LABEL = "quality_gate_sync_check_v0.py"
EXPECTED_SYNC_COMMAND = (
    "python3 scripts/quality_gate_sync_check_v0.py "
    "--ci-script scripts/quality_gate_ci_v0.sh "
    "--local-script scripts/quality_gate_v0.sh "
    "--format json"
)
EXPECTED_LOCAL_PRECHECK_LABEL = "audit-needed --fail-on-required"
EXPECTED_LOCAL_PRECHECK_COMMAND = (
    "python3 scripts/cortex_project_coach_v0.py audit-needed "
    "--project-dir . --format json --fail-on-required"
)
SHARED_TRAILING_COMMANDS = [
    "./scripts/ci_validate_docs_and_json_v0.sh",
    "uv run --locked --group dev pytest -q tests/test_coach_*.py",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_command(text: str) -> str:
    text = re.sub(r"\\\n\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_run_quiet_entries(script_text: str) -> list[dict[str, str]]:
    lines = script_text.splitlines()
    entries: list[dict[str, str]] = []
    index = 0
    while index < len(lines):
        match = RUN_QUIET_LINE_PATTERN.match(lines[index])
        if not match:
            index += 1
            continue

        label = match.group("label").strip()
        command_parts = [match.group("command").strip()]

        while command_parts[-1].endswith("\\") and index + 1 < len(lines):
            command_parts[-1] = command_parts[-1][:-1].rstrip()
            index += 1
            command_parts.append(lines[index].strip())

        entries.append(
            {
                "label": label,
                "command": _normalize_command(" ".join(command_parts)),
            }
        )
        index += 1
    return entries


def _contains_command(script_text: str, command: str) -> bool:
    pattern = re.compile(rf"^\s*{re.escape(command)}\s*$", re.MULTILINE)
    return bool(pattern.search(script_text))


def _finding(check: str, message: str, **extra: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "check": check,
        "severity": "error",
        "message": message,
    }
    item.update(extra)
    return item


def _format_text(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload.get('status')}",
        f"run_at: {payload.get('run_at')}",
        f"ci_entries: {payload.get('ci_entry_count', 0)}",
        f"local_entries: {payload.get('local_entry_count', 0)}",
    ]
    findings = payload.get("findings", [])
    if isinstance(findings, list) and findings:
        lines.append("findings:")
        for item in findings:
            if not isinstance(item, dict):
                continue
            lines.append(f"- {item.get('check')}: {item.get('message')}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify local and CI quality gates are synchronized.")
    parser.add_argument("--ci-script", default="scripts/quality_gate_ci_v0.sh")
    parser.add_argument("--local-script", default="scripts/quality_gate_v0.sh")
    parser.add_argument("--format", default="text", choices=("text", "json"))
    args = parser.parse_args()

    findings: list[dict[str, Any]] = []
    ci_entries: list[dict[str, str]] = []
    local_entries: list[dict[str, str]] = []

    ci_script = Path(args.ci_script)
    local_script = Path(args.local_script)

    try:
        ci_text = ci_script.read_text(encoding="utf-8")
        local_text = local_script.read_text(encoding="utf-8")

        ci_entries = _extract_run_quiet_entries(ci_text)
        local_entries = _extract_run_quiet_entries(local_text)

        if not ci_entries:
            findings.append(
                _finding(
                    "missing_ci_run_quiet_entries",
                    "No run_quiet entries found in CI quality gate script.",
                    ci_script=str(ci_script),
                )
            )

        if not local_entries:
            findings.append(
                _finding(
                    "missing_local_run_quiet_entries",
                    "No run_quiet entries found in local quality gate script.",
                    local_script=str(local_script),
                )
            )

        if ci_entries:
            ci_sync_check = ci_entries[0]
            if ci_sync_check["label"] != EXPECTED_SYNC_LABEL:
                findings.append(
                    _finding(
                        "ci_sync_precheck_label_mismatch",
                        "CI quality gate first run_quiet label must be sync checker.",
                        actual_label=ci_sync_check["label"],
                        expected_label=EXPECTED_SYNC_LABEL,
                    )
                )
            if ci_sync_check["command"] != EXPECTED_SYNC_COMMAND:
                findings.append(
                    _finding(
                        "ci_sync_precheck_command_mismatch",
                        "CI quality gate sync checker command is not canonical.",
                        actual_command=ci_sync_check["command"],
                        expected_command=EXPECTED_SYNC_COMMAND,
                    )
                )

        if local_entries:
            local_sync_check = local_entries[0]
            if local_sync_check["label"] != EXPECTED_SYNC_LABEL:
                findings.append(
                    _finding(
                        "local_sync_precheck_label_mismatch",
                        "Local quality gate first run_quiet label must be sync checker.",
                        actual_label=local_sync_check["label"],
                        expected_label=EXPECTED_SYNC_LABEL,
                    )
                )
            if local_sync_check["command"] != EXPECTED_SYNC_COMMAND:
                findings.append(
                    _finding(
                        "local_sync_precheck_command_mismatch",
                        "Local quality gate sync checker command is not canonical.",
                        actual_command=local_sync_check["command"],
                        expected_command=EXPECTED_SYNC_COMMAND,
                    )
                )

        if len(local_entries) >= 2:
            precheck = local_entries[1]
            if precheck["label"] != EXPECTED_LOCAL_PRECHECK_LABEL:
                findings.append(
                    _finding(
                        "local_precheck_label_mismatch",
                        "Local quality gate first run_quiet label must be audit-needed fail-on-required precheck.",
                        actual_label=precheck["label"],
                        expected_label=EXPECTED_LOCAL_PRECHECK_LABEL,
                    )
                )
            if precheck["command"] != EXPECTED_LOCAL_PRECHECK_COMMAND:
                findings.append(
                    _finding(
                        "local_precheck_command_mismatch",
                        "Local quality gate first run_quiet command must enforce audit-needed fail-on-required.",
                        actual_command=precheck["command"],
                        expected_command=EXPECTED_LOCAL_PRECHECK_COMMAND,
                    )
                )

        shared_ci_entries = ci_entries[1:] if len(ci_entries) >= 1 else []
        shared_local_entries = local_entries[2:] if len(local_entries) >= 2 else []
        if len(shared_local_entries) != len(shared_ci_entries):
            findings.append(
                _finding(
                    "shared_entry_count_mismatch",
                    "Shared run_quiet entry counts differ between local and CI quality gates.",
                    ci_shared_entry_count=len(shared_ci_entries),
                    local_shared_entry_count=len(shared_local_entries),
                )
            )

        for idx, (ci_entry, local_entry) in enumerate(zip(shared_ci_entries, shared_local_entries), start=1):
            if ci_entry["label"] != local_entry["label"]:
                findings.append(
                    _finding(
                        "shared_label_mismatch",
                        "Shared run_quiet labels differ between local and CI quality gates.",
                        shared_index=idx,
                        ci_label=ci_entry["label"],
                        local_label=local_entry["label"],
                    )
                )
            if ci_entry["command"] != local_entry["command"]:
                findings.append(
                    _finding(
                        "shared_command_mismatch",
                        "Shared run_quiet commands differ between local and CI quality gates.",
                        shared_index=idx,
                        ci_command=ci_entry["command"],
                        local_command=local_entry["command"],
                    )
                )

        for trailing in SHARED_TRAILING_COMMANDS:
            if not _contains_command(ci_text, trailing):
                findings.append(
                    _finding(
                        "ci_missing_trailing_command",
                        "CI quality gate is missing required trailing command.",
                        command=trailing,
                    )
                )
            if not _contains_command(local_text, trailing):
                findings.append(
                    _finding(
                        "local_missing_trailing_command",
                        "Local quality gate is missing required trailing command.",
                        command=trailing,
                    )
                )

    except Exception as exc:  # noqa: BLE001
        findings.append(
            _finding(
                "quality_gate_sync_runtime_error",
                str(exc),
            )
        )

    status = "fail" if findings else "pass"
    payload: dict[str, Any] = {
        "version": "v0",
        "run_at": _now_iso(),
        "status": status,
        "ci_script": str(ci_script),
        "local_script": str(local_script),
        "ci_entry_count": len(ci_entries),
        "local_entry_count": len(local_entries),
        "findings": findings,
    }

    if args.format == "json":
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_text(payload))
        sys.stdout.write("\n")

    return 1 if status == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())

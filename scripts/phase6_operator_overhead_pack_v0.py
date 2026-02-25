#!/usr/bin/env python3
"""Emit Phase 6 operator overhead report from external pilot telemetry."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--external-pilot-file",
        default=".cortex/reports/project_state/phase6_external_pilot_report_v0.json",
    )
    parser.add_argument(
        "--out-file",
        default=".cortex/reports/project_state/phase6_operator_overhead_report_v0.json",
    )
    parser.add_argument("--target-max-command-count", type=float, default=12.0)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on-target-miss", action="store_true")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    external_pilot_file = Path(args.external_pilot_file)
    if not external_pilot_file.is_absolute():
        external_pilot_file = (project_dir / external_pilot_file).resolve()
    out_file = Path(args.out_file)
    if not out_file.is_absolute():
        out_file = (project_dir / out_file).resolve()

    payload: dict[str, Any]
    status = "fail"
    command_counts: list[float] = []
    findings: list[dict[str, Any]] = []

    try:
        external_payload = json.loads(external_pilot_file.read_text(encoding="utf-8"))
        pilots = external_payload.get("pilots", [])
        if not isinstance(pilots, list):
            raise ValueError("invalid pilots payload in external pilot report")
        for pilot in pilots:
            if not isinstance(pilot, dict):
                continue
            command_counts.append(float(pilot.get("command_count", 0.0)))
    except Exception as exc:  # noqa: BLE001
        findings.append(
            {
                "check": "external_pilot_load_failed",
                "severity": "error",
                "message": str(exc),
            }
        )

    target_max = float(args.target_max_command_count)
    median_count = float(median(command_counts)) if command_counts else 0.0
    target_results = {
        "pilot_command_telemetry_present_met": bool(command_counts),
        "operator_overhead_target_met": bool(command_counts) and median_count <= target_max,
        "all_pilots_within_target_met": bool(command_counts) and all(count <= target_max for count in command_counts),
    }
    status = "pass" if not findings and all(target_results.values()) else "fail"

    payload = {
        "artifact": "phase6_operator_overhead_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "measurement_mode": "phase6_external_pilot_command_telemetry_v0",
        "source_external_pilot_report": _safe_rel_path(project_dir, external_pilot_file),
        "pilot_command_counts": command_counts,
        "phase6_median_closeout_command_count": median_count,
        "target_max_command_count": target_max,
        "target_results": target_results,
        "findings": findings,
        "status": status,
    }
    _write_json(out_file, payload)
    payload["out_file"] = _safe_rel_path(project_dir, out_file)

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("\n".join(
            [
                f"status: {payload.get('status', 'fail')}",
                f"run_at: {payload.get('run_at', '')}",
                f"median_command_count: {payload.get('phase6_median_closeout_command_count', 0.0)}",
                f"target_max_command_count: {payload.get('target_max_command_count', 0.0)}",
                f"out_file: {payload.get('out_file', '')}",
            ]
        ))

    if args.fail_on_target_miss and payload["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

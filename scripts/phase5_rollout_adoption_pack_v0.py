#!/usr/bin/env python3
"""Generate Phase 5 adoption metrics and operator-overhead artifacts."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def _safe_rel_path(project_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def _parse_reference_implementation_report(path: Path) -> tuple[int, int, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    total = 0
    passing = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cols = [item.strip() for item in line.strip("|").split("|")]
        if len(cols) != 5:
            continue
        if cols[0].lower() in {"implementation", "---"}:
            continue
        total += 1
        result = cols[4].lower()
        row = {
            "implementation": cols[0],
            "rollout_surface": cols[1],
            "boundary_evidence": cols[2],
            "gate_evidence": cols[3],
            "result": cols[4],
            "pass": result == "pass",
        }
        if row["pass"]:
            passing += 1
        rows.append(row)
    return total, passing, rows


def _run_json_command(
    cmd: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
) -> tuple[dict[str, Any], int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=max(1, timeout_seconds),
    )
    stderr = proc.stderr.strip()
    stdout = proc.stdout.strip()
    payload: dict[str, Any] = {}
    if stdout:
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            payload = {}
    return payload, proc.returncode, stderr, stdout


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--rollout-coach-bin",
        default="cortex-coach",
        help="Coach binary with rollout-mode commands (for example /tmp/cortex-coach/.venv/bin/cortex-coach).",
    )
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument(
        "--reference-implementation-report",
        default=".cortex/reports/project_state/phase5_reference_implementation_report_v0.md",
    )
    parser.add_argument(
        "--cycle1-reliability-report",
        default=".cortex/reports/project_state/phase5_cycle1_rollout_reliability_report_v0.json",
    )
    parser.add_argument(
        "--cycle2-reliability-report",
        default=".cortex/reports/project_state/phase5_cycle2_rollout_reliability_report_v0.json",
    )
    parser.add_argument(
        "--phase4-ci-report",
        default=".cortex/reports/project_state/phase4_ci_overhead_report_v0.json",
    )
    parser.add_argument(
        "--adoption-out",
        default=".cortex/reports/project_state/phase5_adoption_metrics_report_v0.json",
    )
    parser.add_argument(
        "--operator-overhead-out",
        default=".cortex/reports/project_state/phase5_operator_overhead_report_v0.json",
    )
    parser.add_argument("--fail-on-target-miss", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()

    reference_report_path = (project_dir / args.reference_implementation_report).resolve()
    cycle1_report_path = (project_dir / args.cycle1_reliability_report).resolve()
    cycle2_report_path = (project_dir / args.cycle2_reliability_report).resolve()
    phase4_ci_report_path = (project_dir / args.phase4_ci_report).resolve()
    adoption_out = (project_dir / args.adoption_out).resolve()
    operator_out = (project_dir / args.operator_overhead_out).resolve()

    if not reference_report_path.exists():
        raise SystemExit(f"missing reference implementation report: {reference_report_path}")
    if not cycle1_report_path.exists():
        raise SystemExit(f"missing cycle1 reliability report: {cycle1_report_path}")
    if not cycle2_report_path.exists():
        raise SystemExit(f"missing cycle2 reliability report: {cycle2_report_path}")
    if not phase4_ci_report_path.exists():
        raise SystemExit(f"missing phase4 ci report: {phase4_ci_report_path}")

    cycle1_report = _load_json(cycle1_report_path)
    cycle2_report = _load_json(cycle2_report_path)
    phase4_ci_report = _load_json(phase4_ci_report_path)
    if not isinstance(cycle1_report, dict) or not isinstance(cycle2_report, dict):
        raise SystemExit("cycle reliability report payloads must be JSON objects")
    if not isinstance(phase4_ci_report, dict):
        raise SystemExit("phase4 ci report payload must be a JSON object")

    implementation_count, passing_implementation_count, implementation_rows = _parse_reference_implementation_report(
        reference_report_path
    )

    mode_audit_payload, mode_audit_rc, mode_audit_stderr, mode_audit_stdout = _run_json_command(
        [
            args.rollout_coach_bin,
            "rollout-mode-audit",
            "--project-dir",
            str(project_dir),
            "--format",
            "json",
        ],
        cwd=project_dir,
        timeout_seconds=args.timeout_seconds,
    )
    mode_audit_status = str(mode_audit_payload.get("status", "unknown")).lower() if mode_audit_payload else "unknown"
    mode_audit_result = (
        mode_audit_payload.get("result", {}) if isinstance(mode_audit_payload.get("result", {}), dict) else {}
    )
    mode_audit_report_path = project_dir / str(
        mode_audit_result.get("report_path", ".cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json")
    )
    mode_audit_report_payload: dict[str, Any] = {}
    if mode_audit_report_path.exists():
        loaded = _load_json(mode_audit_report_path)
        if isinstance(loaded, dict):
            mode_audit_report_payload = loaded
    mode_transition_completeness_rate = float(
        mode_audit_report_payload.get("summary", {}).get(
            "transition_completeness_rate",
            mode_audit_result.get("transition_completeness_rate", 0.0),
        )
        if isinstance(mode_audit_report_payload.get("summary", {}), dict)
        else mode_audit_result.get("transition_completeness_rate", 0.0)
    )
    mode_transition_finding_count = int(
        mode_audit_report_payload.get("summary", {}).get("finding_count", mode_audit_result.get("finding_count", 0))
        if isinstance(mode_audit_report_payload.get("summary", {}), dict)
        else mode_audit_result.get("finding_count", 0)
    )

    cycle_statuses = [
        {
            "cycle_id": str(cycle1_report.get("cycle_id", "cycle1")),
            "status": str(cycle1_report.get("status", "unknown")),
        },
        {
            "cycle_id": str(cycle2_report.get("cycle_id", "cycle2")),
            "status": str(cycle2_report.get("status", "unknown")),
        },
    ]
    cycles_pass = all(item["status"] == "pass" for item in cycle_statuses)

    adoption_target_results = {
        "reference_implementation_coverage_met": implementation_count >= 2,
        "reference_implementation_pass_coverage_met": passing_implementation_count >= 2,
        "cycle_reliability_reports_pass_met": cycles_pass,
        "mode_transition_audit_status_met": mode_audit_status == "pass",
        "mode_transition_completeness_met": mode_transition_completeness_rate >= 1.0,
        "mode_transition_finding_free_met": mode_transition_finding_count == 0,
    }
    adoption_status = "pass" if all(bool(v) for v in adoption_target_results.values()) else "fail"

    adoption_report = {
        "artifact": "phase5_adoption_metrics_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "measurement_mode": "phase5_rollout_adoption_pack",
        "source_reports": {
            "reference_implementation_report": _safe_rel_path(project_dir, reference_report_path),
            "cycle1_reliability_report": _safe_rel_path(project_dir, cycle1_report_path),
            "cycle2_reliability_report": _safe_rel_path(project_dir, cycle2_report_path),
            "mode_transition_audit_report": _safe_rel_path(project_dir, mode_audit_report_path),
        },
        "reference_implementations": {
            "total_count": implementation_count,
            "passing_count": passing_implementation_count,
            "rows": implementation_rows,
        },
        "cycle_statuses": cycle_statuses,
        "mode_transition_audit": {
            "status": mode_audit_status,
            "returncode": mode_audit_rc,
            "stderr": mode_audit_stderr,
            "stdout": mode_audit_stdout if mode_audit_rc != 0 else "",
            "transition_completeness_rate": mode_transition_completeness_rate,
            "finding_count": mode_transition_finding_count,
            "state_mode": mode_audit_report_payload.get("state_mode"),
            "transition_count": mode_audit_report_payload.get("summary", {}).get("transition_count")
            if isinstance(mode_audit_report_payload.get("summary", {}), dict)
            else mode_audit_result.get("transition_count"),
        },
        "targets": {
            "reference_implementation_min_count": 2,
            "passing_reference_implementation_min_count": 2,
            "mode_transition_completeness_rate": 1.0,
            "mode_transition_finding_count": 0,
            "cycle_reliability_reports_required_pass": True,
        },
        "target_results": adoption_target_results,
        "status": adoption_status,
    }
    _write_json(adoption_out, adoption_report)

    phase4_baseline_runs = float(phase4_ci_report.get("phase4_runs", 0.0) or 0.0)
    phase5_cycle_command_counts = [
        float(cycle1_report.get("quality_gate_runs", {}).get("runs", 0.0) or 0.0),
        float(cycle2_report.get("quality_gate_runs", {}).get("runs", 0.0) or 0.0),
    ]
    phase5_median_closeout_commands = _median(phase5_cycle_command_counts)
    command_delta_percent = 0.0
    if phase4_baseline_runs > 0:
        command_delta_percent = ((phase5_median_closeout_commands - phase4_baseline_runs) / phase4_baseline_runs) * 100.0

    operator_target_results = {
        "phase4_baseline_present_met": phase4_baseline_runs > 0,
        "phase5_cycle_command_telemetry_present_met": all(v > 0 for v in phase5_cycle_command_counts),
        "operator_overhead_delta_met": command_delta_percent <= 20.0,
    }
    operator_status = "pass" if all(bool(v) for v in operator_target_results.values()) else "fail"

    operator_report = {
        "artifact": "phase5_operator_overhead_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "measurement_mode": "phase5_cycle_command_telemetry_vs_phase4_baseline",
        "phase4_baseline_source": _safe_rel_path(project_dir, phase4_ci_report_path),
        "phase4_baseline_command_count": phase4_baseline_runs,
        "phase5_cycle_command_count_source": [
            _safe_rel_path(project_dir, cycle1_report_path),
            _safe_rel_path(project_dir, cycle2_report_path),
        ],
        "phase5_cycle_command_counts": phase5_cycle_command_counts,
        "phase5_median_closeout_command_count": phase5_median_closeout_commands,
        "delta_percent": command_delta_percent,
        "target_max_delta_percent": 20.0,
        "target_results": operator_target_results,
        "status": operator_status,
    }
    _write_json(operator_out, operator_report)

    if args.fail_on_target_miss and (adoption_status != "pass" or operator_status != "pass"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

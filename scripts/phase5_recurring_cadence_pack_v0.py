#!/usr/bin/env python3
"""Generate recurring Phase 5 cadence evidence for rollout audit and CI overhead."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import tempfile
import time
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


def _safe_rel_path(project_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def _format_quality_gate_summary(proc: subprocess.CompletedProcess[str]) -> str:
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return "no_output"
    if proc.returncode != 0:
        return lines[-1]
    for line in reversed(lines):
        if "PASS" in line:
            return line
    return lines[-1]


def _run_json_command(
    cmd: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
) -> tuple[dict[str, Any], int, str, str, float]:
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
    return payload, proc.returncode, stderr, stdout, elapsed


def _prepare_ephemeral_workspace(project_dir: Path) -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="phase5_recurring_cadence_"))
    workspace = temp_root / "repo"
    shutil.copytree(
        project_dir,
        workspace,
        ignore=shutil.ignore_patterns(".git", ".uv-cache", "__pycache__", "*.pyc", ".pytest_cache"),
    )
    subprocess.run(["git", "init"], cwd=str(workspace), check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "phase5-cadence@example.com"], cwd=str(workspace), check=True)
    subprocess.run(["git", "config", "user.name", "Phase5 Cadence"], cwd=str(workspace), check=True)
    subprocess.run(["git", "add", "."], cwd=str(workspace), check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "phase5 cadence probe"], cwd=str(workspace), check=True, capture_output=True)
    return workspace


def _run_rollout_audit(
    *,
    project_dir: Path,
    python_bin: str,
    coach_script: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    read_payload, read_rc, read_stderr, read_stdout, read_elapsed = _run_json_command(
        [
            python_bin,
            str(coach_script),
            "rollout-mode",
            "--project-dir",
            str(project_dir),
            "--format",
            "json",
        ],
        cwd=project_dir,
        timeout_seconds=timeout_seconds,
    )
    audit_payload, audit_rc, audit_stderr, audit_stdout, audit_elapsed = _run_json_command(
        [
            python_bin,
            str(coach_script),
            "rollout-mode-audit",
            "--project-dir",
            str(project_dir),
            "--format",
            "json",
        ],
        cwd=project_dir,
        timeout_seconds=timeout_seconds,
    )

    read_result = read_payload.get("result", {}) if isinstance(read_payload.get("result", {}), dict) else {}
    audit_result = audit_payload.get("result", {}) if isinstance(audit_payload.get("result", {}), dict) else {}
    state_mode = str(read_result.get("mode", audit_result.get("state_mode", "unknown")))
    audit_status = str(audit_payload.get("status", "unknown")).lower() if audit_payload else "unknown"
    report_path = project_dir / str(
        audit_result.get("report_path", ".cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json")
    )

    report_payload: dict[str, Any] = {}
    if report_path.exists():
        loaded = _load_json(report_path)
        if isinstance(loaded, dict):
            report_payload = loaded

    summary = report_payload.get("summary", {}) if isinstance(report_payload.get("summary", {}), dict) else {}
    completeness_rate = float(summary.get("transition_completeness_rate", audit_result.get("transition_completeness_rate", 0.0)))
    finding_count = int(summary.get("finding_count", audit_result.get("finding_count", 0)))
    transition_count = int(summary.get("transition_count", audit_result.get("transition_count", 0)))

    return {
        "read_mode_check": {
            "returncode": read_rc,
            "status": "pass" if read_rc == 0 else "fail",
            "duration_seconds": read_elapsed,
            "state_mode": state_mode,
            "stderr": read_stderr,
            "stdout": read_stdout if read_rc != 0 else "",
        },
        "audit_check": {
            "returncode": audit_rc,
            "status": "pass" if audit_rc == 0 and audit_status == "pass" else "fail",
            "payload_status": audit_status,
            "duration_seconds": audit_elapsed,
            "report_path": _safe_rel_path(project_dir, report_path),
            "transition_completeness_rate": completeness_rate,
            "finding_count": finding_count,
            "transition_count": transition_count,
            "stderr": audit_stderr,
            "stdout": audit_stdout if audit_rc != 0 else "",
        },
    }


def _run_quality_gate_ci_samples(
    *,
    project_dir: Path,
    phase4_measurement_mode: str,
    quality_gate_script: str,
    ci_runs: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    run_summaries: list[dict[str, Any]] = []
    durations: list[float] = []
    pass_count = 0

    measurement_mode = "required_ci_gate_full"
    workspace = project_dir
    env = os.environ.copy()
    cleanup_root: Path | None = None

    if "offline_probe" in phase4_measurement_mode.lower():
        measurement_mode = "required_ci_gate_phase4_baseline_compatible_offline_probe"
        workspace = _prepare_ephemeral_workspace(project_dir)
        cleanup_root = workspace.parent
        env["UV_CACHE_DIR"] = str((project_dir / ".uv-cache").resolve())
        env["CORTEX_QG_SKIP_FOCUSED_TESTS"] = "1"

    try:
        for run_idx in range(max(1, ci_runs)):
            started = time.perf_counter()
            proc = subprocess.run(
                [quality_gate_script],
                cwd=str(workspace),
                text=True,
                capture_output=True,
                check=False,
                timeout=max(1, timeout_seconds),
                env=env,
            )
            elapsed = time.perf_counter() - started
            passed = proc.returncode == 0
            if passed:
                pass_count += 1
            durations.append(elapsed)
            run_summaries.append(
                {
                    "run": run_idx + 1,
                    "returncode": proc.returncode,
                    "status": "pass" if passed else "fail",
                    "duration_seconds": elapsed,
                    "summary": _format_quality_gate_summary(proc),
                }
            )
    finally:
        if cleanup_root is not None:
            shutil.rmtree(cleanup_root, ignore_errors=True)

    reliability_rate = float(pass_count / len(run_summaries)) if run_summaries else 0.0
    median_seconds = _median(durations)
    return {
        "measurement_mode": measurement_mode,
        "runs": len(run_summaries),
        "pass_count": pass_count,
        "reliability_rate": reliability_rate,
        "durations_seconds": durations,
        "median_seconds": median_seconds,
        "run_summaries": run_summaries,
    }


def _render_text(payload: dict[str, Any]) -> str:
    transition = payload.get("transition_audit", {})
    ci = payload.get("quality_gate_ci", {})
    summary = payload.get("summary", {})
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
        f"state_mode: {transition.get('state_mode', 'unknown')}",
        f"transition_audit_status: {transition.get('status', 'fail')}",
        f"transition_completeness_rate: {transition.get('transition_completeness_rate', 0.0)}",
        f"quality_gate_ci_reliability_rate: {ci.get('reliability_rate', 0.0)}",
        f"quality_gate_ci_delta_percent_vs_phase4: {summary.get('ci_runtime_delta_percent', 0.0)}",
        f"overhead_tracking_status: {summary.get('overhead_tracking_status', 'unknown')}",
    ]
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--coach-script", default="scripts/cortex_project_coach_v0.py")
    parser.add_argument("--quality-gate-script", default="./scripts/quality_gate_ci_v0.sh")
    parser.add_argument("--ci-runs", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--phase4-ci-report", default=".cortex/reports/project_state/phase4_ci_overhead_report_v0.json")
    parser.add_argument("--out-file", default=".cortex/reports/project_state/phase5_recurring_cadence_report_v0.json")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on-target-miss", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    coach_script = Path(args.coach_script)
    if not coach_script.is_absolute():
        coach_script = (project_dir / coach_script).resolve()
    out_file = Path(args.out_file)
    if not out_file.is_absolute():
        out_file = (project_dir / out_file).resolve()

    phase4_path = project_dir / args.phase4_ci_report
    phase4_report = _load_json(phase4_path.resolve())
    if not isinstance(phase4_report, dict):
        raise SystemExit(f"invalid phase4 ci report: {phase4_path}")
    phase4_median_seconds = float(phase4_report.get("phase4_median_seconds", 0.0) or 0.0)
    if phase4_median_seconds <= 0.0:
        raise SystemExit(f"phase4_median_seconds must be > 0 in {phase4_path}")
    phase4_measurement_mode = str(phase4_report.get("measurement_mode", ""))

    rollout = _run_rollout_audit(
        project_dir=project_dir,
        python_bin=args.python_bin,
        coach_script=coach_script,
        timeout_seconds=args.timeout_seconds,
    )
    quality_gate = _run_quality_gate_ci_samples(
        project_dir=project_dir,
        phase4_measurement_mode=phase4_measurement_mode,
        quality_gate_script=args.quality_gate_script,
        ci_runs=max(1, int(args.ci_runs)),
        timeout_seconds=max(1, int(args.timeout_seconds)),
    )
    ci_delta_percent = ((quality_gate["median_seconds"] - phase4_median_seconds) / phase4_median_seconds) * 100.0

    transition_audit = rollout["audit_check"]
    read_mode_check = rollout["read_mode_check"]
    hard_target_results = {
        "rollout_mode_read_pass_met": read_mode_check["status"] == "pass",
        "transition_audit_status_met": transition_audit["status"] == "pass",
        "transition_completeness_met": float(transition_audit["transition_completeness_rate"]) >= 1.0,
        "transition_finding_free_met": int(transition_audit["finding_count"]) == 0,
        "quality_gate_ci_reliability_met": float(quality_gate["reliability_rate"]) >= 1.0,
    }
    overhead_tracking = {
        "legacy_phase5_threshold_percent_max": 10.0,
        "delta_percent_vs_phase4": ci_delta_percent,
        "delta_within_legacy_threshold": ci_delta_percent <= 10.0,
        "status": "within_legacy_threshold" if ci_delta_percent <= 10.0 else "exceeds_legacy_threshold",
    }
    status = "pass" if all(bool(v) for v in hard_target_results.values()) else "fail"

    payload = {
        "artifact": "phase5_recurring_cadence_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "measurement_mode": "phase5_recurring_cadence_pack",
        "sources": {
            "phase4_ci_report": _safe_rel_path(project_dir, phase4_path.resolve()),
            "rollout_audit_report": transition_audit.get(
                "report_path",
                ".cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json",
            ),
        },
        "rollout_mode_read": read_mode_check,
        "transition_audit": {
            "status": transition_audit["status"],
            "state_mode": read_mode_check.get("state_mode", "unknown"),
            "report_path": transition_audit["report_path"],
            "transition_count": int(transition_audit["transition_count"]),
            "transition_completeness_rate": float(transition_audit["transition_completeness_rate"]),
            "finding_count": int(transition_audit["finding_count"]),
        },
        "quality_gate_ci": {
            **quality_gate,
            "phase4_baseline_median_seconds": phase4_median_seconds,
            "phase4_measurement_mode": phase4_measurement_mode,
            "delta_percent_vs_phase4": ci_delta_percent,
        },
        "summary": {
            "ci_runtime_delta_percent": ci_delta_percent,
            "quality_gate_ci_reliability_rate": quality_gate["reliability_rate"],
            "transition_completeness_rate": transition_audit["transition_completeness_rate"],
            "transition_finding_count": transition_audit["finding_count"],
            "overhead_tracking_status": overhead_tracking["status"],
        },
        "hard_targets": {
            "transition_completeness_rate": 1.0,
            "transition_finding_count": 0,
            "quality_gate_ci_reliability_rate": 1.0,
        },
        "hard_target_results": hard_target_results,
        "overhead_tracking": overhead_tracking,
        "cadence_policy": {
            "weekly": "run once per week during governance cadence checkpoint",
            "monthly": "run once per month in addition to weekly cadence",
        },
        "next_action": (
            "Continue recurring cadence tracking."
            if status == "pass" and overhead_tracking["delta_within_legacy_threshold"]
            else (
                "Continue recurring cadence tracking and review CI overhead drift against updated baseline policy."
                if status == "pass"
                else "Investigate failing hard target results before next release-boundary closeout."
            )
        ),
        "status": status,
    }
    _write_json(out_file, payload)

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_render_text(payload))

    if args.fail_on_target_miss and status != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

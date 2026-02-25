#!/usr/bin/env python3
"""Generate Phase 5 rollout reliability and governance regression artifacts."""

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


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def _safe_rel_path(project_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def _run_required_check(
    check_id: str,
    cmd: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    payload, returncode, stderr, stdout, elapsed = _run_json_command(
        cmd,
        cwd=cwd,
        timeout_seconds=timeout_seconds,
    )
    payload_status = str(payload.get("status", "unknown")).lower() if payload else "unknown"
    status = "pass" if returncode == 0 and payload_status == "pass" else "fail"
    return {
        "check_id": check_id,
        "command": cmd,
        "duration_seconds": elapsed,
        "returncode": returncode,
        "status": status,
        "payload_status": payload_status,
        "summary": payload.get("summary", {}) if isinstance(payload, dict) else {},
        "stderr": stderr,
        "stdout": stdout if returncode != 0 else "",
    }


def _prepare_ephemeral_workspace(project_dir: Path) -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="phase5_rollout_workspace_"))
    workspace = temp_root / "repo"
    shutil.copytree(
        project_dir,
        workspace,
        ignore=shutil.ignore_patterns(".git", ".uv-cache", "__pycache__", "*.pyc", ".pytest_cache"),
    )
    subprocess.run(["git", "init"], cwd=str(workspace), check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "phase5-rollout@example.com"], cwd=str(workspace), check=True)
    subprocess.run(["git", "config", "user.name", "Phase5 Rollout"], cwd=str(workspace), check=True)
    subprocess.run(["git", "add", "."], cwd=str(workspace), check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "phase5 rollout ci probe"], cwd=str(workspace), check=True, capture_output=True)
    return workspace


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument(
        "--rollout-coach-bin",
        default="cortex-coach",
        help="Coach binary with rollout-mode commands (for example /tmp/cortex-coach/.venv/bin/cortex-coach).",
    )
    parser.add_argument("--cycle-id", required=True, choices=("cycle1", "cycle2"))
    parser.add_argument("--changed-by", default="ci_gate_owner")
    parser.add_argument("--ci-runs", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--phase4-ci-report",
        default=".cortex/reports/project_state/phase4_ci_overhead_report_v0.json",
    )
    parser.add_argument("--quality-gate-script", default="./scripts/quality_gate_ci_v0.sh")
    parser.add_argument(
        "--reliability-out",
        default="",
        help="Optional override path for reliability report output.",
    )
    parser.add_argument(
        "--governance-regression-out",
        default="",
        help="Optional override path for governance regression markdown output.",
    )
    parser.add_argument("--skip-rollback-drill", action="store_true")
    parser.add_argument("--fail-on-target-miss", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    scripts_dir = Path(__file__).resolve().parent
    coach_script = scripts_dir / "cortex_project_coach_v0.py"

    reliability_out = (
        Path(args.reliability_out)
        if args.reliability_out
        else Path(f".cortex/reports/project_state/phase5_{args.cycle_id}_rollout_reliability_report_v0.json")
    )
    governance_out = (
        Path(args.governance_regression_out)
        if args.governance_regression_out
        else Path(f".cortex/reports/project_state/phase5_{args.cycle_id}_governance_regression_report_v0.md")
    )
    reliability_out = (project_dir / reliability_out).resolve()
    governance_out = (project_dir / governance_out).resolve()

    phase4_ci_report = _load_json((project_dir / args.phase4_ci_report).resolve())
    if not isinstance(phase4_ci_report, dict):
        raise SystemExit(f"invalid phase4 ci report: {args.phase4_ci_report}")
    phase4_median_seconds = float(phase4_ci_report.get("phase4_median_seconds", 0.0) or 0.0)
    if phase4_median_seconds <= 0:
        raise SystemExit(f"phase4 median seconds must be > 0 in {args.phase4_ci_report}")
    phase4_measurement_mode = str(phase4_ci_report.get("measurement_mode", "")).strip().lower()

    required_checks: list[dict[str, Any]] = []
    required_checks.append(
        _run_required_check(
            "audit_all",
            [
                args.python_bin,
                str(coach_script),
                "audit",
                "--project-dir",
                str(project_dir),
                "--audit-scope",
                "all",
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    required_checks.append(
        _run_required_check(
            "decision_gap_check",
            [
                args.python_bin,
                str(coach_script),
                "decision-gap-check",
                "--project-dir",
                str(project_dir),
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    required_checks.append(
        _run_required_check(
            "reflection_enforcement_gate",
            [
                args.python_bin,
                str(scripts_dir / "reflection_enforcement_gate_v0.py"),
                "--project-dir",
                str(project_dir),
                "--required-decision-status",
                "promoted",
                "--min-scaffold-reports",
                "1",
                "--min-required-status-mappings",
                "1",
                "--require-phase4-enforcement-report",
                "--phase4-enforcement-report",
                ".cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json",
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    required_checks.append(
        _run_required_check(
            "mistake_candidate_gate",
            [
                args.python_bin,
                str(scripts_dir / "mistake_candidate_gate_v0.py"),
                "--project-dir",
                str(project_dir),
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    required_checks.append(
        _run_required_check(
            "project_state_boundary_gate",
            [
                args.python_bin,
                str(scripts_dir / "project_state_boundary_gate_v0.py"),
                "--project-dir",
                str(project_dir),
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    required_checks.append(
        _run_required_check(
            "temporal_playbook_release_gate",
            [
                args.python_bin,
                str(scripts_dir / "temporal_playbook_release_gate_v0.py"),
                "--project-dir",
                str(project_dir),
                "--format",
                "json",
            ],
            cwd=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )

    rollout_mode_before_payload, rollout_mode_before_rc, rollout_mode_before_stderr, _, _ = _run_json_command(
        [
            args.rollout_coach_bin,
            "rollout-mode",
            "--project-dir",
            str(project_dir),
            "--format",
            "json",
        ],
        cwd=project_dir,
        timeout_seconds=args.timeout_seconds,
    )
    mode_before = (
        str(rollout_mode_before_payload.get("result", {}).get("mode", "unknown"))
        if isinstance(rollout_mode_before_payload.get("result", {}), dict)
        else "unknown"
    )

    rollback_steps: list[dict[str, Any]] = []
    if not args.skip_rollback_drill:
        for step_id, mode, reason, incident_ref in [
            (
                "rollback_drill_to_off",
                "off",
                f"phase5_{args.cycle_id}_rollback_drill_to_off",
                "",
            ),
            (
                "rollback_drill_restore_experimental",
                "experimental",
                f"phase5_{args.cycle_id}_rollback_drill_restore",
                f"phase5_{args.cycle_id}_rollback_drill_incident",
            ),
        ]:
            cmd = [
                args.rollout_coach_bin,
                "rollout-mode",
                "--project-dir",
                str(project_dir),
                "--set-mode",
                mode,
                "--changed-by",
                args.changed_by,
                "--reason",
                reason,
                "--format",
                "json",
            ]
            if incident_ref:
                cmd.extend(["--incident-ref", incident_ref])
            payload, returncode, stderr, stdout, elapsed = _run_json_command(
                cmd,
                cwd=project_dir,
                timeout_seconds=args.timeout_seconds,
            )
            payload_status = str(payload.get("status", "unknown")).lower() if payload else "unknown"
            status = "pass" if returncode == 0 and payload_status == "pass" else "fail"
            rollback_steps.append(
                {
                    "step_id": step_id,
                    "command": cmd,
                    "duration_seconds": elapsed,
                    "returncode": returncode,
                    "status": status,
                    "payload_status": payload_status,
                    "result": payload.get("result", {}) if isinstance(payload, dict) else {},
                    "stderr": stderr,
                    "stdout": stdout if returncode != 0 else "",
                }
            )

    rollout_mode_after_payload, rollout_mode_after_rc, rollout_mode_after_stderr, _, _ = _run_json_command(
        [
            args.rollout_coach_bin,
            "rollout-mode",
            "--project-dir",
            str(project_dir),
            "--format",
            "json",
        ],
        cwd=project_dir,
        timeout_seconds=args.timeout_seconds,
    )
    mode_after = (
        str(rollout_mode_after_payload.get("result", {}).get("mode", "unknown"))
        if isinstance(rollout_mode_after_payload.get("result", {}), dict)
        else "unknown"
    )

    rollout_audit_payload, rollout_audit_rc, rollout_audit_stderr, rollout_audit_stdout, _ = _run_json_command(
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
    rollout_audit_status = str(rollout_audit_payload.get("status", "unknown")).lower() if rollout_audit_payload else "unknown"
    rollout_audit_result = (
        rollout_audit_payload.get("result", {}) if isinstance(rollout_audit_payload.get("result", {}), dict) else {}
    )
    transition_report_path = project_dir / str(
        rollout_audit_result.get("report_path", ".cortex/reports/project_state/phase5_mode_transition_audit_report_v0.json")
    )
    transition_report_payload = {}
    if transition_report_path.exists():
        loaded = _load_json(transition_report_path)
        if isinstance(loaded, dict):
            transition_report_payload = loaded

    transition_completeness_rate = float(
        transition_report_payload.get("summary", {}).get(
            "transition_completeness_rate",
            rollout_audit_result.get("transition_completeness_rate", 0.0),
        )
        if isinstance(transition_report_payload.get("summary", {}), dict)
        else rollout_audit_result.get("transition_completeness_rate", 0.0)
    )
    transition_finding_count = int(
        transition_report_payload.get("summary", {}).get("finding_count", rollout_audit_result.get("finding_count", 0))
        if isinstance(transition_report_payload.get("summary", {}), dict)
        else rollout_audit_result.get("finding_count", 0)
    )

    quality_gate_runs: list[dict[str, Any]] = []
    quality_gate_durations: list[float] = []
    quality_gate_pass_count = 0
    quality_gate_measurement_mode = "required_ci_gate_full"
    quality_gate_workspace = project_dir
    quality_gate_env = os.environ.copy()
    workspace_cleanup_root: Path | None = None
    if "offline_probe" in phase4_measurement_mode:
        quality_gate_measurement_mode = "required_ci_gate_phase4_baseline_compatible_offline_probe"
        quality_gate_workspace = _prepare_ephemeral_workspace(project_dir)
        workspace_cleanup_root = quality_gate_workspace.parent
        quality_gate_env["UV_CACHE_DIR"] = str((project_dir / ".uv-cache").resolve())
        quality_gate_env["CORTEX_QG_SKIP_FOCUSED_TESTS"] = "1"

    try:
        for run_idx in range(max(1, int(args.ci_runs))):
            started = time.perf_counter()
            proc = subprocess.run(
                [args.quality_gate_script],
                cwd=str(quality_gate_workspace),
                text=True,
                capture_output=True,
                check=False,
                timeout=max(1, int(args.timeout_seconds)),
                env=quality_gate_env,
            )
            elapsed = time.perf_counter() - started
            quality_gate_durations.append(elapsed)
            passed = proc.returncode == 0
            if passed:
                quality_gate_pass_count += 1
            quality_gate_runs.append(
                {
                    "run": run_idx + 1,
                    "duration_seconds": elapsed,
                    "returncode": proc.returncode,
                    "status": "pass" if passed else "fail",
                    "summary": _format_quality_gate_summary(proc),
                }
            )
    finally:
        if workspace_cleanup_root is not None:
            shutil.rmtree(workspace_cleanup_root, ignore_errors=True)

    quality_gate_reliability = (
        float(quality_gate_pass_count / len(quality_gate_runs)) if quality_gate_runs else 0.0
    )
    quality_gate_median_seconds = _median(quality_gate_durations)
    ci_delta_percent = ((quality_gate_median_seconds - phase4_median_seconds) / phase4_median_seconds) * 100.0

    required_checks_pass = all(item["status"] == "pass" for item in required_checks)
    rollback_steps_pass = all(item["status"] == "pass" for item in rollback_steps)
    rollback_success = (
        rollout_mode_before_rc == 0
        and rollout_mode_after_rc == 0
        and rollout_audit_rc == 0
        and rollout_audit_status == "pass"
        and rollback_steps_pass
        and mode_after == "experimental"
    )
    if args.skip_rollback_drill:
        rollback_success = (
            rollout_mode_before_rc == 0
            and rollout_mode_after_rc == 0
            and rollout_audit_rc == 0
            and rollout_audit_status == "pass"
            and mode_after in {"experimental", "off", "default"}
        )

    stop_rule_incidents: list[dict[str, Any]] = []
    if not required_checks_pass:
        stop_rule_incidents.append(
            {
                "incident_id": f"phase5_{args.cycle_id}_required_gate_regression",
                "type": "required_governance_gate_failure",
                "detail": "One or more required governance checks failed.",
            }
        )
    if quality_gate_reliability < 1.0:
        stop_rule_incidents.append(
            {
                "incident_id": f"phase5_{args.cycle_id}_ci_reliability_drop",
                "type": "required_ci_reliability_failure",
                "detail": "quality_gate_ci had one or more failing runs.",
            }
        )
    if transition_finding_count > 0 or transition_completeness_rate < 1.0:
        stop_rule_incidents.append(
            {
                "incident_id": f"phase5_{args.cycle_id}_transition_audit_gap",
                "type": "transition_audit_incomplete",
                "detail": "Mode-transition audit reported findings or completeness below 1.0.",
            }
        )
    if not rollback_success:
        stop_rule_incidents.append(
            {
                "incident_id": f"phase5_{args.cycle_id}_rollback_drill_failure",
                "type": "rollback_drill_failed",
                "detail": "Rollback drill did not complete with final mode experimental.",
            }
        )

    target_results = {
        "required_governance_gate_reliability_met": quality_gate_reliability >= 1.0,
        "required_governance_checks_pass_met": required_checks_pass,
        "ci_runtime_delta_met": ci_delta_percent <= 10.0,
        "rollback_drill_success_met": rollback_success,
        "mode_transition_completeness_met": transition_completeness_rate >= 1.0,
        "stop_rule_incident_free_met": len(stop_rule_incidents) == 0,
    }
    status = "pass" if all(bool(v) for v in target_results.values()) else "fail"

    reliability_report = {
        "artifact": f"phase5_{args.cycle_id}_rollout_reliability_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "cycle_id": args.cycle_id,
        "measurement_mode": "phase5_rollout_reliability_pack_required_governance_bundle",
        "quality_gate_measurement_mode": quality_gate_measurement_mode,
        "quality_gate_script": args.quality_gate_script,
        "phase4_ci_baseline_source": args.phase4_ci_report,
        "phase4_ci_baseline_median_seconds": phase4_median_seconds,
        "required_checks": required_checks,
        "quality_gate_runs": {
            "runs": len(quality_gate_runs),
            "pass_count": quality_gate_pass_count,
            "reliability_rate": quality_gate_reliability,
            "durations_seconds": quality_gate_durations,
            "run_summaries": quality_gate_runs,
            "median_seconds": quality_gate_median_seconds,
            "delta_percent_vs_phase4": ci_delta_percent,
        },
        "rollout_mode": {
            "mode_before": mode_before,
            "mode_after": mode_after,
            "before_check_status": "pass" if rollout_mode_before_rc == 0 else "fail",
            "after_check_status": "pass" if rollout_mode_after_rc == 0 else "fail",
            "before_check_stderr": rollout_mode_before_stderr,
            "after_check_stderr": rollout_mode_after_stderr,
            "rollback_drill_skipped": bool(args.skip_rollback_drill),
            "rollback_drill_steps": rollback_steps,
            "rollback_drill_success": rollback_success,
        },
        "mode_transition_audit": {
            "status": rollout_audit_status,
            "returncode": rollout_audit_rc,
            "stderr": rollout_audit_stderr,
            "stdout": rollout_audit_stdout if rollout_audit_rc != 0 else "",
            "report_path": _safe_rel_path(project_dir, transition_report_path),
            "transition_completeness_rate": transition_completeness_rate,
            "finding_count": transition_finding_count,
            "transition_count": int(
                transition_report_payload.get("summary", {}).get(
                    "transition_count",
                    rollout_audit_result.get("transition_count", 0),
                )
                if isinstance(transition_report_payload.get("summary", {}), dict)
                else rollout_audit_result.get("transition_count", 0)
            ),
        },
        "summary": {
            "required_governance_checks_pass": required_checks_pass,
            "required_governance_check_count": len(required_checks),
            "required_governance_gate_reliability_rate": quality_gate_reliability,
            "ci_runtime_delta_percent": ci_delta_percent,
            "rollback_drill_success": rollback_success,
            "mode_transition_completeness_rate": transition_completeness_rate,
            "stop_rule_incident_count": len(stop_rule_incidents),
        },
        "targets": {
            "required_governance_gate_reliability": 1.0,
            "ci_runtime_delta_percent_max": 10.0,
            "mode_transition_completeness_rate": 1.0,
            "stop_rule_incident_count": 0,
        },
        "target_results": target_results,
        "stop_rule_incidents": stop_rule_incidents,
        "status": status,
    }
    _write_json(reliability_out, reliability_report)

    pass_count = sum(1 for item in required_checks if item["status"] == "pass")
    lines: list[str] = []
    lines.append(f"# Phase 5 {args.cycle_id.capitalize()} Governance Regression Report v0")
    lines.append("")
    lines.append(f"- Generated: {_now_iso()}")
    lines.append(f"- Project Dir: `{project_dir}`")
    lines.append(f"- Cycle: `{args.cycle_id}`")
    lines.append(f"- Overall Status: **{status.upper()}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Required checks executed: {len(required_checks)}")
    lines.append(f"- Required checks pass: {pass_count}")
    lines.append(f"- quality-gate-ci reliability: `{quality_gate_reliability:.3f}`")
    lines.append(f"- quality-gate-ci median delta vs Phase 4: `{ci_delta_percent:.6f}%`")
    lines.append(f"- Rollback drill success: `{rollback_success}`")
    lines.append(f"- Transition completeness rate: `{transition_completeness_rate:.3f}`")
    lines.append(f"- Stop-rule incidents: `{len(stop_rule_incidents)}`")
    lines.append("")
    lines.append("## Required Check Results")
    lines.append("")
    lines.append("| Check | Status | Return Code | Duration (s) |")
    lines.append("|---|---|---:|---:|")
    for item in required_checks:
        lines.append(
            f"| `{item['check_id']}` | `{item['status']}` | `{item['returncode']}` | `{item['duration_seconds']:.6f}` |"
        )
    lines.append("")
    lines.append("## quality_gate_ci Runs")
    lines.append("")
    lines.append("| Run | Status | Return Code | Duration (s) | Summary |")
    lines.append("|---:|---|---:|---:|---|")
    for run in quality_gate_runs:
        lines.append(
            f"| {run['run']} | `{run['status']}` | `{run['returncode']}` | `{run['duration_seconds']:.6f}` | {run['summary']} |"
        )
    if stop_rule_incidents:
        lines.append("")
        lines.append("## Stop-Rule Incidents")
        lines.append("")
        for incident in stop_rule_incidents:
            lines.append(f"- `{incident['incident_id']}`: {incident['detail']}")

    _write_text(governance_out, "\n".join(lines).rstrip() + "\n")

    if args.fail_on_target_miss and status != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

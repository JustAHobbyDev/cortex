#!/usr/bin/env python3
"""Generate Phase 2 performance and governance non-regression artifacts."""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run_command(
    cmd: list[str],
    cwd: Path,
    *,
    timeout_seconds: int,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = None
    if env_overrides:
        env = os.environ.copy()
        env.update(env_overrides)
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout_seconds,
        env=env,
    )


def _run_json_command(
    cmd: list[str],
    cwd: Path,
    *,
    timeout_seconds: int,
    env_overrides: dict[str, str] | None = None,
) -> tuple[dict[str, Any], subprocess.CompletedProcess[str]]:
    proc = _run_command(cmd, cwd, timeout_seconds=timeout_seconds, env_overrides=env_overrides)
    if not proc.stdout.strip():
        raise RuntimeError(f"missing JSON stdout for command: {cmd}\nstderr={proc.stderr}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"invalid JSON stdout for command: {cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        ) from exc
    return payload, proc


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil((pct / 100.0) * len(ordered)))
    idx = min(len(ordered) - 1, rank - 1)
    return float(ordered[idx])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--fixture-file",
        default=".cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json",
    )
    parser.add_argument("--coach-bin", default="cortex-coach")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--weighting-mode", choices=["uniform", "evidence_outcome_bias"], default="evidence_outcome_bias")
    parser.add_argument("--max-files", type=int, default=16)
    parser.add_argument("--max-chars-per-file", type=int, default=2000)
    parser.add_argument("--latency-runs-per-profile", type=int, default=30)
    parser.add_argument("--ci-runs", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--cortex-coach-repo", default="/tmp/cortex-coach")
    parser.add_argument(
        "--phase1-ci-report",
        default=".cortex/reports/project_state/phase1_ci_overhead_report_v0.json",
    )
    parser.add_argument(
        "--latency-out",
        default=".cortex/reports/project_state/phase2_latency_report_v0.json",
    )
    parser.add_argument(
        "--context-budget-out",
        default=".cortex/reports/project_state/phase2_context_budget_report_v0.json",
    )
    parser.add_argument(
        "--ci-overhead-out",
        default=".cortex/reports/project_state/phase2_ci_overhead_report_v0.json",
    )
    parser.add_argument(
        "--governance-regression-out",
        default=".cortex/reports/project_state/phase2_governance_regression_report_v0.md",
    )
    parser.add_argument("--fail-on-target-miss", action="store_true")
    return parser.parse_args()


def _build_query_map(fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(query["query_id"]): query for query in fixture.get("queries", []) if isinstance(query, dict)}


def _run_context_load(
    coach_bin: str,
    project_dir: Path,
    *,
    task: str,
    profile_id: str,
    weighting_mode: str,
    max_files: int,
    max_chars_per_file: int,
    timeout_seconds: int,
) -> tuple[dict[str, Any], float]:
    cmd = [
        coach_bin,
        "context-load",
        "--project-dir",
        str(project_dir),
        "--task",
        task,
        "--retrieval-profile",
        profile_id,
        "--weighting-mode",
        weighting_mode,
        "--max-files",
        str(max_files),
        "--max-chars-per-file",
        str(max_chars_per_file),
    ]
    started = time.perf_counter()
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout_seconds)
    elapsed = time.perf_counter() - started
    if proc.returncode != 0:
        raise RuntimeError(
            "context-load command failed\n"
            f"cmd={cmd}\n"
            f"returncode={proc.returncode}\n"
            f"stdout={proc.stdout}\n"
            f"stderr={proc.stderr}"
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"context-load output was not valid JSON\ncmd={cmd}\nstdout={proc.stdout}") from exc
    return payload, elapsed


def _budget_failures(bundle: dict[str, Any], *, max_files: int, max_chars_per_file: int) -> list[str]:
    failures: list[str] = []
    budget = bundle.get("budget", {})
    if bool(budget.get("unrestricted", False)):
        failures.append("unrestricted_fallback_used")
    selected_count = int(bundle.get("selected_file_count", 0))
    if selected_count > max_files:
        failures.append(f"selected_file_count_exceeded:{selected_count}>{max_files}")
    for item in bundle.get("files", []):
        excerpt = str(item.get("excerpt", ""))
        if len(excerpt) > max_chars_per_file:
            failures.append(
                f"excerpt_too_long:{item.get('path','unknown')}:{len(excerpt)}>{max_chars_per_file}"
            )
    return failures


def _format_quality_gate_summary(proc: subprocess.CompletedProcess[str]) -> str:
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return "no_output"
    if proc.returncode != 0:
        return lines[-1]
    for line in reversed(lines):
        if "passed in" in line or "PASS" in line:
            return line
    return lines[-1]


def main() -> int:
    args = _parse_args()
    repo_root = Path(args.project_dir).resolve()
    coach_repo = Path(args.cortex_coach_repo).resolve()
    fixture_path = Path(args.fixture_file)
    phase1_ci_report_path = Path(args.phase1_ci_report)

    fixture = _load_json(fixture_path)
    query_map = _build_query_map(fixture)

    # 1) Context-load latency and context-budget checks.
    profile_rows: list[dict[str, Any]] = []
    budget_failures_all: list[dict[str, Any]] = []
    all_durations: list[float] = []

    for profile in fixture.get("profiles", []):
        profile_id = str(profile.get("profile_id", ""))
        query_ids = [str(qid) for qid in profile.get("query_ids", [])]
        if not query_ids:
            raise ValueError(f"profile has no query ids: {profile_id}")
        durations: list[float] = []
        profile_failures: list[dict[str, Any]] = []

        for run_idx in range(args.latency_runs_per_profile):
            query_id = query_ids[run_idx % len(query_ids)]
            query = query_map.get(query_id)
            if query is None:
                raise ValueError(f"fixture missing query id {query_id!r}")
            bundle, elapsed = _run_context_load(
                args.coach_bin,
                repo_root,
                task=str(query["query_text"]),
                profile_id=profile_id,
                weighting_mode=args.weighting_mode,
                max_files=args.max_files,
                max_chars_per_file=args.max_chars_per_file,
                timeout_seconds=args.timeout_seconds,
            )
            durations.append(elapsed)
            all_durations.append(elapsed)

            failures = _budget_failures(bundle, max_files=args.max_files, max_chars_per_file=args.max_chars_per_file)
            if failures:
                detail = {
                    "profile_id": profile_id,
                    "query_id": query_id,
                    "run": run_idx + 1,
                    "failures": failures,
                }
                profile_failures.append(detail)
                budget_failures_all.append(detail)

        p95 = _percentile(durations, 95.0)
        profile_rows.append(
            {
                "profile_id": profile_id,
                "runs": len(durations),
                "query_ids_cycle": query_ids,
                "durations_seconds": durations,
                "min_seconds": min(durations),
                "max_seconds": max(durations),
                "mean_seconds": float(sum(durations) / len(durations)),
                "p50_seconds": _median(durations),
                "p95_seconds": p95,
                "target_p95_seconds": 2.0,
                "target_met": p95 <= 2.0,
                "budget_failures": len(profile_failures),
            }
        )

    latency_target_met = all(row["target_met"] for row in profile_rows)
    latency_report = {
        "artifact": "phase2_latency_report_v0",
        "version": "v0",
        "command": "context-load",
        "measurement_mode": "frozen_fixture_profile_cycle",
        "fixture_artifact": fixture.get("artifact"),
        "coach_bin": args.coach_bin,
        "weighting_mode": args.weighting_mode,
        "profiles": profile_rows,
        "aggregate": {
            "runs": len(all_durations),
            "min_seconds": min(all_durations) if all_durations else 0.0,
            "max_seconds": max(all_durations) if all_durations else 0.0,
            "mean_seconds": float(sum(all_durations) / len(all_durations)) if all_durations else 0.0,
            "p50_seconds": _median(all_durations),
            "p95_seconds": _percentile(all_durations, 95.0),
        },
        "target_p95_seconds": 2.0,
        "target_met": latency_target_met,
        "run_at": _now_iso(),
    }

    total_runs = args.latency_runs_per_profile * len(profile_rows)
    pass_runs = total_runs - len(budget_failures_all)
    compliance_rate = float(pass_runs / total_runs) if total_runs else 0.0
    context_budget_report = {
        "artifact": "phase2_context_budget_report_v0",
        "version": "v0",
        "command": "context-load",
        "measurement_mode": "frozen_fixture_profile_cycle",
        "fixture_artifact": fixture.get("artifact"),
        "coach_bin": args.coach_bin,
        "weighting_mode": args.weighting_mode,
        "max_files": args.max_files,
        "max_chars_per_file": args.max_chars_per_file,
        "runs": total_runs,
        "pass_runs": pass_runs,
        "compliance_rate": compliance_rate,
        "target_compliance_rate": 1.0,
        "target_met": compliance_rate >= 1.0,
        "profile_summaries": [
            {
                "profile_id": row["profile_id"],
                "runs": row["runs"],
                "budget_failures": row["budget_failures"],
                "compliance_rate": float((row["runs"] - row["budget_failures"]) / row["runs"]),
            }
            for row in profile_rows
        ],
        "failure_samples": budget_failures_all[:30],
        "run_at": _now_iso(),
    }

    # 2) CI overhead vs Phase 1 post baseline.
    phase1_ci_report = _load_json(phase1_ci_report_path)
    baseline_median = float(phase1_ci_report.get("post_phase_median_seconds", 0.0))
    ci_durations: list[float] = []
    ci_samples: list[dict[str, Any]] = []
    for idx in range(args.ci_runs):
        started = time.perf_counter()
        proc = _run_command(["./scripts/quality_gate_ci_v0.sh"], repo_root, timeout_seconds=args.timeout_seconds)
        elapsed = time.perf_counter() - started
        ci_durations.append(elapsed)
        ci_samples.append(
            {
                "run": idx + 1,
                "duration_seconds": elapsed,
                "returncode": proc.returncode,
                "summary": _format_quality_gate_summary(proc),
            }
        )
        if proc.returncode != 0:
            raise RuntimeError(f"quality gate failed during CI overhead run {idx+1}\n{proc.stdout}\n{proc.stderr}")

    phase2_ci_median = _median(ci_durations)
    delta_percent = 0.0
    if baseline_median > 0:
        delta_percent = ((phase2_ci_median - baseline_median) / baseline_median) * 100.0
    ci_overhead_report = {
        "artifact": "phase2_ci_overhead_report_v0",
        "version": "v0",
        "measurement_mode": "required_ci_gate_vs_phase1_post_baseline",
        "phase1_baseline_source": str(phase1_ci_report_path),
        "phase1_post_phase_median_seconds": baseline_median,
        "phase2_required_gate": "scripts/quality_gate_ci_v0.sh",
        "phase2_runs": args.ci_runs,
        "phase2_durations_seconds": ci_durations,
        "phase2_run_summaries": ci_samples,
        "phase2_median_seconds": phase2_ci_median,
        "delta_percent": delta_percent,
        "target_max_delta_percent": 10.0,
        "target_met": delta_percent <= 10.0,
        "run_at": _now_iso(),
    }

    # 3) Governance non-regression verification.
    decision_gap_cmd = [
        args.python_bin,
        "scripts/cortex_project_coach_v0.py",
        "decision-gap-check",
        "--project-dir",
        str(repo_root),
        "--format",
        "json",
    ]
    decision_gap_json, decision_gap_proc = _run_json_command(decision_gap_cmd, repo_root, timeout_seconds=args.timeout_seconds)

    reflection_cmd = [
        args.python_bin,
        "scripts/reflection_enforcement_gate_v0.py",
        "--project-dir",
        str(repo_root),
        "--required-decision-status",
        "promoted",
        "--min-scaffold-reports",
        "1",
        "--min-required-status-mappings",
        "1",
        "--format",
        "json",
    ]
    reflection_json, reflection_proc = _run_json_command(reflection_cmd, repo_root, timeout_seconds=args.timeout_seconds)

    audit_cmd = [
        args.python_bin,
        "scripts/cortex_project_coach_v0.py",
        "audit",
        "--project-dir",
        str(repo_root),
        "--audit-scope",
        "all",
        "--format",
        "json",
    ]
    audit_json, audit_proc = _run_json_command(audit_cmd, repo_root, timeout_seconds=args.timeout_seconds)

    coach_qg_proc = _run_command(["./scripts/quality_gate_ci_v0.sh"], coach_repo, timeout_seconds=args.timeout_seconds)
    coach_qg_summary = _format_quality_gate_summary(coach_qg_proc)

    governance_pass = (
        decision_gap_proc.returncode == 0
        and str(decision_gap_json.get("status", "")).lower() == "pass"
        and reflection_proc.returncode == 0
        and str(reflection_json.get("status", "")).lower() == "pass"
        and audit_proc.returncode == 0
        and str(audit_json.get("status", "")).lower() == "pass"
        and all(sample["returncode"] == 0 for sample in ci_samples)
        and coach_qg_proc.returncode == 0
    )

    governance_lines = [
        "# Phase 2 Governance Regression Report v0",
        "",
        "Version: v0  ",
        f"Status: {'Pass' if governance_pass else 'Fail'}  ",
        f"Date: {_today_utc()}  ",
        "Scope: Governance non-regression verification for Phase 2 retrieval/context quality implementation",
        "",
        "## Purpose",
        "",
        "Verify Phase 2 retrieval/context quality changes did not regress required governance checks or release-boundary gates.",
        "",
        "## Commands Executed",
        "",
        f"1. `{ ' '.join(decision_gap_cmd) }`",
        f"2. `{ ' '.join(reflection_cmd) }`",
        f"3. `{ ' '.join(audit_cmd) }`",
        f"4. `./scripts/quality_gate_ci_v0.sh` (in `{repo_root}`; repeated {args.ci_runs}x for CI overhead sample)",
        f"5. `./scripts/quality_gate_ci_v0.sh` (in `{coach_repo}`)",
        "",
        "## Results",
        "",
        "- `decision-gap-check`:",
        f"  - status: `{decision_gap_json.get('status', 'unknown')}`",
        f"  - run_at: `{decision_gap_json.get('run_at', 'unknown')}`",
        f"  - returncode: `{decision_gap_proc.returncode}`",
        "- `reflection_enforcement_gate_v0.py`:",
        f"  - status: `{reflection_json.get('status', 'unknown')}`",
        f"  - run_at: `{reflection_json.get('run_at', 'unknown')}`",
        f"  - returncode: `{reflection_proc.returncode}`",
        "- `audit --audit-scope all`:",
        f"  - status: `{audit_json.get('status', 'unknown')}`",
        f"  - run_at: `{audit_json.get('run_at', 'unknown')}`",
        f"  - artifact_conformance: `{audit_json.get('artifact_conformance', {}).get('status', 'unknown') if isinstance(audit_json.get('artifact_conformance'), dict) else 'unknown'}`",
        f"  - returncode: `{audit_proc.returncode}`",
        "- `cortex` quality gate (`scripts/quality_gate_ci_v0.sh`):",
        f"  - status: `{'PASS' if all(sample['returncode'] == 0 for sample in ci_samples) else 'FAIL'}`",
        f"  - runs: `{args.ci_runs}`",
        f"  - median_duration_seconds: `{phase2_ci_median:.6f}`",
        f"  - sample_summary: `{ci_samples[-1]['summary'] if ci_samples else 'n/a'}`",
        "- `cortex-coach` quality gate (`scripts/quality_gate_ci_v0.sh`):",
        f"  - status: `{'PASS' if coach_qg_proc.returncode == 0 else 'FAIL'}`",
        f"  - summary: `{coach_qg_summary}`",
        "",
        "## Conclusion",
        "",
        (
            "Governance non-regression target is satisfied for Phase 2 implementation."
            if governance_pass
            else "Governance non-regression target is not satisfied; see failing checks above."
        ),
        "",
    ]
    governance_report = "\n".join(governance_lines)

    # Persist artifacts.
    _write_json(Path(args.latency_out), latency_report)
    _write_json(Path(args.context_budget_out), context_budget_report)
    _write_json(Path(args.ci_overhead_out), ci_overhead_report)
    _write_text(Path(args.governance_regression_out), governance_report)

    all_targets_met = (
        latency_report["target_met"]
        and context_budget_report["target_met"]
        and ci_overhead_report["target_met"]
        and governance_pass
    )
    if args.fail_on_target_miss and not all_targets_met:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

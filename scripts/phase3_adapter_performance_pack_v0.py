#!/usr/bin/env python3
"""Generate Phase 3 adapter latency, budget, and CI overhead artifacts."""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import subprocess
import time
from dataclasses import dataclass
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


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil((pct / 100.0) * len(ordered)))
    idx = min(len(ordered) - 1, rank - 1)
    return float(ordered[idx])


def _format_quality_gate_summary(proc: subprocess.CompletedProcess[str]) -> str:
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return "no_output"
    if proc.returncode != 0:
        return lines[-1]
    for line in reversed(lines):
        if line.endswith("PASS") or "PASS" in line:
            return line
    return lines[-1]


def _warning_class(warning: str) -> str:
    parts = str(warning).split(":")
    if len(parts) >= 2:
        return f"{parts[0]}:{parts[1]}"
    return str(warning)


@dataclass(frozen=True)
class EvalCase:
    profile_id: str
    scenario_id: str
    query_id: str
    query_text: str
    adapter_mode: str
    fixture_ref: str
    expected_adapter_status: str


def _build_cases_by_profile(fixture: dict[str, Any]) -> dict[str, list[EvalCase]]:
    scenario_map = {
        str(item["scenario_id"]): item for item in fixture.get("scenarios", []) if isinstance(item, dict)
    }
    query_map = {
        str(item["query_id"]): item for item in fixture.get("queries", []) if isinstance(item, dict)
    }
    out: dict[str, list[EvalCase]] = {}
    for profile in fixture.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        profile_id = str(profile.get("profile_id", ""))
        cases: list[EvalCase] = []
        for scenario_id in profile.get("scenario_ids", []):
            scenario_id_str = str(scenario_id)
            scenario = scenario_map.get(scenario_id_str)
            if scenario is None:
                raise ValueError(f"missing scenario: {scenario_id_str}")
            for query_id in profile.get("query_ids", []):
                query_id_str = str(query_id)
                query = query_map.get(query_id_str)
                if query is None:
                    raise ValueError(f"missing query: {query_id_str}")
                if str(query.get("profile_id", "")) != profile_id:
                    raise ValueError(
                        f"query/profile mismatch for {query_id_str}: expected {profile_id}, "
                        f"got {query.get('profile_id')}"
                    )
                cases.append(
                    EvalCase(
                        profile_id=profile_id,
                        scenario_id=scenario_id_str,
                        query_id=query_id_str,
                        query_text=str(query.get("query_text", "")),
                        adapter_mode=str(scenario.get("adapter_mode", "off")),
                        fixture_ref=str(scenario.get("fixture_ref", "")),
                        expected_adapter_status=str(scenario.get("adapter_status_expected", "")),
                    )
                )
        out[profile_id] = cases
    return out


def _build_context_base_cmd(args: argparse.Namespace) -> list[str]:
    if args.coach_script:
        return [args.python_bin, str(Path(args.coach_script).resolve())]
    return [args.coach_bin]


def _build_context_env(args: argparse.Namespace) -> dict[str, str]:
    env = os.environ.copy()
    coach_pythonpath = str(args.coach_pythonpath).strip()
    if coach_pythonpath:
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = coach_pythonpath if not existing else f"{coach_pythonpath}{os.pathsep}{existing}"
    return env


def _run_context_load(
    base_cmd: list[str],
    env: dict[str, str],
    *,
    project_dir: Path,
    case: EvalCase,
    weighting_mode: str,
    adapter_max_items: int,
    adapter_stale_seconds: int,
    max_files: int,
    max_chars_per_file: int,
    timeout_seconds: int,
) -> tuple[dict[str, Any], float]:
    cmd = [
        *base_cmd,
        "context-load",
        "--project-dir",
        str(project_dir),
        "--task",
        case.query_text,
        "--retrieval-profile",
        case.profile_id,
        "--weighting-mode",
        weighting_mode,
        "--adapter-mode",
        case.adapter_mode,
        "--adapter-max-items",
        str(adapter_max_items),
        "--adapter-stale-seconds",
        str(adapter_stale_seconds),
        "--max-files",
        str(max_files),
        "--max-chars-per-file",
        str(max_chars_per_file),
    ]
    if case.adapter_mode == "beads_file":
        cmd.extend(["--adapter-file", case.fixture_ref])

    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=str(project_dir),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout_seconds,
        env=env,
    )
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
        raise RuntimeError(f"context-load returned invalid JSON\ncmd={cmd}\nstdout={proc.stdout}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"context-load returned non-object JSON\ncmd={cmd}\nstdout={proc.stdout}")
    return payload, elapsed


def _budget_failures(
    bundle: dict[str, Any],
    *,
    case: EvalCase,
    max_files: int,
    max_chars_per_file: int,
    adapter_max_items: int,
) -> list[str]:
    failures: list[str] = []
    budget = bundle.get("budget", {})
    if bool(budget.get("unrestricted", False)):
        failures.append("unrestricted_fallback_used")

    selected_count = int(bundle.get("selected_file_count", 0))
    if selected_count > max_files:
        failures.append(f"selected_file_count_exceeded:{selected_count}>{max_files}")

    for item in bundle.get("files", []):
        if not isinstance(item, dict):
            continue
        excerpt = str(item.get("excerpt", ""))
        if len(excerpt) > max_chars_per_file:
            failures.append(
                f"excerpt_too_long:{item.get('path','unknown')}:{len(excerpt)}>{max_chars_per_file}"
            )

    adapter = bundle.get("adapter", {})
    adapter_status = str(adapter.get("status", "")) if isinstance(adapter, dict) else ""
    if adapter_status != case.expected_adapter_status:
        failures.append(
            f"adapter_status_mismatch:{adapter_status or 'missing'}!={case.expected_adapter_status}"
        )
    adapter_mode = str(adapter.get("mode", "")) if isinstance(adapter, dict) else ""
    if adapter_mode != "beads_file":
        failures.append(f"adapter_mode_mismatch:{adapter_mode or 'missing'}!=beads_file")
    adapter_selected_count = int(adapter.get("selected_count", 0)) if isinstance(adapter, dict) else 0
    if adapter_selected_count > adapter_max_items:
        failures.append(f"adapter_selected_count_exceeded:{adapter_selected_count}>{adapter_max_items}")
    return failures


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--fixture-file",
        default=".cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json",
    )
    parser.add_argument("--coach-bin", default="cortex-coach")
    parser.add_argument("--coach-script", default="")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--coach-pythonpath", default="")
    parser.add_argument(
        "--weighting-mode",
        choices=["uniform", "evidence_outcome_bias"],
        default="evidence_outcome_bias",
    )
    parser.add_argument("--adapter-max-items", type=int, default=4)
    parser.add_argument("--adapter-stale-seconds", type=int, default=86400)
    parser.add_argument("--max-files", type=int, default=24)
    parser.add_argument("--max-chars-per-file", type=int, default=1200)
    parser.add_argument("--latency-runs-per-profile", type=int, default=30)
    parser.add_argument("--ci-runs", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument(
        "--phase2-ci-report",
        default=".cortex/reports/project_state/phase2_ci_overhead_report_v0.json",
    )
    parser.add_argument(
        "--latency-out",
        default=".cortex/reports/project_state/phase3_adapter_latency_report_v0.json",
    )
    parser.add_argument(
        "--budget-out",
        default=".cortex/reports/project_state/phase3_adapter_budget_report_v0.json",
    )
    parser.add_argument(
        "--ci-overhead-out",
        default=".cortex/reports/project_state/phase3_ci_overhead_report_v0.json",
    )
    parser.add_argument("--fail-on-target-miss", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    fixture = _load_json(Path(args.fixture_file))
    if not isinstance(fixture, dict):
        raise ValueError(f"fixture must be object: {args.fixture_file}")
    cases_by_profile = _build_cases_by_profile(fixture)
    if not cases_by_profile:
        raise ValueError("no profile cases generated from fixture")

    base_cmd = _build_context_base_cmd(args)
    env = _build_context_env(args)

    profile_rows: list[dict[str, Any]] = []
    all_durations: list[float] = []
    budget_failures_all: list[dict[str, Any]] = []

    for profile_id, profile_cases in cases_by_profile.items():
        if not profile_cases:
            raise ValueError(f"profile has zero cases: {profile_id}")
        durations: list[float] = []
        profile_failures: list[dict[str, Any]] = []
        case_ids = [f"{c.scenario_id}:{c.query_id}" for c in profile_cases]

        for run_idx in range(args.latency_runs_per_profile):
            case = profile_cases[run_idx % len(profile_cases)]
            bundle, elapsed = _run_context_load(
                base_cmd,
                env,
                project_dir=project_dir,
                case=case,
                weighting_mode=args.weighting_mode,
                adapter_max_items=max(1, int(args.adapter_max_items)),
                adapter_stale_seconds=max(0, int(args.adapter_stale_seconds)),
                max_files=max(1, int(args.max_files)),
                max_chars_per_file=max(100, int(args.max_chars_per_file)),
                timeout_seconds=max(1, int(args.timeout_seconds)),
            )
            durations.append(elapsed)
            all_durations.append(elapsed)

            failures = _budget_failures(
                bundle,
                case=case,
                max_files=max(1, int(args.max_files)),
                max_chars_per_file=max(100, int(args.max_chars_per_file)),
                adapter_max_items=max(1, int(args.adapter_max_items)),
            )
            if failures:
                detail = {
                    "profile_id": profile_id,
                    "run": run_idx + 1,
                    "case_id": f"{case.scenario_id}:{case.query_id}",
                    "failures": failures,
                    "warning_classes": sorted(
                        {_warning_class(str(w)) for w in list(bundle.get("warnings", []))}
                    ),
                }
                profile_failures.append(detail)
                budget_failures_all.append(detail)

        p95 = _percentile(durations, 95.0)
        profile_rows.append(
            {
                "profile_id": profile_id,
                "runs": len(durations),
                "fixture_cases_cycle": case_ids,
                "durations_seconds": durations,
                "min_seconds": min(durations),
                "max_seconds": max(durations),
                "mean_seconds": float(sum(durations) / len(durations)),
                "p50_seconds": _median(durations),
                "p95_seconds": p95,
                "target_p95_seconds": 2.5,
                "target_met": p95 <= 2.5,
                "budget_failures": len(profile_failures),
            }
        )

    latency_target_met = all(row["target_met"] for row in profile_rows)
    latency_report = {
        "artifact": "phase3_adapter_latency_report_v0",
        "version": "v0",
        "measurement_mode": "frozen_fixture_profile_cycle_adapter_enabled",
        "fixture_artifact": fixture.get("artifact"),
        "coach_command": base_cmd,
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
        "target_p95_seconds": 2.5,
        "target_met": latency_target_met,
        "run_at": _now_iso(),
    }

    total_runs = args.latency_runs_per_profile * len(profile_rows)
    pass_runs = total_runs - len(budget_failures_all)
    compliance_rate = float(pass_runs / total_runs) if total_runs else 0.0
    budget_report = {
        "artifact": "phase3_adapter_budget_report_v0",
        "version": "v0",
        "measurement_mode": "frozen_fixture_profile_cycle_adapter_enabled",
        "fixture_artifact": fixture.get("artifact"),
        "coach_command": base_cmd,
        "weighting_mode": args.weighting_mode,
        "max_files": max(1, int(args.max_files)),
        "max_chars_per_file": max(100, int(args.max_chars_per_file)),
        "adapter_max_items": max(1, int(args.adapter_max_items)),
        "runs": total_runs,
        "pass_runs": pass_runs,
        "compliance_rate": compliance_rate,
        "target_compliance_rate": 1.0,
        "target_min_runs": 50,
        "target_met": bool(compliance_rate >= 1.0 and total_runs >= 50),
        "profile_summaries": [
            {
                "profile_id": row["profile_id"],
                "runs": row["runs"],
                "budget_failures": row["budget_failures"],
                "compliance_rate": float((row["runs"] - row["budget_failures"]) / row["runs"]),
            }
            for row in profile_rows
        ],
        "failure_samples": budget_failures_all[:50],
        "run_at": _now_iso(),
    }

    phase2_ci_report = _load_json(Path(args.phase2_ci_report))
    phase2_median = float(phase2_ci_report.get("phase2_median_seconds", 0.0))
    ci_durations: list[float] = []
    ci_samples: list[dict[str, Any]] = []
    for idx in range(args.ci_runs):
        started = time.perf_counter()
        proc = subprocess.run(
            ["./scripts/quality_gate_ci_v0.sh"],
            cwd=str(project_dir),
            text=True,
            capture_output=True,
            check=False,
            timeout=max(1, int(args.timeout_seconds)),
        )
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
            raise RuntimeError(
                f"quality_gate_ci failed on CI run {idx + 1}\nstdout={proc.stdout}\nstderr={proc.stderr}"
            )

    phase3_median = _median(ci_durations)
    delta_percent = 0.0
    if phase2_median > 0:
        delta_percent = ((phase3_median - phase2_median) / phase2_median) * 100.0
    ci_overhead_report = {
        "artifact": "phase3_ci_overhead_report_v0",
        "version": "v0",
        "measurement_mode": "required_ci_gate_vs_phase2_baseline",
        "phase2_baseline_source": str(args.phase2_ci_report),
        "phase2_median_seconds": phase2_median,
        "phase3_required_gate": "scripts/quality_gate_ci_v0.sh",
        "phase3_runs": args.ci_runs,
        "phase3_durations_seconds": ci_durations,
        "phase3_run_summaries": ci_samples,
        "phase3_median_seconds": phase3_median,
        "delta_percent": delta_percent,
        "target_max_delta_percent": 10.0,
        "target_met": delta_percent <= 10.0,
        "run_at": _now_iso(),
    }

    _write_json(Path(args.latency_out), latency_report)
    _write_json(Path(args.budget_out), budget_report)
    _write_json(Path(args.ci_overhead_out), ci_overhead_report)

    all_targets_met = latency_report["target_met"] and budget_report["target_met"] and ci_overhead_report["target_met"]
    if args.fail_on_target_miss and not all_targets_met:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

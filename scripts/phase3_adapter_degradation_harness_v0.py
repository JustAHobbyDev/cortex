#!/usr/bin/env python3
"""Generate Phase 3 adapter degradation and determinism artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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


def _json_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _round_float(value: Any, default: float = 0.0) -> float:
    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return round(default, 6)


def _warning_class(warning: str) -> str:
    parts = str(warning).split(":")
    if len(parts) >= 2:
        return f"{parts[0]}:{parts[1]}"
    return str(warning)


def _warning_classes(warnings: list[Any]) -> list[str]:
    classes = {_warning_class(str(item)) for item in warnings}
    return sorted(classes)


def _failure_mode_for_scenario(scenario_id: str) -> str:
    sid = scenario_id.lower()
    if "missing_file" in sid:
        return "missing_file"
    if "invalid_json" in sid:
        return "invalid_json"
    if "stale" in sid:
        return "stale_metadata"
    if "timeout" in sid:
        return "timeout_simulated"
    return "healthy"


def _normalize_score_breakdown(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, float] = {}
    for key in sorted(value):
        out[str(key)] = _round_float(value[key], 0.0)
    return out


def _normalize_bundle_for_hash(bundle: dict[str, Any]) -> dict[str, Any]:
    adapter_raw = bundle.get("adapter", {})
    adapter = {
        "mode": str(adapter_raw.get("mode", "")) if isinstance(adapter_raw, dict) else "",
        "status": str(adapter_raw.get("status", "")) if isinstance(adapter_raw, dict) else "",
        "adapter_id": str(adapter_raw.get("adapter_id", "")) if isinstance(adapter_raw, dict) else "",
        "candidate_count": int(adapter_raw.get("candidate_count", 0)) if isinstance(adapter_raw, dict) else 0,
        "selected_count": int(adapter_raw.get("selected_count", 0)) if isinstance(adapter_raw, dict) else 0,
        "max_items": int(adapter_raw.get("max_items", 0)) if isinstance(adapter_raw, dict) else 0,
        "stale_threshold_seconds": int(adapter_raw.get("stale_threshold_seconds", 0))
        if isinstance(adapter_raw, dict)
        else 0,
    }

    files: list[dict[str, Any]] = []
    for item in bundle.get("files", []):
        if not isinstance(item, dict):
            continue
        prov = item.get("provenance", {})
        adapter_item = item.get("adapter", {})
        files.append(
            {
                "path": str(item.get("path", "")),
                "selected_by": str(item.get("selected_by", "")),
                "rank": item.get("rank"),
                "combined_score": _round_float(item.get("combined_score", 0.0)),
                "confidence": _round_float(item.get("confidence", 0.0)),
                "score_breakdown": _normalize_score_breakdown(item.get("score_breakdown", {})),
                "provenance": {
                    "source_kind": str(prov.get("source_kind", "")) if isinstance(prov, dict) else "",
                    "source_ref": str(prov.get("source_ref", "")) if isinstance(prov, dict) else "",
                    "source_refs": sorted(str(v) for v in prov.get("source_refs", []))
                    if isinstance(prov, dict) and isinstance(prov.get("source_refs"), list)
                    else [],
                },
                "adapter": {
                    "adapter_id": str(adapter_item.get("adapter_id", "")) if isinstance(adapter_item, dict) else "",
                    "item_id": str(adapter_item.get("item_id", "")) if isinstance(adapter_item, dict) else "",
                    "state": str(adapter_item.get("state", "")) if isinstance(adapter_item, dict) else "",
                    "priority": adapter_item.get("priority") if isinstance(adapter_item, dict) else None,
                    "source_updated_at": str(adapter_item.get("source_updated_at", ""))
                    if isinstance(adapter_item, dict)
                    else "",
                    "adapter_fetched_at": str(adapter_item.get("adapter_fetched_at", ""))
                    if isinstance(adapter_item, dict)
                    else "",
                    "staleness_seconds": adapter_item.get("staleness_seconds")
                    if isinstance(adapter_item, dict)
                    else None,
                },
            }
        )

    return {
        "task_key": str(bundle.get("task_key", "")),
        "retrieval_profile": str(bundle.get("retrieval_profile", "")),
        "weighting_mode": str(bundle.get("weighting_mode", "")),
        "adapter": adapter,
        "selected_file_count": int(bundle.get("selected_file_count", 0)),
        "files": files,
        "warning_classes": _warning_classes(list(bundle.get("warnings", []))),
    }


@dataclass(frozen=True)
class EvalCase:
    profile_id: str
    scenario_id: str
    scenario_description: str
    query_id: str
    query_text: str
    adapter_mode: str
    fixture_ref: str
    expected_adapter_status: str

    @property
    def case_id(self) -> str:
        return f"{self.profile_id}:{self.scenario_id}:{self.query_id}"


@dataclass
class RunResult:
    command_success: bool
    returncode: int
    elapsed_seconds: float
    bundle: dict[str, Any] | None
    error: str | None


def _build_cases(fixture: dict[str, Any]) -> list[EvalCase]:
    scenario_map = {
        str(item["scenario_id"]): item for item in fixture.get("scenarios", []) if isinstance(item, dict)
    }
    query_map = {
        str(item["query_id"]): item for item in fixture.get("queries", []) if isinstance(item, dict)
    }
    cases: list[EvalCase] = []
    for profile in fixture.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        profile_id = str(profile.get("profile_id", ""))
        for scenario_id in profile.get("scenario_ids", []):
            scenario = scenario_map.get(str(scenario_id))
            if scenario is None:
                raise ValueError(f"missing scenario definition: {scenario_id}")
            for query_id in profile.get("query_ids", []):
                query = query_map.get(str(query_id))
                if query is None:
                    raise ValueError(f"missing query definition: {query_id}")
                if str(query.get("profile_id", "")) != profile_id:
                    raise ValueError(
                        f"query/profile mismatch for {query_id}: expected profile {profile_id}, "
                        f"got {query.get('profile_id')}"
                    )
                cases.append(
                    EvalCase(
                        profile_id=profile_id,
                        scenario_id=str(scenario_id),
                        scenario_description=str(scenario.get("description", "")),
                        query_id=str(query_id),
                        query_text=str(query.get("query_text", "")),
                        adapter_mode=str(scenario.get("adapter_mode", "off")),
                        fixture_ref=str(scenario.get("fixture_ref", "")),
                        expected_adapter_status=str(scenario.get("adapter_status_expected", "")),
                    )
                )
    return cases


def _build_coach_base_command(args: argparse.Namespace) -> list[str]:
    if args.coach_script:
        return [args.python_bin, str(Path(args.coach_script).resolve())]
    return [args.coach_bin]


def _build_env(args: argparse.Namespace) -> dict[str, str]:
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
) -> RunResult:
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
        error = (
            "context-load returned non-zero exit code "
            f"({proc.returncode}) for {case.case_id}; stderr={proc.stderr.strip()}; stdout={proc.stdout.strip()}"
        )
        return RunResult(False, proc.returncode, elapsed, None, error)

    try:
        bundle = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return RunResult(
            False,
            proc.returncode,
            elapsed,
            None,
            f"context-load returned invalid JSON for {case.case_id}: {exc}; stdout={proc.stdout.strip()}",
        )
    if not isinstance(bundle, dict):
        return RunResult(
            False,
            proc.returncode,
            elapsed,
            None,
            f"context-load returned non-object payload for {case.case_id}",
        )
    return RunResult(True, proc.returncode, elapsed, bundle, None)


def _has_selected_prefix(bundle: dict[str, Any], prefix: str) -> bool:
    for item in bundle.get("files", []):
        if str(item.get("selected_by", "")).startswith(prefix):
            return True
    return False


def _evaluate_degradation(
    cases: list[EvalCase],
    *,
    project_dir: Path,
    base_cmd: list[str],
    env: dict[str, str],
    weighting_mode: str,
    adapter_max_items: int,
    adapter_stale_seconds: int,
    max_files: int,
    max_chars_per_file: int,
    timeout_seconds: int,
    degradation_runs_per_case: int,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    total_duration_seconds = 0.0
    run_count = 0

    for case in cases:
        failure_mode = _failure_mode_for_scenario(case.scenario_id)
        case_runs: list[dict[str, Any]] = []
        for run_index in range(1, degradation_runs_per_case + 1):
            run = _run_context_load(
                base_cmd,
                env,
                project_dir=project_dir,
                case=case,
                weighting_mode=weighting_mode,
                adapter_max_items=adapter_max_items,
                adapter_stale_seconds=adapter_stale_seconds,
                max_files=max_files,
                max_chars_per_file=max_chars_per_file,
                timeout_seconds=timeout_seconds,
            )
            run_count += 1
            total_duration_seconds += run.elapsed_seconds

            observed_status = None
            has_control_plane = False
            has_task_slice = False
            warning_classes: list[str] = []
            degraded_warning_present = False
            stale_warning_present = False
            if run.bundle is not None:
                adapter = run.bundle.get("adapter", {})
                if isinstance(adapter, dict):
                    observed_status = str(adapter.get("status", ""))
                has_control_plane = _has_selected_prefix(run.bundle, "control_plane")
                has_task_slice = _has_selected_prefix(run.bundle, "task:")
                warning_classes = _warning_classes(list(run.bundle.get("warnings", [])))
                degraded_warning_present = any(
                    warning.startswith("adapter_degraded:") for warning in warning_classes
                )
                stale_warning_present = "adapter_warning:stale_item" in warning_classes

            fail_open_success = run.command_success and has_control_plane and has_task_slice
            status_match = observed_status == case.expected_adapter_status
            warning_expectation_met = True
            if case.expected_adapter_status == "degraded":
                warning_expectation_met = degraded_warning_present
            elif failure_mode == "stale_metadata":
                warning_expectation_met = stale_warning_present

            passed = bool(fail_open_success and status_match and warning_expectation_met)
            case_runs.append(
                {
                    "run_index": run_index,
                    "elapsed_seconds": round(run.elapsed_seconds, 6),
                    "command_success": run.command_success,
                    "returncode": run.returncode,
                    "error": run.error,
                    "expected_adapter_status": case.expected_adapter_status,
                    "observed_adapter_status": observed_status,
                    "status_match": status_match,
                    "has_control_plane": has_control_plane,
                    "has_task_slice": has_task_slice,
                    "fail_open_success": fail_open_success,
                    "warning_classes": warning_classes,
                    "degraded_warning_present": degraded_warning_present,
                    "stale_warning_present": stale_warning_present,
                    "warning_expectation_met": warning_expectation_met,
                    "pass": passed,
                }
            )

        case_pass = all(run["pass"] for run in case_runs)
        results.append(
            {
                "case_id": case.case_id,
                "profile_id": case.profile_id,
                "scenario_id": case.scenario_id,
                "scenario_description": case.scenario_description,
                "query_id": case.query_id,
                "query_text": case.query_text,
                "adapter_fixture": case.fixture_ref,
                "failure_mode": failure_mode,
                "expected_adapter_status": case.expected_adapter_status,
                "pass": case_pass,
                "runs": case_runs,
            }
        )

    failure_cases = [row for row in results if row["failure_mode"] != "healthy"]
    failure_case_count = len(failure_cases)
    failure_case_pass_count = sum(1 for row in failure_cases if row["pass"])
    fail_open_rate = (
        round(failure_case_pass_count / failure_case_count, 6) if failure_case_count else 0.0
    )

    return {
        "artifact": "phase3_adapter_degradation_report_v0",
        "version": "v0",
        "generated_at": _now_iso(),
        "target": {
            "failure_scenario_fail_open_rate": 1.0,
            "degradation_runs_per_case": degradation_runs_per_case,
        },
        "summary": {
            "case_count": len(results),
            "failure_case_count": failure_case_count,
            "failure_case_pass_count": failure_case_pass_count,
            "failure_case_fail_open_rate": fail_open_rate,
            "pass": bool(failure_case_count > 0 and failure_case_pass_count == failure_case_count),
            "total_duration_seconds": round(total_duration_seconds, 6),
            "run_count": run_count,
        },
        "cases": results,
    }


def _evaluate_determinism(
    cases: list[EvalCase],
    *,
    project_dir: Path,
    base_cmd: list[str],
    env: dict[str, str],
    weighting_mode: str,
    adapter_max_items: int,
    adapter_stale_seconds: int,
    max_files: int,
    max_chars_per_file: int,
    timeout_seconds: int,
    runs_per_case: int,
) -> dict[str, Any]:
    case_rows: list[dict[str, Any]] = []
    total_duration_seconds = 0.0
    total_runs = 0

    for case in cases:
        hash_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        warning_class_set: set[str] = set()
        errors: list[str] = []

        for _ in range(runs_per_case):
            run = _run_context_load(
                base_cmd,
                env,
                project_dir=project_dir,
                case=case,
                weighting_mode=weighting_mode,
                adapter_max_items=adapter_max_items,
                adapter_stale_seconds=adapter_stale_seconds,
                max_files=max_files,
                max_chars_per_file=max_chars_per_file,
                timeout_seconds=timeout_seconds,
            )
            total_runs += 1
            total_duration_seconds += run.elapsed_seconds
            if not run.command_success or run.bundle is None:
                errors.append(run.error or f"unknown_error:{case.case_id}")
                continue

            adapter = run.bundle.get("adapter", {})
            observed_status = str(adapter.get("status", "")) if isinstance(adapter, dict) else ""
            status_counts[observed_status] = status_counts.get(observed_status, 0) + 1
            warning_class_set.update(_warning_classes(list(run.bundle.get("warnings", []))))
            normalized = _normalize_bundle_for_hash(run.bundle)
            digest = _json_hash(normalized)
            hash_counts[digest] = hash_counts.get(digest, 0) + 1

        unique_hashes = sorted(hash_counts.keys())
        unique_statuses = sorted(status_counts.keys())
        status_match_all_runs = bool(unique_statuses == [case.expected_adapter_status])
        deterministic = bool(
            not errors and len(unique_hashes) == 1 and status_match_all_runs and sum(hash_counts.values()) == runs_per_case
        )
        case_rows.append(
            {
                "case_id": case.case_id,
                "profile_id": case.profile_id,
                "scenario_id": case.scenario_id,
                "query_id": case.query_id,
                "query_text": case.query_text,
                "failure_mode": _failure_mode_for_scenario(case.scenario_id),
                "expected_adapter_status": case.expected_adapter_status,
                "runs_per_case": runs_per_case,
                "command_failure_count": len(errors),
                "errors": errors[:5],
                "status_counts": status_counts,
                "status_match_all_runs": status_match_all_runs,
                "unique_warning_classes": sorted(warning_class_set),
                "unique_hash_count": len(unique_hashes),
                "hash_counts": hash_counts,
                "deterministic_hash": unique_hashes[0] if len(unique_hashes) == 1 else None,
                "deterministic": deterministic,
            }
        )

    deterministic_case_count = sum(1 for row in case_rows if row["deterministic"])
    determinism_rate = round(deterministic_case_count / len(case_rows), 6) if case_rows else 0.0

    return {
        "artifact": "phase3_adapter_determinism_report_v0",
        "version": "v0",
        "generated_at": _now_iso(),
        "target": {
            "determinism_rate": 1.0,
            "runs_per_case_min": 30,
        },
        "summary": {
            "case_count": len(case_rows),
            "deterministic_case_count": deterministic_case_count,
            "determinism_rate": determinism_rate,
            "runs_per_case": runs_per_case,
            "total_runs": total_runs,
            "pass": bool(
                case_rows
                and deterministic_case_count == len(case_rows)
                and runs_per_case >= 30
            ),
            "total_duration_seconds": round(total_duration_seconds, 6),
        },
        "cases": case_rows,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--fixture-file",
        default=".cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json",
    )
    parser.add_argument(
        "--coach-bin",
        default="cortex-coach",
        help="Coach binary when --coach-script is not provided.",
    )
    parser.add_argument(
        "--coach-script",
        default="",
        help="Optional coach script path. When set, command becomes: --python-bin <coach-script> ...",
    )
    parser.add_argument(
        "--python-bin",
        default="python3",
        help="Python interpreter used with --coach-script.",
    )
    parser.add_argument(
        "--coach-pythonpath",
        default="",
        help="Optional PYTHONPATH prefix for coach script execution.",
    )
    parser.add_argument(
        "--weighting-mode",
        choices=["uniform", "evidence_outcome_bias"],
        default="evidence_outcome_bias",
    )
    parser.add_argument("--adapter-max-items", type=int, default=4)
    parser.add_argument("--adapter-stale-seconds", type=int, default=86400)
    parser.add_argument("--max-files", type=int, default=24)
    parser.add_argument("--max-chars-per-file", type=int, default=1200)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--runs-per-case", type=int, default=30)
    parser.add_argument("--degradation-runs-per-case", type=int, default=1)
    parser.add_argument(
        "--degradation-out",
        default=".cortex/reports/project_state/phase3_adapter_degradation_report_v0.json",
    )
    parser.add_argument(
        "--determinism-out",
        default=".cortex/reports/project_state/phase3_adapter_determinism_report_v0.json",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    fixture_path = Path(args.fixture_file)
    fixture = _load_json(fixture_path)
    if not isinstance(fixture, dict):
        raise ValueError(f"fixture must be a JSON object: {fixture_path}")

    cases = _build_cases(fixture)
    if not cases:
        raise ValueError(f"fixture generated zero cases: {fixture_path}")

    base_cmd = _build_coach_base_command(args)
    env = _build_env(args)

    degradation_report = _evaluate_degradation(
        cases,
        project_dir=project_dir,
        base_cmd=base_cmd,
        env=env,
        weighting_mode=args.weighting_mode,
        adapter_max_items=max(1, int(args.adapter_max_items)),
        adapter_stale_seconds=max(0, int(args.adapter_stale_seconds)),
        max_files=max(1, int(args.max_files)),
        max_chars_per_file=max(100, int(args.max_chars_per_file)),
        timeout_seconds=max(1, int(args.timeout_seconds)),
        degradation_runs_per_case=max(1, int(args.degradation_runs_per_case)),
    )
    determinism_report = _evaluate_determinism(
        cases,
        project_dir=project_dir,
        base_cmd=base_cmd,
        env=env,
        weighting_mode=args.weighting_mode,
        adapter_max_items=max(1, int(args.adapter_max_items)),
        adapter_stale_seconds=max(0, int(args.adapter_stale_seconds)),
        max_files=max(1, int(args.max_files)),
        max_chars_per_file=max(100, int(args.max_chars_per_file)),
        timeout_seconds=max(1, int(args.timeout_seconds)),
        runs_per_case=max(1, int(args.runs_per_case)),
    )

    degradation_report["fixture_file"] = str(fixture_path)
    degradation_report["coach_command"] = base_cmd
    determinism_report["fixture_file"] = str(fixture_path)
    determinism_report["coach_command"] = base_cmd

    _write_json(Path(args.degradation_out), degradation_report)
    _write_json(Path(args.determinism_out), determinism_report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

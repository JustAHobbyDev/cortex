#!/usr/bin/env python3
"""Generate Phase 3 governance non-regression evidence under adapter failure scenarios."""

from __future__ import annotations

import argparse
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


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _warning_class(warning: str) -> str:
    parts = str(warning).split(":")
    if len(parts) >= 2:
        return f"{parts[0]}:{parts[1]}"
    return str(warning)


def _warning_classes(warnings: list[Any]) -> list[str]:
    return sorted({_warning_class(str(item)) for item in warnings})


def _failure_mode_for_scenario(scenario_id: str) -> str:
    sid = scenario_id.lower()
    if "missing_file" in sid:
        return "missing_file"
    if "invalid_json" in sid:
        return "invalid_json_or_payload_fault"
    if "stale" in sid:
        return "stale_metadata"
    if "timeout" in sid:
        return "timeout_simulated"
    return "healthy"


@dataclass(frozen=True)
class ProbeCase:
    profile_id: str
    scenario_id: str
    query_id: str
    query_text: str
    adapter_mode: str
    fixture_ref: str
    expected_adapter_status: str
    failure_mode: str

    @property
    def case_id(self) -> str:
        return f"{self.profile_id}:{self.scenario_id}:{self.query_id}"


def _build_cases(fixture: dict[str, Any]) -> list[ProbeCase]:
    scenario_map = {
        str(item["scenario_id"]): item for item in fixture.get("scenarios", []) if isinstance(item, dict)
    }
    query_map = {
        str(item["query_id"]): item for item in fixture.get("queries", []) if isinstance(item, dict)
    }
    out: list[ProbeCase] = []
    for profile in fixture.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        profile_id = str(profile.get("profile_id", ""))
        for scenario_id in profile.get("scenario_ids", []):
            scenario_id_str = str(scenario_id)
            scenario = scenario_map.get(scenario_id_str)
            if scenario is None:
                raise ValueError(f"missing scenario: {scenario_id_str}")
            failure_mode = _failure_mode_for_scenario(scenario_id_str)
            if failure_mode == "healthy":
                continue
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
                out.append(
                    ProbeCase(
                        profile_id=profile_id,
                        scenario_id=scenario_id_str,
                        query_id=query_id_str,
                        query_text=str(query.get("query_text", "")),
                        adapter_mode=str(scenario.get("adapter_mode", "off")),
                        fixture_ref=str(scenario.get("fixture_ref", "")),
                        expected_adapter_status=str(scenario.get("adapter_status_expected", "")),
                        failure_mode=failure_mode,
                    )
                )
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


def _run_command(
    cmd: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
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
    *,
    cwd: Path,
    timeout_seconds: int,
    env: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any] | None, str | None]:
    proc = _run_command(cmd, cwd=cwd, timeout_seconds=timeout_seconds, env=env)
    if proc.returncode != 0:
        return proc, None, f"command_failed:{proc.returncode}:{proc.stderr.strip()}"
    if not proc.stdout.strip():
        return proc, None, "empty_stdout"
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return proc, None, f"invalid_json_stdout:{exc}"
    if not isinstance(payload, dict):
        return proc, None, "json_payload_not_object"
    return proc, payload, None


def _status_is_pass(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return str(payload.get("status", "")).lower() == "pass"


def _run_context_probe(
    base_cmd: list[str],
    env: dict[str, str],
    *,
    project_dir: Path,
    case: ProbeCase,
    weighting_mode: str,
    adapter_max_items: int,
    adapter_stale_seconds: int,
    max_files: int,
    max_chars_per_file: int,
    timeout_seconds: int,
) -> dict[str, Any]:
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
    proc = _run_command(cmd, cwd=project_dir, timeout_seconds=timeout_seconds, env=env)
    elapsed = time.perf_counter() - started
    if proc.returncode != 0:
        return {
            "command": cmd,
            "elapsed_seconds": round(elapsed, 6),
            "returncode": proc.returncode,
            "success": False,
            "error": proc.stderr.strip() or proc.stdout.strip(),
            "expected_adapter_status": case.expected_adapter_status,
            "observed_adapter_status": None,
            "has_control_plane": False,
            "has_task_slice": False,
            "warning_classes": [],
            "pass": False,
        }

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "command": cmd,
            "elapsed_seconds": round(elapsed, 6),
            "returncode": proc.returncode,
            "success": False,
            "error": f"invalid_json_stdout:{exc}",
            "expected_adapter_status": case.expected_adapter_status,
            "observed_adapter_status": None,
            "has_control_plane": False,
            "has_task_slice": False,
            "warning_classes": [],
            "pass": False,
        }

    if not isinstance(payload, dict):
        return {
            "command": cmd,
            "elapsed_seconds": round(elapsed, 6),
            "returncode": proc.returncode,
            "success": False,
            "error": "json_payload_not_object",
            "expected_adapter_status": case.expected_adapter_status,
            "observed_adapter_status": None,
            "has_control_plane": False,
            "has_task_slice": False,
            "warning_classes": [],
            "pass": False,
        }

    files = payload.get("files", [])
    has_control_plane = any(
        str(item.get("selected_by", "")).startswith("control_plane")
        for item in files
        if isinstance(item, dict)
    )
    has_task_slice = any(
        str(item.get("selected_by", "")).startswith("task:")
        for item in files
        if isinstance(item, dict)
    )
    adapter = payload.get("adapter", {})
    observed_adapter_status = str(adapter.get("status", "")) if isinstance(adapter, dict) else ""
    warning_classes = _warning_classes(list(payload.get("warnings", [])))

    context_pass = bool(
        observed_adapter_status == case.expected_adapter_status and has_control_plane and has_task_slice
    )
    return {
        "command": cmd,
        "elapsed_seconds": round(elapsed, 6),
        "returncode": proc.returncode,
        "success": True,
        "error": None,
        "expected_adapter_status": case.expected_adapter_status,
        "observed_adapter_status": observed_adapter_status,
        "has_control_plane": has_control_plane,
        "has_task_slice": has_task_slice,
        "warning_classes": warning_classes,
        "pass": context_pass,
    }


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
    parser.add_argument("--governance-python-bin", default="python3")
    parser.add_argument(
        "--weighting-mode",
        choices=["uniform", "evidence_outcome_bias"],
        default="evidence_outcome_bias",
    )
    parser.add_argument("--adapter-max-items", type=int, default=4)
    parser.add_argument("--adapter-stale-seconds", type=int, default=86400)
    parser.add_argument("--max-files", type=int, default=24)
    parser.add_argument("--max-chars-per-file", type=int, default=1200)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument(
        "--out-file",
        default=".cortex/reports/project_state/phase3_governance_regression_report_v0.md",
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
        raise ValueError(f"no failure-scenario cases found in fixture: {fixture_path}")

    context_base_cmd = _build_context_base_cmd(args)
    context_env = _build_context_env(args)

    governance_cmds = {
        "decision-gap-check": [
            args.governance_python_bin,
            "scripts/cortex_project_coach_v0.py",
            "decision-gap-check",
            "--project-dir",
            str(project_dir),
            "--format",
            "json",
        ],
        "reflection-enforcement-gate": [
            args.governance_python_bin,
            "scripts/reflection_enforcement_gate_v0.py",
            "--project-dir",
            str(project_dir),
            "--required-decision-status",
            "promoted",
            "--min-scaffold-reports",
            "1",
            "--min-required-status-mappings",
            "1",
            "--format",
            "json",
        ],
        "audit-all": [
            args.governance_python_bin,
            "scripts/cortex_project_coach_v0.py",
            "audit",
            "--project-dir",
            str(project_dir),
            "--audit-scope",
            "all",
            "--format",
            "json",
        ],
    }

    rows: list[dict[str, Any]] = []
    total_elapsed_seconds = 0.0

    for case in cases:
        context = _run_context_probe(
            context_base_cmd,
            context_env,
            project_dir=project_dir,
            case=case,
            weighting_mode=args.weighting_mode,
            adapter_max_items=max(1, int(args.adapter_max_items)),
            adapter_stale_seconds=max(0, int(args.adapter_stale_seconds)),
            max_files=max(1, int(args.max_files)),
            max_chars_per_file=max(100, int(args.max_chars_per_file)),
            timeout_seconds=max(1, int(args.timeout_seconds)),
        )
        total_elapsed_seconds += float(context.get("elapsed_seconds", 0.0))

        governance_results: dict[str, dict[str, Any]] = {}
        for check_name, cmd in governance_cmds.items():
            started = time.perf_counter()
            proc, payload, error = _run_json_command(
                cmd,
                cwd=project_dir,
                timeout_seconds=max(1, int(args.timeout_seconds)),
            )
            elapsed = time.perf_counter() - started
            total_elapsed_seconds += elapsed
            governance_results[check_name] = {
                "command": cmd,
                "returncode": proc.returncode,
                "elapsed_seconds": round(elapsed, 6),
                "status": str(payload.get("status", "")) if isinstance(payload, dict) else "unknown",
                "pass": bool(proc.returncode == 0 and _status_is_pass(payload)),
                "error": error,
            }

        governance_pass = all(item["pass"] for item in governance_results.values())
        case_pass = bool(context["pass"] and governance_pass)
        rows.append(
            {
                "case_id": case.case_id,
                "profile_id": case.profile_id,
                "scenario_id": case.scenario_id,
                "query_id": case.query_id,
                "query_text": case.query_text,
                "adapter_fixture": case.fixture_ref,
                "failure_mode": case.failure_mode,
                "context_probe": context,
                "governance": governance_results,
                "pass": case_pass,
            }
        )

    passed = sum(1 for row in rows if row["pass"])
    overall_pass = bool(passed == len(rows))

    lines = [
        "# Phase 3 Governance Regression Report v0",
        "",
        "Version: v0  ",
        f"Status: {'Pass' if overall_pass else 'Fail'}  ",
        f"Date: {_today_utc()}  ",
        "Scope: Governance non-regression verification for adapter-unhealthy scenarios",
        "",
        "## Source Inputs",
        "",
        "- `.cortex/reports/project_state/phase3_work_graph_eval_fixture_freeze_v0.json`",
        "- `.cortex/reports/project_state/phase3_adapter_degradation_report_v0.json`",
        "- `contracts/context_load_work_graph_adapter_contract_v0.md`",
        "",
        "## Commands",
        "",
        f"- context probe base command: `{' '.join(context_base_cmd)} context-load ...`",
        f"- decision gap: `{' '.join(governance_cmds['decision-gap-check'])}`",
        f"- reflection gate: `{' '.join(governance_cmds['reflection-enforcement-gate'])}`",
        f"- audit all: `{' '.join(governance_cmds['audit-all'])}`",
        "",
        "## Summary",
        "",
        f"- cases evaluated: `{len(rows)}`",
        f"- passing cases: `{passed}`",
        f"- total elapsed seconds: `{round(total_elapsed_seconds, 6)}`",
        f"- overall result: `{'pass' if overall_pass else 'fail'}`",
        "",
        "## Case Results",
        "",
        "| Case | Failure Mode | Context Probe | Decision Gap | Reflection Gate | Audit All | Pass |",
        "|---|---|---|---|---|---|---|",
    ]

    for row in rows:
        context_state = "pass" if row["context_probe"]["pass"] else "fail"
        decision_state = "pass" if row["governance"]["decision-gap-check"]["pass"] else "fail"
        reflection_state = "pass" if row["governance"]["reflection-enforcement-gate"]["pass"] else "fail"
        audit_state = "pass" if row["governance"]["audit-all"]["pass"] else "fail"
        row_pass = "pass" if row["pass"] else "fail"
        lines.append(
            f"| `{row['case_id']}` | `{row['failure_mode']}` | `{context_state}` | `{decision_state}` | `{reflection_state}` | `{audit_state}` | `{row_pass}` |"
        )

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            (
                "Required governance commands remained passing across all adapter-unhealthy probes."
                if overall_pass
                else "One or more adapter-unhealthy probes regressed required governance checks; inspect failing cases above."
            ),
            "",
            f"_Generated at: `{_now_iso()}`_",
            "",
        ]
    )

    _write_text(Path(args.out_file), "\n".join(lines))
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

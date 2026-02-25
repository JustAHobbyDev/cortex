#!/usr/bin/env python3
"""Generate client onboarding certification pack + recurring cadence checks."""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jsonschema


SCORECARD_SCHEMA_PATH = Path("contracts/client_onboarding_certification_scorecard_schema_v0.json")

RUBRIC = {
    "governance_integrity": {"weight_percent": 35.0, "minimum_required_percent": 85.0},
    "operational_reliability": {"weight_percent": 35.0, "minimum_required_percent": 85.0},
    "team_readiness": {"weight_percent": 20.0, "minimum_required_percent": 80.0},
    "documentation_quality": {"weight_percent": 10.0, "minimum_required_percent": 80.0},
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _clamp_score(value: float) -> float:
    if math.isnan(value):
        return 0.0
    return max(0.0, min(100.0, value))


def _as_status_from_json_payload(payload: dict[str, Any]) -> str:
    status = str(payload.get("status", "")).strip().lower()
    if status in {"pass", "fail", "not_needed", "warning"}:
        return status
    return "unknown"


def _first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


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


def _run_shell_command(
    cmd: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
) -> tuple[int, str, str, float]:
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
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip(), elapsed


def _check_dependency_bootstrap(project_dir: Path) -> dict[str, Any]:
    uv_lock = project_dir / "uv.lock"
    local_venv = project_dir / ".venv"
    local_uv_cache = project_dir / ".uv-cache"
    env_uv_cache = Path(os.environ.get("UV_CACHE_DIR", "")).expanduser() if os.environ.get("UV_CACHE_DIR") else None

    lock_exists = uv_lock.exists()
    venv_ready = local_venv.exists()
    local_cache_ready = local_uv_cache.exists() and any(local_uv_cache.iterdir())
    env_cache_ready = env_uv_cache is not None and env_uv_cache.exists() and any(env_uv_cache.iterdir())

    ready = lock_exists and (venv_ready or local_cache_ready or env_cache_ready)

    reasons: list[str] = []
    if not lock_exists:
        reasons.append("missing_uv_lock")
    if lock_exists and not (venv_ready or local_cache_ready or env_cache_ready):
        reasons.append("missing_dependency_cache_or_virtualenv")

    remediation_hints: list[str] = []
    if not ready:
        remediation_hints.append("Run `UV_CACHE_DIR=.uv-cache uv sync --locked --group dev` to pre-provision dependencies.")
        remediation_hints.append("Commit/update onboarding runbook notes with environment bootstrap instructions.")

    return {
        "check_id": "dependency_bootstrap_control",
        "status": "pass" if ready else "fail",
        "reason_codes": reasons,
        "lock_file": _safe_rel_path(project_dir, uv_lock),
        "lock_exists": lock_exists,
        "venv_path": _safe_rel_path(project_dir, local_venv),
        "venv_exists": venv_ready,
        "local_uv_cache_path": _safe_rel_path(project_dir, local_uv_cache),
        "local_uv_cache_ready": local_cache_ready,
        "env_uv_cache_path": str(env_uv_cache) if env_uv_cache else "",
        "env_uv_cache_ready": env_cache_ready,
        "remediation_hints": remediation_hints,
    }


def _check_documentation_quality(
    project_dir: Path,
    completion_report_path: Path,
    requested_score: float,
) -> tuple[float, list[str], bool]:
    score = _clamp_score(requested_score)
    notes: list[str] = []
    has_completion_report = completion_report_path.exists()
    if not has_completion_report:
        score = min(score, 70.0)
        notes.append("Completion report missing; documentation score capped at 70.")
        return score, notes, False

    text = completion_report_path.read_text(encoding="utf-8")
    placeholder_markers = ["<status>", "<artifact_path>", "<name>", "<date>", "<YYYY-MM-DD>"]
    unresolved_placeholders = any(marker in text for marker in placeholder_markers)
    if unresolved_placeholders:
        score = min(score, 79.0)
        notes.append("Completion report still contains template placeholders.")
    else:
        notes.append("Completion report exists and appears populated.")
    return score, notes, True


def _check_entry(
    check_id: str,
    cmd: list[str],
    *,
    project_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    payload, rc, stderr, stdout, elapsed = _run_json_command(cmd, cwd=project_dir, timeout_seconds=timeout_seconds)
    payload_status = _as_status_from_json_payload(payload)
    status = "pass" if rc == 0 and payload_status == "pass" else "fail"
    return {
        "check_id": check_id,
        "command": cmd,
        "duration_seconds": elapsed,
        "returncode": rc,
        "status": status,
        "payload_status": payload_status,
        "summary": payload.get("summary", {}) if isinstance(payload, dict) else {},
        "stderr": stderr,
        "stdout_excerpt": _first_line(stdout),
        "report_path": payload.get("report_path") if isinstance(payload, dict) else None,
    }


def _check_quality_gate(project_dir: Path, timeout_seconds: int) -> dict[str, Any]:
    rc, stdout, stderr, elapsed = _run_shell_command(
        ["./scripts/quality_gate_ci_v0.sh"], cwd=project_dir, timeout_seconds=timeout_seconds
    )
    summary_line = ""
    for line in reversed(stdout.splitlines()):
        stripped = line.strip()
        if stripped:
            summary_line = stripped
            break
    return {
        "check_id": "quality_gate_ci",
        "command": ["./scripts/quality_gate_ci_v0.sh"],
        "duration_seconds": elapsed,
        "returncode": rc,
        "status": "pass" if rc == 0 else "fail",
        "summary_line": summary_line,
        "stderr_first_line": _first_line(stderr),
    }


def _score_from_checks(checks: list[dict[str, Any]]) -> tuple[float, list[str]]:
    if not checks:
        return 0.0, ["No checks executed."]
    passed = sum(1 for check in checks if check.get("status") == "pass")
    score = _clamp_score((passed / len(checks)) * 100.0)
    notes = [f"{passed}/{len(checks)} checks passed."]
    failed = [str(check.get("check_id", "unknown")) for check in checks if check.get("status") != "pass"]
    if failed:
        notes.append(f"Failed checks: {', '.join(failed)}.")
    return score, notes


def _build_cadence_schedule(go_live_date: date) -> dict[str, Any]:
    weekly = [(go_live_date + timedelta(days=7 * i)).isoformat() for i in range(1, 5)]
    monthly = [(go_live_date + timedelta(days=30 * i)).isoformat() for i in range(1, 4)]
    return {
        "weekly_checkpoints": weekly,
        "monthly_checkpoints": monthly,
    }


def _parse_reviewer_list(raw: str) -> list[str]:
    reviewers = [item.strip() for item in raw.split(",") if item.strip()]
    if not reviewers:
        return ["Maintainer Council"]
    return reviewers


def _render_text(payload: dict[str, Any]) -> str:
    scorecard = payload.get("scorecard", {})
    cadence = payload.get("cadence", {})
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"generated_at: {payload.get('generated_at', '')}",
        f"scorecard_status: {scorecard.get('status', 'fail') if isinstance(scorecard, dict) else 'fail'}",
        (
            "weighted_score_percent: "
            f"{scorecard.get('totals', {}).get('weighted_score_percent', 0.0) if isinstance(scorecard, dict) else 0.0}"
        ),
        f"cadence_status: {cadence.get('status', 'fail') if isinstance(cadence, dict) else 'fail'}",
    ]

    findings = payload.get("findings", [])
    if isinstance(findings, list) and findings:
        lines.append("findings:")
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            lines.append(f"- {finding.get('check')}: {finding.get('message')}")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--track-variant", default="standard", choices=("accelerated", "standard", "custom"))
    parser.add_argument("--track-start-date", default="")
    parser.add_argument("--track-end-date", default="")
    parser.add_argument("--go-live-date", default="")
    parser.add_argument("--client-id", default="internal")
    parser.add_argument("--project-id", default="cortex")
    parser.add_argument("--project-name", default="cortex")
    parser.add_argument("--assessor-name", default="automation")
    parser.add_argument("--assessor-role", default="Conformance QA Lead")
    parser.add_argument("--reviewers", default="Maintainer Council,CI/Gate Owner")
    parser.add_argument("--team-readiness-score", type=float, default=85.0)
    parser.add_argument("--documentation-quality-score", type=float, default=85.0)
    parser.add_argument(
        "--completion-report",
        default=".cortex/reports/project_state/client_onboarding_completion_report_v0.md",
    )
    parser.add_argument("--run-quality-gate", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--out-file",
        default=".cortex/reports/project_state/client_onboarding_certification_pack_v0.json",
    )
    parser.add_argument("--format", default="text", choices=("text", "json"))
    parser.add_argument("--fail-on-target-miss", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    scripts_dir = Path(__file__).resolve().parent
    coach_delegator = scripts_dir / "cortex_project_coach_v0.py"

    completion_report_path = Path(args.completion_report)
    if not completion_report_path.is_absolute():
        completion_report_path = (project_dir / completion_report_path).resolve()

    out_file = Path(args.out_file)
    if not out_file.is_absolute():
        out_file = (project_dir / out_file).resolve()

    today_iso = _today_utc().isoformat()
    track_start_date = args.track_start_date or today_iso
    track_end_date = args.track_end_date or today_iso
    go_live_date = date.fromisoformat(args.go_live_date) if args.go_live_date else _today_utc()

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    preflight_check = _check_entry(
        "command_surface_preflight",
        [
            args.python_bin,
            str(scripts_dir / "client_onboarding_command_preflight_v0.py"),
            "--project-dir",
            str(project_dir),
            "--format",
            "json",
        ],
        project_dir=project_dir,
        timeout_seconds=args.timeout_seconds,
    )
    checks.append(preflight_check)

    dependency_bootstrap = _check_dependency_bootstrap(project_dir)
    checks.append(dependency_bootstrap)

    checks.append(
        _check_entry(
            "audit_all",
            [
                args.python_bin,
                str(coach_delegator),
                "audit",
                "--project-dir",
                str(project_dir),
                "--audit-scope",
                "all",
                "--format",
                "json",
            ],
            project_dir=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    checks.append(
        _check_entry(
            "decision_gap_check",
            [
                args.python_bin,
                str(coach_delegator),
                "decision-gap-check",
                "--project-dir",
                str(project_dir),
                "--format",
                "json",
            ],
            project_dir=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    checks.append(
        _check_entry(
            "reflection_completeness_check",
            [
                args.python_bin,
                str(coach_delegator),
                "reflection-completeness-check",
                "--project-dir",
                str(project_dir),
                "--required-decision-status",
                "promoted",
                "--format",
                "json",
            ],
            project_dir=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    checks.append(
        _check_entry(
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
                "--format",
                "json",
            ],
            project_dir=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    checks.append(
        _check_entry(
            "project_state_boundary_gate",
            [
                args.python_bin,
                str(scripts_dir / "project_state_boundary_gate_v0.py"),
                "--project-dir",
                str(project_dir),
                "--format",
                "json",
            ],
            project_dir=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )
    checks.append(
        _check_entry(
            "quality_gate_sync_check",
            [
                args.python_bin,
                str(scripts_dir / "quality_gate_sync_check_v0.py"),
                "--ci-script",
                "scripts/quality_gate_ci_v0.sh",
                "--local-script",
                "scripts/quality_gate_v0.sh",
                "--format",
                "json",
            ],
            project_dir=project_dir,
            timeout_seconds=args.timeout_seconds,
        )
    )

    if args.run_quality_gate:
        checks.append(_check_quality_gate(project_dir, args.timeout_seconds))
    else:
        checks.append(
            {
                "check_id": "quality_gate_ci",
                "command": ["./scripts/quality_gate_ci_v0.sh"],
                "status": "fail",
                "returncode": -1,
                "reason": "not_executed",
                "summary_line": "skipped",
                "stderr_first_line": "",
                "duration_seconds": 0.0,
            }
        )

    governance_check_ids = {
        "audit_all",
        "decision_gap_check",
        "reflection_completeness_check",
        "reflection_enforcement_gate",
    }
    reliability_check_ids = {
        "command_surface_preflight",
        "dependency_bootstrap_control",
        "project_state_boundary_gate",
        "quality_gate_sync_check",
        "quality_gate_ci",
    }

    governance_checks = [check for check in checks if check.get("check_id") in governance_check_ids]
    reliability_checks = [check for check in checks if check.get("check_id") in reliability_check_ids]

    governance_score, governance_notes = _score_from_checks(governance_checks)
    reliability_score, reliability_notes = _score_from_checks(reliability_checks)
    team_readiness_score = _clamp_score(args.team_readiness_score)
    documentation_score, documentation_notes, completion_report_present = _check_documentation_quality(
        project_dir,
        completion_report_path,
        args.documentation_quality_score,
    )

    rollout_preflight_failed = any(
        check.get("check_id") == "command_surface_preflight" and check.get("status") != "pass" for check in checks
    )
    decision_gap_failed = any(check.get("check_id") == "decision_gap_check" and check.get("status") != "pass" for check in checks)
    governance_failed = any(check.get("check_id") in governance_check_ids and check.get("status") != "pass" for check in checks)

    governance_category = {
        "weight_percent": RUBRIC["governance_integrity"]["weight_percent"],
        "score_percent": governance_score,
        "minimum_required_percent": RUBRIC["governance_integrity"]["minimum_required_percent"],
        "pass": governance_score >= RUBRIC["governance_integrity"]["minimum_required_percent"],
        "notes": " ".join(governance_notes),
        "evidence_refs": [
            ".cortex/reports/lifecycle_audit_v0.json",
            ".cortex/reports/decision_candidates_v0.json",
        ],
    }
    reliability_category = {
        "weight_percent": RUBRIC["operational_reliability"]["weight_percent"],
        "score_percent": reliability_score,
        "minimum_required_percent": RUBRIC["operational_reliability"]["minimum_required_percent"],
        "pass": reliability_score >= RUBRIC["operational_reliability"]["minimum_required_percent"],
        "notes": " ".join(reliability_notes),
        "evidence_refs": [
            ".cortex/reports/project_state/client_onboarding_command_preflight_v0.json",
            ".cortex/reports/project_state/client_onboarding_certification_pack_v0.json",
        ],
    }
    team_category = {
        "weight_percent": RUBRIC["team_readiness"]["weight_percent"],
        "score_percent": team_readiness_score,
        "minimum_required_percent": RUBRIC["team_readiness"]["minimum_required_percent"],
        "pass": team_readiness_score >= RUBRIC["team_readiness"]["minimum_required_percent"],
        "notes": "Team readiness score provided by assessor inputs.",
    }
    documentation_category = {
        "weight_percent": RUBRIC["documentation_quality"]["weight_percent"],
        "score_percent": documentation_score,
        "minimum_required_percent": RUBRIC["documentation_quality"]["minimum_required_percent"],
        "pass": documentation_score >= RUBRIC["documentation_quality"]["minimum_required_percent"],
        "notes": " ".join(documentation_notes),
        "evidence_refs": [
            _safe_rel_path(project_dir, completion_report_path),
        ]
        if completion_report_present
        else [],
    }

    weighted_score = (
        (governance_category["score_percent"] * governance_category["weight_percent"])
        + (reliability_category["score_percent"] * reliability_category["weight_percent"])
        + (team_category["score_percent"] * team_category["weight_percent"])
        + (documentation_category["score_percent"] * documentation_category["weight_percent"])
    ) / 100.0
    weighted_score = _clamp_score(round(weighted_score, 2))

    hard_fail_conditions = {
        "required_governance_gate_bypass_detected": False,
        "unlinked_governance_closure_detected": bool(decision_gap_failed),
        "rollback_drill_failed": bool(rollout_preflight_failed),
        "triggered": bool(decision_gap_failed or rollout_preflight_failed),
        "notes": (
            "Rollout command surface unavailable in preflight."
            if rollout_preflight_failed
            else ("Decision gap check failed." if decision_gap_failed else "")
        ),
    }

    pass_by_score = weighted_score >= 85.0
    scorecard_status = (
        "pass"
        if (
            pass_by_score
            and governance_category["pass"]
            and reliability_category["pass"]
            and team_category["pass"]
            and documentation_category["pass"]
            and not hard_fail_conditions["triggered"]
            and not governance_failed
        )
        else "fail"
    )

    scorecard = {
        "artifact": "client_onboarding_certification_scorecard_v0",
        "version": "v0",
        "generated_at": _now_iso(),
        "client": {
            "client_id": args.client_id,
            "project_id": args.project_id,
            "project_name": args.project_name,
        },
        "track": {
            "variant": args.track_variant,
            "start_date": track_start_date,
            "end_date": track_end_date,
        },
        "assessment": {
            "assessor_name": args.assessor_name,
            "assessor_role": args.assessor_role,
            "reviewers": _parse_reviewer_list(args.reviewers),
        },
        "categories": {
            "governance_integrity": governance_category,
            "operational_reliability": reliability_category,
            "team_readiness": team_category,
            "documentation_quality": documentation_category,
        },
        "totals": {
            "weighted_score_percent": weighted_score,
            "minimum_required_percent": 85.0,
            "pass_by_score": pass_by_score,
        },
        "hard_fail_conditions": hard_fail_conditions,
        "status": scorecard_status,
        "evidence_refs": [
            _safe_rel_path(project_dir, completion_report_path),
            ".cortex/reports/project_state/client_onboarding_certification_pack_v0.json",
        ],
    }

    schema_path = (project_dir / SCORECARD_SCHEMA_PATH).resolve()
    if not schema_path.exists():
        raise SystemExit(f"missing scorecard schema: {schema_path}")
    scorecard_schema = _load_json(schema_path)
    schema_validation = {"status": "pass", "error": ""}
    try:
        jsonschema.validate(instance=scorecard, schema=scorecard_schema)
    except jsonschema.ValidationError as exc:
        schema_validation = {"status": "fail", "error": str(exc)}
        findings.append(
            {
                "check": "scorecard_schema_validation",
                "severity": "error",
                "message": "Generated scorecard failed schema validation.",
            }
        )

    cadence_schedule = _build_cadence_schedule(go_live_date)
    cadence_required_check_ids = [
        "audit_all",
        "decision_gap_check",
        "reflection_completeness_check",
        "reflection_enforcement_gate",
        "project_state_boundary_gate",
        "command_surface_preflight",
        "dependency_bootstrap_control",
    ]
    cadence_check_results = [check for check in checks if check.get("check_id") in cadence_required_check_ids]
    cadence_pass = all(check.get("status") == "pass" for check in cadence_check_results)
    cadence = {
        "status": "pass" if cadence_pass else "fail",
        "policy": {
            "week_1_to_4_cadence": "weekly",
            "month_2_plus_cadence": "monthly",
        },
        "schedule": cadence_schedule,
        "required_check_ids": cadence_required_check_ids,
        "latest_results": [
            {"check_id": check.get("check_id"), "status": check.get("status")} for check in cadence_check_results
        ],
        "next_action": (
            "Proceed with scheduled weekly cadence checks."
            if cadence_pass
            else "Remediate failed cadence prerequisite checks before go-live handoff."
        ),
    }

    remediation_hints: list[str] = []
    for check in checks:
        if check.get("check_id") == "dependency_bootstrap_control":
            remediation_hints.extend(check.get("remediation_hints", []))
    if rollout_preflight_failed:
        remediation_hints.append(
            "Upgrade cortex-coach command surface to support onboarding rollback-mode requirements before certification pass."
        )
    if not args.run_quality_gate:
        remediation_hints.append("Run with --run-quality-gate during final certification review to enforce CI readiness.")
    if schema_validation["status"] == "fail":
        remediation_hints.append("Fix scorecard schema validation errors before approving certification.")
    if not completion_report_present:
        remediation_hints.append("Populate onboarding completion report before final M6 certification review.")

    status = "pass" if scorecard_status == "pass" and cadence["status"] == "pass" and schema_validation["status"] == "pass" else "fail"
    if status == "fail":
        findings.append(
            {
                "check": "certification_pack_status",
                "severity": "error",
                "message": "Certification pack did not meet pass criteria.",
                "scorecard_status": scorecard_status,
                "cadence_status": cadence["status"],
                "schema_validation_status": schema_validation["status"],
            }
        )

    payload = {
        "artifact": "client_onboarding_certification_pack_v0",
        "version": "v0",
        "generated_at": _now_iso(),
        "project_dir": str(project_dir),
        "inputs": {
            "client_id": args.client_id,
            "project_id": args.project_id,
            "project_name": args.project_name,
            "track_variant": args.track_variant,
            "track_start_date": track_start_date,
            "track_end_date": track_end_date,
            "go_live_date": go_live_date.isoformat(),
            "assessor_name": args.assessor_name,
            "assessor_role": args.assessor_role,
            "reviewers": _parse_reviewer_list(args.reviewers),
            "completion_report": _safe_rel_path(project_dir, completion_report_path),
            "run_quality_gate": args.run_quality_gate,
        },
        "checks": checks,
        "scorecard_schema_path": _safe_rel_path(project_dir, schema_path),
        "scorecard_schema_validation": schema_validation,
        "scorecard": scorecard,
        "cadence": cadence,
        "findings": findings,
        "remediation_hints": sorted(set(remediation_hints)),
        "status": status,
    }

    _write_json(out_file, payload)

    if args.format == "json":
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_render_text(payload))
        sys.stdout.write("\n")

    if args.fail_on_target_miss and status != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

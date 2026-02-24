#!/usr/bin/env python3
"""Fail closed when reflection linkage/completeness checks pass vacuously."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            out.append(item)
    return out


def _non_empty_str(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _run_json_command(cmd: list[str], command_name: str) -> tuple[dict[str, Any], int, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    stderr = proc.stderr.strip()
    payload: dict[str, Any] = {}
    if proc.stdout.strip():
        try:
            parsed = json.loads(proc.stdout)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            payload = {}

    if proc.returncode != 0 and not payload:
        payload = {
            "status": "fail",
            "error": f"{command_name} exited with {proc.returncode} and emitted non-JSON output",
            "stdout": proc.stdout.strip(),
            "stderr": stderr,
        }

    return payload, proc.returncode, stderr


def _resolve_report_path(project_dir: Path, report: str) -> Path:
    report_path = Path(report)
    if report_path.is_absolute():
        return report_path
    return project_dir / report_path


def _load_json_file(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _finding(check: str, message: str, **extra: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "check": check,
        "severity": "error",
        "message": message,
    }
    item.update(extra)
    return item


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _phase4_enforcement_report_status(
    project_dir: Path,
    report_path_text: str,
) -> tuple[dict[str, Any] | None, Path]:
    resolved_path = _resolve_report_path(project_dir, report_path_text)
    payload = _load_json_file(resolved_path)
    return payload, resolved_path


def _validate_reflection_linkage(
    entry: dict[str, Any],
    project_dir: Path,
    context: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    decision_id = _non_empty_str(entry.get("decision_id")) or "<unknown>"

    reflection_id = _non_empty_str(entry.get("reflection_id"))
    reflection_report = _non_empty_str(entry.get("reflection_report"))

    if reflection_id is None:
        findings.append(
            _finding(
                "missing_reflection_id",
                "Decision is missing reflection_id.",
                decision_id=decision_id,
                context=context,
            )
        )

    if reflection_report is None:
        findings.append(
            _finding(
                "missing_reflection_report",
                "Decision is missing reflection_report.",
                decision_id=decision_id,
                context=context,
            )
        )
        return findings

    resolved_report = _resolve_report_path(project_dir, reflection_report)
    if not resolved_report.exists():
        findings.append(
            _finding(
                "missing_reflection_report_file",
                "Decision reflection_report file does not exist.",
                decision_id=decision_id,
                context=context,
                reflection_report=reflection_report,
                resolved_path=str(resolved_report),
            )
        )
        return findings

    report_payload = _load_json_file(resolved_report)
    if report_payload is None:
        findings.append(
            _finding(
                "invalid_reflection_report",
                "Decision reflection_report is not a valid JSON object.",
                decision_id=decision_id,
                context=context,
                reflection_report=reflection_report,
                resolved_path=str(resolved_report),
            )
        )
        return findings

    report_reflection_id = _non_empty_str(report_payload.get("reflection_id"))
    if reflection_id and report_reflection_id and reflection_id != report_reflection_id:
        findings.append(
            _finding(
                "reflection_id_mismatch",
                "Decision reflection_id does not match reflection_report reflection_id.",
                decision_id=decision_id,
                context=context,
                reflection_id=reflection_id,
                report_reflection_id=report_reflection_id,
                reflection_report=reflection_report,
            )
        )

    return findings


def _load_decision_entries(project_dir: Path, cortex_root: str) -> list[dict[str, Any]]:
    report_path = project_dir / cortex_root / "reports" / "decision_candidates_v0.json"
    payload = _load_json_file(report_path)
    if not payload:
        return []
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return []
    out: list[dict[str, Any]] = []
    for item in entries:
        if isinstance(item, dict):
            out.append(item)
    return out


def _render_text(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"status: {payload.get('status', 'fail')}")
    lines.append(f"run_at: {payload.get('run_at', '')}")

    thresholds = payload.get("thresholds", {})
    if isinstance(thresholds, dict):
        lines.append(
            "thresholds: "
            f"min_scaffold_reports={thresholds.get('min_scaffold_reports')} "
            f"min_required_status_mappings={thresholds.get('min_required_status_mappings')}"
        )

    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        lines.append(
            "summary: "
            f"governance_impact_files={summary.get('governance_impact_file_count', 0)} "
            f"decision_matches={summary.get('decision_match_count', 0)} "
            f"required_status_entries={summary.get('required_status_entry_count', 0)} "
            f"scaffolds_scanned={summary.get('scaffold_reports_scanned', 0)} "
            f"mappings={summary.get('required_status_mapping_count', 0)}"
        )

    findings = payload.get("findings", [])
    if isinstance(findings, list) and findings:
        lines.append("findings:")
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            check = finding.get("check", "unknown")
            message = finding.get("message", "")
            decision_id = finding.get("decision_id")
            context = finding.get("context")
            suffix_parts: list[str] = []
            if decision_id:
                suffix_parts.append(f"decision_id={decision_id}")
            if context:
                suffix_parts.append(f"context={context}")
            suffix = f" ({', '.join(suffix_parts)})" if suffix_parts else ""
            lines.append(f"- {check}: {message}{suffix}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enforce reflection linkage and non-vacuous reflection completeness checks."
    )
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--cortex-root", default=".cortex")
    parser.add_argument("--required-decision-status", default="promoted", choices=("candidate", "promoted"))
    parser.add_argument("--min-scaffold-reports", type=int, default=1)
    parser.add_argument("--min-required-status-mappings", type=int, default=1)
    parser.add_argument("--require-phase4-enforcement-report", action="store_true")
    parser.add_argument(
        "--phase4-enforcement-report",
        default=".cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json",
    )
    parser.add_argument("--strict-generated", action="store_true")
    parser.add_argument("--format", default="text", choices=("text", "json"))
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    coach_script = Path(__file__).resolve().parent / "cortex_project_coach_v0.py"

    findings: list[dict[str, Any]] = []

    gap_cmd = [
        sys.executable,
        str(coach_script),
        "decision-gap-check",
        "--project-dir",
        str(project_dir),
        "--format",
        "json",
    ]
    if args.strict_generated:
        gap_cmd.append("--strict-generated")

    gap_payload, gap_returncode, gap_stderr = _run_json_command(gap_cmd, "decision-gap-check")
    if gap_returncode != 0:
        findings.append(
            _finding(
                "decision_gap_command_failed",
                "decision-gap-check command failed.",
                returncode=gap_returncode,
                stderr=gap_stderr,
            )
        )

    reflection_cmd = [
        sys.executable,
        str(coach_script),
        "reflection-completeness-check",
        "--project-dir",
        str(project_dir),
        "--required-decision-status",
        args.required_decision_status,
        "--format",
        "json",
    ]
    reflection_payload, reflection_returncode, reflection_stderr = _run_json_command(
        reflection_cmd,
        "reflection-completeness-check",
    )
    if reflection_returncode != 0:
        findings.append(
            _finding(
                "reflection_completeness_command_failed",
                "reflection-completeness-check command failed.",
                returncode=reflection_returncode,
                stderr=reflection_stderr,
            )
        )

    if gap_payload.get("status") == "fail":
        findings.append(
            _finding(
                "decision_gap_failed",
                "decision-gap-check reported uncovered governance-impact files.",
                uncovered_files=_as_str_list(gap_payload.get("uncovered_files")),
            )
        )

    if reflection_payload.get("status") == "fail":
        findings.append(
            _finding(
                "reflection_completeness_failed",
                "reflection-completeness-check reported missing reflection mappings.",
                findings=reflection_payload.get("findings", []),
            )
        )

    entries = _load_decision_entries(project_dir, args.cortex_root)
    by_decision_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        decision_id = _non_empty_str(entry.get("decision_id"))
        if decision_id:
            by_decision_id[decision_id] = entry

    decision_matches = gap_payload.get("decision_matches")
    match_items = decision_matches if isinstance(decision_matches, list) else []
    for item in match_items:
        if not isinstance(item, dict):
            continue
        decision_id = _non_empty_str(item.get("decision_id"))
        if decision_id is None:
            findings.append(
                _finding(
                    "decision_match_missing_id",
                    "decision-gap-check emitted a decision match without decision_id.",
                )
            )
            continue
        entry = by_decision_id.get(decision_id)
        if entry is None:
            findings.append(
                _finding(
                    "decision_match_missing_entry",
                    "decision-gap-check matched a decision_id not present in decision candidates report.",
                    decision_id=decision_id,
                )
            )
            continue
        findings.extend(_validate_reflection_linkage(entry, project_dir, context="matched_governance_change"))

    required_entries: list[dict[str, Any]] = []
    for entry in entries:
        status = _non_empty_str(entry.get("status"))
        impact_scope = _as_str_list(entry.get("impact_scope"))
        if status == args.required_decision_status and impact_scope:
            required_entries.append(entry)

    for entry in required_entries:
        findings.extend(
            _validate_reflection_linkage(
                entry,
                project_dir,
                context=f"required_status:{args.required_decision_status}",
            )
        )

    scaffold_reports_scanned = int(reflection_payload.get("scaffold_reports_scanned", 0) or 0)
    if scaffold_reports_scanned < args.min_scaffold_reports:
        findings.append(
            _finding(
                "insufficient_scaffold_reports",
                "reflection-completeness-check scanned fewer scaffold reports than required minimum.",
                scaffold_reports_scanned=scaffold_reports_scanned,
                min_scaffold_reports=args.min_scaffold_reports,
            )
        )

    mappings = reflection_payload.get("mappings")
    mapping_items = mappings if isinstance(mappings, list) else []
    if required_entries and len(mapping_items) < args.min_required_status_mappings:
        findings.append(
            _finding(
                "insufficient_required_status_mappings",
                "reflection-completeness-check produced fewer mappings than required minimum.",
                required_status=args.required_decision_status,
                required_status_entry_count=len(required_entries),
                mapping_count=len(mapping_items),
                min_required_status_mappings=args.min_required_status_mappings,
            )
        )

    phase4_enforcement_payload: dict[str, Any] | None = None
    phase4_enforcement_resolved_path = _resolve_report_path(project_dir, args.phase4_enforcement_report)
    if args.require_phase4_enforcement_report:
        phase4_enforcement_payload, phase4_enforcement_resolved_path = _phase4_enforcement_report_status(
            project_dir,
            args.phase4_enforcement_report,
        )
        if phase4_enforcement_payload is None:
            findings.append(
                _finding(
                    "missing_phase4_enforcement_report",
                    "Phase 4 enforcement blocking report is missing or invalid JSON.",
                    report_path=args.phase4_enforcement_report,
                    resolved_path=str(phase4_enforcement_resolved_path),
                )
            )
        else:
            report_status = str(phase4_enforcement_payload.get("status", "unknown")).lower()
            summary = phase4_enforcement_payload.get("summary", {})
            if not isinstance(summary, dict):
                summary = {}
            block_rate = _as_float(summary.get("unlinked_closure_block_rate"), default=0.0)
            false_block_rate = _as_float(summary.get("linked_closure_false_block_rate"), default=1.0)
            if report_status != "pass":
                findings.append(
                    _finding(
                        "phase4_enforcement_report_failed",
                        "Phase 4 enforcement blocking report status is not pass.",
                        report_status=report_status,
                        report_path=args.phase4_enforcement_report,
                        resolved_path=str(phase4_enforcement_resolved_path),
                    )
                )
            if block_rate < 1.0:
                findings.append(
                    _finding(
                        "phase4_enforcement_block_rate_below_target",
                        "Phase 4 unlinked closure block rate is below 100%.",
                        block_rate=block_rate,
                        target=1.0,
                        report_path=args.phase4_enforcement_report,
                        resolved_path=str(phase4_enforcement_resolved_path),
                    )
                )
            if false_block_rate > 0.05:
                findings.append(
                    _finding(
                        "phase4_linked_false_block_rate_above_target",
                        "Phase 4 linked closure false-block rate exceeds threshold.",
                        linked_false_block_rate=false_block_rate,
                        target_max=0.05,
                        report_path=args.phase4_enforcement_report,
                        resolved_path=str(phase4_enforcement_resolved_path),
                    )
                )

    payload: dict[str, Any] = {
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "status": "fail" if findings else "pass",
        "required_decision_status": args.required_decision_status,
        "phase4_enforcement_report_required": args.require_phase4_enforcement_report,
        "thresholds": {
            "min_scaffold_reports": args.min_scaffold_reports,
            "min_required_status_mappings": args.min_required_status_mappings,
        },
        "summary": {
            "governance_impact_file_count": len(_as_str_list(gap_payload.get("governance_impact_files"))),
            "decision_match_count": len(match_items),
            "required_status_entry_count": len(required_entries),
            "scaffold_reports_scanned": scaffold_reports_scanned,
            "required_status_mapping_count": len(mapping_items),
        },
        "decision_gap": {
            "status": gap_payload.get("status", "unknown"),
            "governance_impact_files": _as_str_list(gap_payload.get("governance_impact_files")),
            "covered_files": _as_str_list(gap_payload.get("covered_files")),
            "uncovered_files": _as_str_list(gap_payload.get("uncovered_files")),
            "decision_matches": match_items,
        },
        "reflection_completeness": {
            "status": reflection_payload.get("status", "unknown"),
            "scaffold_reports_scanned": scaffold_reports_scanned,
            "decision_entries_scanned": int(reflection_payload.get("decision_entries_scanned", 0) or 0),
            "mappings": mapping_items,
            "findings": reflection_payload.get("findings", []),
        },
        "phase4_enforcement": {
            "report_path": args.phase4_enforcement_report,
            "resolved_path": str(phase4_enforcement_resolved_path),
            "status": phase4_enforcement_payload.get("status", "unknown")
            if isinstance(phase4_enforcement_payload, dict)
            else "missing",
            "summary": phase4_enforcement_payload.get("summary", {})
            if isinstance(phase4_enforcement_payload, dict)
            else {},
        },
        "findings": findings,
    }

    if args.format == "json":
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_render_text(payload))
        sys.stdout.write("\n")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

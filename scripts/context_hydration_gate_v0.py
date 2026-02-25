#!/usr/bin/env python3
"""Emit and verify governance capsule hydration receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jsonschema


EVENTS = ("new_session", "window_rollover", "pre_mutation", "pre_closeout")
ENFORCEMENT_MODES = ("advisory", "warn", "block")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _to_iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _parse_iso(value: str) -> datetime | None:
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_rel_path(project_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def _run_git_head(project_dir: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(project_dir),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _required_capsule_paths(project_dir: Path, cortex_root: str) -> dict[str, Path]:
    return {
        "manifest_path": project_dir / cortex_root / "manifest_v0.json",
        "audit_path": project_dir / cortex_root / "reports" / "lifecycle_audit_v0.json",
        "decision_candidates_path": project_dir / cortex_root / "reports" / "decision_candidates_v0.json",
        "authority_policy_path": project_dir / "policies" / "cortex_coach_final_ownership_boundary_v0.md",
        "boundary_policy_path": project_dir / "policies" / "project_state_boundary_policy_v0.md",
        "roadmap_path": project_dir / "playbooks" / "cortex_vision_master_roadmap_v1.md",
    }


def _build_capsule(
    project_dir: Path,
    cortex_root: str,
) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    paths = _required_capsule_paths(project_dir, cortex_root)
    capsule: dict[str, Any] = {}
    hydration_inputs: list[dict[str, str]] = []
    missing: list[str] = []
    for path_key, file_path in paths.items():
        hash_key = path_key.replace("_path", "_sha256")
        rel_path = _safe_rel_path(project_dir, file_path)
        capsule[path_key] = rel_path
        if not file_path.exists():
            missing.append(rel_path)
            continue
        digest = _sha256(file_path)
        capsule[hash_key] = digest
        hydration_inputs.append({"path": rel_path, "sha256": digest})
    return capsule, hydration_inputs, missing


def _schema_path(project_dir: Path) -> Path:
    return (project_dir / "contracts" / "context_hydration_receipt_schema_v0.json").resolve()


def _validate_receipt_schema(project_dir: Path, payload: dict[str, Any]) -> str | None:
    schema_file = _schema_path(project_dir)
    schema = _load_json(schema_file)
    if schema is None:
        return f"invalid or missing schema: {schema_file}"
    try:
        jsonschema.validate(instance=payload, schema=schema)
    except jsonschema.ValidationError as exc:
        return str(exc)
    return None


def _as_findings(
    findings: list[dict[str, Any]],
    check: str,
    message: str,
    **extra: Any,
) -> None:
    item: dict[str, Any] = {"check": check, "severity": "error", "message": message}
    item.update(extra)
    findings.append(item)


def _build_receipt(
    *,
    project_dir: Path,
    cortex_root: str,
    event: str,
    enforcement_mode: str,
    max_age_minutes: int,
    session_id: str,
    turn_count: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    now = _now_utc()
    fresh_until = now + timedelta(minutes=max(1, max_age_minutes))
    git_head = _run_git_head(project_dir)
    capsule, hydration_inputs, missing_capsule = _build_capsule(project_dir, cortex_root)

    findings: list[dict[str, Any]] = []
    if not git_head:
        _as_findings(findings, "missing_git_head", "Unable to resolve git HEAD for hydration receipt.")
    if missing_capsule:
        _as_findings(
            findings,
            "missing_governance_capsule_inputs",
            "Missing required governance capsule inputs for hydration receipt.",
            missing_paths=missing_capsule,
        )

    receipt = {
        "version": "v0",
        "receipt_id": f"chr_{now.strftime('%Y%m%dT%H%M%SZ')}_{event}",
        "event": event,
        "enforcement_mode": enforcement_mode,
        "hydrated_at": _to_iso(now),
        "fresh_until": _to_iso(fresh_until),
        "project_dir": str(project_dir),
        "cortex_root": cortex_root,
        "git_head": git_head,
        "governance_capsule": capsule,
        "hydration_inputs": hydration_inputs,
        "warnings": [],
        "metadata": {
            "policy_version": "v0",
            "session_id": session_id,
            "turn_count": max(0, turn_count),
        },
    }
    schema_error = _validate_receipt_schema(project_dir, receipt)
    if schema_error:
        _as_findings(
            findings,
            "receipt_schema_validation_failed",
            "Hydration receipt failed schema validation.",
            error=schema_error,
        )
    return receipt, findings


def _list_history_events(history_dir: Path) -> list[str]:
    if not history_dir.exists():
        return []
    events: list[str] = []
    for path in sorted(history_dir.glob("*.json")):
        payload = _load_json(path)
        if not payload:
            continue
        event = payload.get("event")
        if isinstance(event, str):
            events.append(event)
    return events


def _verify_receipt(
    *,
    project_dir: Path,
    cortex_root: str,
    receipt_payload: dict[str, Any],
    max_age_minutes: int,
    history_events: list[str],
    required_events: list[str],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    schema_error = _validate_receipt_schema(project_dir, receipt_payload)
    if schema_error:
        _as_findings(
            findings,
            "receipt_schema_validation_failed",
            "Hydration receipt failed schema validation.",
            error=schema_error,
        )
        return findings

    hydrated_at = _parse_iso(str(receipt_payload.get("hydrated_at", "")))
    fresh_until = _parse_iso(str(receipt_payload.get("fresh_until", "")))
    now = _now_utc()
    if hydrated_at is None:
        _as_findings(findings, "invalid_hydrated_at", "hydrated_at is missing or invalid.")
    else:
        age_minutes = (now - hydrated_at).total_seconds() / 60.0
        if age_minutes > float(max(1, max_age_minutes)):
            _as_findings(
                findings,
                "stale_receipt_age",
                "Hydration receipt age exceeds policy threshold.",
                receipt_age_minutes=age_minutes,
                max_age_minutes=max_age_minutes,
            )
    if fresh_until is None:
        _as_findings(findings, "invalid_fresh_until", "fresh_until is missing or invalid.")
    elif now > fresh_until:
        _as_findings(
            findings,
            "stale_receipt_fresh_until",
            "Hydration receipt is stale by fresh_until threshold.",
            fresh_until=_to_iso(fresh_until),
            now=_to_iso(now),
        )

    current_head = _run_git_head(project_dir)
    receipt_head = str(receipt_payload.get("git_head", ""))
    if not current_head:
        _as_findings(findings, "missing_git_head", "Unable to resolve current git HEAD for verification.")
    elif not receipt_head:
        _as_findings(findings, "missing_receipt_git_head", "Receipt git_head is missing.")
    elif current_head != receipt_head:
        _as_findings(
            findings,
            "git_head_drift",
            "Hydration receipt git_head differs from current git HEAD.",
            receipt_git_head=receipt_head,
            current_git_head=current_head,
        )

    capsule = receipt_payload.get("governance_capsule", {})
    if not isinstance(capsule, dict):
        _as_findings(findings, "invalid_governance_capsule", "governance_capsule object is missing or invalid.")
        return findings

    required_paths = _required_capsule_paths(project_dir, cortex_root)
    for path_key, file_path in required_paths.items():
        hash_key = path_key.replace("_path", "_sha256")
        expected_rel = _safe_rel_path(project_dir, file_path)
        receipt_path = str(capsule.get(path_key, ""))
        receipt_hash = str(capsule.get(hash_key, ""))
        if receipt_path != expected_rel:
            _as_findings(
                findings,
                "receipt_path_mismatch",
                "Receipt governance capsule path does not match expected path.",
                key=path_key,
                receipt_path=receipt_path,
                expected_path=expected_rel,
            )
            continue
        if not file_path.exists():
            _as_findings(
                findings,
                "missing_governance_capsule_input",
                "Required governance capsule input is missing.",
                key=path_key,
                path=expected_rel,
            )
            continue
        current_hash = _sha256(file_path)
        if receipt_hash != current_hash:
            _as_findings(
                findings,
                "governance_capsule_hash_drift",
                "Receipt governance capsule hash differs from current file hash.",
                key=hash_key,
                path=expected_rel,
                receipt_sha256=receipt_hash,
                current_sha256=current_hash,
            )

    if required_events:
        missing = sorted(set(required_events) - set(str(event) for event in history_events))
        if missing:
            _as_findings(
                findings,
                "missing_required_hydration_events",
                "Required hydration events are missing from history coverage.",
                required_events=required_events,
                history_events=history_events,
                missing_events=missing,
            )

    return findings


def _status_for_findings(
    findings: list[dict[str, Any]],
    enforcement_mode: str,
    override_reason: str,
) -> tuple[str, int]:
    if not findings:
        return "pass", 0
    if override_reason.strip():
        return "warn", 0
    if enforcement_mode == "block":
        return "fail", 1
    return "warn", 0


def _render_text(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
        f"mode: {payload.get('mode', '')}",
    ]
    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        lines.append(
            "summary: "
            f"findings={summary.get('finding_count', 0)} "
            f"required_events_covered={summary.get('required_events_covered', False)}"
        )
    findings = payload.get("findings", [])
    if isinstance(findings, list) and findings:
        lines.append("findings:")
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            lines.append(f"- {finding.get('check')}: {finding.get('message')}")
    return "\n".join(lines)


def _emit_payload(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(_render_text(payload))


def _write_optional_out_file(project_dir: Path, out_file: str, payload: dict[str, Any]) -> str:
    if not out_file:
        return ""
    out_path = Path(out_file)
    if not out_path.is_absolute():
        out_path = (project_dir / out_path).resolve()
    _write_json(out_path, payload)
    return str(out_path)


def _handle_emit(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    latest_path = Path(args.latest_receipt_path)
    if not latest_path.is_absolute():
        latest_path = (project_dir / latest_path).resolve()
    history_dir = Path(args.history_dir)
    if not history_dir.is_absolute():
        history_dir = (project_dir / history_dir).resolve()

    receipt, findings = _build_receipt(
        project_dir=project_dir,
        cortex_root=args.cortex_root,
        event=args.event,
        enforcement_mode=args.enforcement_mode,
        max_age_minutes=args.max_age_minutes,
        session_id=args.session_id,
        turn_count=args.turn_count,
    )
    status, returncode = _status_for_findings(findings, args.enforcement_mode, args.override_reason)
    if status in {"pass", "warn"}:
        _write_json(latest_path, receipt)
        if args.write_history:
            history_name = f"receipt_{receipt['hydrated_at'].replace(':', '').replace('-', '')}_{args.event}_v0.json"
            _write_json(history_dir / history_name, receipt)

    payload: dict[str, Any] = {
        "artifact": "context_hydration_gate_v0",
        "version": "v0",
        "mode": "emit",
        "run_at": _to_iso(_now_utc()),
        "project_dir": str(project_dir),
        "event": args.event,
        "enforcement_mode": args.enforcement_mode,
        "latest_receipt_path": _safe_rel_path(project_dir, latest_path),
        "history_dir": _safe_rel_path(project_dir, history_dir),
        "override_reason": args.override_reason.strip(),
        "receipt": receipt,
        "findings": findings,
        "summary": {
            "finding_count": len(findings),
            "receipt_written": status in {"pass", "warn"},
        },
        "status": status,
    }
    out_path = _write_optional_out_file(project_dir, args.out_file, payload)
    if out_path:
        payload["out_file"] = out_path
    _emit_payload(payload, args.format)
    return returncode


def _handle_verify(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    latest_path = Path(args.latest_receipt_path)
    if not latest_path.is_absolute():
        latest_path = (project_dir / latest_path).resolve()
    history_dir = Path(args.history_dir)
    if not history_dir.is_absolute():
        history_dir = (project_dir / history_dir).resolve()

    receipt_payload = _load_json(latest_path)
    findings: list[dict[str, Any]] = []
    if receipt_payload is None:
        _as_findings(
            findings,
            "missing_receipt",
            "Hydration receipt file is missing or invalid.",
            latest_receipt_path=_safe_rel_path(project_dir, latest_path),
        )
        status, returncode = _status_for_findings(findings, args.enforcement_mode, args.override_reason)
        payload = {
            "artifact": "context_hydration_gate_v0",
            "version": "v0",
            "mode": "verify",
            "run_at": _to_iso(_now_utc()),
            "project_dir": str(project_dir),
            "event": args.event,
            "enforcement_mode": args.enforcement_mode,
            "latest_receipt_path": _safe_rel_path(project_dir, latest_path),
            "history_dir": _safe_rel_path(project_dir, history_dir),
            "override_reason": args.override_reason.strip(),
            "findings": findings,
            "summary": {
                "finding_count": len(findings),
                "required_events_covered": False,
            },
            "status": status,
        }
        out_path = _write_optional_out_file(project_dir, args.out_file, payload)
        if out_path:
            payload["out_file"] = out_path
        _emit_payload(payload, args.format)
        return returncode

    history_events = _list_history_events(history_dir)
    required_events = [item.strip() for item in args.required_events.split(",") if item.strip()]
    findings = _verify_receipt(
        project_dir=project_dir,
        cortex_root=args.cortex_root,
        receipt_payload=receipt_payload,
        max_age_minutes=args.max_age_minutes,
        history_events=history_events,
        required_events=required_events,
    )
    status, returncode = _status_for_findings(findings, args.enforcement_mode, args.override_reason)
    payload = {
        "artifact": "context_hydration_gate_v0",
        "version": "v0",
        "mode": "verify",
        "run_at": _to_iso(_now_utc()),
        "project_dir": str(project_dir),
        "event": args.event,
        "enforcement_mode": args.enforcement_mode,
        "latest_receipt_path": _safe_rel_path(project_dir, latest_path),
        "history_dir": _safe_rel_path(project_dir, history_dir),
        "required_events": required_events,
        "history_events": history_events,
        "override_reason": args.override_reason.strip(),
        "receipt": receipt_payload,
        "findings": findings,
        "summary": {
            "finding_count": len(findings),
            "required_events_covered": not any(
                finding.get("check") == "missing_required_hydration_events" for finding in findings
            ),
            "stale_receipt_detected": any(
                finding.get("check") in {"stale_receipt_age", "stale_receipt_fresh_until"} for finding in findings
            ),
            "hash_drift_detected": any(
                finding.get("check") == "governance_capsule_hash_drift" for finding in findings
            ),
        },
        "status": status,
    }
    out_path = _write_optional_out_file(project_dir, args.out_file, payload)
    if out_path:
        payload["out_file"] = out_path
    _emit_payload(payload, args.format)
    return returncode


def _handle_compliance(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    if args.latest_receipt_path:
        latest_path = Path(args.latest_receipt_path)
        if not latest_path.is_absolute():
            latest_path = (project_dir / latest_path).resolve()
    else:
        latest_path = Path(tempfile.mkstemp(prefix="context_hydration_latest_", suffix=".json")[1])

    if args.history_dir:
        history_dir = Path(args.history_dir)
        if not history_dir.is_absolute():
            history_dir = (project_dir / history_dir).resolve()
        history_dir.mkdir(parents=True, exist_ok=True)
    else:
        history_dir = Path(tempfile.mkdtemp(prefix="context_hydration_history_"))

    events_to_emit = [item.strip() for item in args.emit_events.split(",") if item.strip()]
    emit_results: list[dict[str, Any]] = []
    overall_findings: list[dict[str, Any]] = []

    for event in events_to_emit:
        receipt, emit_findings = _build_receipt(
            project_dir=project_dir,
            cortex_root=args.cortex_root,
            event=event,
            enforcement_mode=args.enforcement_mode,
            max_age_minutes=args.max_age_minutes,
            session_id=args.session_id,
            turn_count=args.turn_count,
        )
        emit_status, emit_rc = _status_for_findings(emit_findings, args.enforcement_mode, "")
        if emit_status in {"pass", "warn"}:
            _write_json(latest_path, receipt)
            history_name = f"receipt_{receipt['hydrated_at'].replace(':', '').replace('-', '')}_{event}_v0.json"
            _write_json(history_dir / history_name, receipt)
        emit_results.append(
            {
                "event": event,
                "returncode": emit_rc,
                "status": emit_status,
                "finding_count": len(emit_findings),
                "latest_receipt_written": emit_status in {"pass", "warn"},
            }
        )
        for finding in emit_findings:
            finding_copy = dict(finding)
            finding_copy["event"] = event
            overall_findings.append(finding_copy)
        if emit_rc != 0:
            _as_findings(
                overall_findings,
                "emit_event_failed",
                "Hydration emit step failed.",
                event=event,
            )

    required_events = [item.strip() for item in args.required_events.split(",") if item.strip()]
    history_events = _list_history_events(history_dir)
    verify_payload = _load_json(latest_path) or {}
    verify_findings = _verify_receipt(
        project_dir=project_dir,
        cortex_root=args.cortex_root,
        receipt_payload=verify_payload if verify_payload else {"version": "v0"},
        max_age_minutes=args.max_age_minutes,
        history_events=history_events,
        required_events=required_events,
    )
    verify_status, verify_rc = _status_for_findings(verify_findings, args.enforcement_mode, args.override_reason)
    overall_findings.extend(verify_findings)

    missing_events = sorted(set(required_events) - set(history_events))
    if missing_events:
        _as_findings(
            overall_findings,
            "missing_required_hydration_events",
            "Required hydration events are missing from compliance coverage.",
            required_events=required_events,
            history_events=history_events,
            missing_events=missing_events,
        )
    if verify_rc != 0:
        _as_findings(
            overall_findings,
            "verify_step_failed",
            "Hydration verify step failed in compliance mode.",
            verify_event=args.verify_event,
        )

    status, returncode = _status_for_findings(overall_findings, args.enforcement_mode, args.override_reason)
    payload: dict[str, Any] = {
        "artifact": "phase6_hydration_compliance_report_v0",
        "version": "v0",
        "mode": "compliance",
        "run_at": _to_iso(_now_utc()),
        "project_dir": str(project_dir),
        "policy_source": "policies/context_hydration_policy_v0.md",
        "contract_source": "contracts/context_hydration_receipt_schema_v0.json",
        "enforcement_mode": args.enforcement_mode,
        "emit_events": events_to_emit,
        "verify_event": args.verify_event,
        "required_events": required_events,
        "history_events": history_events,
        "latest_receipt_path": _safe_rel_path(project_dir, latest_path),
        "history_dir": _safe_rel_path(project_dir, history_dir),
        "emit_results": emit_results,
        "verify_result": {
            "returncode": verify_rc,
            "status": verify_status,
            "finding_count": len(verify_findings),
            "latest_receipt_loaded": bool(verify_payload),
        },
        "targets": {
            "required_events_covered": True,
            "verify_step_pass": True,
        },
        "target_results": {
            "required_events_covered": len(missing_events) == 0,
            "verify_step_pass": verify_rc == 0,
        },
        "findings": overall_findings,
        "summary": {
            "finding_count": len(overall_findings),
            "required_events_covered": len(missing_events) == 0,
            "verify_step_pass": verify_rc == 0,
        },
        "status": status,
    }
    out_path = _write_optional_out_file(project_dir, args.out_file, payload)
    if out_path:
        payload["out_file"] = out_path
    _emit_payload(payload, args.format)
    return returncode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)

    def add_common(target: argparse.ArgumentParser) -> None:
        target.add_argument("--project-dir", default=".")
        target.add_argument("--cortex-root", default=".cortex")
        target.add_argument("--enforcement-mode", default="block", choices=ENFORCEMENT_MODES)
        target.add_argument("--max-age-minutes", type=int, default=45)
        target.add_argument("--latest-receipt-path", default=".cortex/reports/context_hydration/latest.json")
        target.add_argument("--history-dir", default=".cortex/reports/context_hydration/history")
        target.add_argument("--override-reason", default="")
        target.add_argument("--out-file", default="")
        target.add_argument("--format", default="text", choices=("text", "json"))

    emit = subparsers.add_parser("emit")
    add_common(emit)
    emit.add_argument("--event", required=True, choices=EVENTS)
    emit.add_argument("--write-history", action="store_true")
    emit.add_argument("--session-id", default="session")
    emit.add_argument("--turn-count", type=int, default=0)

    verify = subparsers.add_parser("verify")
    add_common(verify)
    verify.add_argument("--event", required=True, choices=EVENTS)
    verify.add_argument("--required-events", default="new_session,window_rollover")

    compliance = subparsers.add_parser("compliance")
    compliance.add_argument("--project-dir", default=".")
    compliance.add_argument("--cortex-root", default=".cortex")
    compliance.add_argument("--enforcement-mode", default="block", choices=ENFORCEMENT_MODES)
    compliance.add_argument("--max-age-minutes", type=int, default=45)
    compliance.add_argument("--latest-receipt-path", default="")
    compliance.add_argument("--history-dir", default="")
    compliance.add_argument("--emit-events", default="new_session,window_rollover")
    compliance.add_argument("--verify-event", default="pre_closeout", choices=EVENTS)
    compliance.add_argument("--required-events", default="new_session,window_rollover")
    compliance.add_argument("--override-reason", default="")
    compliance.add_argument("--session-id", default="session")
    compliance.add_argument("--turn-count", type=int, default=0)
    compliance.add_argument("--out-file", default="")
    compliance.add_argument("--format", default="text", choices=("text", "json"))
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    if args.mode == "emit":
        return _handle_emit(args)
    if args.mode == "verify":
        return _handle_verify(args)
    return _handle_compliance(args)


if __name__ == "__main__":
    raise SystemExit(main())

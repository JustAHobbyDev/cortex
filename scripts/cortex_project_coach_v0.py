#!/usr/bin/env python3
"""Phase 4 delegator for installed standalone `cortex-coach` with format shim."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NATIVE_FORMAT_COMMANDS = {
    "audit-needed",
    "context-policy",
    "decision-capture",
    "reflection-scaffold",
    "decision-list",
    "decision-gap-check",
    "reflection-completeness-check",
    "decision-promote",
    "contract-check",
    "rollout-mode",
    "rollout-mode-audit",
}

ROLLOUT_MODES = {"off", "experimental", "default"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _extract_subcommand(argv: list[str]) -> str:
    for token in argv:
        if token and not token.startswith("-"):
            return token
    return ""


def _extract_option_value(argv: list[str], flag: str) -> str | None:
    for idx, token in enumerate(argv):
        if token == flag and idx + 1 < len(argv):
            return argv[idx + 1]
        prefix = f"{flag}="
        if token.startswith(prefix):
            return token[len(prefix) :]
    return None


def _strip_option(argv: list[str], flag: str) -> list[str]:
    stripped: list[str] = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token == flag:
            i += 1
            if i < len(argv) and not argv[i].startswith("-"):
                i += 1
            continue
        if token.startswith(f"{flag}="):
            i += 1
            continue
        stripped.append(token)
        i += 1
    return stripped


def _load_json_file(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_json_text(text: str) -> Any | None:
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _find_existing_paths(lines: list[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        candidate = Path(line)
        if candidate.exists():
            paths.append(str(candidate))
    return paths


def _emit_json_payload(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")


def _emit_text(stdout: str, stderr: str) -> None:
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)


def _safe_rel_path(project_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_args_with_exit(parser: argparse.ArgumentParser, args: list[str]) -> tuple[argparse.Namespace | None, int]:
    try:
        return parser.parse_args(args), 0
    except SystemExit as exc:  # argparse exits on parse errors / --help
        return None, int(exc.code) if isinstance(exc.code, int) else 1


def _build_rollout_mode_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cortex-coach rollout-mode")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--cortex-root", default=".cortex")
    parser.add_argument("--set-mode", choices=sorted(ROLLOUT_MODES))
    parser.add_argument("--changed-by", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--incident-ref", default="")
    parser.add_argument("--decision-refs", default="")
    parser.add_argument("--reflection-refs", default="")
    parser.add_argument("--audit-refs", default="")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _build_rollout_mode_audit_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cortex-coach rollout-mode-audit")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--cortex-root", default=".cortex")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _rollout_paths(project_dir: Path, cortex_root: str) -> tuple[Path, Path, Path]:
    root = project_dir / cortex_root
    state_path = root / "state" / "rollout_mode_state_v0.json"
    transitions_path = root / "state" / "rollout_mode_transitions_v0.jsonl"
    audit_report_path = root / "reports" / "project_state" / "phase5_mode_transition_audit_report_v0.json"
    return state_path, transitions_path, audit_report_path


def _default_rollout_state() -> dict[str, Any]:
    return {
        "version": "v0",
        "mode": "experimental",
        "updated_at": _now_iso(),
        "updated_by": "system",
        "reason": "initial_rollout_mode_state",
        "last_transition_id": "",
        "decision_refs": [],
        "reflection_refs": [],
        "audit_refs": [],
    }


def _load_rollout_state(state_path: Path) -> tuple[dict[str, Any], str | None]:
    if not state_path.exists():
        return _default_rollout_state(), None
    payload = _load_json_file(state_path)
    if not isinstance(payload, dict):
        return {}, f"invalid rollout mode state payload: {state_path}"
    mode = str(payload.get("mode", "")).strip()
    if mode not in ROLLOUT_MODES:
        return {}, f"invalid rollout mode in state: {mode!r}"
    payload.setdefault("version", "v0")
    payload.setdefault("decision_refs", [])
    payload.setdefault("reflection_refs", [])
    payload.setdefault("audit_refs", [])
    return payload, None


def _write_rollout_state(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_rollout_transition(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True))
        fh.write("\n")


def _transition_id(payload: dict[str, Any]) -> str:
    seed = json.dumps(payload, sort_keys=True)
    return f"rmt_{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:16]}"


def _emit_rollout_payload(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        _emit_json_payload(payload)
        return
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
    ]
    result = payload.get("result", {})
    if isinstance(result, dict):
        mode = result.get("mode")
        if isinstance(mode, str) and mode:
            lines.append(f"mode: {mode}")
        transition_id = result.get("transition_id")
        if isinstance(transition_id, str) and transition_id:
            lines.append(f"transition_id: {transition_id}")
        report_path = result.get("report_path")
        if isinstance(report_path, str) and report_path:
            lines.append(f"report_path: {report_path}")
    message = payload.get("message")
    if isinstance(message, str) and message:
        lines.append(f"message: {message}")
    sys.stdout.write("\n".join(lines))
    sys.stdout.write("\n")


def _run_rollout_mode_command(argv: list[str]) -> int:
    subcommand = "rollout-mode"
    args = argv[1:] if len(argv) > 1 else []
    parsed, parse_code = _parse_args_with_exit(_build_rollout_mode_parser(), args)
    if parsed is None:
        return parse_code

    project_dir = Path(parsed.project_dir).resolve()
    cortex_root = str(parsed.cortex_root or ".cortex")
    output_format = str(parsed.format)
    state_path, transitions_path, _ = _rollout_paths(project_dir, cortex_root)
    state, state_error = _load_rollout_state(state_path)
    if state_error:
        payload = {
            "version": "v0",
            "command": subcommand,
            "status": "fail",
            "returncode": 3,
            "run_at": _now_iso(),
            "project_dir": str(project_dir),
            "format_source": "delegator_rollout_fallback_v0",
            "message": state_error,
        }
        _emit_rollout_payload(payload, output_format)
        return 3

    current_mode = str(state.get("mode", "experimental"))
    set_mode = str(parsed.set_mode) if parsed.set_mode else ""
    if not set_mode:
        payload = {
            "version": "v0",
            "command": subcommand,
            "status": "pass",
            "returncode": 0,
            "run_at": _now_iso(),
            "project_dir": str(project_dir),
            "format_source": "delegator_rollout_fallback_v0",
            "result": {
                "mode": current_mode,
                "state_path": _safe_rel_path(project_dir, state_path),
                "transitions_path": _safe_rel_path(project_dir, transitions_path),
                "changed": False,
                "transition_id": "",
            },
        }
        _emit_rollout_payload(payload, output_format)
        return 0

    changed_by = str(parsed.changed_by).strip()
    reason = str(parsed.reason).strip()
    incident_ref = str(parsed.incident_ref).strip()
    decision_refs = _split_csv(str(parsed.decision_refs))
    reflection_refs = _split_csv(str(parsed.reflection_refs))
    audit_refs = _split_csv(str(parsed.audit_refs))

    findings: list[str] = []
    if not changed_by:
        findings.append("missing_changed_by")
    if not reason:
        findings.append("missing_reason")
    if set_mode == "default":
        if not decision_refs:
            findings.append("missing_decision_refs_for_default")
        if not reflection_refs:
            findings.append("missing_reflection_refs_for_default")
        if not audit_refs:
            findings.append("missing_audit_refs_for_default")
    if current_mode == "default" and set_mode in {"experimental", "off"} and not incident_ref:
        findings.append("missing_incident_ref_for_default_rollback")

    if findings:
        payload = {
            "version": "v0",
            "command": subcommand,
            "status": "fail",
            "returncode": 3,
            "run_at": _now_iso(),
            "project_dir": str(project_dir),
            "format_source": "delegator_rollout_fallback_v0",
            "message": "rollout-mode policy preconditions not met",
            "findings": findings,
            "result": {
                "mode": current_mode,
                "state_path": _safe_rel_path(project_dir, state_path),
                "transitions_path": _safe_rel_path(project_dir, transitions_path),
                "changed": False,
                "transition_id": "",
            },
        }
        _emit_rollout_payload(payload, output_format)
        return 3

    if set_mode == current_mode:
        payload = {
            "version": "v0",
            "command": subcommand,
            "status": "pass",
            "returncode": 0,
            "run_at": _now_iso(),
            "project_dir": str(project_dir),
            "format_source": "delegator_rollout_fallback_v0",
            "message": "requested mode already active",
            "result": {
                "mode": current_mode,
                "state_path": _safe_rel_path(project_dir, state_path),
                "transitions_path": _safe_rel_path(project_dir, transitions_path),
                "changed": False,
                "transition_id": "",
            },
        }
        _emit_rollout_payload(payload, output_format)
        return 0

    transition_base = {
        "version": "v0",
        "from_mode": current_mode,
        "to_mode": set_mode,
        "changed_at": _now_iso(),
        "changed_by": changed_by,
        "reason": reason,
        "incident_ref": incident_ref,
        "decision_refs": decision_refs,
        "reflection_refs": reflection_refs,
        "audit_refs": audit_refs,
    }
    transition_id = _transition_id(transition_base)
    transition_payload = {
        **transition_base,
        "transition_id": transition_id,
    }
    _append_rollout_transition(transitions_path, transition_payload)

    next_state = {
        "version": "v0",
        "mode": set_mode,
        "updated_at": transition_payload["changed_at"],
        "updated_by": changed_by,
        "reason": reason,
        "last_transition_id": transition_id,
        "decision_refs": decision_refs,
        "reflection_refs": reflection_refs,
        "audit_refs": audit_refs,
    }
    _write_rollout_state(state_path, next_state)

    payload = {
        "version": "v0",
        "command": subcommand,
        "status": "pass",
        "returncode": 0,
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "format_source": "delegator_rollout_fallback_v0",
        "result": {
            "mode": set_mode,
            "from_mode": current_mode,
            "to_mode": set_mode,
            "changed": True,
            "transition_id": transition_id,
            "state_path": _safe_rel_path(project_dir, state_path),
            "transitions_path": _safe_rel_path(project_dir, transitions_path),
        },
    }
    _emit_rollout_payload(payload, output_format)
    return 0


def _read_transition_records(transitions_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    if not transitions_path.exists():
        return records, findings
    for line_no, raw_line in enumerate(transitions_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            findings.append(
                {
                    "check": "invalid_transition_json",
                    "severity": "error",
                    "line": line_no,
                    "message": "Transition log line is not valid JSON.",
                }
            )
            continue
        if not isinstance(parsed, dict):
            findings.append(
                {
                    "check": "invalid_transition_record",
                    "severity": "error",
                    "line": line_no,
                    "message": "Transition record must be a JSON object.",
                }
            )
            continue
        parsed["_line"] = line_no
        records.append(parsed)
    return records, findings


def _transition_findings(transition: dict[str, Any]) -> list[dict[str, Any]]:
    transition_id = str(transition.get("transition_id", "<missing>"))
    findings: list[dict[str, Any]] = []

    required_fields = ("transition_id", "from_mode", "to_mode", "changed_at", "changed_by", "reason")
    for field in required_fields:
        value = transition.get(field)
        if not isinstance(value, str) or not value.strip():
            findings.append(
                {
                    "check": "missing_transition_field",
                    "severity": "error",
                    "transition_id": transition_id,
                    "field": field,
                    "message": f"Transition missing required field: {field}.",
                }
            )

    from_mode = str(transition.get("from_mode", ""))
    to_mode = str(transition.get("to_mode", ""))
    if from_mode not in ROLLOUT_MODES:
        findings.append(
            {
                "check": "invalid_from_mode",
                "severity": "error",
                "transition_id": transition_id,
                "message": f"Invalid from_mode: {from_mode!r}.",
            }
        )
    if to_mode not in ROLLOUT_MODES:
        findings.append(
            {
                "check": "invalid_to_mode",
                "severity": "error",
                "transition_id": transition_id,
                "message": f"Invalid to_mode: {to_mode!r}.",
            }
        )

    decision_refs = transition.get("decision_refs")
    reflection_refs = transition.get("reflection_refs")
    audit_refs = transition.get("audit_refs")
    if not isinstance(decision_refs, list):
        decision_refs = []
    if not isinstance(reflection_refs, list):
        reflection_refs = []
    if not isinstance(audit_refs, list):
        audit_refs = []

    if to_mode == "default":
        if not decision_refs or not reflection_refs or not audit_refs:
            findings.append(
                {
                    "check": "missing_default_linkage",
                    "severity": "error",
                    "transition_id": transition_id,
                    "message": "Default transition requires decision/reflection/audit linkage refs.",
                }
            )

    incident_ref = str(transition.get("incident_ref", "")).strip()
    if from_mode == "default" and to_mode in {"experimental", "off"} and not incident_ref:
        findings.append(
            {
                "check": "missing_default_rollback_incident_ref",
                "severity": "error",
                "transition_id": transition_id,
                "message": "Rollback from default requires incident_ref.",
            }
        )

    return findings


def _run_rollout_mode_audit_command(argv: list[str]) -> int:
    subcommand = "rollout-mode-audit"
    args = argv[1:] if len(argv) > 1 else []
    parsed, parse_code = _parse_args_with_exit(_build_rollout_mode_audit_parser(), args)
    if parsed is None:
        return parse_code

    project_dir = Path(parsed.project_dir).resolve()
    cortex_root = str(parsed.cortex_root or ".cortex")
    output_format = str(parsed.format)
    state_path, transitions_path, audit_report_path = _rollout_paths(project_dir, cortex_root)

    state, state_error = _load_rollout_state(state_path)
    if state_error:
        payload = {
            "version": "v0",
            "command": subcommand,
            "status": "fail",
            "returncode": 3,
            "run_at": _now_iso(),
            "project_dir": str(project_dir),
            "format_source": "delegator_rollout_fallback_v0",
            "message": state_error,
        }
        _emit_rollout_payload(payload, output_format)
        return 3

    transition_records, findings = _read_transition_records(transitions_path)
    complete_transition_count = 0
    for transition in transition_records:
        tf = _transition_findings(transition)
        if tf:
            findings.extend(tf)
        else:
            complete_transition_count += 1

    transition_count = len(transition_records)
    completeness_rate = 1.0 if transition_count == 0 else float(complete_transition_count / transition_count)
    status = "pass" if not findings and completeness_rate >= 1.0 else "fail"

    report_payload = {
        "artifact": "phase5_mode_transition_audit_report_v0",
        "version": "v0",
        "project_dir": str(project_dir),
        "run_at": _now_iso(),
        "state_mode": str(state.get("mode", "experimental")),
        "state_path": _safe_rel_path(project_dir, state_path),
        "transitions_path": _safe_rel_path(project_dir, transitions_path),
        "summary": {
            "transition_count": transition_count,
            "complete_transition_count": complete_transition_count,
            "finding_count": len(findings),
            "transition_completeness_rate": completeness_rate,
        },
        "targets": {
            "transition_completeness_rate": 1.0,
        },
        "target_results": {
            "transition_completeness_rate_met": completeness_rate >= 1.0 and not findings,
        },
        "findings": findings,
        "status": status,
    }
    audit_report_path.parent.mkdir(parents=True, exist_ok=True)
    audit_report_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    payload = {
        "version": "v0",
        "command": subcommand,
        "status": status,
        "returncode": 0 if status == "pass" else 3,
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "format_source": "delegator_rollout_fallback_v0",
        "result": {
            "report_path": _safe_rel_path(project_dir, audit_report_path),
            "transition_count": transition_count,
            "finding_count": len(findings),
            "transition_completeness_rate": completeness_rate,
            "state_mode": str(state.get("mode", "experimental")),
        },
    }
    _emit_rollout_payload(payload, output_format)
    return 0 if status == "pass" else 3


def _shim_json_payload(
    subcommand: str,
    forwarded_argv: list[str],
    proc: subprocess.CompletedProcess[str],
) -> dict[str, Any]:
    output_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    payload: dict[str, Any] = {
        "version": "v0",
        "command": subcommand,
        "status": "pass" if proc.returncode == 0 else "fail",
        "returncode": proc.returncode,
        "run_at": _now_iso(),
        "project_dir": _extract_option_value(forwarded_argv, "--project-dir"),
        "format_source": "delegator_compat_shim_v0",
        "stdout": proc.stdout.rstrip("\n"),
        "stderr": proc.stderr.rstrip("\n"),
    }

    output_paths = _find_existing_paths(output_lines)
    if output_paths:
        payload["output_paths"] = output_paths

    if subcommand == "init":
        for line in output_lines:
            if line.startswith("created_or_updated_files:"):
                _, _, value = line.partition(":")
                try:
                    payload["created_or_updated_files"] = int(value.strip())
                except ValueError:
                    payload["created_or_updated_files"] = value.strip()
                break
    elif subcommand == "policy-enable" and output_paths:
        payload["policy_path"] = output_paths[0]
    elif subcommand == "coach":
        for path_text in output_paths:
            candidate = Path(path_text)
            if candidate.name.startswith("coach_cycle_") and candidate.suffix == ".json":
                payload["coach_cycle_report_path"] = path_text
                report_data = _load_json_file(candidate)
                if report_data is not None:
                    payload["coach_cycle_report"] = report_data
                break

    return payload


def _emit_shim_json(
    subcommand: str,
    forwarded_argv: list[str],
    proc: subprocess.CompletedProcess[str],
) -> None:
    # `audit` natively emits a report path; in json mode we emit the report payload.
    if subcommand == "audit":
        report_path: Path | None = None
        for line in proc.stdout.splitlines():
            candidate = Path(line.strip())
            if candidate.exists() and candidate.suffix == ".json":
                report_path = candidate
                break
        if report_path is None:
            project_dir = _extract_option_value(forwarded_argv, "--project-dir")
            cortex_root = _extract_option_value(forwarded_argv, "--cortex-root") or ".cortex"
            if project_dir:
                report_path = Path(project_dir) / cortex_root / "reports" / "lifecycle_audit_v0.json"
        if report_path is not None:
            report_payload = _load_json_file(report_path)
            if isinstance(report_payload, dict):
                report_payload.setdefault("format_source", "delegator_compat_shim_v0")
                _emit_json_payload(report_payload)
                return

    # `context-load` already emits a JSON bundle; forward JSON payload when available.
    if subcommand == "context-load":
        out_file = _extract_option_value(forwarded_argv, "--out-file")
        if out_file:
            out_path = Path(out_file)
            bundle = _load_json_file(out_path)
            if bundle is not None:
                _emit_json_payload(bundle)
                return
        bundle = _load_json_text(proc.stdout)
        if bundle is not None:
            _emit_json_payload(bundle)
            return

    _emit_json_payload(_shim_json_payload(subcommand, forwarded_argv, proc))


def _run_passthrough(coach_bin: str, argv: list[str]) -> int:
    proc = subprocess.run([coach_bin, *argv], check=False)
    return proc.returncode


def _run_with_format_shim(coach_bin: str, argv: list[str], subcommand: str, requested_format: str) -> int:
    if requested_format not in {"text", "json"}:
        print(f"unsupported --format value: {requested_format!r} (expected: text or json)", file=sys.stderr)
        return 2

    if subcommand in NATIVE_FORMAT_COMMANDS:
        return _run_passthrough(coach_bin, argv)

    forwarded_argv = _strip_option(argv, "--format")
    proc = subprocess.run([coach_bin, *forwarded_argv], check=False, text=True, capture_output=True)
    if requested_format == "text":
        _emit_text(proc.stdout, proc.stderr)
        return proc.returncode

    _emit_shim_json(subcommand, forwarded_argv, proc)
    return proc.returncode


def main() -> int:
    argv = sys.argv[1:]
    subcommand = _extract_subcommand(argv)
    if subcommand in {"rollout-mode", "rollout-mode-audit"}:
        try:
            idx = argv.index(subcommand)
        except ValueError:
            idx = 0
        command_argv = argv[idx:]
        if subcommand == "rollout-mode":
            return _run_rollout_mode_command(command_argv)
        return _run_rollout_mode_audit_command(command_argv)

    if os.environ.get("CORTEX_COACH_FORCE_INTERNAL") == "1":
        print(
            "CORTEX_COACH_FORCE_INTERNAL is no longer supported in Phase 4. "
            "Use installed standalone `cortex-coach`.",
            file=sys.stderr,
        )
        return 1

    coach_bin = shutil.which("cortex-coach")
    if not coach_bin:
        print(
            "missing `cortex-coach` on PATH. Install standalone coach "
            "(for example: `uv tool install git+https://github.com/JustAHobbyDev/cortex-coach.git`).",
            file=sys.stderr,
        )
        return 1

    requested_format = _extract_option_value(argv, "--format")
    if requested_format is None:
        return _run_passthrough(coach_bin, argv)

    return _run_with_format_shim(coach_bin, argv, subcommand, requested_format)


if __name__ == "__main__":
    raise SystemExit(main())

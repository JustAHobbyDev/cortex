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
BOOTSTRAP_REQUIRED_PATHS = (
    ".cortex/manifest_v0.json",
    ".cortex/spec_registry_v0.json",
    ".cortex/artifacts",
    ".cortex/prompts",
    ".cortex/reports",
)
BOOTSTRAP_PORTABILITY_SEED_PATHS = (
    "contracts/context_hydration_receipt_schema_v0.json",
    "contracts/project_state_boundary_contract_v0.json",
    ".cortex/policies/project_state_boundary_waivers_v0.json",
    ".cortex/reports/lifecycle_audit_v0.json",
    ".cortex/reports/decision_candidates_v0.json",
    "policies/cortex_coach_final_ownership_boundary_v0.md",
    "policies/project_state_boundary_policy_v0.md",
    "playbooks/cortex_vision_master_roadmap_v1.md",
)
BOOTSTRAP_PORTABILITY_FORCE_TEMPLATE_PATHS = {
    ".cortex/reports/lifecycle_audit_v0.json",
    ".cortex/reports/decision_candidates_v0.json",
    "playbooks/cortex_vision_master_roadmap_v1.md",
}
BOOTSTRAP_TEMPLATE_REL_PATH = ".cortex/templates/bootstrap_first_green_gate_checklist_template_v0.md"
BOOTSTRAP_TEMPLATE_FALLBACK = """# Bootstrap First Green Gate Checklist v0

Version: v0
Date: <YYYY-MM-DD>
Project: <project_name> (<project_id>)

## Required Setup

1. Confirm `.cortex/` was initialized and committed.
2. Run `cortex-coach audit-needed --project-dir . --format json`.
3. If `audit_required=true`, run `cortex-coach coach --project-dir .` then `cortex-coach audit --project-dir .`.
4. Run required gate bundle: `./scripts/quality_gate_ci_v0.sh`.

## Exit Criteria

1. Required governance gate bundle is green.
2. No unresolved decision gaps for governance-impacting files.
3. Boundary and hydration enforcement checks pass in block mode.
"""
BOOTSTRAP_OWNERSHIP_BOUNDARY_FALLBACK = """# Cortex Coach Final Ownership Boundary v0

Version: v0
Date: <YYYY-MM-DD>

## Boundary

The agent may propose and implement project changes but cannot self-approve governance policy exceptions.
Maintainer approval is required for boundary overrides, release-surface exceptions, and enforcement downgrades.
"""
BOOTSTRAP_BOUNDARY_POLICY_FALLBACK = """# Project State Boundary Policy v0

Version: v0
Date: <YYYY-MM-DD>

## Policy

1. Project-state artifacts default to `<cortex_root>/`.
2. Writes outside the project-state root require an approved waiver.
3. Boundary violations block governed closeout.
"""
BOOTSTRAP_ROADMAP_FALLBACK = """# <project_name> Vision Roadmap v1

Version: v1
Date: <YYYY-MM-DD>
Project: <project_name> (<project_id>)

## Intent

Establish governed delivery with deterministic closeout quality gates.

## Immediate Sequence

1. Baseline governance policies and contracts.
2. Run required gate bundle and fix blockers.
3. Capture decision and reflection linkage for release-boundary changes.
"""


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


def _build_bootstrap_scaffold_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cortex-coach bootstrap-scaffold")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--cortex-root", default=".cortex")
    parser.add_argument("--assets-dir", default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-init", action="store_true")
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


def _emit_bootstrap_payload(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        _emit_json_payload(payload)
        return

    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
    ]
    result = payload.get("result", {})
    if isinstance(result, dict):
        report_path = result.get("report_path")
        checklist_path = result.get("checklist_path")
        if isinstance(report_path, str) and report_path:
            lines.append(f"report_path: {report_path}")
        if isinstance(checklist_path, str) and checklist_path:
            lines.append(f"checklist_path: {checklist_path}")
        created = result.get("created_or_updated_paths", [])
        if isinstance(created, list):
            lines.append(f"created_or_updated_files: {len(created)}")
    message = payload.get("message")
    if isinstance(message, str) and message:
        lines.append(f"message: {message}")
    sys.stdout.write("\n".join(lines))
    sys.stdout.write("\n")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_bootstrap_template() -> str:
    template_path = _repo_root() / BOOTSTRAP_TEMPLATE_REL_PATH
    if template_path.exists():
        try:
            return template_path.read_text(encoding="utf-8")
        except OSError:
            return BOOTSTRAP_TEMPLATE_FALLBACK
    return BOOTSTRAP_TEMPLATE_FALLBACK


def _render_bootstrap_checklist(template_text: str, project_id: str, project_name: str) -> str:
    return (
        template_text.replace("<project_id>", project_id)
        .replace("<project_name>", project_name)
        .replace("<YYYY-MM-DD>", _now_iso()[:10])
    )


def _bootstrap_rel_path(rel: str, cortex_root: str) -> str:
    if rel == ".cortex":
        return cortex_root
    if rel.startswith(".cortex/"):
        return f"{cortex_root}{rel[len('.cortex'):]}"
    return rel


def _bootstrap_required_paths(project_dir: Path, cortex_root: str) -> list[str]:
    required: list[str] = []
    for rel in BOOTSTRAP_REQUIRED_PATHS:
        required.append(_bootstrap_rel_path(rel, cortex_root))
    return required


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _render_bootstrap_text_template(template_text: str, project_id: str, project_name: str, cortex_root: str) -> str:
    return (
        template_text.replace("<project_id>", project_id)
        .replace("<project_name>", project_name)
        .replace("<YYYY-MM-DD>", _now_iso()[:10])
        .replace("<cortex_root>", cortex_root)
    )


def _bootstrap_portability_fallback(
    rel: str,
    *,
    project_id: str,
    project_name: str,
    cortex_root: str,
) -> dict[str, Any] | str | None:
    if rel == "contracts/context_hydration_receipt_schema_v0.json":
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
        }
    if rel == "contracts/project_state_boundary_contract_v0.json":
        return {
            "version": "v0",
            "project_state_root": cortex_root,
            "forbidden_outside_project_state_roots": ["reports"],
            "waiver_file": _bootstrap_rel_path(".cortex/policies/project_state_boundary_waivers_v0.json", cortex_root),
        }
    if rel == ".cortex/policies/project_state_boundary_waivers_v0.json":
        return {
            "version": "v0",
            "waivers": [],
        }
    if rel == ".cortex/reports/lifecycle_audit_v0.json":
        return {
            "artifact": "lifecycle_audit_v0",
            "version": "v0",
            "run_at": _now_iso(),
            "project_id": project_id,
            "project_name": project_name,
            "status": "pass",
            "checks": [],
        }
    if rel == ".cortex/reports/decision_candidates_v0.json":
        return {
            "version": "v0",
            "generated_at": _now_iso(),
            "project_id": project_id,
            "project_name": project_name,
            "candidate_count": 0,
            "candidates": [],
        }
    if rel == "policies/cortex_coach_final_ownership_boundary_v0.md":
        return _render_bootstrap_text_template(BOOTSTRAP_OWNERSHIP_BOUNDARY_FALLBACK, project_id, project_name, cortex_root)
    if rel == "policies/project_state_boundary_policy_v0.md":
        return _render_bootstrap_text_template(BOOTSTRAP_BOUNDARY_POLICY_FALLBACK, project_id, project_name, cortex_root)
    if rel == "playbooks/cortex_vision_master_roadmap_v1.md":
        return _render_bootstrap_text_template(BOOTSTRAP_ROADMAP_FALLBACK, project_id, project_name, cortex_root)
    return None


def _seed_bootstrap_portability_bundle(
    *,
    project_dir: Path,
    cortex_root: str,
    project_id: str,
    project_name: str,
    force: bool,
) -> tuple[list[str], list[str], list[str], list[str]]:
    created_or_updated: list[str] = []
    skipped: list[str] = []
    fallback_used: list[str] = []
    missing: list[str] = []
    repo_root = _repo_root()

    for rel in BOOTSTRAP_PORTABILITY_SEED_PATHS:
        target_rel = _bootstrap_rel_path(rel, cortex_root)
        target_path = project_dir / target_rel
        if target_path.exists() and not force:
            skipped.append(target_rel)
            continue

        source_path = repo_root / rel
        source_allowed = rel not in BOOTSTRAP_PORTABILITY_FORCE_TEMPLATE_PATHS
        if source_allowed and source_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)
            created_or_updated.append(target_rel)
            continue

        fallback_payload = _bootstrap_portability_fallback(
            rel,
            project_id=project_id,
            project_name=project_name,
            cortex_root=cortex_root,
        )
        if fallback_payload is None:
            missing.append(target_rel)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(fallback_payload, dict):
            _write_json_file(target_path, fallback_payload)
        else:
            target_path.write_text(fallback_payload, encoding="utf-8")
        created_or_updated.append(target_rel)
        fallback_used.append(target_rel)

    return created_or_updated, skipped, fallback_used, missing


def _run_bootstrap_scaffold_command(argv: list[str], coach_bin: str | None) -> int:
    subcommand = "bootstrap-scaffold"
    args = argv[1:] if len(argv) > 1 else []
    parsed, parse_code = _parse_args_with_exit(_build_bootstrap_scaffold_parser(), args)
    if parsed is None:
        return parse_code

    project_dir = Path(parsed.project_dir).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    cortex_root = str(parsed.cortex_root or ".cortex").strip() or ".cortex"
    if cortex_root.endswith("/"):
        cortex_root = cortex_root.rstrip("/")
    output_format = str(parsed.format)
    project_id = str(parsed.project_id).strip()
    project_name = str(parsed.project_name).strip()
    skip_init = bool(parsed.skip_init)
    force = bool(parsed.force)

    if not project_id or not project_name:
        payload = {
            "version": "v0",
            "command": subcommand,
            "status": "fail",
            "returncode": 2,
            "run_at": _now_iso(),
            "project_dir": str(project_dir),
            "format_source": "delegator_bootstrap_scaffolder_v0",
            "message": "project-id and project-name are required.",
        }
        _emit_bootstrap_payload(payload, output_format)
        return 2

    init_result: dict[str, Any] = {
        "performed": False,
        "returncode": 0,
        "stdout": "",
        "stderr": "",
        "command": [],
    }
    if not skip_init:
        if coach_bin is None:
            payload = {
                "version": "v0",
                "command": subcommand,
                "status": "fail",
                "returncode": 1,
                "run_at": _now_iso(),
                "project_dir": str(project_dir),
                "format_source": "delegator_bootstrap_scaffolder_v0",
                "message": "missing `cortex-coach` on PATH; cannot run bootstrap init.",
            }
            _emit_bootstrap_payload(payload, output_format)
            return 1
        init_cmd = [
            coach_bin,
            "init",
            "--project-dir",
            str(project_dir),
            "--project-id",
            project_id,
            "--project-name",
            project_name,
            "--cortex-root",
            cortex_root,
        ]
        assets_dir = str(parsed.assets_dir).strip()
        if assets_dir:
            init_cmd.extend(["--assets-dir", assets_dir])
        if force:
            init_cmd.append("--force")

        proc = subprocess.run(init_cmd, check=False, text=True, capture_output=True)
        init_result = {
            "performed": True,
            "returncode": proc.returncode,
            "stdout": proc.stdout.rstrip("\n"),
            "stderr": proc.stderr.rstrip("\n"),
            "command": init_cmd,
        }
        if proc.returncode != 0:
            payload = {
                "version": "v0",
                "command": subcommand,
                "status": "fail",
                "returncode": 3,
                "run_at": _now_iso(),
                "project_dir": str(project_dir),
                "format_source": "delegator_bootstrap_scaffolder_v0",
                "message": "bootstrap init command failed.",
                "result": {
                    "init": init_result,
                },
            }
            _emit_bootstrap_payload(payload, output_format)
            return 3

    required_paths = _bootstrap_required_paths(project_dir, cortex_root)
    missing_required: list[str] = []
    for rel in required_paths:
        path = project_dir / rel
        if not path.exists():
            missing_required.append(rel)

    created_or_updated_paths: list[str] = []
    skipped_paths: list[str] = []
    portability_bundle_created: list[str] = []
    portability_bundle_skipped: list[str] = []
    portability_bundle_fallback_used: list[str] = []
    portability_bundle_missing: list[str] = []
    if not missing_required:
        (
            portability_bundle_created,
            portability_bundle_skipped,
            portability_bundle_fallback_used,
            portability_bundle_missing,
        ) = _seed_bootstrap_portability_bundle(
            project_dir=project_dir,
            cortex_root=cortex_root,
            project_id=project_id,
            project_name=project_name,
            force=force,
        )
        created_or_updated_paths.extend(portability_bundle_created)
        skipped_paths.extend(portability_bundle_skipped)

    checklist_path = project_dir / cortex_root / "templates" / "bootstrap_first_green_gate_checklist_v0.md"
    checklist_text = _render_bootstrap_checklist(_load_bootstrap_template(), project_id, project_name)
    if checklist_path.exists() and not force:
        skipped_paths.append(_safe_rel_path(project_dir, checklist_path))
    else:
        checklist_path.parent.mkdir(parents=True, exist_ok=True)
        checklist_path.write_text(checklist_text, encoding="utf-8")
        created_or_updated_paths.append(_safe_rel_path(project_dir, checklist_path))

    first_green_gate_commands = [
        "cortex-coach audit-needed --project-dir . --format json",
        "cortex-coach coach --project-dir .",
        "cortex-coach audit --project-dir .",
        "./scripts/quality_gate_ci_v0.sh",
    ]

    report_path = project_dir / cortex_root / "reports" / "project_state" / "phase6_bootstrap_scaffold_report_v0.json"
    status = "pass" if not missing_required and not portability_bundle_missing else "fail"
    report_payload = {
        "artifact": "phase6_bootstrap_scaffold_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "project_id": project_id,
        "project_name": project_name,
        "cortex_root": cortex_root,
        "measurement_mode": "phase6_bootstrap_scaffolder_v0",
        "required_paths": required_paths,
        "missing_required_paths": missing_required,
        "init": {
            "performed": bool(init_result.get("performed", False)),
            "returncode": int(init_result.get("returncode", 0)),
        },
        "portability_bundle": {
            "seed_paths": [_bootstrap_rel_path(rel, cortex_root) for rel in BOOTSTRAP_PORTABILITY_SEED_PATHS],
            "created_or_updated_paths": portability_bundle_created,
            "skipped_paths": portability_bundle_skipped,
            "fallback_used_paths": portability_bundle_fallback_used,
            "missing_paths": portability_bundle_missing,
        },
        "first_green_gate_commands": first_green_gate_commands,
        "bootstrap_assets": {
            "checklist_path": _safe_rel_path(project_dir, checklist_path),
        },
        "status": status,
    }
    _write_json_file(report_path, report_payload)
    created_or_updated_paths.append(_safe_rel_path(project_dir, report_path))

    returncode = 0 if status == "pass" else 3
    if status == "pass":
        message = "bootstrap scaffold complete"
    elif missing_required:
        message = "required bootstrap artifacts missing; run without --skip-init or fix init outputs."
    else:
        message = "bootstrap portability bundle incomplete; verify governance seed templates."

    payload = {
        "version": "v0",
        "command": subcommand,
        "status": status,
        "returncode": returncode,
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "format_source": "delegator_bootstrap_scaffolder_v0",
        "message": message,
        "result": {
            "required_paths": required_paths,
            "missing_required_paths": missing_required,
            "created_or_updated_paths": created_or_updated_paths,
            "skipped_paths": skipped_paths,
            "portability_bundle": report_payload["portability_bundle"],
            "report_path": _safe_rel_path(project_dir, report_path),
            "checklist_path": _safe_rel_path(project_dir, checklist_path),
            "first_green_gate_commands": first_green_gate_commands,
            "init": init_result,
        },
    }
    _emit_bootstrap_payload(payload, output_format)
    return returncode


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
    if subcommand in {"rollout-mode", "rollout-mode-audit", "bootstrap-scaffold"}:
        try:
            idx = argv.index(subcommand)
        except ValueError:
            idx = 0
        command_argv = argv[idx:]
        if subcommand == "rollout-mode":
            return _run_rollout_mode_command(command_argv)
        if subcommand == "rollout-mode-audit":
            return _run_rollout_mode_audit_command(command_argv)
        coach_bin_for_bootstrap = shutil.which("cortex-coach")
        return _run_bootstrap_scaffold_command(command_argv, coach_bin_for_bootstrap)

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

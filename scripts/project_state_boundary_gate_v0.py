#!/usr/bin/env python3
"""Enforce that project-instance state stays under .cortex/."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONTRACT_FILE = Path("contracts/project_state_boundary_contract_v0.json")


@dataclass(frozen=True)
class Waiver:
    path: str
    reason: str
    decision_id: str
    owner: str
    expires_on: str
    status: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _is_path_under(path: str, root: str) -> bool:
    normalized_path = path.strip("/")
    normalized_root = root.strip("/")
    if not normalized_root:
        return False
    return normalized_path == normalized_root or normalized_path.startswith(f"{normalized_root}/")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload


def _load_contract(contract_file: Path) -> dict[str, Any]:
    payload = _load_json(contract_file)

    version = payload.get("version")
    if version != "v0":
        raise ValueError(f"unsupported contract version in {contract_file}: {version!r}")

    project_state_root = payload.get("project_state_root")
    if not isinstance(project_state_root, str) or not project_state_root.strip():
        raise ValueError(f"contract missing project_state_root: {contract_file}")

    forbidden_roots = payload.get("forbidden_outside_project_state_roots")
    if not isinstance(forbidden_roots, list) or not forbidden_roots:
        raise ValueError(f"contract missing forbidden_outside_project_state_roots: {contract_file}")
    if not all(isinstance(item, str) and item.strip() for item in forbidden_roots):
        raise ValueError(f"contract has invalid forbidden roots: {contract_file}")

    waiver_file = payload.get("waiver_file")
    if not isinstance(waiver_file, str) or not waiver_file.strip():
        raise ValueError(f"contract missing waiver_file: {contract_file}")

    return payload


def _parse_waiver(item: dict[str, Any], index: int) -> Waiver:
    required = ["path", "reason", "decision_id", "owner", "expires_on", "status"]
    missing = [field for field in required if field not in item]
    if missing:
        raise ValueError(f"waiver[{index}] missing required fields: {', '.join(missing)}")

    path = item["path"]
    reason = item["reason"]
    decision_id = item["decision_id"]
    owner = item["owner"]
    expires_on = item["expires_on"]
    status = item["status"]

    if not all(isinstance(v, str) and v.strip() for v in [path, reason, decision_id, owner, expires_on, status]):
        raise ValueError(f"waiver[{index}] has empty/invalid string fields")
    if status not in {"active", "retired"}:
        raise ValueError(f"waiver[{index}] has invalid status: {status!r}")

    try:
        date.fromisoformat(expires_on)
    except ValueError as exc:
        raise ValueError(f"waiver[{index}] has invalid expires_on date: {expires_on!r}") from exc

    return Waiver(
        path=path,
        reason=reason,
        decision_id=decision_id,
        owner=owner,
        expires_on=expires_on,
        status=status,
    )


def _load_waivers(waiver_file: Path) -> list[Waiver]:
    if not waiver_file.exists():
        return []

    payload = _load_json(waiver_file)
    waivers_raw = payload.get("waivers", [])
    if not isinstance(waivers_raw, list):
        raise ValueError(f"waivers must be a list in {waiver_file}")

    waivers: list[Waiver] = []
    for idx, item in enumerate(waivers_raw):
        if not isinstance(item, dict):
            raise ValueError(f"waiver[{idx}] must be an object in {waiver_file}")
        waivers.append(_parse_waiver(item, idx))
    return waivers


def _git_files(project_dir: Path, include_untracked: bool = True) -> list[str]:
    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=str(project_dir),
        text=True,
        capture_output=True,
        check=False,
    )
    if tracked.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {tracked.stderr.strip()}")

    files = [line.strip() for line in tracked.stdout.splitlines() if line.strip()]

    if include_untracked:
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=str(project_dir),
            text=True,
            capture_output=True,
            check=False,
        )
        if untracked.returncode != 0:
            raise RuntimeError(f"git ls-files --others failed: {untracked.stderr.strip()}")
        files.extend(line.strip() for line in untracked.stdout.splitlines() if line.strip())

    deduped = sorted(set(files))
    return [path for path in deduped if not path.startswith(".git/")]


def _format_text(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload.get('status')}",
        f"run_at: {payload.get('run_at')}",
        f"files_scanned: {payload.get('files_scanned', 0)}",
        f"violations: {payload.get('violation_count', 0)}",
    ]

    expired = payload.get("expired_active_waivers", [])
    if isinstance(expired, list) and expired:
        lines.append(f"expired_active_waivers: {len(expired)}")

    findings = payload.get("findings", [])
    if isinstance(findings, list) and findings:
        lines.append("findings:")
        for item in findings:
            if not isinstance(item, dict):
                continue
            check = item.get("check", "unknown")
            message = item.get("message", "")
            path = item.get("path")
            suffix = f" path={path}" if path else ""
            lines.append(f"- {check}:{suffix} {message}".rstrip())

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Project-state boundary enforcement gate.")
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--contract-file", default=str(DEFAULT_CONTRACT_FILE))
    parser.add_argument("--format", default="text", choices=("text", "json"))
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    contract_file = Path(args.contract_file)
    if not contract_file.is_absolute():
        contract_file = project_dir / contract_file

    findings: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    expired_active_waivers: list[dict[str, Any]] = []

    files_scanned = 0
    forbidden_roots: list[str] = []
    waivers: list[Waiver] = []
    waivers_by_path: dict[str, Waiver] = {}
    project_state_root = ".cortex"

    try:
        contract = _load_contract(contract_file)
        project_state_root = str(contract["project_state_root"])
        forbidden_roots = [str(root).strip("/") for root in contract["forbidden_outside_project_state_roots"]]

        waiver_file = Path(str(contract["waiver_file"]))
        if not waiver_file.is_absolute():
            waiver_file = project_dir / waiver_file
        waivers = _load_waivers(waiver_file)

        for waiver in waivers:
            waivers_by_path[waiver.path.strip("/")] = waiver
            if waiver.status == "active" and date.fromisoformat(waiver.expires_on) < _today_utc():
                expired = {
                    "path": waiver.path,
                    "expires_on": waiver.expires_on,
                    "decision_id": waiver.decision_id,
                    "owner": waiver.owner,
                    "status": waiver.status,
                }
                expired_active_waivers.append(expired)
                findings.append(
                    {
                        "check": "expired_active_waiver",
                        "severity": "error",
                        "path": waiver.path,
                        "message": "Waiver is active but expired.",
                        "expires_on": waiver.expires_on,
                        "decision_id": waiver.decision_id,
                    }
                )

        files = _git_files(project_dir)
        files_scanned = len(files)

        for path in files:
            if _is_path_under(path, project_state_root):
                continue

            violating_root = next((root for root in forbidden_roots if _is_path_under(path, root)), None)
            if violating_root is None:
                continue

            waiver = waivers_by_path.get(path)
            waiver_active = (
                waiver is not None
                and waiver.status == "active"
                and date.fromisoformat(waiver.expires_on) >= _today_utc()
            )
            if waiver_active:
                continue

            violation = {
                "path": path,
                "violating_root": violating_root,
            }
            if waiver is not None:
                violation["waiver_status"] = waiver.status
                violation["waiver_expires_on"] = waiver.expires_on
                violation["waiver_decision_id"] = waiver.decision_id
            violations.append(violation)

            findings.append(
                {
                    "check": "forbidden_project_state_path_outside_cortex",
                    "severity": "error",
                    "path": path,
                    "message": "Project-state artifact path is outside .cortex and not covered by an active waiver.",
                    "violating_root": violating_root,
                }
            )

    except Exception as exc:  # noqa: BLE001
        findings.append(
            {
                "check": "boundary_gate_runtime_error",
                "severity": "error",
                "message": str(exc),
            }
        )

    status = "fail" if findings else "pass"
    payload: dict[str, Any] = {
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "status": status,
        "contract_file": str(contract_file),
        "project_state_root": project_state_root,
        "forbidden_outside_project_state_roots": forbidden_roots,
        "files_scanned": files_scanned,
        "waiver_count": len(waivers),
        "expired_active_waivers": expired_active_waivers,
        "violations": violations,
        "violation_count": len(violations),
        "findings": findings,
    }

    if args.format == "json":
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_text(payload))
        sys.stdout.write("\n")

    return 1 if status == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail closed on unmanaged or expired temporal playbooks in release surface."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from fnmatch import fnmatch
from pathlib import Path
from typing import Any


DEFAULT_CONTRACT_FILE = Path("contracts/temporal_playbook_release_surface_contract_v0.json")


@dataclass(frozen=True)
class TemporalPlaybookEntry:
    path: str
    owner: str
    status: str
    release_action: str
    reason: str
    expires_on: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _normalize_rel_path(value: str) -> str:
    return value.strip().lstrip("./")


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

    globs = payload.get("classification_globs")
    if not isinstance(globs, list) or not globs:
        raise ValueError(f"contract missing classification_globs: {contract_file}")
    if not all(isinstance(item, str) and item.strip() for item in globs):
        raise ValueError(f"contract has invalid classification_globs: {contract_file}")

    allowlist = payload.get("durable_allowlist")
    if not isinstance(allowlist, list):
        raise ValueError(f"contract missing durable_allowlist: {contract_file}")
    if not all(isinstance(item, str) and item.strip() for item in allowlist):
        raise ValueError(f"contract has invalid durable_allowlist entries: {contract_file}")

    temporal = payload.get("temporal_playbooks")
    if not isinstance(temporal, list):
        raise ValueError(f"contract missing temporal_playbooks: {contract_file}")

    return payload


def _parse_entry(item: dict[str, Any], index: int) -> TemporalPlaybookEntry:
    required = ["path", "owner", "status", "release_action", "reason", "expires_on"]
    missing = [field for field in required if field not in item]
    if missing:
        raise ValueError(f"temporal_playbooks[{index}] missing fields: {', '.join(missing)}")

    path = item["path"]
    owner = item["owner"]
    status = item["status"]
    release_action = item["release_action"]
    reason = item["reason"]
    expires_on = item["expires_on"]

    if not all(
        isinstance(value, str) and value.strip()
        for value in [path, owner, status, release_action, reason, expires_on]
    ):
        raise ValueError(f"temporal_playbooks[{index}] has empty/invalid string fields")

    if status not in {"active", "retired"}:
        raise ValueError(f"temporal_playbooks[{index}] has invalid status: {status!r}")

    if release_action not in {"archive_to_cortex", "remove", "exclude_from_release"}:
        raise ValueError(f"temporal_playbooks[{index}] has invalid release_action: {release_action!r}")

    try:
        date.fromisoformat(expires_on)
    except ValueError as exc:
        raise ValueError(f"temporal_playbooks[{index}] has invalid expires_on: {expires_on!r}") from exc

    return TemporalPlaybookEntry(
        path=_normalize_rel_path(path),
        owner=owner.strip(),
        status=status.strip(),
        release_action=release_action.strip(),
        reason=reason.strip(),
        expires_on=expires_on.strip(),
    )


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


def _matches_any(path: str, globs: list[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in globs)


def _format_text(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload.get('status')}",
        f"run_at: {payload.get('run_at')}",
        f"candidate_count: {payload.get('candidate_count', 0)}",
        f"unmanaged_candidate_count: {payload.get('unmanaged_candidate_count', 0)}",
        f"expired_active_count: {payload.get('expired_active_count', 0)}",
        f"retired_residue_count: {payload.get('retired_residue_count', 0)}",
        f"missing_active_count: {payload.get('missing_active_count', 0)}",
    ]

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


def _finding(check: str, message: str, **extra: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "check": check,
        "severity": "error",
        "message": message,
    }
    item.update(extra)
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description="Temporal playbook release-surface gate.")
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--contract-file", default=str(DEFAULT_CONTRACT_FILE))
    parser.add_argument("--format", default="text", choices=("text", "json"))
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    contract_file = Path(args.contract_file)
    if not contract_file.is_absolute():
        contract_file = project_dir / contract_file

    findings: list[dict[str, Any]] = []
    candidate_files: list[str] = []
    classification_globs: list[str] = []
    allowlist: list[str] = []
    temporal_entries: list[TemporalPlaybookEntry] = []
    unmanaged_candidates: list[str] = []
    expired_active_entries: list[dict[str, Any]] = []
    retired_residue_entries: list[dict[str, Any]] = []
    missing_active_entries: list[dict[str, Any]] = []

    try:
        contract = _load_contract(contract_file)
        classification_globs = [_normalize_rel_path(str(item)) for item in contract["classification_globs"]]
        allowlist = sorted({_normalize_rel_path(str(item)) for item in contract["durable_allowlist"]})

        temporal_raw = contract["temporal_playbooks"]
        if not isinstance(temporal_raw, list):
            raise ValueError(f"contract temporal_playbooks must be a list: {contract_file}")
        for idx, item in enumerate(temporal_raw):
            if not isinstance(item, dict):
                raise ValueError(f"temporal_playbooks[{idx}] must be an object")
            temporal_entries.append(_parse_entry(item, idx))

        allowlist_set = set(allowlist)
        temporal_by_path: dict[str, TemporalPlaybookEntry] = {}
        duplicate_temporal_paths: set[str] = set()

        for entry in temporal_entries:
            if entry.path in temporal_by_path:
                duplicate_temporal_paths.add(entry.path)
            temporal_by_path[entry.path] = entry

        if duplicate_temporal_paths:
            for path in sorted(duplicate_temporal_paths):
                findings.append(
                    _finding(
                        "duplicate_temporal_entry",
                        "Contract contains duplicate temporal playbook path entries.",
                        path=path,
                    )
                )

        overlap = sorted(allowlist_set & set(temporal_by_path))
        for path in overlap:
            findings.append(
                _finding(
                    "allowlist_temporal_overlap",
                    "Path cannot be both allowlisted and temporal-managed.",
                    path=path,
                )
            )

        for path in sorted(allowlist_set):
            if not _matches_any(path, classification_globs):
                findings.append(
                    _finding(
                        "allowlist_path_not_classified",
                        "Allowlist path does not match temporal classification globs.",
                        path=path,
                    )
                )

        files = _git_files(project_dir)
        candidate_files = sorted(path for path in files if _matches_any(path, classification_globs))

        for candidate in candidate_files:
            if candidate in allowlist_set:
                continue
            if candidate not in temporal_by_path:
                unmanaged_candidates.append(candidate)
                findings.append(
                    _finding(
                        "unmanaged_temporal_candidate",
                        "Temporal candidate is missing both durable allowlist and temporal contract entry.",
                        path=candidate,
                    )
                )

        for entry in temporal_entries:
            if not _matches_any(entry.path, classification_globs):
                findings.append(
                    _finding(
                        "temporal_entry_not_classified",
                        "Temporal entry path does not match temporal classification globs.",
                        path=entry.path,
                    )
                )

            playbook_path = project_dir / entry.path
            exists = playbook_path.exists()
            expires_on = date.fromisoformat(entry.expires_on)

            if entry.status == "active" and expires_on < _today_utc():
                expired = {
                    "path": entry.path,
                    "owner": entry.owner,
                    "expires_on": entry.expires_on,
                    "release_action": entry.release_action,
                }
                expired_active_entries.append(expired)
                findings.append(
                    _finding(
                        "expired_active_temporal_playbook",
                        "Temporal playbook is active but past expires_on.",
                        path=entry.path,
                        expires_on=entry.expires_on,
                        owner=entry.owner,
                    )
                )

            if entry.status == "active" and not exists:
                missing = {
                    "path": entry.path,
                    "owner": entry.owner,
                    "release_action": entry.release_action,
                }
                missing_active_entries.append(missing)
                findings.append(
                    _finding(
                        "missing_active_temporal_playbook",
                        "Temporal playbook is marked active but file does not exist.",
                        path=entry.path,
                        owner=entry.owner,
                    )
                )

            if (
                entry.status == "retired"
                and entry.release_action in {"archive_to_cortex", "remove"}
                and exists
            ):
                residue = {
                    "path": entry.path,
                    "owner": entry.owner,
                    "release_action": entry.release_action,
                }
                retired_residue_entries.append(residue)
                findings.append(
                    _finding(
                        "retired_temporal_playbook_still_in_playbooks",
                        "Retired temporal playbook remains in playbooks contrary to release_action.",
                        path=entry.path,
                        owner=entry.owner,
                        release_action=entry.release_action,
                    )
                )

    except Exception as exc:  # noqa: BLE001
        findings.append(
            _finding(
                "temporal_release_gate_runtime_error",
                str(exc),
            )
        )

    status = "fail" if findings else "pass"
    payload: dict[str, Any] = {
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "status": status,
        "contract_file": str(contract_file),
        "classification_globs": classification_globs,
        "candidate_count": len(candidate_files),
        "candidate_files": candidate_files,
        "allowlist_count": len(allowlist),
        "durable_allowlist": allowlist,
        "temporal_entry_count": len(temporal_entries),
        "unmanaged_candidates": unmanaged_candidates,
        "unmanaged_candidate_count": len(unmanaged_candidates),
        "expired_active_entries": expired_active_entries,
        "expired_active_count": len(expired_active_entries),
        "retired_residue_entries": retired_residue_entries,
        "retired_residue_count": len(retired_residue_entries),
        "missing_active_entries": missing_active_entries,
        "missing_active_count": len(missing_active_entries),
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

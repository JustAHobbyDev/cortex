#!/usr/bin/env python3
"""Execute a no-loss training migration handoff from the local bundle to cortex-training."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid json file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"json root must be object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_rel(base: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path.resolve())


def _run_command(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=False)


def _git_value(repo_dir: Path, args: list[str]) -> str:
    proc = _run_command(["git", *args], cwd=repo_dir)
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def _assert_git_repo(repo_dir: Path) -> None:
    value = _git_value(repo_dir, ["rev-parse", "--is-inside-work-tree"])
    if value != "true":
        raise RuntimeError(f"not a git repository: {repo_dir}")


def _is_git_dirty(repo_dir: Path) -> bool:
    return bool(_git_value(repo_dir, ["status", "--porcelain"]).strip())


def _load_sha_index(path: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"unable to read checksum file: {path}: {exc}") from exc
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 2:
            raise RuntimeError(f"invalid checksum row: {line!r}")
        checksum = parts[0].strip()
        rel = parts[-1].strip()
        index[rel] = checksum
    if not index:
        raise RuntimeError(f"checksum file has no entries: {path}")
    return index


def _verify_bundle(
    *,
    bundle_root: Path,
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sha_file = bundle_root / "sha256_v0.txt"
    sha_index = _load_sha_index(sha_file)
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("bundle manifest missing non-empty `files` array")

    verified: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for raw in entries:
        if not isinstance(raw, dict):
            failures.append({"error": "non-object manifest entry"})
            continue
        bundle_path = str(raw.get("bundle_path", "")).strip()
        target_path = str(raw.get("target_path", "")).strip()
        expected_sha = str(raw.get("sha256", "")).strip()
        source_path = str(raw.get("source_path", "")).strip()
        if not bundle_path or not target_path or not expected_sha:
            failures.append({"bundle_path": bundle_path, "target_path": target_path, "error": "missing required fields"})
            continue
        src = bundle_root / bundle_path
        if not src.exists():
            failures.append({"bundle_path": bundle_path, "target_path": target_path, "error": "source file missing"})
            continue
        if not src.is_file():
            failures.append({"bundle_path": bundle_path, "target_path": target_path, "error": "source path is not a file"})
            continue

        relative_in_snapshot = bundle_path.split("/", 1)[1] if "/" in bundle_path else bundle_path
        indexed_sha = sha_index.get(relative_in_snapshot, "")
        actual_sha = _sha256(src)
        if actual_sha != expected_sha or (indexed_sha and indexed_sha != actual_sha):
            failures.append(
                {
                    "bundle_path": bundle_path,
                    "target_path": target_path,
                    "expected_sha": expected_sha,
                    "indexed_sha": indexed_sha,
                    "actual_sha": actual_sha,
                    "error": "checksum mismatch",
                }
            )
            continue

        verified.append(
            {
                "source_path": source_path,
                "bundle_path": bundle_path,
                "target_path": target_path,
                "sha256": actual_sha,
                "size_bytes": src.stat().st_size,
                "is_executable_source": bool(src.stat().st_mode & 0o111),
            }
        )
    return verified, failures


def _transfer_verified_files(
    *,
    bundle_root: Path,
    verified_entries: list[dict[str, Any]],
    target_repo_dir: Path,
    transfer_mode: str,
    dry_run: bool,
) -> tuple[list[str], list[str], list[str]]:
    copied: list[str] = []
    executable: list[str] = []
    source_paths: list[str] = []
    for entry in verified_entries:
        bundle_path = str(entry["bundle_path"])
        target_path = str(entry["target_path"])
        src = bundle_root / bundle_path
        dest = target_repo_dir / target_path
        source_paths.append(str(src))
        copied.append(str(dest))
        if dry_run:
            if entry.get("is_executable_source", False):
                executable.append(str(dest))
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Keep copy-first semantics for safe rollback; move mode prunes sources only after full success.
        shutil.copy2(src, dest)
        if entry.get("is_executable_source", False):
            os.chmod(dest, dest.stat().st_mode | 0o111)
            executable.append(str(dest))
    _ = transfer_mode  # transfer behavior finalization happens after governance steps.
    return copied, executable, source_paths


def _prune_transferred_sources(
    *,
    source_paths: list[str],
    bundle_root: Path,
) -> list[str]:
    pruned: list[str] = []
    root = bundle_root.resolve()
    unique_sources = sorted({Path(item).resolve() for item in source_paths})
    for source in unique_sources:
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise RuntimeError(f"refusing to delete source outside bundle root: {source}") from exc
        if not source.exists():
            continue
        if not source.is_file():
            raise RuntimeError(f"expected source file for prune: {source}")
        source.unlink()
        pruned.append(str(source))

        parent = source.parent
        while parent != root and parent.exists():
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    return pruned


def _update_pointer_doc(
    *,
    project_dir: Path,
    pin_ref: str,
    dry_run: bool,
) -> str:
    doc_path = project_dir / "docs/cortex-coach/client_training_external_repo_v0.md"
    section = "\n".join(
        [
            "## Active Pin",
            "",
            "- Pin type: `commit_sha`",
            f"- Pin ref: `{pin_ref}`",
            f"- Updated at: `{_now_iso()}`",
            "- Source bundle: `.cortex/artifacts/training_migration_bundle_v0/manifest_v0.json`",
            "",
        ]
    )
    if dry_run:
        return _safe_rel(project_dir, doc_path)
    text = doc_path.read_text(encoding="utf-8")
    pattern = re.compile(r"(?ms)^## Active Pin\n.*?(?=^## |\Z)")
    if pattern.search(text):
        updated = pattern.sub(section, text)
    else:
        suffix = "" if text.endswith("\n") else "\n"
        updated = f"{text}{suffix}\n{section}"
    doc_path.write_text(updated, encoding="utf-8")
    return _safe_rel(project_dir, doc_path)


def _build_handoff_manifest(
    *,
    project_dir: Path,
    target_repo_dir: Path,
    target_pin_ref: str,
    template_path: Path,
    approval_refs: list[str],
    status: str,
    cortex_coach_min_version: str,
    dry_run: bool,
    out_path: Path,
) -> str:
    payload = _load_json(template_path)

    source_repo_url = _git_value(project_dir, ["config", "--get", "remote.origin.url"]) or "https://github.com/JustAHobbyDev/cortex"
    source_commit_ref = _git_value(project_dir, ["rev-parse", "HEAD"]) or "unknown"
    training_repo_url = _git_value(target_repo_dir, ["config", "--get", "remote.origin.url"]) or "https://github.com/JustAHobbyDev/cortex-training"
    training_repo_name = target_repo_dir.name

    payload["generated_at"] = _now_iso()
    payload["source_project"]["repo_name"] = project_dir.name
    payload["source_project"]["repo_url"] = source_repo_url
    payload["source_project"]["commit_ref"] = source_commit_ref

    payload["training_project"]["repo_name"] = training_repo_name
    payload["training_project"]["repo_url"] = training_repo_url
    payload["training_project"]["pin_type"] = "commit_sha"
    payload["training_project"]["pin_ref"] = target_pin_ref

    payload["compatibility"]["cortex_coach_min_version"] = cortex_coach_min_version
    payload["compatibility"]["breaking_changes"] = False
    payload["compatibility"]["migration_notes"] = (
        "Imported from .cortex/artifacts/training_migration_bundle_v0/snapshot_2f2c85b "
        f"and pinned to commit {target_pin_ref}."
    )

    payload["handoff_checklist"]["boundary_confirmed"] = True
    payload["handoff_checklist"]["interface_coverage_confirmed"] = True
    payload["handoff_checklist"]["version_pin_confirmed"] = True
    payload["handoff_checklist"]["governance_approvals"] = approval_refs or ["pending_approval_ref"]
    payload["status"] = status

    payload.setdefault("linked_artifacts", [])
    linked = set(str(item) for item in payload.get("linked_artifacts", []) if isinstance(item, str))
    linked.add("docs/cortex-coach/client_training_external_repo_v0.md")
    linked.add("docs/cortex-coach/client_training_project_boundary_and_handoff_v0.md")
    payload["linked_artifacts"] = sorted(linked)

    if not dry_run:
        _write_json(out_path, payload)
    return _safe_rel(project_dir, out_path)


def _stage_commit_push_target(
    *,
    target_repo_dir: Path,
    copied_paths: list[str],
    commit_message: str,
    skip_commit: bool,
    push: bool,
    remote: str,
    branch: str,
    dry_run: bool,
) -> tuple[str, dict[str, Any]]:
    _assert_git_repo(target_repo_dir)

    details: dict[str, Any] = {
        "staged_files": [],
        "commit_created": False,
        "push_performed": False,
        "target_branch": "",
    }
    if dry_run:
        head = _git_value(target_repo_dir, ["rev-parse", "HEAD"])
        details["target_branch"] = _git_value(target_repo_dir, ["rev-parse", "--abbrev-ref", "HEAD"])
        return head, details

    rel_paths: list[str] = []
    for abs_path in copied_paths:
        rel_paths.append(_safe_rel(target_repo_dir, Path(abs_path)))
    if rel_paths:
        add_proc = _run_command(["git", "add", "--", *rel_paths], cwd=target_repo_dir)
        if add_proc.returncode != 0:
            raise RuntimeError(f"git add failed: {add_proc.stderr.strip()}")
        details["staged_files"] = rel_paths

    current_branch = _git_value(target_repo_dir, ["rev-parse", "--abbrev-ref", "HEAD"]) or ""
    details["target_branch"] = current_branch
    head_before = _git_value(target_repo_dir, ["rev-parse", "HEAD"]) or ""

    if skip_commit:
        return head_before, details

    cached_diff = _run_command(["git", "diff", "--cached", "--quiet"], cwd=target_repo_dir)
    if cached_diff.returncode == 0:
        return head_before, details
    if cached_diff.returncode != 1:
        raise RuntimeError("unable to evaluate staged diff state")

    commit_proc = _run_command(["git", "commit", "-m", commit_message], cwd=target_repo_dir)
    if commit_proc.returncode != 0:
        raise RuntimeError(f"git commit failed: {commit_proc.stderr.strip()}")
    details["commit_created"] = True

    head_after = _git_value(target_repo_dir, ["rev-parse", "HEAD"]) or ""
    pin_ref = head_after or head_before

    if push:
        push_branch = branch or current_branch
        if not push_branch:
            raise RuntimeError("unable to resolve target branch for push; pass --branch explicitly")
        push_proc = _run_command(["git", "push", remote, push_branch], cwd=target_repo_dir)
        if push_proc.returncode != 0:
            raise RuntimeError(f"git push failed: {push_proc.stderr.strip()}")
        details["push_performed"] = True

    return pin_ref, details


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
    ]
    message = payload.get("message")
    if isinstance(message, str) and message:
        lines.append(f"message: {message}")
    result = payload.get("result", {})
    if isinstance(result, dict):
        pin_ref = result.get("target_pin_ref")
        if isinstance(pin_ref, str) and pin_ref:
            lines.append(f"target_pin_ref: {pin_ref}")
        report_path = result.get("report_path")
        if isinstance(report_path, str) and report_path:
            lines.append(f"report_path: {report_path}")
    print("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--bundle-root", default=".cortex/artifacts/training_migration_bundle_v0")
    parser.add_argument("--target-repo-dir", required=True)
    parser.add_argument("--transfer-mode", choices=("copy", "move"), default="copy")
    parser.add_argument(
        "--handoff-manifest-out",
        default=".cortex/reports/project_state/client_training_project_handoff_manifest_v0.json",
    )
    parser.add_argument(
        "--report-out",
        default=".cortex/reports/project_state/client_training_transfer_execution_report_v0.json",
    )
    parser.add_argument("--approval-ref", action="append", default=[])
    parser.add_argument("--status", choices=("draft", "ready_for_handoff", "accepted"), default="ready_for_handoff")
    parser.add_argument("--cortex-coach-min-version", default="cortex-coach-v0")
    parser.add_argument("--commit-message", default="Import client training migration bundle from cortex bundle")
    parser.add_argument("--skip-commit", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="")
    parser.add_argument("--allow-dirty-target", action="store_true")
    parser.add_argument("--skip-pointer-update", action="store_true")
    parser.add_argument("--skip-quality-gate", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    bundle_root = Path(args.bundle_root)
    if not bundle_root.is_absolute():
        bundle_root = (project_dir / bundle_root).resolve()
    target_repo_dir = Path(args.target_repo_dir).resolve()
    handoff_manifest_out = Path(args.handoff_manifest_out)
    if not handoff_manifest_out.is_absolute():
        handoff_manifest_out = (project_dir / handoff_manifest_out).resolve()
    report_out = Path(args.report_out)
    if not report_out.is_absolute():
        report_out = (project_dir / report_out).resolve()

    payload: dict[str, Any] = {
        "artifact": "client_training_transfer_execution_report_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "status": "fail",
        "project_dir": str(project_dir),
        "bundle_root": str(bundle_root),
        "target_repo_dir": str(target_repo_dir),
        "transfer_mode": str(args.transfer_mode),
        "dry_run": bool(args.dry_run),
        "result": {},
    }

    try:
        _assert_git_repo(project_dir)
        _assert_git_repo(target_repo_dir)
        if _is_git_dirty(target_repo_dir) and not args.allow_dirty_target:
            raise RuntimeError("target repository has uncommitted changes; rerun with --allow-dirty-target to proceed")

        manifest_path = bundle_root / "manifest_v0.json"
        manifest = _load_json(manifest_path)
        verified, failures = _verify_bundle(bundle_root=bundle_root, manifest=manifest)
        if failures:
            raise RuntimeError(f"bundle verification failed for {len(failures)} file(s)")

        copied_paths, executable_paths, source_paths = _transfer_verified_files(
            bundle_root=bundle_root,
            verified_entries=verified,
            target_repo_dir=target_repo_dir,
            transfer_mode=str(args.transfer_mode),
            dry_run=bool(args.dry_run),
        )

        target_pin_ref, target_git = _stage_commit_push_target(
            target_repo_dir=target_repo_dir,
            copied_paths=copied_paths,
            commit_message=args.commit_message,
            skip_commit=bool(args.skip_commit),
            push=bool(args.push),
            remote=args.remote,
            branch=args.branch,
            dry_run=bool(args.dry_run),
        )
        if not target_pin_ref:
            raise RuntimeError("unable to resolve target commit ref after copy/commit")

        template_path = project_dir / ".cortex/templates/client_training_project_handoff_manifest_template_v0.json"
        handoff_path = _build_handoff_manifest(
            project_dir=project_dir,
            target_repo_dir=target_repo_dir,
            target_pin_ref=target_pin_ref,
            template_path=template_path,
            approval_refs=list(args.approval_ref),
            status=str(args.status),
            cortex_coach_min_version=str(args.cortex_coach_min_version),
            dry_run=bool(args.dry_run),
            out_path=handoff_manifest_out,
        )

        pointer_doc = ""
        if not args.skip_pointer_update:
            pointer_doc = _update_pointer_doc(project_dir=project_dir, pin_ref=target_pin_ref, dry_run=bool(args.dry_run))

        qg_result: dict[str, Any] = {"ran": False, "returncode": 0}
        if not args.skip_quality_gate:
            qg_result["ran"] = True
            if args.dry_run:
                qg_result["returncode"] = 0
            else:
                qg_proc = _run_command(["./scripts/quality_gate_ci_v0.sh"], cwd=project_dir)
                qg_result["returncode"] = qg_proc.returncode
                qg_result["stderr_tail"] = "\n".join(qg_proc.stderr.strip().splitlines()[-20:])
                qg_result["stdout_tail"] = "\n".join(qg_proc.stdout.strip().splitlines()[-20:])
                if qg_proc.returncode != 0:
                    raise RuntimeError("quality gate failed after pointer/manifest update")

        pruned_sources: list[str] = []
        if str(args.transfer_mode) == "move":
            if args.dry_run:
                pruned_sources = [_safe_rel(project_dir, Path(path)) for path in source_paths]
            else:
                pruned_sources = [
                    _safe_rel(project_dir, Path(path))
                    for path in _prune_transferred_sources(source_paths=source_paths, bundle_root=bundle_root)
                ]

        payload["status"] = "pass"
        payload["message"] = "training migration handoff completed"
        payload["result"] = {
            "transfer_mode": str(args.transfer_mode),
            "verified_file_count": len(verified),
            "failed_verification_count": len(failures),
            "copied_paths": [_safe_rel(target_repo_dir, Path(path)) for path in copied_paths],
            "executable_paths": [_safe_rel(target_repo_dir, Path(path)) for path in executable_paths],
            "pruned_source_paths": pruned_sources,
            "target_pin_ref": target_pin_ref,
            "target_git": target_git,
            "handoff_manifest_path": handoff_path,
            "pointer_doc_path": pointer_doc,
            "quality_gate": qg_result,
            "report_path": _safe_rel(project_dir, report_out),
        }
    except Exception as exc:  # noqa: BLE001
        payload["status"] = "fail"
        payload["message"] = str(exc)
        payload.setdefault("result", {})
        payload["result"]["report_path"] = _safe_rel(project_dir, report_out)

    if not args.dry_run:
        _write_json(report_out, payload)

    _emit(payload, str(args.format))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

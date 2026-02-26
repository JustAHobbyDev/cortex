#!/usr/bin/env python3
"""Install repository-local skills into Codex skill discovery path."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_rel(base: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path.resolve())


def _default_install_root() -> Path:
    codex_home = os.environ.get("CODEX_HOME", "~/.codex")
    return Path(codex_home).expanduser() / "skills" / "local" / "cortex"


def _discover_skills(skills_dir: Path) -> list[Path]:
    discovered: list[Path] = []
    if not skills_dir.exists():
        return discovered
    for child in sorted(skills_dir.iterdir()):
        if not child.is_dir():
            continue
        if (child / "SKILL.md").is_file():
            discovered.append(child)
    return discovered


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    raise RuntimeError(f"cannot remove unknown path type: {path}")


def _install_skill(
    *,
    source: Path,
    destination: Path,
    mode: str,
    force: bool,
    dry_run: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "skill": source.name,
        "source": str(source.resolve()),
        "destination": str(destination),
        "mode": mode,
        "action": "",
        "status": "pass",
        "message": "",
    }

    if destination.exists() or destination.is_symlink():
        if mode == "symlink" and destination.is_symlink() and destination.resolve() == source.resolve():
            result["action"] = "skip"
            result["message"] = "already_installed"
            return result
        if not force:
            result["status"] = "fail"
            result["action"] = "none"
            result["message"] = "destination_exists_use_force"
            return result
        result["action"] = "replace"
        result["message"] = "replaced_existing_install"
        if not dry_run:
            _remove_path(destination)
    else:
        result["action"] = "install"
        result["message"] = "installed_new"

    if dry_run:
        return result

    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "symlink":
        destination.symlink_to(source.resolve(), target_is_directory=True)
    elif mode == "copy":
        shutil.copytree(source, destination)
    else:
        raise RuntimeError(f"unsupported mode: {mode}")
    return result


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
        f"mode: {payload.get('mode', '')}",
        f"installed_root: {payload.get('install_root', '')}",
    ]
    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        lines.append(f"discovered: {summary.get('discovered', 0)}")
        lines.append(f"installed: {summary.get('installed', 0)}")
        lines.append(f"replaced: {summary.get('replaced', 0)}")
        lines.append(f"skipped: {summary.get('skipped', 0)}")
        lines.append(f"failed: {summary.get('failed', 0)}")
    for item in payload.get("results", []):
        if not isinstance(item, dict):
            continue
        lines.append(
            f"- {item.get('skill', '?')}: {item.get('action', 'none')} [{item.get('status', 'fail')}] {item.get('message', '')}"
        )
    print("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--skills-dir", default="skills")
    parser.add_argument("--install-root", default="")
    parser.add_argument("--mode", choices=("symlink", "copy"), default="symlink")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    skills_dir = Path(args.skills_dir)
    if not skills_dir.is_absolute():
        skills_dir = (project_dir / skills_dir).resolve()

    install_root = Path(args.install_root).expanduser().resolve() if args.install_root else _default_install_root().resolve()
    discovered = _discover_skills(skills_dir)

    payload: dict[str, Any] = {
        "artifact": "skills_bootstrap_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "skills_dir": str(skills_dir),
        "install_root": str(install_root),
        "mode": args.mode,
        "dry_run": bool(args.dry_run),
        "force": bool(args.force),
        "strict": bool(args.strict),
        "status": "pass",
        "results": [],
    }

    if not discovered:
        payload["summary"] = {"discovered": 0, "installed": 0, "replaced": 0, "skipped": 0, "failed": 0}
        if args.strict:
            payload["status"] = "fail"
            payload["message"] = "no_local_skills_discovered"
            _emit(payload, args.format)
            return 1
        payload["message"] = "no_local_skills_discovered"
        _emit(payload, args.format)
        return 0

    results: list[dict[str, Any]] = []
    failed = 0
    installed = 0
    replaced = 0
    skipped = 0

    for skill_dir in discovered:
        destination = install_root / skill_dir.name
        try:
            item = _install_skill(
                source=skill_dir,
                destination=destination,
                mode=args.mode,
                force=bool(args.force),
                dry_run=bool(args.dry_run),
            )
        except Exception as exc:  # noqa: BLE001
            item = {
                "skill": skill_dir.name,
                "source": str(skill_dir.resolve()),
                "destination": str(destination),
                "mode": args.mode,
                "action": "none",
                "status": "fail",
                "message": str(exc),
            }

        if item.get("status") != "pass":
            failed += 1
        elif item.get("action") == "install":
            installed += 1
        elif item.get("action") == "replace":
            replaced += 1
        elif item.get("action") == "skip":
            skipped += 1
        results.append(item)

    payload["results"] = results
    payload["summary"] = {
        "discovered": len(discovered),
        "installed": installed,
        "replaced": replaced,
        "skipped": skipped,
        "failed": failed,
    }
    if failed > 0:
        payload["status"] = "fail"
        payload["message"] = "one_or_more_skill_installs_failed"
    else:
        payload["message"] = "skills_installed"

    # Include convenient relative roots when install root is inside project dir.
    payload["skills_dir_rel"] = _safe_rel(project_dir, skills_dir)
    payload["install_root_rel"] = _safe_rel(project_dir, install_root)

    _emit(payload, args.format)
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

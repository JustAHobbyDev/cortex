#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False, env=env)


def init_git_repo(path: Path) -> None:
    run(["git", "init"], cwd=path)
    run(["git", "config", "user.email", "test@example.com"], cwd=path)
    run(["git", "config", "user.name", "Parity Test"], cwd=path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_nondeterministic(obj: dict[str, Any]) -> dict[str, Any]:
    out = dict(obj)
    out.pop("run_at", None)
    out.pop("project_dir", None)
    out.pop("cortex_root", None)
    out.pop("assets_dir", None)
    out.pop("contract_file", None)
    return out


class Runner:
    def __init__(self, kind: str, repo_root: Path, external_bin: Path) -> None:
        self.kind = kind
        self.repo_root = repo_root
        self.external_bin = external_bin

    def cmd(self, *coach_args: str) -> tuple[list[str], dict[str, str]]:
        env = os.environ.copy()
        env["UV_CACHE_DIR"] = str(self.repo_root / ".uv-cache")
        if self.kind == "internal":
            env["CORTEX_COACH_FORCE_INTERNAL"] = "1"
            return ["./scripts/cortex_coach_wrapper_v0.sh", *coach_args], env
        return [str(self.external_bin), *coach_args], env

    def exec(self, *coach_args: str, expect_code: int = 0) -> subprocess.CompletedProcess[str]:
        cmd, env = self.cmd(*coach_args)
        proc = run(cmd, cwd=self.repo_root, env=env)
        if proc.returncode != expect_code:
            raise RuntimeError(
                f"{self.kind} command failed: {cmd}\nexpected={expect_code} got={proc.returncode}\n"
                f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
            )
        return proc


def compare(name: str, left: Any, right: Any) -> None:
    if left != right:
        raise RuntimeError(
            f"parity mismatch: {name}\n"
            f"internal={json.dumps(left, indent=2, sort_keys=True)}\n"
            f"external={json.dumps(right, indent=2, sort_keys=True)}"
        )


def stage_project(base: Path, suffix: str) -> Path:
    p = base / suffix
    p.mkdir(parents=True, exist_ok=True)
    init_git_repo(p)
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 3 parity check between internal and external coach.")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument(
        "--external-bin",
        default="/home/d/codex/cortex-coach/.venv/bin/cortex-coach",
        help="Path to external standalone cortex-coach binary.",
    )
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    external_bin = Path(args.external_bin).resolve()
    if not external_bin.exists():
        print(f"missing external bin: {external_bin}")
        return 1

    internal = Runner("internal", repo_root, external_bin)
    external = Runner("external", repo_root, external_bin)

    temp_root = Path(tempfile.mkdtemp(prefix="phase3_parity_"))
    try:
        p_internal = stage_project(temp_root, "internal_proj")
        p_external = stage_project(temp_root, "external_proj")

        # init
        internal.exec("init", "--project-dir", str(p_internal), "--project-id", "demo", "--project-name", "Demo")
        external.exec("init", "--project-dir", str(p_external), "--project-id", "demo", "--project-name", "Demo")
        mi = load_json(p_internal / ".cortex" / "manifest_v0.json")
        me = load_json(p_external / ".cortex" / "manifest_v0.json")
        compare("init.manifest.version", mi.get("version"), me.get("version"))
        compare("init.manifest.artifacts.keys", sorted(mi.get("artifacts", {}).keys()), sorted(me.get("artifacts", {}).keys()))

        # baseline commit for clean audit-needed parity
        run(["git", "add", "."], cwd=p_internal)
        run(["git", "commit", "-m", "baseline"], cwd=p_internal)
        run(["git", "add", "."], cwd=p_external)
        run(["git", "commit", "-m", "baseline"], cwd=p_external)

        # audit-needed
        ai = json.loads(internal.exec("audit-needed", "--project-dir", str(p_internal), "--format", "json").stdout)
        ae = json.loads(external.exec("audit-needed", "--project-dir", str(p_external), "--format", "json").stdout)
        compare("audit-needed", strip_nondeterministic(ai), strip_nondeterministic(ae))

        # contract-check
        ci = json.loads(internal.exec("contract-check", "--project-dir", str(p_internal), "--format", "json").stdout)
        ce = json.loads(external.exec("contract-check", "--project-dir", str(p_external), "--format", "json").stdout)
        compare("contract-check.status", ci.get("status"), ce.get("status"))
        compare(
            "contract-check.checks",
            [(c.get("check"), c.get("status")) for c in ci.get("checks", [])],
            [(c.get("check"), c.get("status")) for c in ce.get("checks", [])],
        )

        # audit
        internal.exec("audit", "--project-dir", str(p_internal))
        external.exec("audit", "--project-dir", str(p_external))
        ri = load_json(p_internal / ".cortex" / "reports" / "lifecycle_audit_v0.json")
        re = load_json(p_external / ".cortex" / "reports" / "lifecycle_audit_v0.json")
        compare("audit.status", ri.get("status"), re.get("status"))
        compare(
            "audit.checks",
            [(c.get("check"), c.get("status")) for c in ri.get("checks", [])],
            [(c.get("check"), c.get("status")) for c in re.get("checks", [])],
        )

        # context-load
        bi = p_internal / ".cortex" / "reports" / "bundle.json"
        be = p_external / ".cortex" / "reports" / "bundle.json"
        internal.exec(
            "context-load",
            "--project-dir",
            str(p_internal),
            "--task",
            "governance",
            "--max-files",
            "8",
            "--max-chars-per-file",
            "600",
            "--out-file",
            str(bi),
        )
        external.exec(
            "context-load",
            "--project-dir",
            str(p_external),
            "--task",
            "governance",
            "--max-files",
            "8",
            "--max-chars-per-file",
            "600",
            "--out-file",
            str(be),
        )
        bji = load_json(bi)
        bje = load_json(be)
        compare("context-load.task_key", bji.get("task_key"), bje.get("task_key"))
        compare("context-load.selected_file_count", bji.get("selected_file_count"), bje.get("selected_file_count"))

        # decision lifecycle
        di = json.loads(
            internal.exec(
                "decision-capture",
                "--project-dir",
                str(p_internal),
                "--title",
                "Parity decision",
                "--decision",
                "Parity check.",
                "--rationale",
                "phase3",
                "--impact-scope",
                "governance",
                "--linked-artifacts",
                ".cortex/manifest_v0.json",
                "--format",
                "json",
            ).stdout
        )
        de = json.loads(
            external.exec(
                "decision-capture",
                "--project-dir",
                str(p_external),
                "--title",
                "Parity decision",
                "--decision",
                "Parity check.",
                "--rationale",
                "phase3",
                "--impact-scope",
                "governance",
                "--linked-artifacts",
                ".cortex/manifest_v0.json",
                "--format",
                "json",
            ).stdout
        )
        compare("decision-capture.status", di.get("status"), de.get("status"))
        compare("decision-capture.title", di.get("title"), de.get("title"))

        pi = json.loads(
            internal.exec(
                "decision-promote",
                "--project-dir",
                str(p_internal),
                "--decision-id",
                str(di.get("decision_id")),
                "--format",
                "json",
            ).stdout
        )
        pe = json.loads(
            external.exec(
                "decision-promote",
                "--project-dir",
                str(p_external),
                "--decision-id",
                str(de.get("decision_id")),
                "--format",
                "json",
            ).stdout
        )
        compare("decision-promote.status", pi.get("status"), pe.get("status"))

        print("phase3 parity check: PASS")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compatibility shim: client onboarding preflight moved to external training project."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--out-file", default="")
    parser.add_argument("--format", default="text", choices=("text", "json"))
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    payload: dict[str, Any] = {
        "artifact": "client_onboarding_command_preflight_v0",
        "version": "v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "status": "moved",
        "message": (
            "Client onboarding preflight has moved to the standalone training project. "
            "See docs/cortex-coach/client_training_external_repo_v0.md and "
            "docs/cortex-coach/client_training_project_boundary_and_handoff_v0.md."
        ),
    }

    if args.out_file:
        out_file = Path(args.out_file)
        if not out_file.is_absolute():
            out_file = (project_dir / out_file).resolve()
        _write_json(out_file, payload)
        payload["out_file"] = str(out_file)

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("\n".join([f"status: {payload['status']}", payload["message"]]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

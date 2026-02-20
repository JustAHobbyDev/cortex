#!/usr/bin/env python3
"""
Thin Phase 4 delegator for cortex-coach runtime.

Behavior:
- prefer installed `cortex-coach`
- fallback to in-repo legacy runtime for compatibility
- force legacy mode with `CORTEX_COACH_FORCE_INTERNAL=1`
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _run_legacy() -> int:
    legacy = Path(__file__).resolve().with_name("cortex_project_coach_runtime_legacy_v0.py")
    proc = subprocess.run([sys.executable, str(legacy), *sys.argv[1:]], check=False)
    return proc.returncode


def main() -> int:
    if os.environ.get("CORTEX_COACH_FORCE_INTERNAL") == "1":
        return _run_legacy()

    coach_bin = shutil.which("cortex-coach")
    if coach_bin:
        proc = subprocess.run(
            [coach_bin, *sys.argv[1:]],
            check=False,
            text=True,
            capture_output=True,
        )
        if proc.returncode == 0:
            if proc.stdout:
                print(proc.stdout, end="")
            return 0
        stderr = proc.stderr or ""
        startup_fail = (
            "No module named" in stderr
            or "ModuleNotFoundError" in stderr
            or "ImportError" in stderr
        )
        if not startup_fail:
            if proc.stdout:
                print(proc.stdout, end="")
            if proc.stderr:
                print(proc.stderr, end="", file=sys.stderr)
            return proc.returncode

    # Compatibility fallback during migration window.
    return _run_legacy()


if __name__ == "__main__":
    raise SystemExit(main())

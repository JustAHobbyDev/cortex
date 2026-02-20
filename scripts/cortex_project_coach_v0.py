#!/usr/bin/env python3
"""Thin Phase 4 delegator for installed standalone `cortex-coach`."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys


def main() -> int:
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

    proc = subprocess.run([coach_bin, *sys.argv[1:]], check=False)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
set -euo pipefail

# Phase 3 dual-path wrapper:
# - prefer installed `cortex-coach`
# - fallback to in-repo script runtime for parity stabilization

if [[ "${CORTEX_COACH_FORCE_INTERNAL:-0}" == "1" ]]; then
  UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.uv-cache}" uv run python3 scripts/cortex_project_coach_v0.py "$@"
  exit $?
fi

if command -v cortex-coach >/dev/null 2>&1; then
  cortex-coach "$@"
  exit $?
fi

UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.uv-cache}" uv run python3 scripts/cortex_project_coach_v0.py "$@"

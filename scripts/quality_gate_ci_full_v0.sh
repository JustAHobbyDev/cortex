#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.uv-cache}"
mkdir -p "$UV_CACHE_DIR"

echo "[quality-gate-ci-full] 1/2 required CI gate"
./scripts/quality_gate_ci_v0.sh

echo "[quality-gate-ci-full] 2/2 full coach test matrix"
uv run --locked --group dev pytest -q tests/test_coach_*.py

echo "[quality-gate-ci-full] PASS"

#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/move_training_files_to_repo_v0.sh \
    --target-repo-dir <path> \
    --approval-ref <id> [--approval-ref <id> ...] \
    [--move] [--dry-run] [--push] [--remote <name>] [--branch <name>] \
    [--allow-dirty-target] [--skip-commit] [--skip-pointer-update] [--skip-quality-gate] \
    [--status <draft|ready_for_handoff|accepted>] \
    [--handoff-manifest-out <path>] [--report-out <path>] \
    [--format <text|json>]

Behavior:
  - Runs the governed transfer workflow in:
      scripts/client_training_migration_handoff_v0.py
  - Performs file transfer from the training bundle + governance handoff outputs.
  - Default transfer mode is copy. Use --move to prune source files after successful handoff.
USAGE
}

TARGET_REPO_DIR=""
TRANSFER_MODE="copy"
STATUS="ready_for_handoff"
HANDOFF_MANIFEST_OUT=""
REPORT_OUT=""
FORMAT="text"
PUSH=0
SKIP_COMMIT=0
ALLOW_DIRTY_TARGET=0
SKIP_POINTER_UPDATE=0
SKIP_QUALITY_GATE=0
DRY_RUN=0
REMOTE="origin"
BRANCH=""
APPROVAL_REFS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-repo-dir)
      TARGET_REPO_DIR="${2:-}"
      shift 2
      ;;
    --approval-ref)
      APPROVAL_REFS+=("${2:-}")
      shift 2
      ;;
    --move)
      TRANSFER_MODE="move"
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --push)
      PUSH=1
      shift
      ;;
    --remote)
      REMOTE="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --allow-dirty-target)
      ALLOW_DIRTY_TARGET=1
      shift
      ;;
    --skip-commit)
      SKIP_COMMIT=1
      shift
      ;;
    --skip-pointer-update)
      SKIP_POINTER_UPDATE=1
      shift
      ;;
    --skip-quality-gate)
      SKIP_QUALITY_GATE=1
      shift
      ;;
    --status)
      STATUS="${2:-}"
      shift 2
      ;;
    --handoff-manifest-out)
      HANDOFF_MANIFEST_OUT="${2:-}"
      shift 2
      ;;
    --report-out)
      REPORT_OUT="${2:-}"
      shift 2
      ;;
    --format)
      FORMAT="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$TARGET_REPO_DIR" ]]; then
  echo "error: --target-repo-dir is required" >&2
  usage
  exit 2
fi

if [[ ${#APPROVAL_REFS[@]} -eq 0 ]]; then
  echo "error: at least one --approval-ref is required" >&2
  usage
  exit 2
fi

if [[ "$STATUS" != "draft" && "$STATUS" != "ready_for_handoff" && "$STATUS" != "accepted" ]]; then
  echo "error: --status must be one of draft|ready_for_handoff|accepted" >&2
  exit 2
fi

if [[ "$FORMAT" != "text" && "$FORMAT" != "json" ]]; then
  echo "error: --format must be text or json" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

CMD=(
  python3
  "${PROJECT_ROOT}/scripts/client_training_migration_handoff_v0.py"
  --project-dir "${PROJECT_ROOT}"
  --target-repo-dir "${TARGET_REPO_DIR}"
  --transfer-mode "${TRANSFER_MODE}"
  --status "${STATUS}"
  --remote "${REMOTE}"
  --format "${FORMAT}"
)

if [[ -n "$HANDOFF_MANIFEST_OUT" ]]; then
  CMD+=(--handoff-manifest-out "$HANDOFF_MANIFEST_OUT")
fi

if [[ -n "$REPORT_OUT" ]]; then
  CMD+=(--report-out "$REPORT_OUT")
fi

if [[ "$PUSH" -eq 1 ]]; then
  CMD+=(--push)
fi

if [[ -n "$BRANCH" ]]; then
  CMD+=(--branch "$BRANCH")
fi

if [[ "$ALLOW_DIRTY_TARGET" -eq 1 ]]; then
  CMD+=(--allow-dirty-target)
fi

if [[ "$SKIP_COMMIT" -eq 1 ]]; then
  CMD+=(--skip-commit)
fi

if [[ "$SKIP_POINTER_UPDATE" -eq 1 ]]; then
  CMD+=(--skip-pointer-update)
fi

if [[ "$SKIP_QUALITY_GATE" -eq 1 ]]; then
  CMD+=(--skip-quality-gate)
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  CMD+=(--dry-run)
fi

for ref in "${APPROVAL_REFS[@]}"; do
  CMD+=(--approval-ref "$ref")
done

"${CMD[@]}"

#!/usr/bin/env python3
"""Generate Phase 4 governance debt visibility report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _to_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return sorted(set(out))


def _render_text(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
        f"debt_item_count: {summary.get('debt_item_count', 0)}",
        f"blocked_count: {summary.get('blocked_count', 0)}",
        f"ready_count: {summary.get('ready_count', 0)}",
        f"owner_coverage_rate: {summary.get('owner_coverage_rate', 0.0)}",
        f"next_action_coverage_rate: {summary.get('next_action_coverage_rate', 0.0)}",
        f"required_visibility_coverage_rate: {summary.get('required_visibility_coverage_rate', 0.0)}",
    ]
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--fixture-file",
        default=".cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json",
    )
    parser.add_argument(
        "--out-file",
        default=".cortex/reports/project_state/phase4_governance_debt_visibility_report_v0.json",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    fixture_path = (project_dir / args.fixture_file).resolve()
    out_file = (project_dir / args.out_file).resolve()

    freeze = _load_json(fixture_path)
    if not isinstance(freeze, dict):
        raise SystemExit(f"fixture freeze is not a JSON object: {fixture_path}")

    scenario_by_id = {
        str(item["scenario_id"]): item for item in freeze.get("scenarios", []) if isinstance(item, dict)
    }

    case_rows: list[dict[str, Any]] = []
    all_debt_items: list[dict[str, Any]] = []

    for profile in freeze.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        profile_id = str(profile.get("profile_id", ""))
        for scenario_id in profile.get("scenario_ids", []):
            scenario = scenario_by_id.get(str(scenario_id))
            if scenario is None:
                raise SystemExit(f"missing scenario definition: {scenario_id!r}")
            fixture_ref = str(scenario.get("fixture_ref", "")).strip()
            scenario_fixture_path = (project_dir / fixture_ref).resolve()
            scenario_fixture = _load_json(scenario_fixture_path)
            if not isinstance(scenario_fixture, dict):
                raise SystemExit(f"scenario fixture is not a JSON object: {scenario_fixture_path}")

            debt_items = scenario_fixture.get("governance_debt_items")
            if not isinstance(debt_items, list):
                continue

            normalized_items: list[dict[str, Any]] = []
            for idx, item in enumerate(debt_items, start=1):
                if not isinstance(item, dict):
                    continue
                debt_id = str(item.get("debt_id", f"gd_{idx:03d}")).strip() or f"gd_{idx:03d}"
                state = str(item.get("state", "blocked")).strip().lower() or "blocked"
                owner = str(item.get("owner", "")).strip()
                next_action = str(item.get("next_action", "")).strip()
                dependency_refs = _to_string_list(item.get("dependency_refs", []))
                normalized = {
                    "debt_id": debt_id,
                    "state": state,
                    "owner": owner,
                    "next_action": next_action,
                    "dependency_refs": dependency_refs,
                    "has_owner": bool(owner),
                    "has_next_action": bool(next_action),
                    "visibility_complete": bool(owner) and bool(next_action) and state in {"ready", "blocked"},
                }
                normalized_items.append(normalized)
                all_debt_items.append(normalized)

            normalized_items = sorted(normalized_items, key=lambda item: (str(item["state"]), str(item["debt_id"])))
            case_rows.append(
                {
                    "profile_id": profile_id,
                    "scenario_id": str(scenario_id),
                    "fixture_ref": fixture_ref,
                    "debt_item_count": len(normalized_items),
                    "ready_items": [item for item in normalized_items if item["state"] == "ready"],
                    "blocked_items": [item for item in normalized_items if item["state"] == "blocked"],
                }
            )

    debt_item_count = len(all_debt_items)
    ready_count = sum(1 for item in all_debt_items if item.get("state") == "ready")
    blocked_count = sum(1 for item in all_debt_items if item.get("state") == "blocked")
    owner_coverage_rate = sum(1 for item in all_debt_items if item.get("has_owner")) / max(1, debt_item_count)
    next_action_coverage_rate = sum(1 for item in all_debt_items if item.get("has_next_action")) / max(1, debt_item_count)
    required_visibility_coverage_rate = (
        sum(1 for item in all_debt_items if item.get("visibility_complete")) / max(1, debt_item_count)
    )

    status = (
        "pass"
        if debt_item_count > 0
        and owner_coverage_rate >= 1.0
        and next_action_coverage_rate >= 1.0
        and required_visibility_coverage_rate >= 1.0
        else "fail"
    )

    payload: dict[str, Any] = {
        "version": "v0",
        "artifact": "phase4_governance_debt_visibility_report_v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "fixture_source": str(fixture_path.relative_to(project_dir)),
        "status": status,
        "summary": {
            "debt_item_count": debt_item_count,
            "ready_count": ready_count,
            "blocked_count": blocked_count,
            "owner_coverage_rate": round(owner_coverage_rate, 6),
            "next_action_coverage_rate": round(next_action_coverage_rate, 6),
            "required_visibility_coverage_rate": round(required_visibility_coverage_rate, 6),
        },
        "targets": {
            "owner_coverage_rate": 1.0,
            "next_action_coverage_rate": 1.0,
            "required_visibility_coverage_rate": 1.0,
        },
        "target_results": {
            "owner_coverage_rate_met": owner_coverage_rate >= 1.0,
            "next_action_coverage_rate_met": next_action_coverage_rate >= 1.0,
            "required_visibility_coverage_rate_met": required_visibility_coverage_rate >= 1.0,
        },
        "cases": case_rows,
    }

    _write_json(out_file, payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_render_text(payload))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

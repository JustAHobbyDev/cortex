#!/usr/bin/env python3
"""Generate Phase 4 enforcement blocking report for unlinked governance closures."""

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


def _normalize_candidates(raw_fixture: dict[str, Any]) -> list[dict[str, Any]]:
    tactical_candidates = raw_fixture.get("tactical_candidates")
    debt_items = raw_fixture.get("governance_debt_items")
    out: list[dict[str, Any]] = []
    if isinstance(tactical_candidates, list):
        for idx, item in enumerate(tactical_candidates, start=1):
            if not isinstance(item, dict):
                continue
            out.append(
                {
                    "candidate_id": str(item.get("candidate_id", f"pc_{idx:03d}")).strip() or f"pc_{idx:03d}",
                    "state": str(item.get("state", "ready")).strip().lower() or "ready",
                    "governance_impact": str(item.get("governance_impact", "medium")).strip().lower() or "medium",
                    "decision_refs": _to_string_list(item.get("decision_refs", [])),
                    "reflection_refs": _to_string_list(item.get("reflection_refs", [])),
                    "owner": str(item.get("owner", "")).strip(),
                    "next_action": str(item.get("next_action", "")).strip(),
                }
            )
    elif isinstance(debt_items, list):
        for idx, item in enumerate(debt_items, start=1):
            if not isinstance(item, dict):
                continue
            state = str(item.get("state", "blocked")).strip().lower() or "blocked"
            out.append(
                {
                    "candidate_id": f"pc_{str(item.get('debt_id', f'gd_{idx:03d}')).strip() or f'gd_{idx:03d}'}",
                    "state": state,
                    "governance_impact": "high" if state == "blocked" else "medium",
                    "decision_refs": [],
                    "reflection_refs": [],
                    "owner": str(item.get("owner", "")).strip(),
                    "next_action": str(item.get("next_action", "")).strip(),
                }
            )
    return out


def _enforcement_recommendation(candidate: dict[str, Any]) -> str:
    governance_impact = str(candidate.get("governance_impact", "")).strip().lower()
    linkage_complete = bool(candidate.get("decision_refs")) and bool(candidate.get("reflection_refs"))
    if governance_impact in {"critical", "high"} and not linkage_complete:
        return "block_unlinked_governance_closure"
    return "eligible_for_promotion"


def _render_text(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    lines = [
        f"status: {payload.get('status', 'fail')}",
        f"run_at: {payload.get('run_at', '')}",
        f"unlinked_closure_block_rate: {summary.get('unlinked_closure_block_rate', 0.0)}",
        f"linked_closure_false_block_rate: {summary.get('linked_closure_false_block_rate', 1.0)}",
        f"unlinked_governance_attempt_count: {summary.get('unlinked_governance_attempt_count', 0)}",
        f"linked_governance_attempt_count: {summary.get('linked_governance_attempt_count', 0)}",
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
        default=".cortex/reports/project_state/phase4_enforcement_blocking_report_v0.json",
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
    unlinked_governance_attempt_count = 0
    blocked_unlinked_count = 0
    linked_governance_attempt_count = 0
    linked_false_block_count = 0

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

            candidates = _normalize_candidates(scenario_fixture)
            candidate_rows: list[dict[str, Any]] = []
            for candidate in candidates:
                linkage_complete = bool(candidate.get("decision_refs")) and bool(candidate.get("reflection_refs"))
                governance_impact = str(candidate.get("governance_impact", "")).strip().lower()
                governance_impacting = governance_impact in {"critical", "high"}
                expected_block = governance_impacting and not linkage_complete
                observed_recommendation = _enforcement_recommendation(candidate)
                observed_block = observed_recommendation == "block_unlinked_governance_closure"

                if expected_block:
                    unlinked_governance_attempt_count += 1
                    if observed_block:
                        blocked_unlinked_count += 1
                if governance_impacting and linkage_complete:
                    linked_governance_attempt_count += 1
                    if observed_block:
                        linked_false_block_count += 1

                candidate_rows.append(
                    {
                        "candidate_id": candidate.get("candidate_id"),
                        "governance_impact": governance_impact,
                        "linkage_complete": linkage_complete,
                        "expected_block": expected_block,
                        "observed_recommendation": observed_recommendation,
                        "observed_block": observed_block,
                        "owner": candidate.get("owner", ""),
                        "next_action": candidate.get("next_action", ""),
                    }
                )

            case_rows.append(
                {
                    "profile_id": profile_id,
                    "scenario_id": str(scenario_id),
                    "fixture_ref": fixture_ref,
                    "candidate_count": len(candidate_rows),
                    "candidates": candidate_rows,
                }
            )

    unlinked_closure_block_rate = (
        blocked_unlinked_count / unlinked_governance_attempt_count if unlinked_governance_attempt_count > 0 else 1.0
    )
    linked_closure_false_block_rate = (
        linked_false_block_count / linked_governance_attempt_count if linked_governance_attempt_count > 0 else 0.0
    )
    status = "pass" if unlinked_closure_block_rate >= 1.0 and linked_closure_false_block_rate <= 0.05 else "fail"

    payload: dict[str, Any] = {
        "version": "v0",
        "artifact": "phase4_enforcement_blocking_report_v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "fixture_source": str(fixture_path.relative_to(project_dir)),
        "status": status,
        "summary": {
            "unlinked_governance_attempt_count": unlinked_governance_attempt_count,
            "blocked_unlinked_count": blocked_unlinked_count,
            "unlinked_closure_block_rate": round(unlinked_closure_block_rate, 6),
            "linked_governance_attempt_count": linked_governance_attempt_count,
            "linked_false_block_count": linked_false_block_count,
            "linked_closure_false_block_rate": round(linked_closure_false_block_rate, 6),
        },
        "targets": {
            "unlinked_closure_block_rate": 1.0,
            "linked_closure_false_block_rate_max": 0.05,
        },
        "target_results": {
            "unlinked_closure_block_rate_met": unlinked_closure_block_rate >= 1.0,
            "linked_closure_false_block_rate_met": linked_closure_false_block_rate <= 0.05,
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

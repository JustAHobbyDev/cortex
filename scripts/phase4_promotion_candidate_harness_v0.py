#!/usr/bin/env python3
"""Generate Phase 4 promotion candidate quality and determinism reports."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCORE_MODES = ("uniform", "evidence_bias")
TIE_BREAK_ORDER = [
    "combined_score_desc",
    "evidence_coverage_desc",
    "governance_impact_priority_asc",
    "candidate_id_asc",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _to_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return sorted(set(out))


def _normalize_impacted_artifacts(value: Any, fallback_title: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(value, list):
        return out
    for idx, item in enumerate(value, start=1):
        if isinstance(item, dict):
            artifact_path = str(item.get("artifact_path", "")).strip()
            change_summary = str(item.get("change_summary", "")).strip()
            if artifact_path and change_summary:
                out.append({"artifact_path": artifact_path, "change_summary": change_summary})
            continue
        if isinstance(item, str) and item.strip():
            out.append(
                {
                    "artifact_path": item.strip(),
                    "change_summary": f"promotion candidate update {idx}: {fallback_title}",
                }
            )
    return out


def _normalize_tactical_candidate(raw: dict[str, Any], idx: int) -> dict[str, Any]:
    candidate_id = str(raw.get("candidate_id", raw.get("id", f"pc_{idx:03d}"))).strip() or f"pc_{idx:03d}"
    title = str(raw.get("title", f"Promotion candidate {idx}")).strip() or f"Promotion candidate {idx}"
    summary = str(raw.get("summary", "")).strip()
    state = str(raw.get("state", "ready")).strip().lower() or "ready"
    governance_impact = str(raw.get("governance_impact", "medium")).strip().lower() or "medium"
    decision_refs = _to_string_list(raw.get("decision_refs", []))
    reflection_refs = _to_string_list(raw.get("reflection_refs", []))
    evidence_refs = _to_string_list(raw.get("evidence_refs", []))
    impacted_artifacts = _normalize_impacted_artifacts(raw.get("impacted_artifacts", []), title)
    owner = str(raw.get("owner", "")).strip()
    next_action = str(raw.get("next_action", "")).strip()
    return {
        "candidate_id": candidate_id,
        "title": title,
        "summary": summary,
        "state": state,
        "governance_impact": governance_impact,
        "decision_refs": decision_refs,
        "reflection_refs": reflection_refs,
        "evidence_refs": evidence_refs,
        "impacted_artifacts": impacted_artifacts,
        "owner": owner,
        "next_action": next_action,
    }


def _candidate_from_debt_item(raw: dict[str, Any], idx: int) -> dict[str, Any]:
    debt_id = str(raw.get("debt_id", f"gd_{idx:03d}")).strip() or f"gd_{idx:03d}"
    state = str(raw.get("state", "blocked")).strip().lower() or "blocked"
    owner = str(raw.get("owner", "")).strip()
    next_action = str(raw.get("next_action", "")).strip()
    dependency_refs = _to_string_list(raw.get("dependency_refs", []))
    return {
        "candidate_id": f"pc_{debt_id}",
        "title": f"Governance debt {debt_id}",
        "summary": next_action,
        "state": state,
        "governance_impact": "high" if state == "blocked" else "medium",
        "decision_refs": [],
        "reflection_refs": [],
        "evidence_refs": dependency_refs,
        "impacted_artifacts": [],
        "owner": owner,
        "next_action": next_action,
    }


def _query_tokens(query: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in query.lower():
        if ch.isalnum():
            current.append(ch)
            continue
        if current:
            token = "".join(current)
            if len(token) >= 3:
                tokens.append(token)
            current = []
    if current:
        token = "".join(current)
        if len(token) >= 3:
            tokens.append(token)
    return sorted(set(tokens))


def _impact_priority(impact: str) -> tuple[int, float]:
    value = str(impact).strip().lower()
    if value in {"critical", "high"}:
        return 1, 1.0
    if value == "medium":
        return 2, 0.7
    if value == "low":
        return 3, 0.4
    return 4, 0.2


def _score_weights(score_mode: str) -> dict[str, float]:
    if score_mode == "uniform":
        return {
            "lexical_score": 0.25,
            "evidence_coverage": 0.25,
            "linkage_score": 0.25,
            "impact_score": 0.25,
        }
    return {
        "lexical_score": 0.2,
        "evidence_coverage": 0.35,
        "linkage_score": 0.25,
        "impact_score": 0.2,
    }


def _load_candidates_from_fixture(path: Path) -> list[dict[str, Any]]:
    payload = _load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"fixture is not a JSON object: {path}")

    tactical_candidates = payload.get("tactical_candidates")
    debt_items = payload.get("governance_debt_items")
    out: list[dict[str, Any]] = []
    if isinstance(tactical_candidates, list):
        for idx, item in enumerate(tactical_candidates, start=1):
            if isinstance(item, dict):
                out.append(_normalize_tactical_candidate(item, idx))
    elif isinstance(debt_items, list):
        for idx, item in enumerate(debt_items, start=1):
            if isinstance(item, dict):
                out.append(_candidate_from_debt_item(item, idx))
    else:
        raise ValueError(f"fixture must include tactical_candidates[] or governance_debt_items[]: {path}")

    if not out:
        raise ValueError(f"fixture produced zero candidates: {path}")
    return out


def _candidate_payload_valid(candidate: dict[str, Any]) -> bool:
    required = (
        "candidate_id",
        "title",
        "state",
        "governance_impact",
        "linkage_complete",
        "enforcement_recommendation",
        "combined_score",
        "score_breakdown",
        "rank",
    )
    for key in required:
        if key not in candidate:
            return False
    if not isinstance(candidate.get("score_breakdown"), dict):
        return False
    return True


def _promotion_contract_fields_complete(candidate: dict[str, Any]) -> bool:
    return (
        bool(candidate.get("decision_refs"))
        and bool(candidate.get("reflection_refs"))
        and bool(candidate.get("evidence_refs"))
        and bool(candidate.get("impacted_artifacts"))
    )


def _rank_candidates(
    candidates: list[dict[str, Any]],
    *,
    query: str,
    score_mode: str,
    candidate_limit: int,
) -> list[dict[str, Any]]:
    query_tokens = _query_tokens(query)
    weights = _score_weights(score_mode)
    scored_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        searchable = " ".join(
            [
                str(candidate.get("title", "")),
                str(candidate.get("summary", "")),
                str(candidate.get("state", "")),
                str(candidate.get("governance_impact", "")),
                str(candidate.get("owner", "")),
                str(candidate.get("next_action", "")),
            ]
        ).lower()
        hit_count = sum(1 for token in query_tokens if token in searchable)
        lexical_score = min(1.0, float(hit_count) / 6.0) if query_tokens else 0.0
        evidence_coverage = min(1.0, float(len(candidate.get("evidence_refs", []))) / 3.0)
        linkage_complete = bool(candidate.get("decision_refs")) and bool(candidate.get("reflection_refs"))
        linkage_score = 1.0 if linkage_complete else 0.0
        governance_impact = str(candidate.get("governance_impact", ""))
        impact_priority, impact_score = _impact_priority(governance_impact)

        combined_score = round(
            (weights["lexical_score"] * lexical_score)
            + (weights["evidence_coverage"] * evidence_coverage)
            + (weights["linkage_score"] * linkage_score)
            + (weights["impact_score"] * impact_score),
            6,
        )

        enforcement_recommendation = "eligible_for_promotion"
        if governance_impact in {"critical", "high"} and not linkage_complete:
            enforcement_recommendation = "block_unlinked_governance_closure"

        scored_rows.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "title": candidate.get("title"),
                "summary": candidate.get("summary"),
                "state": candidate.get("state"),
                "governance_impact": governance_impact,
                "owner": candidate.get("owner"),
                "next_action": candidate.get("next_action"),
                "decision_refs": candidate.get("decision_refs"),
                "reflection_refs": candidate.get("reflection_refs"),
                "evidence_refs": candidate.get("evidence_refs"),
                "impacted_artifacts": candidate.get("impacted_artifacts"),
                "linkage_complete": linkage_complete,
                "promotion_contract_fields_complete": _promotion_contract_fields_complete(candidate),
                "enforcement_recommendation": enforcement_recommendation,
                "governance_impact_priority": impact_priority,
                "combined_score": combined_score,
                "score_breakdown": {
                    "lexical_score": round(lexical_score, 6),
                    "evidence_coverage": round(evidence_coverage, 6),
                    "linkage_score": round(linkage_score, 6),
                    "impact_score": round(impact_score, 6),
                },
            }
        )

    ranked = sorted(
        scored_rows,
        key=lambda item: (
            -float(item.get("combined_score", 0.0)),
            -float(item.get("score_breakdown", {}).get("evidence_coverage", 0.0)),
            int(item.get("governance_impact_priority", 99)),
            str(item.get("candidate_id", "")),
        ),
    )
    selected = ranked[:candidate_limit]
    for idx, item in enumerate(selected, start=1):
        item["rank"] = idx
    return selected


def _ranking_hash(ranked_candidates: list[dict[str, Any]]) -> str:
    normalized = [
        {
            "candidate_id": str(item.get("candidate_id", "")),
            "rank": int(item.get("rank", 0)),
            "combined_score": round(float(item.get("combined_score", 0.0)), 6),
            "score_breakdown": {
                key: round(float(value), 6) for key, value in sorted(item.get("score_breakdown", {}).items())
            },
            "enforcement_recommendation": str(item.get("enforcement_recommendation", "")),
            "linkage_complete": bool(item.get("linkage_complete", False)),
        }
        for item in ranked_candidates
    ]
    return _json_hash(normalized)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--fixture-file",
        default=".cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json",
    )
    parser.add_argument("--score-mode", choices=SCORE_MODES, default="evidence_bias")
    parser.add_argument("--candidate-limit", type=int, default=8)
    parser.add_argument("--determinism-runs", type=int, default=30)
    parser.add_argument(
        "--quality-out",
        default=".cortex/reports/project_state/phase4_promotion_candidate_quality_report_v0.json",
    )
    parser.add_argument(
        "--determinism-out",
        default=".cortex/reports/project_state/phase4_promotion_determinism_report_v0.json",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    fixture_path = (project_dir / args.fixture_file).resolve()
    quality_out = (project_dir / args.quality_out).resolve()
    determinism_out = (project_dir / args.determinism_out).resolve()

    freeze_payload = _load_json(fixture_path)
    if not isinstance(freeze_payload, dict):
        raise SystemExit(f"fixture freeze is not a JSON object: {fixture_path}")

    scenario_by_id = {
        str(item["scenario_id"]): item for item in freeze_payload.get("scenarios", []) if isinstance(item, dict)
    }
    query_by_id = {str(item["query_id"]): item for item in freeze_payload.get("queries", []) if isinstance(item, dict)}

    quality_cases: list[dict[str, Any]] = []
    determinism_cases: list[dict[str, Any]] = []

    total_candidates = 0
    payload_valid_count = 0
    contract_fields_complete_count = 0
    blocked_unlinked_count = 0
    linked_candidate_count = 0
    linked_false_block_count = 0
    deterministic_case_count = 0

    for profile in freeze_payload.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        profile_id = str(profile.get("profile_id", ""))
        for scenario_id in profile.get("scenario_ids", []):
            scenario = scenario_by_id.get(str(scenario_id))
            if scenario is None:
                raise SystemExit(f"missing scenario definition for {scenario_id!r}")
            fixture_ref = str(scenario.get("fixture_ref", "")).strip()
            scenario_fixture = (project_dir / fixture_ref).resolve()
            candidates = _load_candidates_from_fixture(scenario_fixture)

            for query_id in profile.get("query_ids", []):
                query = query_by_id.get(str(query_id))
                if query is None:
                    raise SystemExit(f"missing query definition for {query_id!r}")
                query_text = str(query.get("query_text", ""))
                ranked = _rank_candidates(
                    candidates,
                    query=query_text,
                    score_mode=str(args.score_mode),
                    candidate_limit=max(1, int(args.candidate_limit)),
                )

                case_id = f"{profile_id}:{scenario_id}:{query_id}"
                case_payload_valid = sum(1 for item in ranked if _candidate_payload_valid(item))
                case_contract_fields_complete = sum(
                    1 for item in ranked if bool(item.get("promotion_contract_fields_complete", False))
                )
                case_blocked_unlinked = sum(
                    1
                    for item in ranked
                    if str(item.get("enforcement_recommendation", "")) == "block_unlinked_governance_closure"
                    and not bool(item.get("linkage_complete", False))
                )
                case_linked_candidates = sum(1 for item in ranked if bool(item.get("linkage_complete", False)))
                case_linked_false_block = sum(
                    1
                    for item in ranked
                    if bool(item.get("linkage_complete", False))
                    and str(item.get("enforcement_recommendation", "")) == "block_unlinked_governance_closure"
                )

                quality_cases.append(
                    {
                        "case_id": case_id,
                        "profile_id": profile_id,
                        "scenario_id": str(scenario_id),
                        "query_id": str(query_id),
                        "fixture_ref": fixture_ref,
                        "query_text": query_text,
                        "candidate_count": len(ranked),
                        "payload_valid_count": case_payload_valid,
                        "payload_valid_rate": round(case_payload_valid / max(1, len(ranked)), 6),
                        "promotion_contract_fields_complete_count": case_contract_fields_complete,
                        "blocked_unlinked_count": case_blocked_unlinked,
                        "linked_candidate_count": case_linked_candidates,
                        "linked_false_block_count": case_linked_false_block,
                        "ranking_hash": _ranking_hash(ranked),
                        "ranked_candidates": ranked,
                    }
                )

                run_hashes: list[str] = []
                for _ in range(max(1, int(args.determinism_runs))):
                    replay = _rank_candidates(
                        candidates,
                        query=query_text,
                        score_mode=str(args.score_mode),
                        candidate_limit=max(1, int(args.candidate_limit)),
                    )
                    run_hashes.append(_ranking_hash(replay))
                hash_set = sorted(set(run_hashes))
                stable = len(hash_set) == 1
                if stable:
                    deterministic_case_count += 1
                determinism_cases.append(
                    {
                        "case_id": case_id,
                        "profile_id": profile_id,
                        "scenario_id": str(scenario_id),
                        "query_id": str(query_id),
                        "determinism_runs": max(1, int(args.determinism_runs)),
                        "unique_hash_count": len(hash_set),
                        "stable_hash": hash_set[0] if hash_set else "",
                        "hashes": hash_set,
                        "pass": stable,
                    }
                )

                total_candidates += len(ranked)
                payload_valid_count += case_payload_valid
                contract_fields_complete_count += case_contract_fields_complete
                blocked_unlinked_count += case_blocked_unlinked
                linked_candidate_count += case_linked_candidates
                linked_false_block_count += case_linked_false_block

    candidate_payload_validity_rate = round(payload_valid_count / max(1, total_candidates), 6)
    contract_fields_complete_rate = round(contract_fields_complete_count / max(1, total_candidates), 6)
    linked_false_block_rate = round(linked_false_block_count / max(1, linked_candidate_count), 6)
    determinism_rate = round(deterministic_case_count / max(1, len(determinism_cases)), 6)

    quality_report: dict[str, Any] = {
        "version": "v0",
        "artifact": "phase4_promotion_candidate_quality_report_v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "fixture_source": str(fixture_path.relative_to(project_dir)),
        "fixture_hash": _json_hash(freeze_payload),
        "score_mode": str(args.score_mode),
        "candidate_limit": max(1, int(args.candidate_limit)),
        "tie_break_order": list(TIE_BREAK_ORDER),
        "summary": {
            "case_count": len(quality_cases),
            "candidate_count": total_candidates,
            "candidate_payload_valid_count": payload_valid_count,
            "candidate_payload_validity_rate": candidate_payload_validity_rate,
            "promotion_contract_fields_complete_rate": contract_fields_complete_rate,
            "blocked_unlinked_count": blocked_unlinked_count,
            "linked_candidate_count": linked_candidate_count,
            "linked_false_block_count": linked_false_block_count,
            "linked_false_block_rate": linked_false_block_rate,
        },
        "targets": {
            "promotion_contract_validity_rate_target": 1.0,
            "linked_false_block_rate_max": 0.05,
        },
        "target_results": {
            "promotion_contract_validity_rate_met": candidate_payload_validity_rate >= 1.0,
            "linked_false_block_rate_met": linked_false_block_rate <= 0.05,
        },
        "status": "pass"
        if candidate_payload_validity_rate >= 1.0 and linked_false_block_rate <= 0.05
        else "fail",
        "cases": quality_cases,
    }

    determinism_report: dict[str, Any] = {
        "version": "v0",
        "artifact": "phase4_promotion_determinism_report_v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "fixture_source": str(fixture_path.relative_to(project_dir)),
        "fixture_hash": _json_hash(freeze_payload),
        "score_mode": str(args.score_mode),
        "candidate_limit": max(1, int(args.candidate_limit)),
        "determinism_runs": max(1, int(args.determinism_runs)),
        "summary": {
            "case_count": len(determinism_cases),
            "deterministic_case_count": deterministic_case_count,
            "ordering_consistency_rate": determinism_rate,
        },
        "targets": {
            "ordering_consistency_rate_target": 1.0,
        },
        "target_results": {
            "ordering_consistency_rate_met": determinism_rate >= 1.0,
        },
        "status": "pass" if determinism_rate >= 1.0 else "fail",
        "cases": determinism_cases,
    }

    _write_json(quality_out, quality_report)
    _write_json(determinism_out, determinism_report)

    return 0 if quality_report["status"] == "pass" and determinism_report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

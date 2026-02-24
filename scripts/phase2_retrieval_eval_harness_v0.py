#!/usr/bin/env python3
"""Phase 2 retrieval evaluation harness for relevance and determinism artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _tokenize(value: str) -> list[str]:
    token = []
    out: list[str] = []
    for ch in value.lower():
        if ch.isalnum():
            token.append(ch)
            continue
        if token:
            t = "".join(token)
            if len(t) >= 3:
                out.append(t)
            token = []
    if token:
        t = "".join(token)
        if len(t) >= 3:
            out.append(t)
    return out


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--fixture-file",
        default=".cortex/reports/project_state/phase2_retrieval_eval_fixture_freeze_v0.json",
    )
    parser.add_argument(
        "--coach-bin",
        default="cortex-coach",
        help="Path to cortex-coach executable used for current retrieval evaluation.",
    )
    parser.add_argument(
        "--legacy-loader-script",
        default="scripts/agent_context_loader_v0.py",
        help="Path to legacy context loader script used as pre-change baseline proxy.",
    )
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--runs-per-query", type=int, default=30)
    parser.add_argument("--max-files", type=int, default=16)
    parser.add_argument("--max-chars-per-file", type=int, default=2000)
    parser.add_argument(
        "--weighting-mode",
        default="evidence_outcome_bias",
        choices=["uniform", "evidence_outcome_bias"],
    )
    parser.add_argument(
        "--relevance-out",
        default=".cortex/reports/project_state/phase2_retrieval_relevance_report_v0.json",
    )
    parser.add_argument(
        "--determinism-out",
        default=".cortex/reports/project_state/phase2_retrieval_determinism_report_v0.json",
    )
    parser.add_argument("--timeout-seconds", type=int, default=60)
    return parser


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_command(cmd: list[str], timeout_seconds: int) -> str:
    proc = subprocess.run(cmd, check=False, text=True, capture_output=True, timeout=timeout_seconds)
    if proc.returncode != 0:
        raise RuntimeError(
            "command failed\n"
            f"cmd={cmd}\n"
            f"returncode={proc.returncode}\n"
            f"stdout={proc.stdout}\n"
            f"stderr={proc.stderr}"
        )
    return proc.stdout


def _run_context_load(
    coach_bin: str,
    project_dir: Path,
    query_text: str,
    profile_id: str,
    weighting_mode: str,
    max_files: int,
    max_chars_per_file: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    cmd = [
        coach_bin,
        "context-load",
        "--project-dir",
        str(project_dir),
        "--task",
        query_text,
        "--retrieval-profile",
        profile_id,
        "--weighting-mode",
        weighting_mode,
        "--max-files",
        str(max_files),
        "--max-chars-per-file",
        str(max_chars_per_file),
    ]
    return json.loads(_run_command(cmd, timeout_seconds=timeout_seconds))


def _run_legacy_loader(
    python_bin: str,
    legacy_loader_script: Path,
    project_dir: Path,
    query_text: str,
    max_files: int,
    max_chars_per_file: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    cmd = [
        python_bin,
        str(legacy_loader_script),
        "--project-dir",
        str(project_dir),
        "--task",
        query_text,
        "--max-files",
        str(max_files),
        "--max-chars-per-file",
        str(max_chars_per_file),
    ]
    return json.loads(_run_command(cmd, timeout_seconds=timeout_seconds))


def _entry_text(entry: dict[str, Any]) -> str:
    excerpt = str(entry.get("excerpt", ""))
    if len(excerpt) > 6000:
        excerpt = excerpt[:6000]
    return " ".join(
        [
            str(entry.get("path", "")),
            str(entry.get("selected_by", "")),
            excerpt,
        ]
    ).lower()


def _any_token_hit(text: str, tokens: list[str]) -> bool:
    if not tokens:
        return False
    return any(token.lower() in text for token in tokens)


def _query_overlap_score(query_text: str, document_text: str) -> float:
    query_tokens = set(_tokenize(query_text))
    if not query_tokens:
        return 0.0
    doc_tokens = set(_tokenize(document_text))
    overlap = len(query_tokens.intersection(doc_tokens)) / max(1, len(query_tokens))
    return round(min(1.0, overlap * 1.5), 6)


def _relevance_gain(query: dict[str, Any], entry: dict[str, Any]) -> float:
    text = _entry_text(entry)
    signals = [str(s).lower() for s in query.get("must_include_signals_any", [])]
    tags = [str(s).lower() for s in query.get("must_include_tags_any", [])]
    excludes = [str(s).lower() for s in query.get("must_exclude_tags_all", [])]
    if _any_token_hit(text, excludes):
        return 0.0
    signal_gain = 1.0 if _any_token_hit(text, signals) else 0.0
    tag_gain = 1.0 if _any_token_hit(text, tags) else 0.0
    overlap_gain = _query_overlap_score(str(query.get("query_text", "")), text)
    return round(signal_gain + tag_gain + overlap_gain, 6)


def _dcg_at_k(gains: list[float], k: int) -> float:
    total = 0.0
    for idx, gain in enumerate(gains[:k], start=1):
        total += (math.pow(2.0, gain) - 1.0) / math.log2(idx + 1)
    return total


def _ndcg_at_k(gains: list[float], k: int) -> float:
    actual = _dcg_at_k(gains, k)
    ideal = _dcg_at_k(sorted(gains, reverse=True), k)
    if ideal <= 0:
        return 0.0
    return round(actual / ideal, 6)


def _group_hits(query: dict[str, Any], top_entries: list[dict[str, Any]]) -> dict[str, bool]:
    texts = [_entry_text(entry) for entry in top_entries]
    signal_tokens = [str(s).lower() for s in query.get("must_include_signals_any", [])]
    tag_tokens = [str(s).lower() for s in query.get("must_include_tags_any", [])]
    exclude_tokens = [str(s).lower() for s in query.get("must_exclude_tags_all", [])]
    signal_hit = any(_any_token_hit(text, signal_tokens) for text in texts) if signal_tokens else True
    tag_hit = any(_any_token_hit(text, tag_tokens) for text in texts) if tag_tokens else True
    exclude_hit = any(_any_token_hit(text, exclude_tokens) for text in texts) if exclude_tokens else False
    return {
        "must_include_signals_any": signal_hit,
        "must_include_tags_any": tag_hit,
        "must_exclude_tags_all": not exclude_hit,
    }


def _top_k_recall(query: dict[str, Any], top_entries: list[dict[str, Any]]) -> float:
    hits = _group_hits(query, top_entries)
    required = [hits["must_include_signals_any"], hits["must_include_tags_any"]]
    score = sum(1 for item in required if item) / len(required)
    if not hits["must_exclude_tags_all"]:
        return 0.0
    return round(score, 6)


def _normalized_ranking_hash(bundle: dict[str, Any]) -> str:
    normalized_files: list[dict[str, Any]] = []
    for entry in bundle.get("files", []):
        breakdown = entry.get("score_breakdown", {})
        norm_breakdown = {}
        if isinstance(breakdown, dict):
            for key in sorted(breakdown):
                value = breakdown[key]
                if isinstance(value, (int, float)):
                    norm_breakdown[key] = round(float(value), 6)
        normalized_files.append(
            {
                "path": str(entry.get("path", "")),
                "selected_by": str(entry.get("selected_by", "")),
                "rank": entry.get("rank"),
                "combined_score": round(float(entry.get("combined_score", 0.0)), 6),
                "confidence": round(float(entry.get("confidence", 0.0)), 6),
                "score_breakdown": norm_breakdown,
            }
        )
    payload = {
        "retrieval_profile": bundle.get("retrieval_profile"),
        "weighting_mode": bundle.get("weighting_mode"),
        "fallback_level": bundle.get("fallback_level"),
        "files": normalized_files,
    }
    return _json_hash(payload)


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(float(statistics.median(values)), 6)


@dataclass(frozen=True)
class QueryRunResult:
    profile_id: str
    query_id: str
    post_ndcg: float
    baseline_ndcg: float
    post_recall: float
    baseline_recall: float
    post_group_hits: dict[str, bool]
    baseline_group_hits: dict[str, bool]
    post_top_paths: list[str]
    baseline_top_paths: list[str]
    ranking_hash: str


def _collect_queries(fixture: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    query_by_id: dict[str, dict[str, Any]] = {
        str(query["query_id"]): query for query in fixture.get("queries", []) if isinstance(query, dict)
    }
    ordered: list[tuple[str, dict[str, Any]]] = []
    for profile in fixture.get("profiles", []):
        profile_id = str(profile.get("profile_id", ""))
        for query_id in profile.get("query_ids", []):
            query = query_by_id.get(str(query_id))
            if query is None:
                raise ValueError(f"missing query definition for id={query_id!r}")
            ordered.append((profile_id, query))
    return ordered


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    fixture_path = Path(args.fixture_file)
    legacy_loader_script = Path(args.legacy_loader_script)
    relevance_out = Path(args.relevance_out)
    determinism_out = Path(args.determinism_out)

    fixture = _load_json(fixture_path)
    fixture_hash = _json_hash(fixture)
    ordered_queries = _collect_queries(fixture)

    query_results: list[QueryRunResult] = []
    determinism_results: list[dict[str, Any]] = []

    for profile_id, query in ordered_queries:
        query_id = str(query["query_id"])
        query_text = str(query["query_text"])

        post_bundle = _run_context_load(
            coach_bin=args.coach_bin,
            project_dir=project_dir,
            query_text=query_text,
            profile_id=profile_id,
            weighting_mode=args.weighting_mode,
            max_files=args.max_files,
            max_chars_per_file=args.max_chars_per_file,
            timeout_seconds=args.timeout_seconds,
        )
        baseline_bundle = _run_legacy_loader(
            python_bin=args.python_bin,
            legacy_loader_script=legacy_loader_script,
            project_dir=project_dir,
            query_text=query_text,
            max_files=args.max_files,
            max_chars_per_file=args.max_chars_per_file,
            timeout_seconds=args.timeout_seconds,
        )

        post_files = list(post_bundle.get("files", []))
        baseline_files = list(baseline_bundle.get("files", []))
        post_task_files = [entry for entry in post_files if str(entry.get("selected_by", "")).startswith("task:")]
        baseline_task_files = [entry for entry in baseline_files if str(entry.get("selected_by", "")).startswith("task:")]
        post_eval_files = post_task_files if post_task_files else post_files
        baseline_eval_files = baseline_task_files if baseline_task_files else baseline_files
        post_gains = [_relevance_gain(query, entry) for entry in post_eval_files]
        baseline_gains = [_relevance_gain(query, entry) for entry in baseline_eval_files]
        post_top = post_eval_files[: args.top_k]
        baseline_top = baseline_eval_files[: args.top_k]
        ranking_hash = _normalized_ranking_hash(post_bundle)

        query_results.append(
            QueryRunResult(
                profile_id=profile_id,
                query_id=query_id,
                post_ndcg=_ndcg_at_k(post_gains, args.top_k),
                baseline_ndcg=_ndcg_at_k(baseline_gains, args.top_k),
                post_recall=_top_k_recall(query, post_top),
                baseline_recall=_top_k_recall(query, baseline_top),
                post_group_hits=_group_hits(query, post_top),
                baseline_group_hits=_group_hits(query, baseline_top),
                post_top_paths=[str(entry.get("path", "")) for entry in post_top],
                baseline_top_paths=[str(entry.get("path", "")) for entry in baseline_top],
                ranking_hash=ranking_hash,
            )
        )

        hashes = [ranking_hash]
        for _ in range(1, args.runs_per_query):
            repeat_bundle = _run_context_load(
                coach_bin=args.coach_bin,
                project_dir=project_dir,
                query_text=query_text,
                profile_id=profile_id,
                weighting_mode=args.weighting_mode,
                max_files=args.max_files,
                max_chars_per_file=args.max_chars_per_file,
                timeout_seconds=args.timeout_seconds,
            )
            hashes.append(_normalized_ranking_hash(repeat_bundle))

        unique_hashes = sorted(set(hashes))
        deterministic = len(unique_hashes) == 1
        determinism_results.append(
            {
                "profile_id": profile_id,
                "query_id": query_id,
                "runs": args.runs_per_query,
                "sample_hash": hashes[0],
                "unique_hash_count": len(unique_hashes),
                "deterministic": deterministic,
            }
        )

    ndcg_post_all = [item.post_ndcg for item in query_results]
    ndcg_base_all = [item.baseline_ndcg for item in query_results]
    recall_post_all = [item.post_recall for item in query_results]
    recall_base_all = [item.baseline_recall for item in query_results]

    post_median_ndcg = _median(ndcg_post_all)
    baseline_median_ndcg = _median(ndcg_base_all)
    ndcg_uplift_percent = 0.0
    if baseline_median_ndcg > 0:
        ndcg_uplift_percent = round(((post_median_ndcg - baseline_median_ndcg) / baseline_median_ndcg) * 100.0, 6)

    post_median_recall = _median(recall_post_all)
    baseline_median_recall = _median(recall_base_all)

    profile_ids = [str(profile.get("profile_id", "")) for profile in fixture.get("profiles", [])]
    profile_summaries: list[dict[str, Any]] = []
    for profile_id in profile_ids:
        profile_rows = [row for row in query_results if row.profile_id == profile_id]
        post_ndcg_values = [row.post_ndcg for row in profile_rows]
        base_ndcg_values = [row.baseline_ndcg for row in profile_rows]
        post_recall_values = [row.post_recall for row in profile_rows]
        base_recall_values = [row.baseline_recall for row in profile_rows]
        profile_post_ndcg = _median(post_ndcg_values)
        profile_base_ndcg = _median(base_ndcg_values)
        profile_uplift = 0.0
        if profile_base_ndcg > 0:
            profile_uplift = round(((profile_post_ndcg - profile_base_ndcg) / profile_base_ndcg) * 100.0, 6)
        profile_summaries.append(
            {
                "profile_id": profile_id,
                "query_count": len(profile_rows),
                "post_median_ndcg_at_5": profile_post_ndcg,
                "baseline_median_ndcg_at_5": profile_base_ndcg,
                "ndcg_uplift_percent": profile_uplift,
                "post_median_top_k_recall": _median(post_recall_values),
                "baseline_median_top_k_recall": _median(base_recall_values),
            }
        )

    relevance_query_rows = []
    for row in query_results:
        relevance_query_rows.append(
            {
                "profile_id": row.profile_id,
                "query_id": row.query_id,
                "post_change": {
                    "ndcg_at_5": row.post_ndcg,
                    "top_k_recall": row.post_recall,
                    "group_hits": row.post_group_hits,
                    "top_paths": row.post_top_paths,
                },
                "baseline_proxy": {
                    "ndcg_at_5": row.baseline_ndcg,
                    "top_k_recall": row.baseline_recall,
                    "group_hits": row.baseline_group_hits,
                    "top_paths": row.baseline_top_paths,
                },
                "delta": {
                    "ndcg_at_5": round(row.post_ndcg - row.baseline_ndcg, 6),
                    "top_k_recall": round(row.post_recall - row.baseline_recall, 6),
                },
            }
        )

    ndcg_target_met = ndcg_uplift_percent >= 10.0
    recall_target_met = (post_median_recall >= 0.8) and (post_median_recall >= baseline_median_recall)

    relevance_report = {
        "artifact": "phase2_retrieval_relevance_report_v0",
        "version": "v0",
        "fixture_artifact": fixture.get("artifact"),
        "fixture_version": fixture.get("version"),
        "fixture_hash": fixture_hash,
        "coach_bin": args.coach_bin,
        "legacy_baseline_proxy": {
            "script": str(legacy_loader_script),
            "description": "Legacy deterministic context loader used as pre-change baseline proxy.",
        },
        "top_k": args.top_k,
        "weighting_mode": args.weighting_mode,
        "query_results": relevance_query_rows,
        "profile_summaries": profile_summaries,
        "aggregate": {
            "query_count": len(query_results),
            "post_median_ndcg_at_5": post_median_ndcg,
            "baseline_median_ndcg_at_5": baseline_median_ndcg,
            "ndcg_uplift_percent": ndcg_uplift_percent,
            "post_median_top_k_recall": post_median_recall,
            "baseline_median_top_k_recall": baseline_median_recall,
        },
        "targets": {
            "ndcg_uplift_percent_min": 10.0,
            "top_k_recall_min": 0.8,
            "top_k_recall_not_below_baseline": True,
            "ndcg_target_met": ndcg_target_met,
            "top_k_recall_target_met": recall_target_met,
            "target_met": ndcg_target_met and recall_target_met,
        },
        "scoring_contract": {
            "version": "v0",
            "relevance_gain_formula": "signal_hit + tag_hit + overlap_gain (exclude-hit => 0)",
            "signal_hit": "any top document contains token from must_include_signals_any",
            "tag_hit": "any top document contains token from must_include_tags_any",
            "overlap_gain": "min(1.0, 1.5 * token_overlap_ratio(query_text, document_text))",
            "top_k_recall_definition": "required-group hit rate over must_include_signals_any and must_include_tags_any (0 if excluded token appears)",
        },
        "run_at": _now_iso(),
    }

    deterministic_count = sum(1 for row in determinism_results if row["deterministic"])
    query_count = len(determinism_results)
    consistency_rate = round(deterministic_count / query_count, 6) if query_count else 0.0

    determinism_report = {
        "artifact": "phase2_retrieval_determinism_report_v0",
        "version": "v0",
        "fixture_artifact": fixture.get("artifact"),
        "fixture_version": fixture.get("version"),
        "fixture_hash": fixture_hash,
        "coach_bin": args.coach_bin,
        "weighting_mode": args.weighting_mode,
        "runs_per_query": args.runs_per_query,
        "hash_contract": {
            "version": "v0",
            "normalization": "retrieval_profile, weighting_mode, fallback_level, and ordered file ranking fields",
        },
        "results": determinism_results,
        "query_count": query_count,
        "deterministic_queries": deterministic_count,
        "consistency_rate": consistency_rate,
        "target_consistency_rate": 1.0,
        "deterministic_all": deterministic_count == query_count,
        "target_met": consistency_rate >= 1.0 and deterministic_count == query_count,
        "run_at": _now_iso(),
    }

    _write_json(relevance_out, relevance_report)
    _write_json(determinism_out, determinism_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

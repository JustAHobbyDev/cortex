#!/usr/bin/env python3
"""Generate Phase 4 promotion-path latency and CI-overhead reports."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import statistics
import subprocess
import tempfile
import time
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


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil((pct / 100.0) * len(ordered)))
    idx = min(len(ordered) - 1, rank - 1)
    return float(ordered[idx])


def _format_quality_gate_summary(proc: subprocess.CompletedProcess[str]) -> str:
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return "no_output"
    if proc.returncode != 0:
        return lines[-1]
    for line in reversed(lines):
        if line.endswith("PASS") or "PASS" in line:
            return line
    return lines[-1]


def _to_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return sorted(set(out))


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


def _normalize_candidates(raw_fixture: dict[str, Any]) -> list[dict[str, Any]]:
    tactical_candidates = raw_fixture.get("tactical_candidates")
    debt_items = raw_fixture.get("governance_debt_items")
    out: list[dict[str, Any]] = []
    if isinstance(tactical_candidates, list):
        for idx, item in enumerate(tactical_candidates, start=1):
            if not isinstance(item, dict):
                continue
            candidate_id = str(item.get("candidate_id", f"pc_{idx:03d}")).strip() or f"pc_{idx:03d}"
            title = str(item.get("title", f"Promotion candidate {idx}")).strip() or f"Promotion candidate {idx}"
            out.append(
                {
                    "candidate_id": candidate_id,
                    "title": title,
                    "summary": str(item.get("summary", "")).strip(),
                    "state": str(item.get("state", "ready")).strip().lower() or "ready",
                    "governance_impact": str(item.get("governance_impact", "medium")).strip().lower() or "medium",
                    "decision_refs": _to_string_list(item.get("decision_refs", [])),
                    "reflection_refs": _to_string_list(item.get("reflection_refs", [])),
                    "evidence_refs": _to_string_list(item.get("evidence_refs", [])),
                    "impacted_artifacts": _normalize_impacted_artifacts(item.get("impacted_artifacts", []), title),
                }
            )
    elif isinstance(debt_items, list):
        for idx, item in enumerate(debt_items, start=1):
            if not isinstance(item, dict):
                continue
            debt_id = str(item.get("debt_id", f"gd_{idx:03d}")).strip() or f"gd_{idx:03d}"
            state = str(item.get("state", "blocked")).strip().lower() or "blocked"
            out.append(
                {
                    "candidate_id": f"pc_{debt_id}",
                    "title": f"Governance debt {debt_id}",
                    "summary": str(item.get("next_action", "")).strip(),
                    "state": state,
                    "governance_impact": "high" if state == "blocked" else "medium",
                    "decision_refs": [],
                    "reflection_refs": [],
                    "evidence_refs": _to_string_list(item.get("dependency_refs", [])),
                    "impacted_artifacts": [],
                }
            )
    return out


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
            ]
        ).lower()
        hit_count = sum(1 for token in query_tokens if token in searchable)
        lexical_score = min(1.0, float(hit_count) / 6.0) if query_tokens else 0.0
        evidence_coverage = min(1.0, float(len(candidate.get("evidence_refs", []))) / 3.0)
        linkage_complete = bool(candidate.get("decision_refs")) and bool(candidate.get("reflection_refs"))
        linkage_score = 1.0 if linkage_complete else 0.0
        impact_priority, impact_score = _impact_priority(str(candidate.get("governance_impact", "")))
        combined_score = round(
            (weights["lexical_score"] * lexical_score)
            + (weights["evidence_coverage"] * evidence_coverage)
            + (weights["linkage_score"] * linkage_score)
            + (weights["impact_score"] * impact_score),
            6,
        )
        scored_rows.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "combined_score": combined_score,
                "evidence_coverage": round(evidence_coverage, 6),
                "governance_impact_priority": impact_priority,
            }
        )
    ranked = sorted(
        scored_rows,
        key=lambda item: (
            -float(item.get("combined_score", 0.0)),
            -float(item.get("evidence_coverage", 0.0)),
            int(item.get("governance_impact_priority", 99)),
            str(item.get("candidate_id", "")),
        ),
    )
    return ranked[:candidate_limit]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument(
        "--fixture-file",
        default=".cortex/reports/project_state/phase4_promotion_eval_fixture_freeze_v0.json",
    )
    parser.add_argument("--score-mode", choices=["uniform", "evidence_bias"], default="evidence_bias")
    parser.add_argument("--candidate-limit", type=int, default=8)
    parser.add_argument("--latency-runs-per-profile", type=int, default=30)
    parser.add_argument("--ci-runs", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--phase3-ci-report",
        default=".cortex/reports/project_state/phase3_ci_overhead_report_v0.json",
    )
    parser.add_argument(
        "--latency-out",
        default=".cortex/reports/project_state/phase4_latency_report_v0.json",
    )
    parser.add_argument(
        "--ci-overhead-out",
        default=".cortex/reports/project_state/phase4_ci_overhead_report_v0.json",
    )
    return parser


def _measure_latency(args: argparse.Namespace, project_dir: Path, freeze: dict[str, Any]) -> dict[str, Any]:
    scenario_map = {
        str(item["scenario_id"]): item for item in freeze.get("scenarios", []) if isinstance(item, dict)
    }
    query_map = {
        str(item["query_id"]): item for item in freeze.get("queries", []) if isinstance(item, dict)
    }

    profile_results: list[dict[str, Any]] = []
    all_durations: list[float] = []

    for profile in freeze.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        profile_id = str(profile.get("profile_id", ""))
        scenario_ids = [str(v) for v in profile.get("scenario_ids", [])]
        query_ids = [str(v) for v in profile.get("query_ids", [])]

        scenario_candidates: list[list[dict[str, Any]]] = []
        for scenario_id in scenario_ids:
            scenario = scenario_map.get(scenario_id)
            if scenario is None:
                raise SystemExit(f"missing scenario: {scenario_id}")
            fixture_ref = str(scenario.get("fixture_ref", "")).strip()
            fixture_payload = _load_json((project_dir / fixture_ref).resolve())
            if not isinstance(fixture_payload, dict):
                raise SystemExit(f"invalid fixture payload for scenario {scenario_id}")
            scenario_candidates.append(_normalize_candidates(fixture_payload))

        query_texts: list[str] = []
        for query_id in query_ids:
            query = query_map.get(query_id)
            if query is None:
                raise SystemExit(f"missing query: {query_id}")
            query_texts.append(str(query.get("query_text", "")))

        durations: list[float] = []
        for _ in range(max(1, int(args.latency_runs_per_profile))):
            started = time.perf_counter()
            for candidates in scenario_candidates:
                for query_text in query_texts:
                    _rank_candidates(
                        candidates,
                        query=query_text,
                        score_mode=str(args.score_mode),
                        candidate_limit=max(1, int(args.candidate_limit)),
                    )
            durations.append(time.perf_counter() - started)

        all_durations.extend(durations)
        profile_results.append(
            {
                "profile_id": profile_id,
                "runs": len(durations),
                "durations_seconds": durations,
                "median_seconds": _median(durations),
                "p95_seconds": _percentile(durations, 95.0),
                "max_seconds": max(durations) if durations else 0.0,
            }
        )

    p95_overall = _percentile(all_durations, 95.0)
    payload: dict[str, Any] = {
        "version": "v0",
        "artifact": "phase4_latency_report_v0",
        "run_at": _now_iso(),
        "project_dir": str(project_dir),
        "score_mode": str(args.score_mode),
        "candidate_limit": max(1, int(args.candidate_limit)),
        "latency_runs_per_profile": max(1, int(args.latency_runs_per_profile)),
        "target_p95_seconds": 2.5,
        "summary": {
            "profile_count": len(profile_results),
            "run_count": len(all_durations),
            "median_seconds": _median(all_durations),
            "p95_seconds": p95_overall,
            "max_seconds": max(all_durations) if all_durations else 0.0,
        },
        "target_met": p95_overall <= 2.5,
        "profiles": profile_results,
    }
    return payload


def _prepare_ephemeral_workspace(project_dir: Path) -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="phase4_perf_workspace_"))
    workspace = temp_root / "repo"
    shutil.copytree(
        project_dir,
        workspace,
        ignore=shutil.ignore_patterns(".git", ".uv-cache", "__pycache__", "*.pyc", ".pytest_cache"),
    )
    subprocess.run(["git", "init"], cwd=str(workspace), check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "phase4-perf@example.com"], cwd=str(workspace), check=True)
    subprocess.run(["git", "config", "user.name", "Phase4 Perf"], cwd=str(workspace), check=True)
    subprocess.run(["git", "add", "."], cwd=str(workspace), check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "phase4 perf baseline"], cwd=str(workspace), check=True, capture_output=True)
    return workspace


def _measure_ci_overhead(args: argparse.Namespace, project_dir: Path) -> dict[str, Any]:
    phase3_report = _load_json((project_dir / args.phase3_ci_report).resolve())
    if not isinstance(phase3_report, dict):
        raise SystemExit(f"invalid phase3 baseline report: {args.phase3_ci_report}")
    phase3_median = float(phase3_report.get("phase3_median_seconds", 0.0) or 0.0)

    workspace = _prepare_ephemeral_workspace(project_dir)
    durations: list[float] = []
    run_summaries: list[dict[str, Any]] = []

    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str((project_dir / ".uv-cache").resolve())
    env["CORTEX_QG_SKIP_FOCUSED_TESTS"] = "1"

    try:
        for run_idx in range(1, max(1, int(args.ci_runs)) + 1):
            started = time.perf_counter()
            proc = subprocess.run(
                ["bash", "scripts/quality_gate_ci_v0.sh"],
                cwd=str(workspace),
                text=True,
                capture_output=True,
                check=False,
                timeout=int(args.timeout_seconds),
                env=env,
            )
            elapsed = time.perf_counter() - started
            durations.append(elapsed)
            run_summaries.append(
                {
                    "run": run_idx,
                    "returncode": proc.returncode,
                    "duration_seconds": elapsed,
                    "summary": _format_quality_gate_summary(proc),
                }
            )
    finally:
        shutil.rmtree(workspace.parent, ignore_errors=True)

    phase4_median = _median(durations)
    delta_percent = ((phase4_median - phase3_median) / phase3_median * 100.0) if phase3_median > 0 else 0.0
    all_pass = all(int(item.get("returncode", 1)) == 0 for item in run_summaries)
    target_met = all_pass and delta_percent <= 10.0

    payload: dict[str, Any] = {
        "version": "v0",
        "artifact": "phase4_ci_overhead_report_v0",
        "run_at": _now_iso(),
        "measurement_mode": "required_ci_gate_vs_phase3_baseline_ephemeral_git_workspace_offline_probe",
        "phase3_baseline_source": args.phase3_ci_report,
        "phase3_median_seconds": phase3_median,
        "phase4_required_gate": "scripts/quality_gate_ci_v0.sh",
        "phase4_runs": max(1, int(args.ci_runs)),
        "phase4_durations_seconds": durations,
        "phase4_median_seconds": phase4_median,
        "delta_percent": delta_percent,
        "target_max_delta_percent": 10.0,
        "target_met": target_met,
        "all_runs_passed": all_pass,
        "phase4_run_summaries": run_summaries,
        "residual_risk_tracking": {
            "source_report": ".cortex/reports/project_state/phase3_gate_d_measurement_closeout_v0.md",
            "weekly_ci_overhead_tracking_required": True,
            "standalone_parity_guardrail": "quality_gate_ci_v0.sh must remain synchronized with quality_gate_v0.sh",
            "focused_tests_probe_mode": "skipped via CORTEX_QG_SKIP_FOCUSED_TESTS=1 for offline-overhead reproducibility",
        },
    }
    return payload


def main() -> int:
    args = _build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    fixture_path = (project_dir / args.fixture_file).resolve()
    latency_out = (project_dir / args.latency_out).resolve()
    ci_overhead_out = (project_dir / args.ci_overhead_out).resolve()

    freeze = _load_json(fixture_path)
    if not isinstance(freeze, dict):
        raise SystemExit(f"fixture freeze is not a JSON object: {fixture_path}")

    latency_payload = _measure_latency(args, project_dir, freeze)
    ci_overhead_payload = _measure_ci_overhead(args, project_dir)

    _write_json(latency_out, latency_payload)
    _write_json(ci_overhead_out, ci_overhead_payload)

    return 0 if latency_payload.get("target_met") and ci_overhead_payload.get("target_met") else 1


if __name__ == "__main__":
    raise SystemExit(main())

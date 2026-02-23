#!/usr/bin/env python3
"""Fail closed when machine-caught mistake claims lack provenance requirements."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONTRACT_FILE = Path("contracts/mistake_candidate_schema_v0.json")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload


def _load_contract(path: Path) -> dict[str, Any]:
    payload = _load_json_object(path)
    if payload.get("version") != "v0":
        raise ValueError(f"unsupported contract version in {path}: {payload.get('version')!r}")

    required_provenance_fields = payload.get("required_provenance_fields")
    if not isinstance(required_provenance_fields, list) or not required_provenance_fields:
        raise ValueError(f"contract missing required_provenance_fields: {path}")
    if not all(isinstance(item, str) and item.strip() for item in required_provenance_fields):
        raise ValueError(f"contract has invalid required_provenance_fields: {path}")

    expected_required = {"detected_by", "detector", "evidence_refs", "rule_violated", "confidence", "status"}
    actual_required = {str(item).strip() for item in required_provenance_fields}
    if not expected_required.issubset(actual_required):
        missing = sorted(expected_required - actual_required)
        raise ValueError(f"contract required_provenance_fields missing expected keys: {missing}")

    candidate_file = payload.get("candidate_file")
    if not isinstance(candidate_file, str) or not candidate_file.strip():
        raise ValueError(f"contract missing candidate_file: {path}")

    for key in ("allowed_detected_by", "allowed_confidence", "allowed_status"):
        values = payload.get(key)
        if not isinstance(values, list) or not values:
            raise ValueError(f"contract missing {key}: {path}")
        if not all(isinstance(item, str) and item.strip() for item in values):
            raise ValueError(f"contract has invalid {key}: {path}")

    machine_requirements = payload.get("machine_requirements")
    if not isinstance(machine_requirements, dict):
        raise ValueError(f"contract missing machine_requirements: {path}")
    required_detector_fields = machine_requirements.get("required_detector_fields")
    if not isinstance(required_detector_fields, list) or not required_detector_fields:
        raise ValueError(f"contract missing machine_requirements.required_detector_fields: {path}")
    if not all(isinstance(item, str) and item.strip() for item in required_detector_fields):
        raise ValueError(f"contract has invalid required_detector_fields: {path}")
    minimum_evidence_refs = machine_requirements.get("minimum_evidence_refs")
    if not isinstance(minimum_evidence_refs, int) or minimum_evidence_refs < 1:
        raise ValueError(f"contract has invalid minimum_evidence_refs: {path}")

    legacy_backfill = payload.get("legacy_backfill")
    if not isinstance(legacy_backfill, dict):
        raise ValueError(f"contract missing legacy_backfill: {path}")
    legacy_detected_by = legacy_backfill.get("detected_by_value")
    if not isinstance(legacy_detected_by, str) or not legacy_detected_by.strip():
        raise ValueError(f"contract missing legacy_backfill.detected_by_value: {path}")
    legacy_required_fields = legacy_backfill.get("required_fields")
    if not isinstance(legacy_required_fields, list) or not legacy_required_fields:
        raise ValueError(f"contract missing legacy_backfill.required_fields: {path}")
    if not all(isinstance(item, str) and item.strip() for item in legacy_required_fields):
        raise ValueError(f"contract has invalid legacy_backfill.required_fields: {path}")

    return payload


def _load_candidates(path: Path) -> dict[str, Any]:
    payload = _load_json_object(path)
    if payload.get("version") != "v0":
        raise ValueError(f"unsupported candidate file version in {path}: {payload.get('version')!r}")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError(f"candidate file missing candidates list: {path}")
    return payload


def _finding(check: str, message: str, **extra: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "check": check,
        "severity": "error",
        "message": message,
    }
    item.update(extra)
    return item


def _normalize_non_empty_str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized if normalized else None


def _format_text(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload.get('status')}",
        f"run_at: {payload.get('run_at')}",
        f"candidate_count: {payload.get('candidate_count', 0)}",
        f"machine_claim_count: {payload.get('machine_claim_count', 0)}",
        f"legacy_claim_count: {payload.get('legacy_claim_count', 0)}",
        f"finding_count: {payload.get('finding_count', 0)}",
    ]
    findings = payload.get("findings", [])
    if isinstance(findings, list) and findings:
        lines.append("findings:")
        for item in findings:
            if not isinstance(item, dict):
                continue
            candidate_id = item.get("candidate_id")
            suffix = f" candidate_id={candidate_id}" if candidate_id else ""
            lines.append(f"- {item.get('check')}{suffix}: {item.get('message')}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Machine-caught mistake provenance enforcement gate.")
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--contract-file", default=str(DEFAULT_CONTRACT_FILE))
    parser.add_argument("--format", default="text", choices=("text", "json"))
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    contract_file = Path(args.contract_file)
    if not contract_file.is_absolute():
        contract_file = project_dir / contract_file

    findings: list[dict[str, Any]] = []
    candidate_count = 0
    machine_claim_count = 0
    legacy_claim_count = 0

    try:
        contract = _load_contract(contract_file)

        candidate_file = Path(str(contract["candidate_file"]))
        if not candidate_file.is_absolute():
            candidate_file = project_dir / candidate_file
        if not candidate_file.exists():
            raise ValueError(f"candidate file does not exist: {candidate_file}")

        candidates_payload = _load_candidates(candidate_file)
        candidates_raw = candidates_payload.get("candidates", [])
        if not isinstance(candidates_raw, list):
            raise ValueError(f"candidate file candidates must be a list: {candidate_file}")

        required_fields = [str(item).strip() for item in contract["required_provenance_fields"]]
        allowed_detected_by = {str(item).strip() for item in contract["allowed_detected_by"]}
        allowed_confidence = {str(item).strip() for item in contract["allowed_confidence"]}
        allowed_status = {str(item).strip() for item in contract["allowed_status"]}
        machine_required_detector_fields = [
            str(item).strip() for item in contract["machine_requirements"]["required_detector_fields"]
        ]
        minimum_evidence_refs = int(contract["machine_requirements"]["minimum_evidence_refs"])
        legacy_detected_by = str(contract["legacy_backfill"]["detected_by_value"]).strip()
        legacy_required_fields = [str(item).strip() for item in contract["legacy_backfill"]["required_fields"]]

        seen_candidate_ids: set[str] = set()
        for idx, item in enumerate(candidates_raw):
            if not isinstance(item, dict):
                findings.append(
                    _finding(
                        "candidate_payload_not_object",
                        "Candidate entry must be an object.",
                        index=idx,
                    )
                )
                continue

            candidate_count += 1
            candidate_id = _normalize_non_empty_str(item.get("candidate_id")) or f"candidate[{idx}]"
            if candidate_id in seen_candidate_ids:
                findings.append(
                    _finding(
                        "duplicate_candidate_id",
                        "Candidate ID must be unique.",
                        candidate_id=candidate_id,
                    )
                )
            seen_candidate_ids.add(candidate_id)

            for field in required_fields:
                if field not in item:
                    findings.append(
                        _finding(
                            "missing_required_provenance_field",
                            "Candidate is missing required provenance field.",
                            candidate_id=candidate_id,
                            field=field,
                        )
                    )

            detected_by = _normalize_non_empty_str(item.get("detected_by"))
            confidence = _normalize_non_empty_str(item.get("confidence"))
            status_value = _normalize_non_empty_str(item.get("status"))

            if detected_by is None:
                findings.append(
                    _finding(
                        "invalid_detected_by_value",
                        "detected_by must be a non-empty string.",
                        candidate_id=candidate_id,
                    )
                )
            elif detected_by not in allowed_detected_by:
                findings.append(
                    _finding(
                        "unsupported_detected_by_value",
                        "detected_by uses unsupported value.",
                        candidate_id=candidate_id,
                        detected_by=detected_by,
                    )
                )

            if confidence is None:
                findings.append(
                    _finding(
                        "invalid_confidence_value",
                        "confidence must be a non-empty string.",
                        candidate_id=candidate_id,
                    )
                )
            elif confidence not in allowed_confidence:
                findings.append(
                    _finding(
                        "unsupported_confidence_value",
                        "confidence uses unsupported value.",
                        candidate_id=candidate_id,
                        confidence=confidence,
                    )
                )

            if status_value is None:
                findings.append(
                    _finding(
                        "invalid_status_value",
                        "status must be a non-empty string.",
                        candidate_id=candidate_id,
                    )
                )
            elif status_value not in allowed_status:
                findings.append(
                    _finding(
                        "unsupported_status_value",
                        "status uses unsupported value.",
                        candidate_id=candidate_id,
                        status=status_value,
                    )
                )

            detector = item.get("detector")
            if not isinstance(detector, dict):
                findings.append(
                    _finding(
                        "invalid_detector_payload",
                        "detector must be an object.",
                        candidate_id=candidate_id,
                    )
                )
            else:
                for field in machine_required_detector_fields:
                    if _normalize_non_empty_str(detector.get(field)) is None:
                        findings.append(
                            _finding(
                                "missing_detector_field",
                                "detector is missing required field.",
                                candidate_id=candidate_id,
                                field=field,
                            )
                        )

            evidence_refs = item.get("evidence_refs")
            evidence_count = 0
            if not isinstance(evidence_refs, list):
                findings.append(
                    _finding(
                        "invalid_evidence_refs_type",
                        "evidence_refs must be a list.",
                        candidate_id=candidate_id,
                    )
                )
            else:
                for ref in evidence_refs:
                    if _normalize_non_empty_str(ref) is not None:
                        evidence_count += 1
                    else:
                        findings.append(
                            _finding(
                                "invalid_evidence_ref",
                                "evidence_refs contains an empty/non-string item.",
                                candidate_id=candidate_id,
                            )
                        )

            rule_violated = _normalize_non_empty_str(item.get("rule_violated"))
            if rule_violated is None:
                findings.append(
                    _finding(
                        "missing_rule_violated",
                        "rule_violated must be a non-empty string.",
                        candidate_id=candidate_id,
                    )
                )

            if detected_by == "machine":
                machine_claim_count += 1
                if evidence_count < minimum_evidence_refs:
                    findings.append(
                        _finding(
                            "machine_claim_missing_evidence",
                            "Machine-caught claim has insufficient evidence references.",
                            candidate_id=candidate_id,
                            evidence_count=evidence_count,
                            minimum_required=minimum_evidence_refs,
                        )
                    )
                if confidence == legacy_detected_by or status_value == legacy_detected_by:
                    findings.append(
                        _finding(
                            "machine_claim_invalid_legacy_marker",
                            "Machine-caught claims cannot use legacy confidence/status markers.",
                            candidate_id=candidate_id,
                            confidence=confidence,
                            status=status_value,
                        )
                    )

            if detected_by == legacy_detected_by:
                legacy_claim_count += 1
                for field in legacy_required_fields:
                    if _normalize_non_empty_str(item.get(field)) is None:
                        findings.append(
                            _finding(
                                "legacy_missing_backfill_field",
                                "Legacy claim is missing required migration/backfill field.",
                                candidate_id=candidate_id,
                                field=field,
                            )
                        )

                if confidence != legacy_detected_by:
                    findings.append(
                        _finding(
                            "legacy_confidence_mismatch",
                            "Legacy claim must use legacy confidence marker.",
                            candidate_id=candidate_id,
                            confidence=confidence,
                        )
                    )
                if status_value != legacy_detected_by:
                    findings.append(
                        _finding(
                            "legacy_status_mismatch",
                            "Legacy claim must use legacy status marker.",
                            candidate_id=candidate_id,
                            status=status_value,
                        )
                    )

                backfill_due = _normalize_non_empty_str(item.get("backfill_due"))
                if backfill_due is not None:
                    try:
                        date.fromisoformat(backfill_due)
                    except ValueError:
                        findings.append(
                            _finding(
                                "legacy_backfill_due_invalid_date",
                                "backfill_due must be ISO date (YYYY-MM-DD).",
                                candidate_id=candidate_id,
                                backfill_due=backfill_due,
                            )
                        )

    except Exception as exc:  # noqa: BLE001
        findings.append(
            _finding(
                "mistake_candidate_gate_runtime_error",
                str(exc),
            )
        )

    status = "fail" if findings else "pass"
    payload: dict[str, Any] = {
        "version": "v0",
        "run_at": _now_iso(),
        "status": status,
        "project_dir": str(project_dir),
        "contract_file": str(contract_file),
        "candidate_count": candidate_count,
        "machine_claim_count": machine_claim_count,
        "legacy_claim_count": legacy_claim_count,
        "finding_count": len(findings),
        "findings": findings,
    }

    if args.format == "json":
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_text(payload))
        sys.stdout.write("\n")

    return 1 if status == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())

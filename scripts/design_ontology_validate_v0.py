#!/usr/bin/env python3
"""
Validate design ontology instance files and emit deterministic reports.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema


DEFAULT_SCHEMA = Path("templates/design_ontology_v0.schema.json")
DEFAULT_GLOB = "templates/design_ontology_*.json"
DEFAULT_JSON_REPORT = Path(".cortex/reports/design_ontology_validation_v0.json")
DEFAULT_MD_REPORT = Path(".cortex/reports/design_ontology_validation_v0.md")
VAGUE_TERMS = {"modern", "clean", "nice", "good", "cool", "sleek", "beautiful"}
REQUIRED_LANGUAGE_PATHS = [
    "layout.grid",
    "layout.spacing",
    "layout.structure",
    "typography.hero",
    "typography.body",
    "surface.base",
    "surface.accent",
    "motion.scroll",
    "motion.hover",
    "influence.primary",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema-file", default=str(DEFAULT_SCHEMA))
    parser.add_argument("--instance-glob", default=DEFAULT_GLOB)
    parser.add_argument("--json-report", default=str(DEFAULT_JSON_REPORT))
    parser.add_argument("--md-report", default=str(DEFAULT_MD_REPORT))
    return parser.parse_args()


def get_path(obj: dict[str, Any], path: str) -> Any:
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def syntax_check(path: Path) -> tuple[str, str]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return "pass", ""
    except Exception as exc:  # noqa: BLE001
        return "fail", f"json parse failed: {exc}"


def schema_check(instance: Path, schema: Path) -> tuple[str, str]:
    try:
        schema_obj = json.loads(schema.read_text(encoding="utf-8"))
        instance_obj = json.loads(instance.read_text(encoding="utf-8"))
        jsonschema.validate(instance=instance_obj, schema=schema_obj)
        return "pass", ""
    except Exception as exc:  # noqa: BLE001
        return "fail", str(exc)


def language_quality_check(path: Path) -> tuple[str, list[str]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    notes: list[str] = []
    for field in REQUIRED_LANGUAGE_PATHS:
        value = get_path(obj, field)
        if not isinstance(value, str) or not value.strip():
            notes.append(f"{field}: missing or empty")
            continue
        words = re.findall(r"[a-zA-Z]+", value.lower())
        if len(words) <= 2 and any(w in VAGUE_TERMS for w in words):
            notes.append(f"{field}: overly vague value '{value}'")
    return ("pass", notes) if not notes else ("fail", notes)


def main() -> int:
    args = parse_args()
    schema = Path(args.schema_file)
    instances = sorted(
        p
        for p in Path(".").glob(args.instance_glob)
        if p.name != schema.name
    )
    json_report_path = Path(args.json_report)
    md_report_path = Path(args.md_report)

    results: list[dict[str, Any]] = []
    overall_pass = True

    for instance in instances:
        syntax_state, syntax_note = syntax_check(instance)
        schema_state, schema_note = ("skip", "syntax failure")
        language_state, language_notes = ("skip", ["syntax failure"])

        if syntax_state == "pass":
            schema_state, schema_note = schema_check(instance, schema)
            if schema_state == "pass":
                language_state, language_notes = language_quality_check(instance)
            else:
                language_state, language_notes = ("skip", ["schema failure"])

        notes: list[str] = []
        if syntax_note:
            notes.append(syntax_note)
        if schema_note:
            notes.append(schema_note)
        notes.extend(language_notes if isinstance(language_notes, list) else [])

        file_pass = all(state == "pass" for state in [syntax_state, schema_state, language_state])
        if not file_pass:
            overall_pass = False

        results.append(
            {
                "instance": str(instance),
                "syntax": syntax_state,
                "schema": schema_state,
                "language_quality": language_state,
                "notes": notes,
            }
        )

    report = {
        "version": "v0",
        "run_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema_path": str(schema),
        "instances_checked": [str(p) for p in instances],
        "results": results,
        "status": "pass" if overall_pass else "fail",
    }

    json_report_path.parent.mkdir(parents=True, exist_ok=True)
    json_report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Design Ontology Validation Report v0",
        "",
        f"- status: `{report['status']}`",
        f"- run_at: `{report['run_at']}`",
        f"- schema: `{report['schema_path']}`",
        f"- instances_checked: `{len(instances)}`",
        "",
        "## Results",
    ]
    if not results:
        lines.append("- No matching instances found.")
    else:
        for item in results:
            lines.append(
                f"- `{item['instance']}` | syntax={item['syntax']} schema={item['schema']} language={item['language_quality']}"
            )
            for note in item["notes"]:
                lines.append(f"  - {note}")
    md_report_path.parent.mkdir(parents=True, exist_ok=True)
    md_report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

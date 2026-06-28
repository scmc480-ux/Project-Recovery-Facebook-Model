from __future__ import annotations

from pathlib import Path
from typing import Any


def summary_markdown(case_id: str, source: Path, objects: list[dict[str, Any]], validation: dict[str, Any]) -> str:
    counts = _counts(objects)
    return "\n".join(
        [
            f"# Summary - {case_id}",
            "",
            f"Source: `{source}`",
            "",
            "## What Was Analyzed",
            "",
            "- Facebook JSON and HTML export files readable by Facebook Reader v1.",
            "",
            "## Object Counts",
            "",
            *[f"- {key}: {value}" for key, value in sorted(counts.items())],
            "",
            "## Validation",
            "",
            f"- Status: {validation['status']}",
            f"- Errors: {validation['error_count']}",
            f"- Warnings: {validation['warning_count']}",
            "",
            "## Output References",
            "",
            "- `03_WORKBOOKS/messages.xlsx`",
            "- `03_WORKBOOKS/timeline.xlsx`",
            "- `03_WORKBOOKS/entities.xlsx`",
            "",
        ]
    )


def full_report_markdown(case_id: str, source: Path, objects: list[dict[str, Any]], validation: dict[str, Any]) -> str:
    counts = _counts(objects)
    warnings = validation.get("warnings") or ["None"]
    return "\n".join(
        [
            f"# Full Report - {case_id}",
            "",
            "## Scope",
            "",
            f"This report covers the Facebook export source `{source}`.",
            "",
            "## Method",
            "",
            "The reader inventoried source files, preserved hashes, extracted Facebook JSON/HTML records, normalized them into engine objects, validated object requirements, and promoted outputs into the canonical case tree.",
            "",
            "## Verbatim Summary",
            "",
            f"Message objects: {counts.get('message_object', 0)}",
            "",
            "## Timeline Summary",
            "",
            f"Event objects: {counts.get('event_object', 0)}",
            "",
            "## Entity Summary",
            "",
            f"Entity objects: {counts.get('entity_object', 0)}",
            "",
            "## Gaps And Warnings",
            "",
            *[f"- {item}" for item in warnings],
            "",
            "## References",
            "",
            "- `06_PROVENANCE/source_to_output_map.json`",
            "- `07_VALIDATION/validation_status.json`",
            "",
        ]
    )


def client_summary_markdown(case_id: str, objects: list[dict[str, Any]], validation: dict[str, Any]) -> str:
    counts = _counts(objects)
    return "\n".join(
        [
            f"# Client Summary - {case_id}",
            "",
            "## Confirmed",
            "",
            f"- Recovered message rows: {counts.get('message_object', 0)}",
            f"- Recovered source artifacts: {counts.get('artifact_object', 0)}",
            "",
            "## Probable Or Derived",
            "",
            f"- Derived timeline/activity rows: {counts.get('event_object', 0)}",
            "",
            "## Unresolved",
            "",
            f"- Validation warnings: {validation['warning_count']}",
            "",
            "## Deliverables",
            "",
            "- Workbooks are in `03_WORKBOOKS/`.",
            "- Provenance is in `06_PROVENANCE/`.",
            "- Validation records are in `07_VALIDATION/`.",
            "",
        ]
    )


def _counts(objects: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for obj in objects:
        key = obj.get("object_type", "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts

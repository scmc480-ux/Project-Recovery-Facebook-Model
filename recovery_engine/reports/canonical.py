from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from recovery_engine.intake.container import SourceFile
from recovery_engine.objects.schema import TRUTH_VERBATIM
from recovery_engine.reports.markdown import client_summary_markdown, full_report_markdown, summary_markdown
from recovery_engine.reports.workbook import write_workbooks
from recovery_engine.utils.jsonl import write_jsonl


def write_canonical_case(
    *,
    output_root: Path,
    case_id: str,
    source: Path,
    source_fingerprint: str,
    inventory: list[SourceFile],
    raw_records: list[dict[str, Any]],
    objects: list[dict[str, Any]],
    validation: dict[str, Any],
) -> Path:
    case_root = output_root / case_id
    sections = [
        "01_MASTER/messages",
        "01_MASTER/events",
        "01_MASTER/files",
        "01_MASTER/raw_artifacts",
        "01_MASTER/exact_metadata",
        "02_DERIVED/timelines",
        "02_DERIVED/conversations",
        "02_DERIVED/entities",
        "02_DERIVED/anomalies",
        "03_WORKBOOKS",
        "04_REPORTS",
        "05_RELEASE",
        "06_PROVENANCE",
        "07_VALIDATION",
        "08_LOGS/execution",
        "09_SYSTEM_REFERENCE",
    ]
    for section in sections:
        (case_root / section).mkdir(parents=True, exist_ok=True)

    messages = [obj for obj in objects if obj.get("object_type") == "message_object"]
    events = [obj for obj in objects if obj.get("object_type") == "event_object"]
    entities = [obj for obj in objects if obj.get("object_type") == "entity_object"]
    conversations = [obj for obj in objects if obj.get("object_type") == "conversation_object"]
    artifacts = [obj for obj in objects if obj.get("object_type") == "artifact_object"]

    write_jsonl(case_root / "01_MASTER/messages/messages.jsonl", messages)
    write_jsonl(case_root / "01_MASTER/events/events.jsonl", [obj for obj in events if obj.get("truth_class") == TRUTH_VERBATIM])
    write_jsonl(case_root / "01_MASTER/raw_artifacts/artifacts.jsonl", artifacts)
    write_jsonl(case_root / "02_DERIVED/timelines/timeline.jsonl", sorted(events + messages, key=lambda obj: obj.get("timestamp") or "9999"))
    write_jsonl(case_root / "02_DERIVED/conversations/conversations.jsonl", conversations)
    write_jsonl(case_root / "02_DERIVED/entities/entities.jsonl", entities)

    _write_source_inventory(case_root / "01_MASTER/exact_metadata/source_manifest.json", source, source_fingerprint, inventory)
    _write_chain_of_custody(case_root / "06_PROVENANCE/chain_of_custody.csv", case_id, source, source_fingerprint)
    _write_source_to_output_map(case_root / "06_PROVENANCE/source_to_output_map.json", objects)
    _write_derivation_map(case_root / "06_PROVENANCE/derivation_map.json", objects)

    (case_root / "07_VALIDATION/validation_status.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (case_root / "07_VALIDATION/rejected_items.json").write_text(json.dumps(validation["rejected_items"], indent=2), encoding="utf-8")
    _write_confidence_registry(case_root / "07_VALIDATION/confidence_registry.json", objects)

    write_workbooks(case_root / "03_WORKBOOKS", messages=messages, events=events, entities=entities)

    (case_root / "04_REPORTS/summary.md").write_text(summary_markdown(case_id, source, objects, validation), encoding="utf-8")
    (case_root / "04_REPORTS/full_report.md").write_text(full_report_markdown(case_id, source, objects, validation), encoding="utf-8")
    (case_root / "04_REPORTS/client_summary.md").write_text(client_summary_markdown(case_id, objects, validation), encoding="utf-8")

    output_index = _output_index(case_root)
    (case_root / "OUTPUT_INDEX.json").write_text(json.dumps(output_index, indent=2), encoding="utf-8")
    (case_root / "OUTPUT_INDEX.md").write_text(_output_index_markdown(output_index), encoding="utf-8")
    (case_root / "00_README.md").write_text(_case_readme(case_id, source, source_fingerprint, objects, validation), encoding="utf-8")

    release_manifest = {
        "case_id": case_id,
        "created_at": _now(),
        "status": "ready_for_review" if validation["status"] == "pass" else "validation_failed",
        "public_reader": "facebook_reader_v1",
        "release_note": "Review outputs before client delivery.",
    }
    (case_root / "05_RELEASE/delivery_manifest.json").write_text(json.dumps(release_manifest, indent=2), encoding="utf-8")

    profile = {
        "case_id": case_id,
        "reader": "facebook_reader_v1",
        "source": str(source),
        "source_fingerprint": source_fingerprint,
        "object_count": len(objects),
    }
    (case_root / "09_SYSTEM_REFERENCE/case_output_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    (case_root / "09_SYSTEM_REFERENCE/output_contract.json").write_text(json.dumps({"canonical_sections": output_index["sections"]}, indent=2), encoding="utf-8")

    run_log = {"timestamp": _now(), "case_id": case_id, "objects": len(objects), "validation": validation["status"]}
    (case_root / "08_LOGS/execution/run_log.jsonl").write_text(json.dumps(run_log, sort_keys=True) + "\n", encoding="utf-8")
    return case_root


def _write_source_inventory(path: Path, source: Path, source_fingerprint: str, inventory: list[SourceFile]) -> None:
    payload = {
        "source": str(source),
        "source_fingerprint": source_fingerprint,
        "file_count": len(inventory),
        "files": [item.__dict__ for item in inventory],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_chain_of_custody(path: Path, case_id: str, source: Path, source_fingerprint: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "case_id", "action", "details", "source_fingerprint"])
        writer.writeheader()
        writer.writerow(
            {
                "timestamp": _now(),
                "case_id": case_id,
                "action": "source_read",
                "details": str(source),
                "source_fingerprint": source_fingerprint,
            }
        )


def _write_source_to_output_map(path: Path, objects: list[dict[str, Any]]) -> None:
    mapping = [
        {
            "object_id": obj.get("object_id"),
            "object_type": obj.get("object_type"),
            "source_path": obj.get("source_ref", {}).get("source_path"),
            "truth_class": obj.get("truth_class"),
        }
        for obj in objects
    ]
    path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")


def _write_derivation_map(path: Path, objects: list[dict[str, Any]]) -> None:
    mapping = [
        {
            "object_id": obj.get("object_id"),
            "stage_origin": obj.get("stage_origin"),
            "provenance_ref": obj.get("provenance_ref"),
        }
        for obj in objects
    ]
    path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")


def _write_confidence_registry(path: Path, objects: list[dict[str, Any]]) -> None:
    registry: dict[str, int] = {}
    for obj in objects:
        key = f"{obj.get('truth_class')}|{obj.get('confidence')}"
        registry[key] = registry.get(key, 0) + 1
    path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")


def _output_index(case_root: Path) -> dict[str, Any]:
    files = [
        str(path.relative_to(case_root)).replace("\\", "/")
        for path in sorted(case_root.rglob("*"))
        if path.is_file() and path.name not in {"OUTPUT_INDEX.json", "OUTPUT_INDEX.md"}
    ]
    return {
        "created_at": _now(),
        "sections": [
            "01_MASTER",
            "02_DERIVED",
            "03_WORKBOOKS",
            "04_REPORTS",
            "05_RELEASE",
            "06_PROVENANCE",
            "07_VALIDATION",
            "08_LOGS",
            "09_SYSTEM_REFERENCE",
        ],
        "files": files,
    }


def _output_index_markdown(index: dict[str, Any]) -> str:
    lines = ["# Output Index", "", f"Created: {index['created_at']}", ""]
    for file in index["files"]:
        lines.append(f"- `{file}`")
    return "\n".join(lines) + "\n"


def _case_readme(case_id: str, source: Path, source_fingerprint: str, objects: list[dict[str, Any]], validation: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {case_id}",
            "",
            "Generated by Project Recovery Facebook Reader v1.",
            "",
            f"- Source: `{source}`",
            f"- Source fingerprint: `{source_fingerprint}`",
            f"- Object count: `{len(objects)}`",
            f"- Validation: `{validation['status']}`",
            "",
            "Start with `OUTPUT_INDEX.md`, then review `04_REPORTS/summary.md` and `03_WORKBOOKS/`.",
            "",
        ]
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from recovery_engine.utils.xlsx import write_xlsx


def write_workbooks(root: Path, *, messages: list[dict[str, Any]], events: list[dict[str, Any]], entities: list[dict[str, Any]]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    write_xlsx(root / "messages.xlsx", "messages", [_message_row(item) for item in messages], MESSAGE_COLUMNS)
    write_xlsx(root / "timeline.xlsx", "timeline", [_timeline_row(item) for item in events + messages], TIMELINE_COLUMNS)
    write_xlsx(root / "entities.xlsx", "entities", [_entity_row(item) for item in entities], ENTITY_COLUMNS)


MESSAGE_COLUMNS = [
    "row_id",
    "platform_source",
    "conversation_id",
    "message_id",
    "timestamp",
    "timestamp_raw",
    "sender",
    "recipient_or_participants",
    "content_exact",
    "content_normalized",
    "attachment_present",
    "attachment_reference",
    "truth_class",
    "confidence",
    "source_ref",
    "provenance_ref",
    "stage_origin",
    "notes",
]

TIMELINE_COLUMNS = [
    "row_id",
    "timestamp",
    "timestamp_raw",
    "event_type",
    "event_summary",
    "platform_source",
    "entity_refs",
    "location_ref",
    "conversation_ref",
    "artifact_ref",
    "truth_class",
    "confidence",
    "source_ref",
    "provenance_ref",
    "stage_origin",
    "notes",
]

ENTITY_COLUMNS = [
    "row_id",
    "entity_id",
    "entity_name_or_label",
    "entity_type",
    "platform_source",
    "supporting_occurrence_count",
    "linked_conversation_count",
    "linked_artifact_count",
    "linked_event_count",
    "primary_source_refs",
    "truth_class",
    "confidence",
    "source_ref",
    "provenance_ref",
    "stage_origin",
    "notes",
]


def _message_row(obj: dict[str, Any]) -> dict[str, Any]:
    attachments = obj.get("attachment_refs", [])
    return {
        "row_id": obj.get("object_id"),
        "platform_source": obj.get("platform_source"),
        "conversation_id": obj.get("conversation_id"),
        "message_id": obj.get("message_id_raw"),
        "timestamp": obj.get("timestamp"),
        "timestamp_raw": obj.get("timestamp_raw"),
        "sender": obj.get("sender_ref"),
        "recipient_or_participants": "; ".join(obj.get("participant_refs", [])),
        "content_exact": obj.get("content_exact"),
        "content_normalized": obj.get("content_normalized"),
        "attachment_present": "yes" if attachments else "no",
        "attachment_reference": "; ".join(attachments),
        "truth_class": obj.get("truth_class"),
        "confidence": obj.get("confidence"),
        "source_ref": _compact(obj.get("source_ref")),
        "provenance_ref": _compact(obj.get("provenance_ref")),
        "stage_origin": obj.get("stage_origin"),
        "notes": obj.get("normalization_notes"),
    }


def _timeline_row(obj: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_id": obj.get("object_id"),
        "timestamp": obj.get("timestamp"),
        "timestamp_raw": obj.get("timestamp_raw"),
        "event_type": obj.get("event_type") or obj.get("message_type"),
        "event_summary": obj.get("event_summary") or obj.get("content_normalized"),
        "platform_source": obj.get("platform_source"),
        "entity_refs": "; ".join(obj.get("entity_refs", []) or obj.get("participant_refs", [])),
        "location_ref": obj.get("location_ref", ""),
        "conversation_ref": obj.get("conversation_ref") or obj.get("conversation_id", ""),
        "artifact_ref": "; ".join(obj.get("artifact_refs", []) or obj.get("attachment_refs", [])),
        "truth_class": obj.get("truth_class"),
        "confidence": obj.get("confidence"),
        "source_ref": _compact(obj.get("source_ref")),
        "provenance_ref": _compact(obj.get("provenance_ref")),
        "stage_origin": obj.get("stage_origin"),
        "notes": obj.get("normalization_notes"),
    }


def _entity_row(obj: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_id": obj.get("object_id"),
        "entity_id": obj.get("object_id"),
        "entity_name_or_label": obj.get("entity_name_or_label"),
        "entity_type": obj.get("entity_type"),
        "platform_source": obj.get("platform_source"),
        "supporting_occurrence_count": 1,
        "linked_conversation_count": len(obj.get("linked_conversation_refs", [])),
        "linked_artifact_count": len(obj.get("linked_artifact_refs", [])),
        "linked_event_count": len(obj.get("linked_event_refs", [])),
        "primary_source_refs": _compact(obj.get("source_ref")),
        "truth_class": obj.get("truth_class"),
        "confidence": obj.get("confidence"),
        "source_ref": _compact(obj.get("source_ref")),
        "provenance_ref": _compact(obj.get("provenance_ref")),
        "stage_origin": obj.get("stage_origin"),
        "notes": obj.get("normalization_notes"),
    }


def _compact(value: Any) -> str:
    return json.dumps(value or {}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from recovery_engine.intake.container import SourceContainer, SourceFile
from recovery_engine.normalize.facebook import FacebookNormalizer
from recovery_engine.readers.facebook.html_parser import html_to_lines
from recovery_engine.reports.canonical import write_canonical_case
from recovery_engine.validation.validator import validate_objects


@dataclass(frozen=True)
class FacebookReaderResult:
    case_root: Path
    object_count: int
    validation_status: str


def process_facebook_export(source: Path, case_id: str, output_root: Path, strict: bool = False) -> FacebookReaderResult:
    container = SourceContainer(source)
    inventory = container.iter_files()
    extractor = FacebookExportExtractor(container, inventory, case_id)
    raw_records = extractor.extract()

    normalizer = FacebookNormalizer(case_id=case_id, source_fingerprint=container.fingerprint())
    objects = normalizer.normalize(raw_records)
    validation = validate_objects(objects)

    if strict and validation["warnings"]:
        raise ValueError(f"Validation warnings found: {validation['warnings']}")

    case_root = write_canonical_case(
        output_root=Path(output_root),
        case_id=case_id,
        source=Path(source),
        source_fingerprint=container.fingerprint(),
        inventory=inventory,
        raw_records=raw_records,
        objects=objects,
        validation=validation,
    )
    return FacebookReaderResult(
        case_root=case_root,
        object_count=len(objects),
        validation_status=validation["status"],
    )


class FacebookExportExtractor:
    def __init__(self, container: SourceContainer, inventory: list[SourceFile], case_id: str):
        self.container = container
        self.inventory = inventory
        self.case_id = case_id

    def extract(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for item in self.inventory:
            lower = item.path.lower()
            if lower.endswith(".json"):
                records.extend(self._extract_json(item))
            elif lower.endswith(".html") or lower.endswith(".htm"):
                records.extend(self._extract_html(item))
        return records

    def _extract_json(self, item: SourceFile) -> list[dict[str, Any]]:
        try:
            payload = json.loads(self.container.read_text(item.path))
        except json.JSONDecodeError:
            return [self._artifact_record(item, "unparseable_json", {"error": "JSON parse failed"})]

        records: list[dict[str, Any]] = [self._artifact_record(item, "json_file", {"top_level_type": type(payload).__name__})]
        records.extend(self._message_records(item, payload))
        records.extend(self._activity_records(item, payload))
        return records

    def _extract_html(self, item: SourceFile) -> list[dict[str, Any]]:
        text = self.container.read_text(item.path)
        lines = html_to_lines(text)
        records = [self._artifact_record(item, "html_file", {"line_count": len(lines)})]
        path_lower = item.path.lower()
        if "message" not in path_lower:
            return records

        conversation_id = _conversation_id_from_path(item.path)
        title = lines[0] if lines else conversation_id
        message_rows = _message_rows_from_html_lines(lines)
        participants = sorted({row["sender_name"] for row in message_rows if row["sender_name"]})

        records.append(
            {
                "record_type": "conversation",
                "source_format": "html",
                "source_path": item.path,
                "source_sha256": item.sha256,
                "conversation_id_raw": conversation_id,
                "participant_names": participants,
                "title": title,
            }
        )

        for index, row in enumerate(message_rows):
            records.append(
                {
                    "record_type": "message",
                    "source_format": "html",
                    "source_path": item.path,
                    "source_sha256": item.sha256,
                    "conversation_id_raw": conversation_id,
                    "message_id_raw": f"html-{index + 1}",
                    "timestamp_raw": "not_available_in_html_source",
                    "timestamp": "",
                    "sender_name": row["sender_name"],
                    "participant_names": participants,
                    "content_exact": row["content_exact"],
                    "attachments": [],
                    "message_type": "html_message",
                }
            )
        return records

    def _message_records(self, item: SourceFile, payload: Any) -> list[dict[str, Any]]:
        messages = _find_message_arrays(payload)
        if not messages:
            return []

        participants = _participant_names(payload)
        conversation_id = _conversation_id_from_path(item.path)
        records: list[dict[str, Any]] = [
            {
                "record_type": "conversation",
                "source_format": "json",
                "source_path": item.path,
                "source_sha256": item.sha256,
                "conversation_id_raw": conversation_id,
                "participant_names": participants,
                "title": _safe_str(payload.get("title")) if isinstance(payload, dict) else "",
            }
        ]

        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                continue
            timestamp_ms = message.get("timestamp_ms") or message.get("timestamp")
            records.append(
                {
                    "record_type": "message",
                    "source_format": "json",
                    "source_path": item.path,
                    "source_sha256": item.sha256,
                    "conversation_id_raw": conversation_id,
                    "message_id_raw": _safe_str(message.get("message_id") or message.get("id") or index + 1),
                    "timestamp_raw": _safe_str(timestamp_ms),
                    "timestamp": _timestamp_to_iso(timestamp_ms),
                    "sender_name": _safe_str(message.get("sender_name") or message.get("sender")),
                    "participant_names": participants,
                    "content_exact": _safe_str(message.get("content")),
                    "attachments": _attachments_from_message(message),
                    "message_type": _safe_str(message.get("type") or "message"),
                    "is_unsent": bool(message.get("is_unsent") or message.get("is_deleted")),
                }
            )
        return records

    def _activity_records(self, item: SourceFile, payload: Any) -> list[dict[str, Any]]:
        path_lower = item.path.lower()
        records: list[dict[str, Any]] = []
        if "comments" in path_lower or "reactions" in path_lower or "posts" in path_lower:
            records.extend(_walk_activity_payload(item, payload, "activity"))
        elif "logged_information" in path_lower or "notifications" in path_lower:
            records.extend(_walk_activity_payload(item, payload, "logged_activity"))
        return records

    def _artifact_record(self, item: SourceFile, artifact_type: str, extra: dict[str, Any]) -> dict[str, Any]:
        return {
            "record_type": "artifact",
            "source_format": Path(item.path).suffix.lower().lstrip("."),
            "source_path": item.path,
            "source_sha256": item.sha256,
            "artifact_type": artifact_type,
            "size": item.size,
            "extra": extra,
        }


def _find_message_arrays(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        if isinstance(payload.get("messages"), list):
            return payload["messages"]
        for value in payload.values():
            found = _find_message_arrays(value)
            if found:
                return found
    if isinstance(payload, list):
        for value in payload:
            found = _find_message_arrays(value)
            if found:
                return found
    return []


def _participant_names(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []
    participants = payload.get("participants")
    names: list[str] = []
    if isinstance(participants, list):
        for participant in participants:
            if isinstance(participant, dict):
                name = _safe_str(participant.get("name"))
                if name:
                    names.append(name)
            elif isinstance(participant, str):
                names.append(participant)
    return names


def _message_rows_from_html_lines(lines: list[str]) -> list[dict[str, str]]:
    if not lines:
        return []

    body = lines[1:] if len(lines) > 1 else lines
    rows: list[dict[str, str]] = []
    index = 0
    while index < len(body):
        sender = body[index]
        content = body[index + 1] if index + 1 < len(body) else ""
        if content:
            rows.append({"sender_name": sender, "content_exact": content})
            index += 2
        else:
            rows.append({"sender_name": "", "content_exact": sender})
            index += 1
    return rows


def _attachments_from_message(message: dict[str, Any]) -> list[dict[str, str]]:
    attachments: list[dict[str, str]] = []
    for key in ("photos", "videos", "audio_files", "files", "gifs", "sticker"):
        value = message.get(key)
        values = value if isinstance(value, list) else [value] if isinstance(value, dict) else []
        for item in values:
            if isinstance(item, dict):
                uri = _safe_str(item.get("uri") or item.get("href"))
                if uri:
                    attachments.append({"type": key, "uri": uri})
    return attachments


def _walk_activity_payload(item: SourceFile, payload: Any, activity_type: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def walk(value: Any, trail: str) -> None:
        if isinstance(value, dict):
            text = _first_text(value)
            timestamp = value.get("timestamp") or value.get("creation_timestamp") or value.get("timestamp_ms")
            if text or timestamp:
                records.append(
                    {
                        "record_type": "event",
                        "source_format": "json",
                        "source_path": item.path,
                        "source_sha256": item.sha256,
                        "event_type": activity_type,
                        "timestamp_raw": _safe_str(timestamp),
                        "timestamp": _timestamp_to_iso(timestamp),
                        "event_summary": text,
                        "raw_payload_path": trail,
                    }
                )
            for key, nested in value.items():
                walk(nested, f"{trail}.{key}" if trail else key)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                walk(nested, f"{trail}[{index}]")

    walk(payload, "")
    return records


def _first_text(value: dict[str, Any]) -> str:
    for key in ("title", "name", "text", "comment", "data", "description"):
        raw = value.get(key)
        if isinstance(raw, str) and raw.strip():
            return " ".join(raw.split())
        if isinstance(raw, dict):
            nested = _first_text(raw)
            if nested:
                return nested
    return ""


def _conversation_id_from_path(path: str) -> str:
    parts = Path(path.replace("\\", "/")).parts
    if len(parts) >= 2:
        return parts[-2] if parts[-1].lower().startswith("message_") else Path(path).stem
    return Path(path).stem


def _timestamp_to_iso(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return _safe_str(value)
    if number > 9999999999:
        dt = datetime.fromtimestamp(number / 1000, tz=timezone.utc)
    else:
        dt = datetime.fromtimestamp(number, tz=timezone.utc)
    return dt.isoformat()


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)

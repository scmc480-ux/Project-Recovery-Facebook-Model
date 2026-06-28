from __future__ import annotations

from typing import Any

from recovery_engine.objects.schema import TRUTH_DERIVED_VERIFIED, TRUTH_VERBATIM, base_object
from recovery_engine.utils.hashing import stable_id


class FacebookNormalizer:
    def __init__(self, case_id: str, source_fingerprint: str):
        self.case_id = case_id
        self.source_fingerprint = source_fingerprint

    def normalize(self, raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        objects: list[dict[str, Any]] = []
        seen_entities: set[str] = set()

        for record in raw_records:
            kind = record.get("record_type")
            if kind == "artifact":
                objects.append(self._artifact_object(record))
            elif kind == "conversation":
                objects.append(self._conversation_object(record))
                for name in record.get("participant_names", []):
                    entity = self._entity_object(name, record)
                    if entity["object_id"] not in seen_entities:
                        objects.append(entity)
                        seen_entities.add(entity["object_id"])
            elif kind == "message":
                objects.append(self._message_object(record))
                if record.get("sender_name"):
                    entity = self._entity_object(record["sender_name"], record)
                    if entity["object_id"] not in seen_entities:
                        objects.append(entity)
                        seen_entities.add(entity["object_id"])
                objects.extend(self._attachment_objects(record))
            elif kind == "event":
                objects.append(self._event_object(record))

        return objects

    def _source_ref(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "source_path": record.get("source_path", ""),
            "source_sha256": record.get("source_sha256", ""),
            "source_fingerprint": self.source_fingerprint,
            "source_format": record.get("source_format", ""),
        }

    def _provenance_ref(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "reader": "facebook_reader_v1",
            "record_type": record.get("record_type", ""),
            "stage": "normalization",
        }

    def _artifact_object(self, record: dict[str, Any]) -> dict[str, Any]:
        object_id = stable_id("artifact", self.case_id, record.get("source_path"), record.get("source_sha256"))
        obj = base_object(
            object_id=object_id,
            object_type="artifact_object",
            truth_class=TRUTH_VERBATIM,
            confidence="high",
            source_ref=self._source_ref(record),
            provenance_ref=self._provenance_ref(record),
            stage_origin="facebook_intake",
        )
        obj.update(
            {
                "artifact_type": record.get("artifact_type", "source_file"),
                "artifact_name_or_label": record.get("source_path", ""),
                "artifact_path_or_locator": record.get("source_path", ""),
                "artifact_hash": record.get("source_sha256", ""),
                "artifact_status": "preserved",
            }
        )
        return obj

    def _conversation_object(self, record: dict[str, Any]) -> dict[str, Any]:
        conversation_id = record.get("conversation_id_raw", "")
        object_id = stable_id("conversation", self.case_id, conversation_id, record.get("source_path"))
        obj = base_object(
            object_id=object_id,
            object_type="conversation_object",
            truth_class=TRUTH_VERBATIM,
            confidence="high",
            source_ref=self._source_ref(record),
            provenance_ref=self._provenance_ref(record),
            stage_origin="facebook_normalization",
        )
        obj.update(
            {
                "conversation_id_raw": conversation_id,
                "conversation_type": "facebook_message_thread",
                "participant_refs": [stable_id("entity", self.case_id, name) for name in record.get("participant_names", [])],
                "message_refs": [],
                "conversation_title_or_label": record.get("title") or conversation_id,
                "conversation_status": "observed",
            }
        )
        return obj

    def _message_object(self, record: dict[str, Any]) -> dict[str, Any]:
        object_id = stable_id(
            "message",
            self.case_id,
            record.get("conversation_id_raw"),
            record.get("message_id_raw"),
            record.get("timestamp_raw"),
            record.get("content_exact"),
        )
        sender_name = record.get("sender_name", "")
        obj = base_object(
            object_id=object_id,
            object_type="message_object",
            truth_class=TRUTH_VERBATIM,
            confidence="high" if record.get("content_exact") else "medium",
            source_ref=self._source_ref(record),
            provenance_ref=self._provenance_ref(record),
            stage_origin="facebook_normalization",
            normalization_notes="HTML message rows are text fragments when sender/timestamp cannot be reliably parsed.",
        )
        obj.update(
            {
                "conversation_id": stable_id("conversation", self.case_id, record.get("conversation_id_raw"), record.get("source_path")),
                "message_id_raw": record.get("message_id_raw", ""),
                "timestamp": record.get("timestamp", ""),
                "timestamp_raw": record.get("timestamp_raw", ""),
                "sender_ref": stable_id("entity", self.case_id, sender_name) if sender_name else "",
                "participant_refs": [stable_id("entity", self.case_id, name) for name in record.get("participant_names", [])],
                "content_exact": record.get("content_exact", ""),
                "content_normalized": " ".join(record.get("content_exact", "").split()),
                "attachment_refs": [
                    stable_id("artifact", self.case_id, item.get("uri"), record.get("source_path"))
                    for item in record.get("attachments", [])
                ],
                "message_type": record.get("message_type", "message"),
                "message_status": "unsent_or_deleted_signal" if record.get("is_unsent") else "observed",
            }
        )
        return obj

    def _entity_object(self, name: str, record: dict[str, Any]) -> dict[str, Any]:
        object_id = stable_id("entity", self.case_id, name)
        obj = base_object(
            object_id=object_id,
            object_type="entity_object",
            truth_class=TRUTH_VERBATIM,
            confidence="medium",
            source_ref=self._source_ref(record),
            provenance_ref=self._provenance_ref(record),
            stage_origin="facebook_normalization",
        )
        obj.update(
            {
                "entity_type": "person_or_account",
                "entity_name_or_label": name,
                "entity_id_raw": "",
                "alias_values": [name],
                "linked_conversation_refs": [],
                "linked_artifact_refs": [],
                "linked_event_refs": [],
                "entity_status": "observed_unresolved_identity",
            }
        )
        return obj

    def _event_object(self, record: dict[str, Any]) -> dict[str, Any]:
        object_id = stable_id("event", self.case_id, record.get("source_path"), record.get("raw_payload_path"), record.get("timestamp_raw"), record.get("event_summary"))
        obj = base_object(
            object_id=object_id,
            object_type="event_object",
            truth_class=TRUTH_DERIVED_VERIFIED,
            confidence="medium",
            source_ref=self._source_ref(record),
            provenance_ref=self._provenance_ref(record),
            stage_origin="facebook_normalization",
            normalization_notes="Event summary is derived from a structured Facebook export field.",
        )
        obj.update(
            {
                "event_type": record.get("event_type", "facebook_activity"),
                "event_summary": record.get("event_summary", ""),
                "timestamp": record.get("timestamp", ""),
                "timestamp_raw": record.get("timestamp_raw", ""),
                "entity_refs": [],
                "conversation_ref": "",
                "artifact_refs": [stable_id("artifact", self.case_id, record.get("source_path"), record.get("source_sha256"))],
                "location_ref": "",
                "event_status": "observed",
            }
        )
        return obj

    def _attachment_objects(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        objects: list[dict[str, Any]] = []
        for item in record.get("attachments", []):
            object_id = stable_id("artifact", self.case_id, item.get("uri"), record.get("source_path"))
            obj = base_object(
                object_id=object_id,
                object_type="artifact_object",
                truth_class=TRUTH_VERBATIM,
                confidence="medium",
                source_ref=self._source_ref(record),
                provenance_ref=self._provenance_ref(record),
                stage_origin="facebook_normalization",
            )
            obj.update(
                {
                    "artifact_type": item.get("type", "attachment"),
                    "artifact_name_or_label": item.get("uri", ""),
                    "artifact_path_or_locator": item.get("uri", ""),
                    "artifact_hash": "",
                    "artifact_status": "referenced_by_message",
                }
            )
            objects.append(obj)
        return objects

from __future__ import annotations

from typing import Any

from recovery_engine.objects.schema import ALLOWED_TRUTH_CLASSES, REQUIRED_COMMON_FIELDS


def validate_objects(objects: list[dict[str, Any]]) -> dict[str, Any]:
    warnings: list[str] = []
    errors: list[str] = []
    rejected: list[dict[str, str]] = []

    seen_ids: set[str] = set()
    for index, obj in enumerate(objects):
        missing = sorted(field for field in REQUIRED_COMMON_FIELDS if field not in obj)
        if missing:
            errors.append(f"object[{index}] missing required fields: {', '.join(missing)}")
            rejected.append({"object_id": obj.get("object_id", f"index_{index}"), "reason": "missing_required_fields"})
            continue

        object_id = str(obj["object_id"])
        if object_id in seen_ids:
            warnings.append(f"duplicate object_id observed: {object_id}")
        seen_ids.add(object_id)

        if obj.get("truth_class") not in ALLOWED_TRUTH_CLASSES:
            errors.append(f"{object_id} has invalid truth_class: {obj.get('truth_class')}")
        source_ref = obj.get("source_ref")
        if not isinstance(source_ref, dict) or not source_ref.get("source_path"):
            errors.append(f"{object_id} missing source_ref.source_path")
        if obj.get("object_type") in {"message_object", "event_object"} and not obj.get("timestamp") and not obj.get("timestamp_raw"):
            warnings.append(f"{object_id} has no timestamp")

    status = "pass" if not errors else "fail"
    return {
        "status": status,
        "object_count": len(objects),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "rejected_items": rejected,
    }

from __future__ import annotations

from typing import Any

TRUTH_VERBATIM = "verbatim_provable"
TRUTH_DERIVED_VERIFIED = "derived_verified_support"
TRUTH_DERIVED_PROBABLE = "derived_probable"
TRUTH_DERIVED_INFERRED = "derived_inferred"
TRUTH_WEAK = "weak"
TRUTH_REJECTED = "rejected"

ALLOWED_TRUTH_CLASSES = {
    TRUTH_VERBATIM,
    TRUTH_DERIVED_VERIFIED,
    TRUTH_DERIVED_PROBABLE,
    TRUTH_DERIVED_INFERRED,
    TRUTH_WEAK,
    TRUTH_REJECTED,
}

REQUIRED_COMMON_FIELDS = {
    "object_id",
    "object_type",
    "platform_source",
    "truth_class",
    "confidence",
    "source_ref",
    "provenance_ref",
    "stage_origin",
    "normalization_notes",
}


def base_object(
    *,
    object_id: str,
    object_type: str,
    truth_class: str,
    confidence: str,
    source_ref: dict[str, Any],
    provenance_ref: dict[str, Any],
    stage_origin: str,
    normalization_notes: str = "",
) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "object_type": object_type,
        "platform_source": "facebook",
        "truth_class": truth_class,
        "confidence": confidence,
        "source_ref": source_ref,
        "provenance_ref": provenance_ref,
        "stage_origin": stage_origin,
        "normalization_notes": normalization_notes,
    }

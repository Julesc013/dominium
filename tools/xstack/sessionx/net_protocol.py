"""Deterministic network protocol message wrapper encode/decode helpers."""

from __future__ import annotations

import json
from typing import Dict

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256
from tools.xstack.compatx.validator import validate_instance

from .common import refusal


def build_proto_message(
    msg_type: str,
    msg_id: str,
    sequence: int,
    payload_schema_id: str,
    payload_inline_json: Dict[str, object],
    binary_blob_ref: str = "",
    extensions: Dict[str, object] | None = None,
) -> Dict[str, object]:
    payload_ref = {
        "inline_json": dict(payload_inline_json or {}),
        "binary_blob_ref": str(binary_blob_ref or ""),
    }
    return {
        "schema_version": "1.0.0",
        "msg_type": str(msg_type),
        "msg_id": str(msg_id),
        "sequence": int(sequence),
        "payload_schema_id": str(payload_schema_id),
        "payload_ref": payload_ref,
        "payload_hash": canonical_sha256(payload_ref),
        "extensions": dict(extensions or {}),
    }


def encode_proto_message(proto_message: Dict[str, object]) -> bytes:
    return canonical_json_text(proto_message).encode("utf-8")


def decode_proto_message(repo_root: str, message_bytes: bytes) -> Dict[str, object]:
    try:
        payload = json.loads(bytes(message_bytes or b"").decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return refusal(
            "refusal.net.envelope_invalid",
            "protocol message is not valid UTF-8 JSON",
            "Encode proto messages as canonical UTF-8 JSON.",
            {"schema_id": "net_proto_message"},
            "$",
        )

    checked = validate_instance(
        repo_root=repo_root,
        schema_name="net_proto_message",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return refusal(
            "refusal.net.envelope_invalid",
            "protocol message failed net_proto_message schema validation",
            "Fix protocol envelope fields and retry.",
            {"schema_id": "net_proto_message"},
            "$",
        )

    payload_ref = dict(payload.get("payload_ref") or {})
    expected_hash = str(payload.get("payload_hash", "")).strip()
    actual_hash = canonical_sha256(payload_ref)
    if expected_hash != actual_hash:
        return refusal(
            "refusal.net.envelope_invalid",
            "protocol message payload_hash mismatch",
            "Regenerate payload_hash from canonical payload_ref and resend.",
            {"schema_id": "net_proto_message"},
            "$.payload_hash",
        )
    return {
        "result": "complete",
        "proto_message": payload,
    }

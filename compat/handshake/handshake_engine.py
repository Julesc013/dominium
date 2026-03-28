"""Deterministic CAP-NEG handshake message helpers."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_CONNECTION_NO_NEGOTIATION = "refusal.connection.no_negotiation"
REFUSAL_CONNECTION_NEGOTIATION_MISMATCH = "refusal.connection.negotiation_mismatch"

_ALLOWED_MESSAGE_KINDS = {
    "client_hello",
    "server_hello",
    "negotiation_result",
    "ack",
    "session_begin",
}


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def build_handshake_message(
    *,
    message_kind: str,
    protocol_version: str,
    payload_ref: Mapping[str, object] | None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind = str(message_kind or "").strip()
    if kind not in _ALLOWED_MESSAGE_KINDS:
        raise ValueError("unsupported handshake message_kind '{}'".format(kind))
    payload = {
        "schema_version": "1.0.0",
        "message_kind": kind,
        "protocol_version": str(protocol_version or "").strip() or "1.0.0",
        "payload_ref": _as_map(payload_ref),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_compat_refusal(
    *,
    refusal_code: str,
    remediation_hint: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "refusal_code": str(refusal_code or "").strip(),
        "remediation_hint": str(remediation_hint or "").strip(),
        "deterministic_fingerprint": "",
    }
    if _as_map(extensions):
        payload["extensions"] = _as_map(extensions)
    payload["deterministic_fingerprint"] = canonical_sha256(
        dict(payload, deterministic_fingerprint="")
    )
    return payload


def build_session_begin_payload(
    *,
    connection_id: str,
    compatibility_mode_id: str,
    negotiation_record_hash: str,
    pack_lock_hash: str,
    contract_bundle_hash: str,
    semantic_contract_registry_hash: str = "",
    law_profile_id_override: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "connection_id": str(connection_id or "").strip(),
        "compatibility_mode_id": str(compatibility_mode_id or "").strip(),
        "negotiation_record_hash": str(negotiation_record_hash or "").strip(),
        "pack_lock_hash": str(pack_lock_hash or "").strip(),
        "contract_bundle_hash": str(contract_bundle_hash or "").strip(),
        "semantic_contract_registry_hash": str(semantic_contract_registry_hash or "").strip(),
        "law_profile_id_override": str(law_profile_id_override or "").strip(),
        "extensions": _as_map(extensions),
    }
    return dict((key, payload[key]) for key in sorted(payload.keys()))

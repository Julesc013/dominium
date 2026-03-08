"""Deterministic GEO-5 CCTV SIG delivery stub."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.signals import (
    build_knowledge_receipt,
    build_message_queue_entry,
    build_signal_channel,
    build_signal_message_envelope,
    deterministic_knowledge_receipt_id,
    deterministic_message_queue_entry_id,
    deterministic_signal_message_envelope_id,
)


REFUSAL_GEO_CCTV_INVALID = "refusal.geo.cctv_invalid"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _refusal(message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": REFUSAL_GEO_CCTV_INVALID,
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_cctv_view_delivery(
    *,
    projected_view_artifact: Mapping[str, object] | None,
    created_tick: int,
    sender_subject_id: str,
    recipient_subject_id: str,
    recipient_address: Mapping[str, object] | None,
    channel_id: str = "channel.sig.cctv",
    network_graph_id: str = "network.sig.cctv",
    camera_instrument_id: str = "instrument.camera.remote",
    base_delay_ticks: int = 1,
) -> dict:
    artifact = _as_map(projected_view_artifact)
    if not str(artifact.get("view_id", "")).strip():
        return _refusal("projected_view_artifact is required")
    tick = int(max(0, _as_int(created_tick, 0)))
    delay = int(max(0, _as_int(base_delay_ticks, 1)))
    observation_artifact_id = "artifact.observation.cctv.{}".format(canonical_sha256(artifact)[:16])
    observation_artifact = {
        "schema_version": "1.0.0",
        "observation_artifact_id": observation_artifact_id,
        "modality": "modality.cctv.tile_snapshot",
        "payload_type": "geo.projected_view_artifact",
        "payload": {
            "view_id": str(artifact.get("view_id", "")).strip(),
            "projected_view_artifact": dict(artifact),
        },
        "confidence": {"value": 1, "unit": "ratio"},
        "provenance": {"provenance_id": "prov.geo.cctv.sig"},
        "staleness": {"value": int(delay), "unit": "tick"},
        "epistemic_status": "remote_observation",
        "reason_codes": ["sig.transport.cctv_stub"],
        "extensions": {"camera_instrument_id": str(camera_instrument_id).strip(), "trace_compactable": True},
    }
    info_artifact_row = {
        "artifact_id": observation_artifact_id,
        "artifact_family_id": "OBSERVATION",
        "extensions": {"payload_type": "geo.projected_view_artifact", "camera_instrument_id": str(camera_instrument_id).strip()},
    }
    channel_row = build_signal_channel(
        channel_id=str(channel_id).strip() or "channel.sig.cctv",
        channel_type_id="signal_channel.snapshot",
        network_graph_id=str(network_graph_id).strip() or "network.sig.cctv",
        capacity_per_tick=1,
        base_delay_ticks=int(delay),
        loss_policy_id="loss.none",
        encryption_policy_id=None,
        extensions={"source": "GEO5-6"},
    )
    normalized_recipient = _as_map(recipient_address) or {"address_kind": "subject.direct", "subject_id": str(recipient_subject_id).strip()}
    envelope_id = deterministic_signal_message_envelope_id(
        artifact_id=observation_artifact_id,
        sender_subject_id=str(sender_subject_id).strip(),
        recipient_address=normalized_recipient,
        created_tick=tick,
    )
    envelope_row = build_signal_message_envelope(
        envelope_id=envelope_id,
        artifact_id=observation_artifact_id,
        sender_subject_id=str(sender_subject_id).strip(),
        recipient_address=normalized_recipient,
        created_tick=tick,
        extensions={"source": "GEO5-6", "camera_instrument_id": str(camera_instrument_id).strip()},
    )
    scheduled_tick = int(tick + delay)
    queue_entry_id = deterministic_message_queue_entry_id(
        channel_id=str(channel_row.get("channel_id", "")).strip(),
        envelope_id=envelope_id,
        recipient_subject_id=str(recipient_subject_id).strip(),
        next_hop_node_id="node.cctv.receiver",
        scheduled_tick=scheduled_tick,
    )
    queue_entry_row = build_message_queue_entry(
        queue_entry_id=queue_entry_id,
        channel_id=str(channel_row.get("channel_id", "")).strip(),
        envelope_id=envelope_id,
        next_hop_node_id="node.cctv.receiver",
        scheduled_tick=scheduled_tick,
        extensions={"source": "GEO5-6", "delivery_kind": "cctv_snapshot"},
    )
    receipt_id = deterministic_knowledge_receipt_id(
        subject_id=str(recipient_subject_id).strip(),
        artifact_id=observation_artifact_id,
        envelope_id=envelope_id,
        acquired_tick=scheduled_tick,
    )
    receipt_row = build_knowledge_receipt(
        receipt_id=receipt_id,
        subject_id=str(recipient_subject_id).strip(),
        artifact_id=observation_artifact_id,
        envelope_id=envelope_id,
        acquired_tick=scheduled_tick,
        trust_weight=1.0,
        verification_state="verified",
        extensions={"source": "GEO5-6", "delivery_kind": "cctv_snapshot"},
    )
    payload = {
        "result": "complete",
        "observation_artifact": observation_artifact,
        "info_artifact_row": info_artifact_row,
        "signal_channel_row": channel_row,
        "signal_envelope_row": envelope_row,
        "message_queue_entry_row": queue_entry_row,
        "knowledge_receipt_row": receipt_row,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload

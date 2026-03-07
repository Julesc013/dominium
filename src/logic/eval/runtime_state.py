"""Normalized runtime/evidence rows for LOGIC-4 evaluation."""

from __future__ import annotations

from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import as_int, as_list, as_map, canon, slot_key, token


def build_logic_network_runtime_state_row(
    *,
    network_id: str,
    last_evaluated_tick: int,
    throttled: bool,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "network_id": token(network_id),
        "last_evaluated_tick": int(max(0, as_int(last_evaluated_tick, 0))),
        "throttled": bool(throttled),
        "deterministic_fingerprint": token(deterministic_fingerprint),
        "extensions": canon(as_map(extensions)),
    }
    if not payload["network_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_network_runtime_state_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in as_list(rows) if isinstance(item, Mapping)), key=lambda item: token(item.get("network_id"))):
        normalized = build_logic_network_runtime_state_row(
            network_id=token(row.get("network_id")),
            last_evaluated_tick=as_int(row.get("last_evaluated_tick"), 0),
            throttled=bool(row.get("throttled", False)),
            deterministic_fingerprint=token(row.get("deterministic_fingerprint")),
            extensions=as_map(row.get("extensions")),
        )
        if normalized:
            out[token(normalized.get("network_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_eval_record_row(
    *,
    tick: int,
    network_id: str,
    elements_evaluated_count: int,
    compute_units_used: int,
    throttled: bool,
    record_id: str = "",
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "record_id": token(record_id)
        or "record.logic.eval.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, as_int(tick, 0))),
                    "network_id": token(network_id),
                    "elements_evaluated_count": int(max(0, as_int(elements_evaluated_count, 0))),
                    "compute_units_used": int(max(0, as_int(compute_units_used, 0))),
                    "throttled": bool(throttled),
                }
            )[:16]
        ),
        "tick": int(max(0, as_int(tick, 0))),
        "network_id": token(network_id),
        "elements_evaluated_count": int(max(0, as_int(elements_evaluated_count, 0))),
        "compute_units_used": int(max(0, as_int(compute_units_used, 0))),
        "throttled": bool(throttled),
        "deterministic_fingerprint": token(deterministic_fingerprint),
        "extensions": canon(as_map(extensions)),
    }
    if not payload["network_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_eval_record_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in as_list(rows) if isinstance(item, Mapping)), key=lambda item: (as_int(item.get("tick"), 0), token(item.get("record_id")))):
        normalized = build_logic_eval_record_row(
            tick=as_int(row.get("tick"), 0),
            network_id=token(row.get("network_id")),
            elements_evaluated_count=as_int(row.get("elements_evaluated_count"), 0),
            compute_units_used=as_int(row.get("compute_units_used"), 0),
            throttled=bool(row.get("throttled", False)),
            record_id=token(row.get("record_id")),
            deterministic_fingerprint=token(row.get("deterministic_fingerprint")),
            extensions=as_map(row.get("extensions")),
        )
        if normalized:
            out[token(normalized.get("record_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_throttle_event_row(
    *,
    tick: int,
    network_id: str,
    reason: str,
    event_id: str = "",
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "event_id": token(event_id)
        or "event.logic.throttle.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, as_int(tick, 0))),
                    "network_id": token(network_id),
                    "reason": token(reason),
                    "extensions": canon(as_map(extensions)),
                }
            )[:16]
        ),
        "tick": int(max(0, as_int(tick, 0))),
        "network_id": token(network_id),
        "reason": token(reason),
        "deterministic_fingerprint": token(deterministic_fingerprint),
        "extensions": canon(as_map(extensions)),
    }
    if not payload["network_id"] or not payload["reason"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_throttle_event_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in as_list(rows) if isinstance(item, Mapping)), key=lambda item: (as_int(item.get("tick"), 0), token(item.get("event_id")))):
        normalized = build_logic_throttle_event_row(
            tick=as_int(row.get("tick"), 0),
            network_id=token(row.get("network_id")),
            reason=token(row.get("reason")),
            event_id=token(row.get("event_id")),
            deterministic_fingerprint=token(row.get("deterministic_fingerprint")),
            extensions=as_map(row.get("extensions")),
        )
        if normalized:
            out[token(normalized.get("event_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_state_update_record_row(
    *,
    tick: int,
    owner_id: str,
    prior_snapshot_hash: str | None,
    next_snapshot_hash: str,
    process_id: str,
    update_id: str = "",
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "update_id": token(update_id)
        or "record.logic.state_update.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, as_int(tick, 0))),
                    "owner_id": token(owner_id),
                    "prior_snapshot_hash": None if prior_snapshot_hash is None else token(prior_snapshot_hash) or None,
                    "next_snapshot_hash": token(next_snapshot_hash),
                    "process_id": token(process_id),
                }
            )[:16]
        ),
        "tick": int(max(0, as_int(tick, 0))),
        "owner_id": token(owner_id),
        "prior_snapshot_hash": None if prior_snapshot_hash is None else token(prior_snapshot_hash) or None,
        "next_snapshot_hash": token(next_snapshot_hash),
        "process_id": token(process_id),
        "deterministic_fingerprint": token(deterministic_fingerprint),
        "extensions": canon(as_map(extensions)),
    }
    if not payload["owner_id"] or not payload["next_snapshot_hash"] or not payload["process_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_state_update_record_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in as_list(rows) if isinstance(item, Mapping)), key=lambda item: (as_int(item.get("tick"), 0), token(item.get("update_id")))):
        normalized = build_logic_state_update_record_row(
            tick=as_int(row.get("tick"), 0),
            owner_id=token(row.get("owner_id")),
            prior_snapshot_hash=(None if row.get("prior_snapshot_hash") is None else token(row.get("prior_snapshot_hash")) or None),
            next_snapshot_hash=token(row.get("next_snapshot_hash")),
            process_id=token(row.get("process_id")),
            update_id=token(row.get("update_id")),
            deterministic_fingerprint=token(row.get("deterministic_fingerprint")),
            extensions=as_map(row.get("extensions")),
        )
        if normalized:
            out[token(normalized.get("update_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_pending_signal_update_row(
    *,
    network_id: str,
    source_element_id: str,
    source_port_id: str,
    target_element_id: str,
    target_port_id: str,
    signal_type_id: str,
    carrier_type_id: str,
    delay_policy_id: str,
    noise_policy_id: str,
    deliver_tick: int,
    value_payload: Mapping[str, object],
    pending_id: str = "",
    bus_id: str | None = None,
    protocol_id: str | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "pending_id": token(pending_id)
        or "pending.logic.signal.{}".format(
            canonical_sha256(
                {
                    "network_id": token(network_id),
                    "source_slot_key": slot_key(network_id=network_id, element_id=source_element_id, port_id=source_port_id),
                    "target_slot_key": slot_key(network_id=network_id, element_id=target_element_id, port_id=target_port_id),
                    "deliver_tick": int(max(0, as_int(deliver_tick, 0))),
                    "signal_type_id": token(signal_type_id),
                    "value_payload": canon(as_map(value_payload)),
                }
            )[:16]
        ),
        "network_id": token(network_id),
        "source_element_id": token(source_element_id),
        "source_port_id": token(source_port_id),
        "target_element_id": token(target_element_id),
        "target_port_id": token(target_port_id),
        "signal_type_id": token(signal_type_id),
        "carrier_type_id": token(carrier_type_id),
        "delay_policy_id": token(delay_policy_id),
        "noise_policy_id": token(noise_policy_id),
        "deliver_tick": int(max(0, as_int(deliver_tick, 0))),
        "value_payload": canon(as_map(value_payload)),
        "bus_id": None if bus_id is None else token(bus_id) or None,
        "protocol_id": None if protocol_id is None else token(protocol_id) or None,
        "deterministic_fingerprint": token(deterministic_fingerprint),
        "extensions": canon(as_map(extensions)),
    }
    required = (
        payload["network_id"],
        payload["source_element_id"],
        payload["source_port_id"],
        payload["target_element_id"],
        payload["target_port_id"],
        payload["signal_type_id"],
        payload["carrier_type_id"],
        payload["delay_policy_id"],
        payload["noise_policy_id"],
    )
    if any(not item for item in required):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_pending_signal_update_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (
            as_int(item.get("deliver_tick"), 0),
            token(item.get("network_id")),
            token(item.get("target_element_id")),
            token(item.get("target_port_id")),
            token(item.get("pending_id")),
        ),
    ):
        normalized = build_logic_pending_signal_update_row(
            network_id=token(row.get("network_id")),
            source_element_id=token(row.get("source_element_id")),
            source_port_id=token(row.get("source_port_id")),
            target_element_id=token(row.get("target_element_id")),
            target_port_id=token(row.get("target_port_id")),
            signal_type_id=token(row.get("signal_type_id")),
            carrier_type_id=token(row.get("carrier_type_id")),
            delay_policy_id=token(row.get("delay_policy_id")),
            noise_policy_id=token(row.get("noise_policy_id")),
            deliver_tick=as_int(row.get("deliver_tick"), 0),
            value_payload=as_map(row.get("value_payload")),
            pending_id=token(row.get("pending_id")),
            bus_id=(None if row.get("bus_id") is None else token(row.get("bus_id")) or None),
            protocol_id=(None if row.get("protocol_id") is None else token(row.get("protocol_id")) or None),
            deterministic_fingerprint=token(row.get("deterministic_fingerprint")),
            extensions=as_map(row.get("extensions")),
        )
        if normalized:
            out[token(normalized.get("pending_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_propagation_trace_artifact_row(
    *,
    tick: int,
    network_id: str,
    trace_kind: str,
    slot_key_value: str,
    signal_hash: str,
    artifact_id: str = "",
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "artifact_id": token(artifact_id)
        or "artifact.logic.propagation_trace.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, as_int(tick, 0))),
                    "network_id": token(network_id),
                    "trace_kind": token(trace_kind),
                    "slot_key": token(slot_key_value),
                    "signal_hash": token(signal_hash),
                }
            )[:16]
        ),
        "network_id": token(network_id),
        "created_tick": int(max(0, as_int(tick, 0))),
        "trace_kind": token(trace_kind),
        "slot_key": token(slot_key_value),
        "signal_hash": token(signal_hash),
        "deterministic_fingerprint": token(deterministic_fingerprint),
        "extensions": dict(canon(as_map(extensions)), trace_compactable=True),
    }
    if not payload["network_id"] or not payload["trace_kind"] or not payload["slot_key"] or not payload["signal_hash"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_propagation_trace_artifact_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in as_list(rows) if isinstance(item, Mapping)), key=lambda item: (as_int(item.get("created_tick"), 0), token(item.get("artifact_id")))):
        normalized = build_logic_propagation_trace_artifact_row(
            tick=as_int(row.get("created_tick"), 0),
            network_id=token(row.get("network_id")),
            trace_kind=token(row.get("trace_kind")),
            slot_key_value=token(row.get("slot_key")),
            signal_hash=token(row.get("signal_hash")),
            artifact_id=token(row.get("artifact_id")),
            deterministic_fingerprint=token(row.get("deterministic_fingerprint")),
            extensions=as_map(row.get("extensions")),
        )
        if normalized:
            out[token(normalized.get("artifact_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_logic_eval_state(state: Mapping[str, object] | None) -> dict:
    src = as_map(state)
    return {
        "schema_version": "1.0.0",
        "logic_network_runtime_state_rows": normalize_logic_network_runtime_state_rows(src.get("logic_network_runtime_state_rows")),
        "logic_eval_record_rows": normalize_logic_eval_record_rows(src.get("logic_eval_record_rows")),
        "logic_throttle_event_rows": normalize_logic_throttle_event_rows(src.get("logic_throttle_event_rows")),
        "logic_state_update_record_rows": normalize_logic_state_update_record_rows(src.get("logic_state_update_record_rows")),
        "logic_pending_signal_update_rows": normalize_logic_pending_signal_update_rows(src.get("logic_pending_signal_update_rows")),
        "logic_propagation_trace_artifact_rows": normalize_logic_propagation_trace_artifact_rows(src.get("logic_propagation_trace_artifact_rows")),
        "compute_runtime_state": canon(as_map(src.get("compute_runtime_state"))),
        "extensions": canon(as_map(src.get("extensions"))),
    }


__all__ = [
    "build_logic_eval_record_row",
    "build_logic_network_runtime_state_row",
    "build_logic_pending_signal_update_row",
    "build_logic_propagation_trace_artifact_row",
    "build_logic_state_update_record_row",
    "build_logic_throttle_event_row",
    "normalize_logic_eval_record_rows",
    "normalize_logic_eval_state",
    "normalize_logic_network_runtime_state_rows",
    "normalize_logic_pending_signal_update_rows",
    "normalize_logic_propagation_trace_artifact_rows",
    "normalize_logic_state_update_record_rows",
    "normalize_logic_throttle_event_rows",
]

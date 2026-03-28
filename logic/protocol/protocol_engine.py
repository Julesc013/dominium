"""LOGIC-9 deterministic protocol framing, arbitration, and SIG hooks."""

from __future__ import annotations

from typing import Dict, Mapping

from logic.protocol.rows import (
    build_arbitration_state_row,
    build_protocol_event_record_row,
    build_protocol_frame_row,
    normalize_arbitration_state_rows,
    normalize_protocol_event_record_rows,
    normalize_protocol_frame_rows,
)
from logic.signal import sig_receipt_to_signal_request
from meta.explain import build_explain_artifact
from signals import (
    build_signal_channel,
    normalize_knowledge_receipt_rows,
    normalize_message_delivery_event_rows,
    normalize_signal_channel_rows,
    normalize_signal_message_envelope_rows,
    normalize_transport_queue_rows,
    process_signal_send,
    process_signal_transport_tick,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


def _i(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _m(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _l(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _t(value: object) -> str:
    return str(value or "").strip()


def _c(value: object):
    if isinstance(value, Mapping):
        return {str(key): _c(value[key]) for key in sorted(value.keys(), key=lambda item: str(item))}
    if isinstance(value, list):
        return [_c(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _rows(payload: Mapping[str, object] | None, *keys: str) -> list[dict]:
    body = _m(payload)
    for key in keys:
        rows = body.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _m(body.get("record"))
    for key in keys:
        rows = record.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def _by_id(rows: object, key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _l(rows) if isinstance(item, Mapping)), key=lambda item: _t(item.get(key))):
        token = _t(row.get(key))
        if token:
            out[token] = dict(row)
    return {name: dict(out[name]) for name in sorted(out.keys())}


def _upsert_by_id(rows: object, key: str, row: Mapping[str, object]) -> list[dict]:
    row_id = _t(_m(row).get(key))
    if not row_id:
        return [dict(item) for item in _l(rows) if isinstance(item, Mapping)]
    indexed = _by_id(rows, key)
    indexed[row_id] = dict(_m(row))
    return [dict(indexed[name]) for name in sorted(indexed.keys())]


def _endpoint_id(network_id: str, element_id: str, port_id: str) -> str:
    return "endpoint.logic.{}".format(canonical_sha256({"n": _t(network_id), "e": _t(element_id), "p": _t(port_id)})[:16])


def _subject_id(slot: Mapping[str, object]) -> str:
    return "subject.logic.endpoint.{}".format(
        canonical_sha256({"n": _t(slot.get("network_id")), "e": _t(slot.get("element_id")), "p": _t(slot.get("port_id"))})[:16]
    )


def _explain(kind: str, target_id: str, seed: Mapping[str, object], hints: list[str], extensions: Mapping[str, object] | None = None) -> dict:
    digest = canonical_sha256({"kind": _t(kind), "seed": _c(_m(seed))})[:16]
    return build_explain_artifact(
        explain_id="{}.{}".format(_t(kind), digest),
        event_id="event.logic.protocol.{}".format(digest),
        target_id=_t(target_id),
        cause_chain=["cause.logic.protocol"],
        remediation_hints=list(hints),
        extensions=dict(_c(_m(extensions)), event_kind_id=_t(kind)),
    )


def build_protocol_frame_from_delivery(*, current_tick: int, network_id: str, source_element_id: str, source_port_id: str, delivery: Mapping[str, object], value_payload: Mapping[str, object], protocol_row: Mapping[str, object]) -> dict:
    slot = {
        "network_id": _t(network_id),
        "element_id": _t(delivery.get("target_element_id")),
        "port_id": _t(delivery.get("target_port_id")),
        "node_id": _t(delivery.get("target_node_id")) or "node.logic.protocol.{}".format(canonical_sha256({"n": network_id, "e": delivery.get("target_element_id"), "p": delivery.get("target_port_id")})[:16]),
    }
    slot["subject_id"] = _subject_id(slot)
    payload_ref = {
        "signal_type_id": _t(delivery.get("signal_type_id")),
        "value_payload": _c(_m(value_payload)),
    }
    address_mode = _t(protocol_row.get("addressing_mode")).lower() or "unicast"
    dst_address = {
        "kind": address_mode,
        "subject_id": slot["subject_id"],
        "subject_ids": [slot["subject_id"]],
        "broadcast_subject_ids": [slot["subject_id"]],
        "broadcast_scope": _t(protocol_row.get("bus_id")) or _t(delivery.get("bus_id")) or "scope.logic.protocol",
        "to_node_id": slot["node_id"],
    }
    seed = {
        "tick": int(max(0, _i(current_tick, 0))),
        "protocol_id": _t(protocol_row.get("protocol_id")),
        "src_endpoint_id": _endpoint_id(network_id, source_element_id, source_port_id),
        "dst_address": _c(dst_address),
        "payload_ref": _c(payload_ref),
    }
    return build_protocol_frame_row(
        frame_id="frame.logic.protocol.{}".format(canonical_sha256(seed)[:16]),
        protocol_id=_t(protocol_row.get("protocol_id")),
        src_endpoint_id=seed["src_endpoint_id"],
        dst_address=dst_address,
        payload_ref=payload_ref,
        checksum="none" if _t(protocol_row.get("error_detection_policy_id")) == "err.none" else canonical_sha256(seed)[:16],
        tick_sent=int(max(0, _i(current_tick, 0))),
        extensions={
            "network_id": _t(network_id),
            "bus_id": _t(delivery.get("bus_id")) or _t(protocol_row.get("bus_id")) or None,
            "carrier_type_id": _t(delivery.get("carrier_type_id")) or _t(_m(protocol_row.get("extensions")).get("default_carrier_type_id")) or "carrier.electrical",
            "delay_policy_id": _t(delivery.get("delay_policy_id")) or "delay.none",
            "noise_policy_id": _t(delivery.get("noise_policy_id")) or "noise.none",
            "deliver_delay_ticks": int(max(1, _i(delivery.get("deliver_delay_ticks"), 1))),
            "security_policy_id": _t(protocol_row.get("security_policy_id")) or "sec.none",
            "security_context": _c(_m(delivery.get("security_context"))),
            "target_slots": [slot],
            "source_element_id": _t(source_element_id),
            "source_port_id": _t(source_port_id),
            "status": "queued",
            "next_arbitration_tick": int(max(0, _i(current_tick, 0))),
        },
    )


def transport_logic_sig_receipts(*, current_tick: int, signal_store_state: Mapping[str, object] | None, signal_transport_state: Mapping[str, object] | None, signal_type_registry_payload: Mapping[str, object] | None, carrier_type_registry_payload: Mapping[str, object] | None, signal_delay_policy_registry_payload: Mapping[str, object] | None, signal_noise_policy_registry_payload: Mapping[str, object] | None, bus_encoding_registry_payload: Mapping[str, object] | None, protocol_registry_payload: Mapping[str, object] | None, protocol_frame_rows: object = None, protocol_event_record_rows: object = None, compute_budget_profile_registry_payload: Mapping[str, object] | None = None, compute_degrade_policy_registry_payload: Mapping[str, object] | None = None, tolerance_policy_registry_payload: Mapping[str, object] | None = None, process_signal_set_fn=None) -> dict:
    state = {
        "signal_channel_rows": normalize_signal_channel_rows(_m(signal_transport_state).get("signal_channel_rows")),
        "signal_message_envelope_rows": normalize_signal_message_envelope_rows(_m(signal_transport_state).get("signal_message_envelope_rows")),
        "signal_transport_queue_rows": normalize_transport_queue_rows(_m(signal_transport_state).get("signal_transport_queue_rows")),
        "message_delivery_event_rows": normalize_message_delivery_event_rows(_m(signal_transport_state).get("message_delivery_event_rows")),
        "knowledge_receipt_rows": normalize_knowledge_receipt_rows(_m(signal_transport_state).get("knowledge_receipt_rows")),
        "network_graph_rows": [dict(row) for row in _l(_m(signal_transport_state).get("network_graph_rows")) if isinstance(row, Mapping)],
        "signal_trust_edge_rows": [
            dict(row)
            for row in _l(_m(signal_transport_state).get("signal_trust_edge_rows") or _m(signal_transport_state).get("trust_edge_rows"))
            if isinstance(row, Mapping)
        ],
    }
    protocol_rows = _by_id(_rows(protocol_registry_payload, "protocols"), "protocol_id")
    protocol_frames = _by_id(normalize_protocol_frame_rows(protocol_frame_rows), "frame_id")
    protocol_events = list(normalize_protocol_event_record_rows(protocol_event_record_rows))
    prior_delivery_event_ids = {
        _t(row.get("event_id"))
        for row in list(state["message_delivery_event_rows"] or [])
        if isinstance(row, Mapping) and _t(row.get("event_id"))
    }
    if not state["signal_transport_queue_rows"]:
        return {
            "signal_store_state": signal_store_state,
            "signal_transport_state": state,
            "logic_protocol_frame_rows": normalize_protocol_frame_rows(list(protocol_frames.values())),
            "logic_protocol_event_record_rows": normalize_protocol_event_record_rows(protocol_events),
            "delivered_receipt_count": 0,
        }
    transport = process_signal_transport_tick(
        current_tick=int(max(0, _i(current_tick, 0))),
        signal_channel_rows=state["signal_channel_rows"],
        signal_transport_queue_rows=state["signal_transport_queue_rows"],
        signal_message_envelope_rows=state["signal_message_envelope_rows"],
        message_delivery_event_rows=state["message_delivery_event_rows"],
        knowledge_receipt_rows=state["knowledge_receipt_rows"],
        network_graph_rows=state["network_graph_rows"],
        loss_policy_registry=_m(_m(signal_transport_state).get("loss_policy_registry_payload")),
        routing_policy_registry=_m(_m(signal_transport_state).get("routing_policy_registry_payload")),
        attenuation_policy_registry=_m(_m(signal_transport_state).get("attenuation_policy_registry_payload")),
        trust_edge_rows=state["signal_trust_edge_rows"],
        belief_policy_registry=_m(_m(signal_transport_state).get("belief_policy_registry_payload")),
        belief_policy_id=_t(_m(signal_transport_state).get("belief_policy_id")) or "belief.default",
        max_cost_units=int(max(8, _i(_m(signal_transport_state).get("max_cost_units", 64), 64))),
        cost_units_per_delivery=int(max(1, _i(_m(signal_transport_state).get("cost_units_per_delivery", 2), 2))),
    )
    state["signal_transport_queue_rows"] = normalize_transport_queue_rows(transport.get("signal_transport_queue_rows"))
    state["signal_message_envelope_rows"] = normalize_signal_message_envelope_rows(transport.get("signal_message_envelope_rows") or state["signal_message_envelope_rows"])
    state["message_delivery_event_rows"] = normalize_message_delivery_event_rows(transport.get("message_delivery_event_rows"))
    state["knowledge_receipt_rows"] = normalize_knowledge_receipt_rows(transport.get("knowledge_receipt_rows"))
    envelope_index = {
        _t(row.get("envelope_id")): dict(row)
        for row in list(state["signal_message_envelope_rows"] or [])
        if isinstance(row, Mapping) and _t(row.get("envelope_id"))
    }
    receipt_index = {(_t(row.get("envelope_id")), _t(row.get("subject_id"))): dict(row) for row in state["knowledge_receipt_rows"]}
    updated_signal_store_state = signal_store_state
    delivered_receipt_count = 0
    new_delivery_rows = [
        dict(row)
        for row in list(state["message_delivery_event_rows"] or [])
        if isinstance(row, Mapping) and _t(row.get("event_id")) not in prior_delivery_event_ids
    ]
    for delivery_row in sorted(new_delivery_rows, key=lambda row: (_i(row.get("delivered_tick"), 0), _t(row.get("event_id")))):
        envelope = dict(envelope_index.get(_t(delivery_row.get("envelope_id"))) or {})
        envelope_extensions = _m(envelope.get("extensions"))
        frame_id = _t(envelope_extensions.get("protocol_frame_id"))
        if not frame_id:
            continue
        frame_row = dict(protocol_frames.get(frame_id) or {})
        protocol_id = _t(envelope_extensions.get("protocol_id")) or _t(frame_row.get("protocol_id"))
        protocol_row = dict(protocol_rows.get(protocol_id) or {})
        bus_id = _t(envelope_extensions.get("bus_id")) or _t(_m(frame_row.get("extensions")).get("bus_id")) or _t(protocol_row.get("bus_id"))
        delivery_state = _t(delivery_row.get("delivery_state")).lower() or "lost"
        protocol_result = {"delivered": "delivered", "corrupted": "corrupted"}.get(delivery_state, "dropped")
        matching_receipts = [
            dict(row)
            for row in list(state["knowledge_receipt_rows"] or [])
            if isinstance(row, Mapping)
            and _t(row.get("envelope_id")) == _t(delivery_row.get("envelope_id"))
            and _t(row.get("delivery_event_id")) == _t(delivery_row.get("event_id"))
        ]
        receipt = dict(sorted(matching_receipts, key=lambda row: (_t(row.get("subject_id")), _t(row.get("receipt_id"))))[0]) if matching_receipts else {}
        protocol_events.append(
            build_protocol_event_record_row(
                event_id="event.logic.protocol.{}".format(
                    canonical_sha256(
                        {
                            "delivery_event_id": _t(delivery_row.get("event_id")),
                            "frame_id": frame_id,
                            "result": protocol_result,
                        }
                    )[:16]
                ),
                protocol_id=protocol_id,
                bus_id=bus_id,
                frame_id=frame_id,
                result=protocol_result,
                tick=_i(delivery_row.get("delivered_tick"), current_tick),
                extensions={
                    "delivery_event_id": _t(delivery_row.get("event_id")),
                    "envelope_id": _t(delivery_row.get("envelope_id")),
                    "channel_id": _t(_m(delivery_row.get("extensions")).get("channel_id")),
                    "recipient_subject_id": _t(_m(delivery_row.get("extensions")).get("recipient_subject_id")),
                    "receipt_id": _t(receipt.get("receipt_id")) or None,
                    "verification_state": _t(receipt.get("verification_state")) or None,
                    "transport_delivery_state": delivery_state,
                },
            )
        )
        if frame_row:
            frame_extensions = {
                **_m(frame_row.get("extensions")),
                "status": protocol_result,
                "delivery_event_id": _t(delivery_row.get("event_id")) or None,
                "delivered_tick": int(max(0, _i(delivery_row.get("delivered_tick"), current_tick))),
                "receipt_id": _t(receipt.get("receipt_id")) or None,
                "verification_state": _t(receipt.get("verification_state")) or None,
            }
            protocol_frames[frame_id] = build_protocol_frame_row(
                frame_id=_t(frame_row.get("frame_id")),
                protocol_id=_t(frame_row.get("protocol_id")),
                src_endpoint_id=_t(frame_row.get("src_endpoint_id")),
                dst_address=_m(frame_row.get("dst_address")),
                payload_ref=_m(frame_row.get("payload_ref")),
                checksum=_t(frame_row.get("checksum")),
                tick_sent=_i(frame_row.get("tick_sent"), 0),
                extensions=frame_extensions,
            )
    for delivered_row in [dict(row) for row in _l(transport.get("delivered_rows")) if isinstance(row, Mapping)]:
        receipt = dict(receipt_index.get((_t(delivered_row.get("envelope_id")), _t(delivered_row.get("recipient_subject_id")))) or {})
        if not receipt:
            continue
        envelope_extensions = _m(delivered_row.get("envelope_extensions"))
        protocol_payload_ref = _m(envelope_extensions.get("protocol_payload_ref"))
        for slot in [dict(item) for item in _l(_m(delivered_row.get("envelope_extensions")).get("logic_protocol_target_slots")) if isinstance(item, Mapping)]:
            if protocol_payload_ref:
                protocol_id = _t(envelope_extensions.get("protocol_id")) or "protocol.none"
                protocol_row = dict(_by_id(_rows(protocol_registry_payload, "protocols"), "protocol_id").get(protocol_id) or {})
                request = {
                    "network_id": _t(slot.get("network_id")),
                    "element_id": _t(slot.get("element_id")),
                    "port_id": _t(slot.get("port_id")),
                    "signal_type_id": _t(protocol_payload_ref.get("signal_type_id")) or "signal.message",
                    "carrier_type_id": "carrier.sig",
                    "delay_policy_id": "delay.sig_delivery",
                    "noise_policy_id": "noise.none",
                    "protocol_id": protocol_id,
                    "protocol_definition_rows": [protocol_row] if protocol_row else [],
                    "value_payload": _m(protocol_payload_ref.get("value_payload")),
                    "extensions": {
                        "adapter_kind": "carrier.sig.protocol_delivery",
                        "bus_id": None if envelope_extensions.get("bus_id") is None else _t(envelope_extensions.get("bus_id")) or None,
                        "protocol_frame_id": _t(envelope_extensions.get("protocol_frame_id")) or None,
                        "receipt_id": _t(receipt.get("receipt_id")) or None,
                        "receipt_subject_id": _t(receipt.get("subject_id")) or None,
                        "delivery_event_id": _t(receipt.get("delivery_event_id")) or None,
                        "verification_state": _t(receipt.get("verification_state")) or None,
                    },
                }
            else:
                request = sig_receipt_to_signal_request(
                    network_id=_t(slot.get("network_id")),
                    element_id=_t(slot.get("element_id")),
                    port_id=_t(slot.get("port_id")),
                    receipt_row=receipt,
                    delay_policy_id="delay.sig_delivery",
                    noise_policy_id="noise.none",
                    protocol_id=_t(_m(delivered_row.get("envelope_extensions")).get("protocol_id")) or "protocol.none",
                )
            updated = process_signal_set_fn(
                current_tick=int(max(0, _i(current_tick, 0))),
                signal_store_state=updated_signal_store_state,
                signal_request=request,
                signal_type_registry_payload=signal_type_registry_payload,
                carrier_type_registry_payload=carrier_type_registry_payload,
                signal_delay_policy_registry_payload=signal_delay_policy_registry_payload,
                signal_noise_policy_registry_payload=signal_noise_policy_registry_payload,
                bus_encoding_registry_payload=bus_encoding_registry_payload,
                protocol_registry_payload=protocol_registry_payload,
                compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
                compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
                tolerance_policy_registry_payload=tolerance_policy_registry_payload,
            )
            if _t(updated.get("result")) in {"complete", "throttled"}:
                updated_signal_store_state = updated.get("signal_store_state") or updated_signal_store_state
                delivered_receipt_count += 1
    return {
        "signal_store_state": updated_signal_store_state,
        "signal_transport_state": state,
        "logic_protocol_frame_rows": normalize_protocol_frame_rows(list(protocol_frames.values())),
        "logic_protocol_event_record_rows": normalize_protocol_event_record_rows(protocol_events),
        "delivered_receipt_count": int(delivered_receipt_count),
    }


def arbitrate_logic_protocol_frames(*, current_tick: int, protocol_frame_rows: object, arbitration_state_rows: object, protocol_event_record_rows: object, pending_signal_update_rows: object, signal_transport_state: Mapping[str, object] | None, protocol_registry_payload: Mapping[str, object] | None, arbitration_policy_registry_payload: Mapping[str, object] | None, logic_security_policy_registry_payload: Mapping[str, object] | None) -> dict:
    from logic.eval.runtime_state import build_logic_pending_signal_update_row, normalize_logic_pending_signal_update_rows

    tick = int(max(0, _i(current_tick, 0)))
    protocols = _by_id(_rows(protocol_registry_payload, "protocols"), "protocol_id")
    arb_rows = _by_id(_rows(arbitration_policy_registry_payload, "arbitration_policies", "policies"), "arbitration_policy_id")
    sec_rows = _by_id(_rows(logic_security_policy_registry_payload, "logic_security_policies"), "security_policy_id")
    frames = normalize_protocol_frame_rows(protocol_frame_rows)
    states = _by_id(normalize_arbitration_state_rows(arbitration_state_rows), "bus_id")
    events = list(normalize_protocol_event_record_rows(protocol_event_record_rows))
    pending = list(normalize_logic_pending_signal_update_rows(pending_signal_update_rows))
    transport_state = {
        **_m(signal_transport_state),
        "signal_channel_rows": normalize_signal_channel_rows(_m(signal_transport_state).get("signal_channel_rows")),
        "signal_message_envelope_rows": normalize_signal_message_envelope_rows(_m(signal_transport_state).get("signal_message_envelope_rows")),
        "signal_transport_queue_rows": normalize_transport_queue_rows(_m(signal_transport_state).get("signal_transport_queue_rows")),
        "message_delivery_event_rows": normalize_message_delivery_event_rows(_m(signal_transport_state).get("message_delivery_event_rows")),
        "knowledge_receipt_rows": normalize_knowledge_receipt_rows(_m(signal_transport_state).get("knowledge_receipt_rows")),
        "network_graph_rows": [dict(row) for row in _l(_m(signal_transport_state).get("network_graph_rows")) if isinstance(row, Mapping)],
        "signal_trust_edge_rows": [
            dict(row)
            for row in _l(_m(signal_transport_state).get("signal_trust_edge_rows") or _m(signal_transport_state).get("trust_edge_rows"))
            if isinstance(row, Mapping)
        ],
    }
    explain_rows = []
    security_fail_rows = []
    queued: Dict[str, list[dict]] = {}
    kept = []
    for row in frames:
        ext = _m(row.get("extensions"))
        bus_id = _t(ext.get("bus_id")) or _t(_m(protocols.get(_t(row.get("protocol_id")))).get("bus_id"))
        if _t(ext.get("status")).lower() == "queued" and _i(ext.get("next_arbitration_tick", row.get("tick_sent")), 0) <= tick and bus_id:
            queued.setdefault(bus_id, []).append(dict(row))
        else:
            kept.append(dict(row))
    for bus_id in sorted(queued.keys()):
        contenders = sorted(queued.get(bus_id) or [], key=lambda item: (_t(item.get("src_endpoint_id")), _t(item.get("frame_id"))))
        protocol_row = dict(protocols.get(_t(contenders[0].get("protocol_id"))) or {})
        policy_id = _t(protocol_row.get("arbitration_policy_id")) or "arb.fixed_priority"
        state = dict(states.get(bus_id) or {"bus_id": bus_id, "policy_id": policy_id})
        winner = {}
        if policy_id == "arb.time_slice":
            winner = dict(contenders[tick % len(contenders)])
        elif policy_id == "arb.token":
            token_holder = _t(state.get("token_holder"))
            winner = dict(next((row for row in contenders if _t(row.get("src_endpoint_id")) == token_holder), {}))
            if not winner:
                winner = dict(contenders[0])
            ordered = sorted({_t(row.get("src_endpoint_id")) for row in contenders if _t(row.get("src_endpoint_id"))})
            if ordered:
                index = ordered.index(_t(winner.get("src_endpoint_id"))) if _t(winner.get("src_endpoint_id")) in ordered else 0
                state["token_holder"] = ordered[(index + 1) % len(ordered)]
        else:
            winner = dict(contenders[0])
        state["last_winner"] = _t(winner.get("src_endpoint_id")) or None
        states[bus_id] = build_arbitration_state_row(bus_id=bus_id, policy_id=policy_id, token_holder=(None if state.get("token_holder") is None else _t(state.get("token_holder")) or None), last_winner=(None if state.get("last_winner") is None else _t(state.get("last_winner")) or None), extensions={"last_tick": tick})
        for row in contenders:
            if _t(row.get("frame_id")) == _t(winner.get("frame_id")):
                continue
            ext = _m(row.get("extensions"))
            kept.append(build_protocol_frame_row(frame_id=_t(row.get("frame_id")), protocol_id=_t(row.get("protocol_id")), src_endpoint_id=_t(row.get("src_endpoint_id")), dst_address=_m(row.get("dst_address")), payload_ref=_m(row.get("payload_ref")), checksum=_t(row.get("checksum")), tick_sent=_i(row.get("tick_sent"), tick), extensions={**ext, "next_arbitration_tick": tick + 1, "status": "queued"}))
            explain_rows.append(_explain("explain.protocol_arbitration_loss", bus_id, {"tick": tick, "frame_id": _t(row.get("frame_id"))}, ["retry on a later tick or reduce bus contention"], {"frame_id": _t(row.get("frame_id"))}))
        ext = _m(winner.get("extensions"))
        sec_id = _t(ext.get("security_policy_id")) or _t(protocol_row.get("security_policy_id")) or "sec.none"
        sec_row = dict(sec_rows.get(sec_id) or sec_rows.get("sec.none") or {})
        sec_ctx = _m(ext.get("security_context"))
        blocked = (bool(sec_row.get("requires_auth", False)) and not bool(sec_ctx.get("authenticated", False) and sec_ctx.get("credential_verified", False))) or (bool(sec_row.get("requires_encryption", False)) and not bool(sec_ctx.get("encrypted", False)))
        corrupted = bool(ext.get("corrupted", False) or _m(_m(winner.get("payload_ref")).get("extensions")).get("corrupted", False))
        if blocked:
            events.append(build_protocol_event_record_row(event_id="event.logic.protocol.{}".format(canonical_sha256({"tick": tick, "bus": bus_id, "frame": _t(winner.get("frame_id")), "result": "blocked"})[:16]), protocol_id=_t(winner.get("protocol_id")), bus_id=bus_id, frame_id=_t(winner.get("frame_id")), result="blocked", tick=tick, extensions={"security_policy_id": sec_id}))
            security_fail_rows.append({"schema_version": "1.0.0", "event_id": "event.logic.security_fail.{}".format(canonical_sha256({"tick": tick, "frame": _t(winner.get("frame_id"))})[:16]), "tick": tick, "network_id": _t(ext.get("network_id")), "edge_id": "edge.logic.protocol", "security_policy_id": sec_id, "reason": "protocol_security_block", "signal_id": None, "deterministic_fingerprint": "", "extensions": {}})
            explain_rows.append(_explain("explain.protocol_security_block", bus_id, {"tick": tick, "frame_id": _t(winner.get("frame_id"))}, ["provide valid credentials or encryption"], {"frame_id": _t(winner.get("frame_id"))}))
            continue
        if corrupted:
            events.append(build_protocol_event_record_row(event_id="event.logic.protocol.{}".format(canonical_sha256({"tick": tick, "bus": bus_id, "frame": _t(winner.get("frame_id")), "result": "corrupted"})[:16]), protocol_id=_t(winner.get("protocol_id")), bus_id=bus_id, frame_id=_t(winner.get("frame_id")), result="corrupted", tick=tick, extensions={}))
            explain_rows.append(_explain("explain.protocol_corruption", bus_id, {"tick": tick, "frame_id": _t(winner.get("frame_id"))}, ["inspect LOGIC-8 fault or noise state"], {"frame_id": _t(winner.get("frame_id"))}))
            continue
        if _t(ext.get("carrier_type_id")) == "carrier.sig":
            channel_id = "channel.logic.protocol.{}".format(canonical_sha256({"bus_id": bus_id})[:16])
            graph_id = "graph.logic.protocol.{}".format(canonical_sha256({"bus_id": bus_id})[:16])
            channels = list(transport_state.get("signal_channel_rows") or [])
            if channel_id not in {str(row.get("channel_id", "")).strip() for row in channels if isinstance(row, Mapping)}:
                channels.append(build_signal_channel(channel_id=channel_id, channel_type_id="channel.wired_basic", network_graph_id=graph_id, capacity_per_tick=1, base_delay_ticks=int(max(0, _i(ext.get("deliver_delay_ticks", 1), 1) - 1)), loss_policy_id="loss.none", encryption_policy_id=("enc.required_stub" if sec_id == "sec.encrypted_required_stub" else None), extensions={"routing_policy_id": "route.shortest_delay", "source": "LOGIC9-4"}))
                transport_state["signal_channel_rows"] = normalize_signal_channel_rows(channels)
            source_node = "node.logic.protocol.src.{}".format(_t(winner.get("src_endpoint_id")))
            target_slots = [dict(item) for item in _l(ext.get("target_slots")) if isinstance(item, Mapping)]
            protocol_graph_row = {
                "schema_version": "1.0.0",
                "graph_id": graph_id,
                "validation_mode": "warn",
                "node_type_schema_id": "dominium.schema.signals.signal_node_payload",
                "edge_type_schema_id": "dominium.schema.signals.signal_edge_payload",
                "payload_schema_versions": {
                    "dominium.schema.signals.signal_node_payload": "1.0.0",
                    "dominium.schema.signals.signal_edge_payload": "1.0.0",
                },
                "deterministic_routing_policy_id": "route.shortest_delay",
                "nodes": [{"schema_version": "1.0.0", "node_id": source_node, "node_type_id": "signal_node", "payload_ref": {"node_kind": "relay"}, "tags": []}]
                + [{"schema_version": "1.0.0", "node_id": _t(slot.get("node_id")), "node_type_id": "signal_node", "payload_ref": {"node_kind": "relay"}, "tags": []} for slot in target_slots],
                "edges": [{"schema_version": "1.0.0", "edge_id": "edge.logic.protocol.{}".format(canonical_sha256({"from": source_node, "to": _t(slot.get("node_id"))})[:16]), "from_node_id": source_node, "to_node_id": _t(slot.get("node_id")), "edge_type_id": "signal_edge", "delay_ticks": 0, "capacity": 1, "payload_ref": {"edge_kind": "relay_link"}, "tags": []} for slot in target_slots],
                "extensions": {"source": "LOGIC9-4"},
            }
            transport_state["network_graph_rows"] = _upsert_by_id(
                transport_state.get("network_graph_rows"),
                "graph_id",
                protocol_graph_row,
            )
            send = process_signal_send(current_tick=tick, channel_id=channel_id, from_node_id=source_node, artifact_id=_t(winner.get("frame_id")), sender_subject_id="subject.logic.protocol.{}".format(_t(winner.get("src_endpoint_id"))), recipient_address={"kind": _t(_m(winner.get("dst_address")).get("kind")) or "unicast", "subject_id": _t(_m(winner.get("dst_address")).get("subject_id")) or (_t(target_slots[0].get("subject_id")) if target_slots else ""), "subject_ids": [_t(slot.get("subject_id")) for slot in target_slots if _t(slot.get("subject_id"))], "broadcast_subject_ids": [_t(slot.get("subject_id")) for slot in target_slots if _t(slot.get("subject_id"))], "broadcast_scope": _t(_m(winner.get("dst_address")).get("broadcast_scope")) or bus_id, "to_node_id": _t(_m(winner.get("dst_address")).get("to_node_id")) or (_t(target_slots[0].get("node_id")) if target_slots else "node.unknown")}, signal_channel_rows=transport_state["signal_channel_rows"], signal_message_envelope_rows=transport_state["signal_message_envelope_rows"], signal_transport_queue_rows=transport_state["signal_transport_queue_rows"], envelope_extensions={"protocol_id": _t(winner.get("protocol_id")), "protocol_frame_id": _t(winner.get("frame_id")), "logic_protocol_target_slots": target_slots, "protocol_payload_ref": _m(winner.get("payload_ref")), "carrier_type_id": _t(ext.get("carrier_type_id")) or "carrier.sig", "bus_id": bus_id or None, "security_header": sec_ctx})
            transport_state["signal_message_envelope_rows"] = normalize_signal_message_envelope_rows(send.get("signal_message_envelope_rows"))
            transport_state["signal_transport_queue_rows"] = normalize_transport_queue_rows(send.get("signal_transport_queue_rows"))
            kept.append(
                build_protocol_frame_row(
                    frame_id=_t(winner.get("frame_id")),
                    protocol_id=_t(winner.get("protocol_id")),
                    src_endpoint_id=_t(winner.get("src_endpoint_id")),
                    dst_address=_m(winner.get("dst_address")),
                    payload_ref=_m(winner.get("payload_ref")),
                    checksum=_t(winner.get("checksum")),
                    tick_sent=_i(winner.get("tick_sent"), tick),
                    extensions={**ext, "status": "in_transit", "arbitrated_tick": tick},
                )
            )
        else:
            for slot in [dict(item) for item in _l(ext.get("target_slots")) if isinstance(item, Mapping)]:
                pending.append(build_logic_pending_signal_update_row(network_id=_t(slot.get("network_id")), source_element_id=_t(ext.get("source_element_id")) or _t(winner.get("src_endpoint_id")), source_port_id=_t(ext.get("source_port_id")) or "out.protocol", target_element_id=_t(slot.get("element_id")), target_port_id=_t(slot.get("port_id")), signal_type_id=_t(_m(winner.get("payload_ref")).get("signal_type_id")) or "signal.message", carrier_type_id=_t(ext.get("carrier_type_id")) or "carrier.electrical", delay_policy_id=_t(ext.get("delay_policy_id")) or "delay.none", noise_policy_id=_t(ext.get("noise_policy_id")) or "noise.none", deliver_tick=tick + int(max(1, _i(ext.get("deliver_delay_ticks", 1), 1))), value_payload=_m(_m(winner.get("payload_ref")).get("value_payload")), bus_id=(None if bus_id is None else bus_id), protocol_id=_t(winner.get("protocol_id")) or None, extensions={"protocol_frame_id": _t(winner.get("frame_id")), "scheduled_by": "LOGIC9-3"}))
            kept.append(build_protocol_frame_row(frame_id=_t(winner.get("frame_id")), protocol_id=_t(winner.get("protocol_id")), src_endpoint_id=_t(winner.get("src_endpoint_id")), dst_address=_m(winner.get("dst_address")), payload_ref=_m(winner.get("payload_ref")), checksum=_t(winner.get("checksum")), tick_sent=_i(winner.get("tick_sent"), tick), extensions={**ext, "status": "delivered", "arbitrated_tick": tick}))
            events.append(build_protocol_event_record_row(event_id="event.logic.protocol.{}".format(canonical_sha256({"tick": tick, "bus": bus_id, "frame": _t(winner.get("frame_id")), "result": "delivered"})[:16]), protocol_id=_t(winner.get("protocol_id")), bus_id=bus_id, frame_id=_t(winner.get("frame_id")), result="delivered", tick=tick, extensions={"carrier_type_id": _t(ext.get("carrier_type_id"))}))
    return {"logic_protocol_frame_rows": normalize_protocol_frame_rows(kept), "logic_arbitration_state_rows": normalize_arbitration_state_rows(list(states.values())), "logic_protocol_event_record_rows": normalize_protocol_event_record_rows(events), "logic_pending_signal_update_rows": normalize_logic_pending_signal_update_rows(pending), "signal_transport_state": transport_state, "logic_security_fail_rows": security_fail_rows, "explain_artifact_rows": explain_rows}


__all__ = ["arbitrate_logic_protocol_frames", "build_protocol_frame_from_delivery", "transport_logic_sig_receipts"]

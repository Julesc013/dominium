"""Deterministic SIG-0 signal transport skeleton."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.core.graph.routing_engine import RoutingError, query_route_result
from tools.xstack.compatx.canonical_json import canonical_sha256
from .channel_executor import execute_channel_transport_tick


REFUSAL_SIGNAL_INVALID = "refusal.signal.invalid"
REFUSAL_SIGNAL_ROUTE_UNAVAILABLE = "refusal.signal.route_unavailable"


class SignalTransportError(ValueError):
    """Deterministic signal transport refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_SIGNAL_INVALID)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _clamp_trust_weight(value: object) -> float:
    try:
        token = float(value)
    except (TypeError, ValueError):
        token = 1.0
    if token < 0.0:
        return 0.0
    if token > 1.0:
        return 1.0
    return float(token)


def _routing_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("routing_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("routing_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("policy_id", ""))):
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "policy_id": policy_id,
            "description": str(row.get("description", "")).strip(),
            "tie_break_policy": str(row.get("tie_break_policy", "")).strip() or "edge_id_lexicographic",
            "allow_multi_hop": bool(row.get("allow_multi_hop", True)),
            "optimization_metric": str(row.get("optimization_metric", "")).strip() or "delay_ticks",
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    out = dict(payload)
    out["deterministic_fingerprint"] = canonical_sha256(payload)
    return out


def signal_channel_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("signal_channel_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("signal_channel_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("channel_type_id", ""))):
        channel_type_id = str(row.get("channel_type_id", "")).strip()
        if not channel_type_id:
            continue
        out[channel_type_id] = {
            "schema_version": "1.0.0",
            "channel_type_id": channel_type_id,
            "description": str(row.get("description", "")).strip(),
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def loss_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("loss_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("loss_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("loss_policy_id", ""))):
        loss_policy_id = str(row.get("loss_policy_id", "")).strip()
        if not loss_policy_id:
            continue
        out[loss_policy_id] = {
            "schema_version": "1.0.0",
            "loss_policy_id": loss_policy_id,
            "description": str(row.get("description", "")).strip(),
            "deterministic_function_id": str(row.get("deterministic_function_id", "")).strip() or "loss.none",
            "parameters": _as_map(row.get("parameters")),
            "uses_rng_stream": bool(row.get("uses_rng_stream", False)),
            "rng_stream_name": None if row.get("rng_stream_name") is None else str(row.get("rng_stream_name", "")).strip() or None,
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def encryption_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("encryption_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("encryption_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("encryption_policy_id", ""))):
        encryption_policy_id = str(row.get("encryption_policy_id", "")).strip()
        if not encryption_policy_id:
            continue
        out[encryption_policy_id] = {
            "schema_version": "1.0.0",
            "encryption_policy_id": encryption_policy_id,
            "description": str(row.get("description", "")).strip(),
            "deterministic_function_id": str(row.get("deterministic_function_id", "")).strip() or "enc.none",
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_signal_channel(
    *,
    channel_id: str,
    channel_type_id: str,
    network_graph_id: str,
    capacity_per_tick: int,
    base_delay_ticks: int,
    loss_policy_id: str,
    encryption_policy_id: str | None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "channel_id": str(channel_id or "").strip(),
        "channel_type_id": str(channel_type_id or "").strip(),
        "network_graph_id": str(network_graph_id or "").strip(),
        "capacity_per_tick": int(max(1, _as_int(capacity_per_tick, 1))),
        "base_delay_ticks": int(max(0, _as_int(base_delay_ticks, 0))),
        "loss_policy_id": str(loss_policy_id or "").strip() or "loss.none",
        "encryption_policy_id": None if encryption_policy_id is None else str(encryption_policy_id).strip() or None,
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["channel_id"] or not payload["channel_type_id"] or not payload["network_graph_id"]:
        raise SignalTransportError(REFUSAL_SIGNAL_INVALID, "signal channel requires channel_id, channel_type_id, and network_graph_id", payload)
    return _with_fingerprint(payload)


def normalize_signal_channel_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("channel_id", ""))):
        channel_id = str(row.get("channel_id", "")).strip()
        if not channel_id:
            continue
        try:
            out[channel_id] = build_signal_channel(
                channel_id=channel_id,
                channel_type_id=str(row.get("channel_type_id", "")).strip(),
                network_graph_id=str(row.get("network_graph_id", "")).strip(),
                capacity_per_tick=_as_int(row.get("capacity_per_tick", 1), 1),
                base_delay_ticks=_as_int(row.get("base_delay_ticks", 0), 0),
                loss_policy_id=str(row.get("loss_policy_id", "loss.none")).strip() or "loss.none",
                encryption_policy_id=None if row.get("encryption_policy_id") is None else str(row.get("encryption_policy_id", "")).strip() or None,
                extensions=_as_map(row.get("extensions")),
            )
        except SignalTransportError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def signal_channel_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("channel_id", "")).strip(), dict(row)) for row in normalize_signal_channel_rows(rows))

def deterministic_signal_message_envelope_id(*, artifact_id: str, sender_subject_id: str, recipient_address: Mapping[str, object], created_tick: int) -> str:
    digest = canonical_sha256(
        {
            "artifact_id": str(artifact_id or "").strip(),
            "sender_subject_id": str(sender_subject_id or "").strip(),
            "recipient_address": _as_map(recipient_address),
            "created_tick": int(max(0, _as_int(created_tick, 0))),
        }
    )
    return "env.signal.{}".format(digest[:16])


def build_signal_message_envelope(
    *,
    envelope_id: str,
    artifact_id: str,
    sender_subject_id: str,
    recipient_address: Mapping[str, object],
    created_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "envelope_id": str(envelope_id or "").strip(),
        "artifact_id": str(artifact_id or "").strip(),
        "sender_subject_id": str(sender_subject_id or "").strip(),
        "recipient_address": _as_map(recipient_address),
        "created_tick": int(max(0, _as_int(created_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["envelope_id"] or not payload["artifact_id"] or not payload["sender_subject_id"]:
        raise SignalTransportError(REFUSAL_SIGNAL_INVALID, "signal envelope requires envelope_id, artifact_id, and sender_subject_id", payload)
    return _with_fingerprint(payload)


def normalize_signal_message_envelope_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("envelope_id", ""))):
        envelope_id = str(row.get("envelope_id", "")).strip()
        if not envelope_id:
            continue
        try:
            out[envelope_id] = build_signal_message_envelope(
                envelope_id=envelope_id,
                artifact_id=str(row.get("artifact_id", "")).strip(),
                sender_subject_id=str(row.get("sender_subject_id", "")).strip(),
                recipient_address=_as_map(row.get("recipient_address")),
                created_tick=_as_int(row.get("created_tick", 0), 0),
                extensions=_as_map(row.get("extensions")),
            )
        except SignalTransportError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def deterministic_message_delivery_event_id(*, envelope_id: str, from_node_id: str, to_node_id: str, delivered_tick: int, delivery_state: str, sequence: int) -> str:
    digest = canonical_sha256(
        {
            "envelope_id": str(envelope_id or "").strip(),
            "from_node_id": str(from_node_id or "").strip(),
            "to_node_id": str(to_node_id or "").strip(),
            "delivered_tick": int(max(0, _as_int(delivered_tick, 0))),
            "delivery_state": str(delivery_state or "").strip(),
            "sequence": int(max(0, _as_int(sequence, 0))),
        }
    )
    return "event.signal_delivery.{}".format(digest[:16])


def deterministic_courier_commitment_id(*, channel_id: str, envelope_id: str, recipient_subject_id: str | None, queue_key: str) -> str:
    digest = canonical_sha256(
        {
            "channel_id": str(channel_id or "").strip(),
            "envelope_id": str(envelope_id or "").strip(),
            "recipient_subject_id": None if recipient_subject_id is None else str(recipient_subject_id).strip() or None,
            "queue_key": str(queue_key or "").strip(),
        }
    )
    return "commitment.signal_courier.{}".format(digest[:16])


def build_message_delivery_event(*, event_id: str, envelope_id: str, from_node_id: str, to_node_id: str, delivered_tick: int, delivery_state: str, extensions: Mapping[str, object] | None = None) -> dict:
    state_token = str(delivery_state or "").strip().lower()
    if state_token not in {"delivered", "lost", "corrupted"}:
        state_token = "lost"
    payload = {
        "schema_version": "1.0.0",
        "event_id": str(event_id or "").strip(),
        "envelope_id": str(envelope_id or "").strip(),
        "from_node_id": str(from_node_id or "").strip() or "node.unknown",
        "to_node_id": str(to_node_id or "").strip() or "node.unknown",
        "delivered_tick": int(max(0, _as_int(delivered_tick, 0))),
        "delivery_state": state_token,
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["event_id"] or not payload["envelope_id"]:
        raise SignalTransportError(REFUSAL_SIGNAL_INVALID, "message delivery event requires event_id and envelope_id", payload)
    return _with_fingerprint(payload)


def normalize_message_delivery_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: (_as_int(item.get("delivered_tick", 0), 0), str(item.get("event_id", "")))):
        event_id = str(row.get("event_id", "")).strip()
        if not event_id:
            continue
        try:
            out[event_id] = build_message_delivery_event(
                event_id=event_id,
                envelope_id=str(row.get("envelope_id", "")).strip(),
                from_node_id=str(row.get("from_node_id", "")).strip(),
                to_node_id=str(row.get("to_node_id", "")).strip(),
                delivered_tick=_as_int(row.get("delivered_tick", 0), 0),
                delivery_state=str(row.get("delivery_state", "lost")).strip() or "lost",
                extensions=_as_map(row.get("extensions")),
            )
        except SignalTransportError:
            continue
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda key: (_as_int(out[key].get("delivered_tick", 0), 0), str(key)))]


def normalize_courier_arrival_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        out.append(
            {
                "schema_version": "1.0.0",
                "queue_key": str(row.get("queue_key", "")).strip() or None,
                "envelope_id": str(row.get("envelope_id", "")).strip() or None,
                "recipient_subject_id": str(row.get("recipient_subject_id", "")).strip() or None,
                "arrival_tick": int(max(0, _as_int(row.get("arrival_tick", 0), 0))),
                "extensions": _as_map(row.get("extensions")),
            }
        )
    return sorted(
        out,
        key=lambda row: (
            str(row.get("queue_key", "")),
            str(row.get("envelope_id", "")),
            str(row.get("recipient_subject_id", "")),
            _as_int(row.get("arrival_tick", 0), 0),
        ),
    )


def deterministic_knowledge_receipt_id(*, subject_id: str, artifact_id: str, envelope_id: str, acquired_tick: int) -> str:
    digest = canonical_sha256(
        {
            "subject_id": str(subject_id or "").strip(),
            "artifact_id": str(artifact_id or "").strip(),
            "envelope_id": str(envelope_id or "").strip(),
            "acquired_tick": int(max(0, _as_int(acquired_tick, 0))),
        }
    )
    return "receipt.knowledge.{}".format(digest[:16])


def build_knowledge_receipt(*, receipt_id: str, subject_id: str, artifact_id: str, envelope_id: str, acquired_tick: int, trust_weight: float = 1.0, delivery_event_id: str | None = None, extensions: Mapping[str, object] | None = None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "receipt_id": str(receipt_id or "").strip(),
        "subject_id": str(subject_id or "").strip(),
        "artifact_id": str(artifact_id or "").strip(),
        "envelope_id": str(envelope_id or "").strip(),
        "delivery_event_id": None if delivery_event_id is None else str(delivery_event_id).strip() or None,
        "acquired_tick": int(max(0, _as_int(acquired_tick, 0))),
        "trust_weight": float(trust_weight),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["receipt_id"] or not payload["subject_id"] or not payload["artifact_id"] or not payload["envelope_id"]:
        raise SignalTransportError(REFUSAL_SIGNAL_INVALID, "knowledge receipt requires receipt_id, subject_id, artifact_id, and envelope_id", payload)
    return _with_fingerprint(payload)


def normalize_knowledge_receipt_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: (_as_int(item.get("acquired_tick", 0), 0), str(item.get("receipt_id", "")))):
        receipt_id = str(row.get("receipt_id", "")).strip()
        if not receipt_id:
            continue
        try:
            out[receipt_id] = build_knowledge_receipt(
                receipt_id=receipt_id,
                subject_id=str(row.get("subject_id", "")).strip(),
                artifact_id=str(row.get("artifact_id", "")).strip(),
                envelope_id=str(row.get("envelope_id", "")).strip(),
                acquired_tick=_as_int(row.get("acquired_tick", 0), 0),
                trust_weight=float(row.get("trust_weight", 1.0)),
                delivery_event_id=None if row.get("delivery_event_id") is None else str(row.get("delivery_event_id", "")).strip() or None,
                extensions=_as_map(row.get("extensions")),
            )
        except (SignalTransportError, TypeError, ValueError):
            continue
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda key: (_as_int(out[key].get("acquired_tick", 0), 0), str(key)))]


def normalize_transport_queue_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        out.append(
            {
                "schema_version": "1.0.0",
                "queue_key": str(row.get("queue_key", "")).strip(),
                "channel_id": str(row.get("channel_id", "")).strip(),
                "envelope_id": str(row.get("envelope_id", "")).strip(),
                "artifact_id": str(row.get("artifact_id", "")).strip(),
                "sender_subject_id": str(row.get("sender_subject_id", "")).strip(),
                "recipient_subject_id": None if row.get("recipient_subject_id") is None else str(row.get("recipient_subject_id", "")).strip() or None,
                "from_node_id": str(row.get("from_node_id", "")).strip() or "node.unknown",
                "to_node_id": str(row.get("to_node_id", "")).strip() or "node.unknown",
                "remaining_delay_ticks": int(max(0, _as_int(row.get("remaining_delay_ticks", 0), 0))),
                "attempt_index": int(max(0, _as_int(row.get("attempt_index", 0), 0))),
                "deterministic_fingerprint": "",
                "extensions": _as_map(row.get("extensions")),
            }
        )
    for row in out:
        if not row["queue_key"]:
            row["queue_key"] = "queue.signal.{}".format(canonical_sha256({"channel_id": row["channel_id"], "envelope_id": row["envelope_id"], "recipient_subject_id": row["recipient_subject_id"]})[:16])
        row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return sorted(out, key=lambda row: (str(row.get("channel_id", "")), str(row.get("envelope_id", "")), str(row.get("recipient_subject_id", "")), str(row.get("queue_key", ""))))

def _recipient_rows(envelope_row: Mapping[str, object]) -> List[dict]:
    addr = _as_map(envelope_row.get("recipient_address"))
    kind = str(addr.get("kind", "single")).strip().lower() or "single"
    to_node_id = str(addr.get("to_node_id", "")).strip() or "node.unknown"
    if kind == "single":
        return [{"recipient_subject_id": str(addr.get("subject_id", "")).strip() or None, "to_node_id": to_node_id}]
    if kind == "group":
        return [{"recipient_subject_id": token, "to_node_id": to_node_id} for token in _sorted_tokens(addr.get("subject_ids"))]
    targets = _sorted_tokens(addr.get("broadcast_subject_ids"))
    if targets:
        return [{"recipient_subject_id": token, "to_node_id": to_node_id} for token in targets]
    return [{"recipient_subject_id": None, "to_node_id": to_node_id}]


def enqueue_signal_envelope(*, channel_row: Mapping[str, object], envelope_row: Mapping[str, object], from_node_id: str) -> List[dict]:
    out = []
    for recipient in _recipient_rows(envelope_row):
        out.append(
            {
                "schema_version": "1.0.0",
                "queue_key": "queue.signal.{}".format(canonical_sha256({"channel_id": str(channel_row.get("channel_id", "")).strip(), "envelope_id": str(envelope_row.get("envelope_id", "")).strip(), "recipient_subject_id": recipient.get("recipient_subject_id"), "from_node_id": str(from_node_id or "").strip(), "to_node_id": str(recipient.get("to_node_id", "")).strip()})[:16]),
                "channel_id": str(channel_row.get("channel_id", "")).strip(),
                "envelope_id": str(envelope_row.get("envelope_id", "")).strip(),
                "artifact_id": str(envelope_row.get("artifact_id", "")).strip(),
                "sender_subject_id": str(envelope_row.get("sender_subject_id", "")).strip(),
                "recipient_subject_id": recipient.get("recipient_subject_id"),
                "from_node_id": str(from_node_id or "").strip() or "node.unknown",
                "to_node_id": str(recipient.get("to_node_id", "")).strip() or "node.unknown",
                "remaining_delay_ticks": int(max(0, _as_int(channel_row.get("base_delay_ticks", 0), 0))),
                "attempt_index": 0,
                "extensions": {},
            }
        )
    return normalize_transport_queue_rows(out)


def _upsert_row_by_id(rows: object, id_key: str, row: Mapping[str, object]) -> List[dict]:
    target_id = str(dict(row).get(id_key, "")).strip()
    if not target_id:
        return [dict(item) for item in list(rows or []) if isinstance(item, Mapping)]
    out: Dict[str, dict] = {}
    for item in list(rows or []):
        if not isinstance(item, Mapping):
            continue
        row_id = str(item.get(id_key, "")).strip()
        if not row_id:
            continue
        out[row_id] = dict(item)
    out[target_id] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys())]


def process_signal_send(
    *,
    current_tick: int,
    channel_id: str,
    from_node_id: str,
    artifact_id: str,
    sender_subject_id: str,
    recipient_address: Mapping[str, object],
    signal_channel_rows: object,
    signal_message_envelope_rows: object,
    signal_transport_queue_rows: object,
    envelope_id: str | None = None,
    envelope_extensions: Mapping[str, object] | None = None,
) -> dict:
    channels = signal_channel_rows_by_id(signal_channel_rows)
    channel_token = str(channel_id or "").strip()
    channel_row = dict(channels.get(channel_token) or {})
    if not channel_row:
        raise SignalTransportError(
            REFUSAL_SIGNAL_INVALID,
            "signal_send requires a valid channel_id",
            {"channel_id": channel_token},
        )
    envelope_token = str(envelope_id or "").strip() or deterministic_signal_message_envelope_id(
        artifact_id=str(artifact_id or "").strip(),
        sender_subject_id=str(sender_subject_id or "").strip(),
        recipient_address=_as_map(recipient_address),
        created_tick=int(max(0, _as_int(current_tick, 0))),
    )
    envelope_row = build_signal_message_envelope(
        envelope_id=envelope_token,
        artifact_id=str(artifact_id or "").strip(),
        sender_subject_id=str(sender_subject_id or "").strip(),
        recipient_address=_as_map(recipient_address),
        created_tick=int(max(0, _as_int(current_tick, 0))),
        extensions=_as_map(envelope_extensions),
    )
    next_envelope_rows = _upsert_row_by_id(
        normalize_signal_message_envelope_rows(signal_message_envelope_rows),
        "envelope_id",
        envelope_row,
    )
    queued_rows = enqueue_signal_envelope(
        channel_row=channel_row,
        envelope_row=envelope_row,
        from_node_id=str(from_node_id or "").strip() or "node.unknown",
    )
    next_queue_rows = normalize_transport_queue_rows(
        list(normalize_transport_queue_rows(signal_transport_queue_rows)) + list(queued_rows)
    )
    return {
        "signal_message_envelope_rows": next_envelope_rows,
        "signal_transport_queue_rows": next_queue_rows,
        "envelope_row": dict(envelope_row),
        "queued_count": int(len(queued_rows)),
    }


def process_knowledge_acquire(
    *,
    current_tick: int,
    delivered_row: Mapping[str, object],
    knowledge_receipt_rows: object,
    trust_weight: float = 1.0,
) -> dict:
    row = dict(delivered_row or {})
    subject_id = str(row.get("recipient_subject_id", "")).strip()
    if not subject_id:
        return {
            "knowledge_receipt_rows": normalize_knowledge_receipt_rows(knowledge_receipt_rows),
            "knowledge_receipt_row": None,
            "acquired": False,
        }
    artifact_id = str(row.get("artifact_id", "")).strip()
    envelope_id = str(row.get("envelope_id", "")).strip()
    if (not artifact_id) or (not envelope_id):
        raise SignalTransportError(
            REFUSAL_SIGNAL_INVALID,
            "knowledge_acquire requires delivered artifact_id and envelope_id",
            {"delivered_row": row},
        )
    receipt_id = deterministic_knowledge_receipt_id(
        subject_id=subject_id,
        artifact_id=artifact_id,
        envelope_id=envelope_id,
        acquired_tick=int(max(0, _as_int(current_tick, 0))),
    )
    receipt_row = build_knowledge_receipt(
        receipt_id=receipt_id,
        subject_id=subject_id,
        artifact_id=artifact_id,
        envelope_id=envelope_id,
        acquired_tick=int(max(0, _as_int(current_tick, 0))),
        trust_weight=float(trust_weight),
        delivery_event_id=None if row.get("delivery_event_id") is None else str(row.get("delivery_event_id", "")).strip() or None,
        extensions={
            "channel_id": str(row.get("channel_id", "")).strip() or None,
        },
    )
    next_rows = _upsert_row_by_id(
        normalize_knowledge_receipt_rows(knowledge_receipt_rows),
        "receipt_id",
        receipt_row,
    )
    return {
        "knowledge_receipt_rows": next_rows,
        "knowledge_receipt_row": dict(receipt_row),
        "acquired": True,
    }


def process_signal_transport_tick(
    *,
    current_tick: int,
    signal_channel_rows: object,
    signal_transport_queue_rows: object,
    signal_message_envelope_rows: object,
    message_delivery_event_rows: object,
    knowledge_receipt_rows: object,
    network_graph_rows: object,
    loss_policy_registry: Mapping[str, object] | None,
    routing_policy_registry: Mapping[str, object] | None,
    max_cost_units: int,
    cost_units_per_delivery: int,
    route_cache_state: Mapping[str, object] | None = None,
    courier_arrival_rows: object = None,
    default_trust_weight: float = 1.0,
    trust_weight_by_subject_id: Mapping[str, object] | None = None,
) -> dict:
    transport = tick_signal_transport(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        signal_channel_rows=signal_channel_rows,
        signal_transport_queue_rows=signal_transport_queue_rows,
        envelope_rows=signal_message_envelope_rows,
        existing_delivery_event_rows=message_delivery_event_rows,
        network_graph_rows=network_graph_rows,
        loss_policy_registry=loss_policy_registry,
        routing_policy_registry=routing_policy_registry,
        max_cost_units=int(max(0, _as_int(max_cost_units, 0))),
        cost_units_per_delivery=int(max(1, _as_int(cost_units_per_delivery, 1))),
        route_cache_state=route_cache_state,
        courier_arrival_rows=courier_arrival_rows,
    )
    next_receipts = normalize_knowledge_receipt_rows(knowledge_receipt_rows)
    created_receipts = []
    trust_rows = dict((str(key).strip(), value) for key, value in dict(trust_weight_by_subject_id or {}).items() if str(key).strip())
    for delivered_row in list(dict(transport).get("delivered_rows") or []):
        recipient_subject_id = str(dict(delivered_row or {}).get("recipient_subject_id", "")).strip()
        subject_trust = _clamp_trust_weight(default_trust_weight)
        if recipient_subject_id in trust_rows:
            subject_trust = _clamp_trust_weight(trust_rows.get(recipient_subject_id))
        acquire_result = process_knowledge_acquire(
            current_tick=int(max(0, _as_int(current_tick, 0))),
            delivered_row=dict(delivered_row or {}),
            knowledge_receipt_rows=next_receipts,
            trust_weight=float(subject_trust),
        )
        next_receipts = normalize_knowledge_receipt_rows(acquire_result.get("knowledge_receipt_rows"))
        if bool(acquire_result.get("acquired", False)):
            created_receipts.append(dict(acquire_result.get("knowledge_receipt_row") or {}))
    out = dict(transport)
    out["knowledge_receipt_rows"] = next_receipts
    out["created_receipt_rows"] = sorted(
        (dict(row) for row in created_receipts if isinstance(row, Mapping)),
        key=lambda row: (
            _as_int(row.get("acquired_tick", 0), 0),
            str(row.get("subject_id", "")),
            str(row.get("artifact_id", "")),
            str(row.get("receipt_id", "")),
        ),
    )
    out["delivery_count"] = int(len(list(dict(out).get("delivered_rows") or [])))
    out["receipt_count"] = int(len(list(out.get("created_receipt_rows") or [])))
    return out


def _default_routing_policy_row() -> dict:
    return {
        "schema_version": "1.0.0",
        "policy_id": "route.shortest_delay",
        "description": "default signals routing policy",
        "tie_break_policy": "edge_id_lexicographic",
        "allow_multi_hop": True,
        "optimization_metric": "delay_ticks",
        "extensions": {},
    }


def _resolve_route_query(
    *,
    channel_row: Mapping[str, object],
    queue_row: Mapping[str, object],
    graph_rows_by_id: Mapping[str, dict],
    routing_policy_rows: Mapping[str, dict],
    route_cache_state: Mapping[str, object] | None,
) -> dict:
    from_node = str(queue_row.get("from_node_id", "")).strip()
    to_node = str(queue_row.get("to_node_id", "")).strip()
    if (not from_node) or (not to_node):
        raise SignalTransportError(
            REFUSAL_SIGNAL_ROUTE_UNAVAILABLE,
            "signal route requires from_node_id and to_node_id",
            {"queue_key": str(queue_row.get("queue_key", "")).strip()},
        )
    graph_id = str(channel_row.get("network_graph_id", "")).strip()
    graph_row = dict(graph_rows_by_id.get(graph_id) or {})
    if not graph_row:
        raise SignalTransportError(
            REFUSAL_SIGNAL_ROUTE_UNAVAILABLE,
            "signal route graph '{}' is unavailable".format(graph_id),
            {"graph_id": graph_id},
        )
    channel_extensions = _as_map(channel_row.get("extensions"))
    policy_id = str(channel_extensions.get("routing_policy_id", "")).strip() or "route.shortest_delay"
    routing_policy_row = dict(routing_policy_rows.get(policy_id) or _default_routing_policy_row())
    if (not str(routing_policy_row.get("policy_id", "")).strip()) or (
        str(routing_policy_row.get("policy_id", "")).strip() != policy_id and policy_id in routing_policy_rows
    ):
        routing_policy_row = dict(_default_routing_policy_row())
    graph_row = _routing_compatible_graph_row(
        graph_row=graph_row,
        default_policy_id=str(routing_policy_row.get("policy_id", "")).strip() or "route.shortest_delay",
    )
    try:
        route_result = query_route_result(
            graph_row=graph_row,
            routing_policy_row=routing_policy_row,
            from_node_id=from_node,
            to_node_id=to_node,
            constraints_row=_as_map(channel_extensions.get("route_constraints")),
            cache_state=_as_map(route_cache_state),
            max_cache_entries=max(1, _as_int(channel_extensions.get("route_cache_max_entries", 512), 512)),
            cost_units_per_query=max(1, _as_int(channel_extensions.get("route_cost_units", 1), 1)),
        )
    except RoutingError as exc:
        raise SignalTransportError(
            REFUSAL_SIGNAL_ROUTE_UNAVAILABLE,
            "signal route unavailable",
            {
                "reason_code": str(getattr(exc, "reason_code", "")),
                "details": dict(getattr(exc, "details", {}) or {}),
                "channel_id": str(channel_row.get("channel_id", "")).strip(),
                "from_node_id": from_node,
                "to_node_id": to_node,
            },
        ) from exc
    route_row = dict(route_result.get("route_result") or {})
    return {
        "route_result": route_result,
        "route_row": route_row,
        "path_edge_ids": [str(item).strip() for item in list(route_row.get("path_edge_ids") or []) if str(item).strip()],
        "path_node_ids": [str(item).strip() for item in list(route_row.get("path_node_ids") or []) if str(item).strip()],
        "cache_state": _as_map(route_result.get("cache_state")),
        "cache_key": str(route_result.get("cache_key", "")).strip() or None,
        "policy_id": str(routing_policy_row.get("policy_id", "")).strip() or "route.shortest_delay",
    }


def _routing_compatible_graph_row(*, graph_row: Mapping[str, object], default_policy_id: str) -> dict:
    row = dict(graph_row or {})
    row["schema_version"] = "1.0.0"
    row["graph_id"] = str(row.get("graph_id", "")).strip()
    row["deterministic_routing_policy_id"] = str(row.get("deterministic_routing_policy_id", "")).strip() or str(default_policy_id or "route.shortest_delay")
    row["validation_mode"] = str(row.get("validation_mode", "")).strip() or "warn"
    row["node_type_schema_id"] = str(row.get("node_type_schema_id", "")).strip() or "dominium.schema.signals.signal_node_payload"
    row["edge_type_schema_id"] = str(row.get("edge_type_schema_id", "")).strip() or "dominium.schema.signals.signal_edge_payload"
    payload_schema_versions = _as_map(row.get("payload_schema_versions"))
    payload_schema_versions.setdefault("dominium.schema.signals.signal_node_payload", "1.0.0")
    payload_schema_versions.setdefault("dominium.schema.signals.signal_edge_payload", "1.0.0")
    row["payload_schema_versions"] = payload_schema_versions
    normalized_nodes: List[dict] = []
    for node in list(row.get("nodes") or []):
        if not isinstance(node, Mapping):
            continue
        node_row = dict(node)
        node_row["schema_version"] = "1.0.0"
        node_row["node_id"] = str(node_row.get("node_id", "")).strip()
        node_row["node_type_id"] = str(node_row.get("node_type_id", "")).strip() or "signal_node"
        node_row["tags"] = _sorted_tokens(node_row.get("tags"))
        if ("payload" not in node_row) and ("payload_ref" not in node_row):
            node_row["payload_ref"] = {"node_kind": "relay"}
        normalized_nodes.append(node_row)
    normalized_edges: List[dict] = []
    for edge in list(row.get("edges") or []):
        if not isinstance(edge, Mapping):
            continue
        edge_row = dict(edge)
        edge_row["schema_version"] = "1.0.0"
        edge_row["edge_id"] = str(edge_row.get("edge_id", "")).strip()
        edge_row["from_node_id"] = str(edge_row.get("from_node_id", "")).strip()
        edge_row["to_node_id"] = str(edge_row.get("to_node_id", "")).strip()
        edge_row["edge_type_id"] = str(edge_row.get("edge_type_id", "")).strip() or "signal_edge"
        edge_row["tags"] = _sorted_tokens(edge_row.get("tags"))
        if ("payload" not in edge_row) and ("payload_ref" not in edge_row):
            edge_row["payload_ref"] = {"edge_kind": "relay_link"}
        normalized_edges.append(edge_row)
    row["nodes"] = list(normalized_nodes)
    row["edges"] = list(normalized_edges)
    return row


def _delivery_state(*, policy_row: Mapping[str, object], queue_row: Mapping[str, object], current_tick: int) -> str:
    policy_id = str(policy_row.get("loss_policy_id", "loss.none")).strip() or "loss.none"
    params = _as_map(policy_row.get("parameters"))
    queue_ext = _as_map(_as_map(queue_row).get("extensions"))
    path_edge_ids = [str(item).strip() for item in list(queue_ext.get("path_edge_ids") or []) if str(item).strip()]
    field_loss_modifier_permille = int(max(0, _as_int(queue_ext.get("field_loss_modifier_permille", 0), 0)))
    if policy_id == "loss.none":
        return "delivered"
    if policy_id == "loss.linear_attenuation":
        base_loss_permille = int(max(0, _as_int(params.get("base_loss_permille", 0), 0)))
        distance_loss_permille = int(max(0, _as_int(params.get("distance_loss_permille", 0), 0)))
        field_visibility_weight_permille = int(max(0, _as_int(params.get("field_visibility_weight_permille", 1000), 1000)))
        distance_component = int(max(0, distance_loss_permille * len(path_edge_ids)))
        weighted_field_component = int(max(0, (field_loss_modifier_permille * field_visibility_weight_permille) // 1000))
        loss_permille = int(min(1000, base_loss_permille + distance_component + weighted_field_component))
        return "lost" if loss_permille >= 1000 else "delivered"
    if policy_id == "loss.deterministic_rng":
        stream_name = str(policy_row.get("rng_stream_name", "rng.signals.loss.default")).strip() or "rng.signals.loss.default"
        base_threshold = int(max(0, min(1000, _as_int(params.get("loss_permille", 50), 50))))
        threshold = int(max(0, min(1000, base_threshold + field_loss_modifier_permille)))
        roll = int(int(canonical_sha256({"stream": stream_name, "envelope_id": str(queue_row.get("envelope_id", "")).strip(), "queue_key": str(queue_row.get("queue_key", "")).strip(), "tick": int(current_tick)})[:8], 16) % 1000)
        return "lost" if roll < threshold else "delivered"
    return "delivered"


def tick_signal_transport(
    *,
    current_tick: int,
    signal_channel_rows: object,
    signal_transport_queue_rows: object,
    envelope_rows: object,
    existing_delivery_event_rows: object,
    network_graph_rows: object,
    loss_policy_registry: Mapping[str, object] | None,
    routing_policy_registry: Mapping[str, object] | None,
    max_cost_units: int,
    cost_units_per_delivery: int,
    route_cache_state: Mapping[str, object] | None = None,
    courier_arrival_rows: object = None,
    field_visibility_by_channel_id: Mapping[str, object] | None = None,
) -> dict:
    del field_visibility_by_channel_id
    tick = int(max(0, _as_int(current_tick, 0)))
    channels = signal_channel_rows_by_id(signal_channel_rows)
    queue_rows = normalize_transport_queue_rows(signal_transport_queue_rows)
    envelope_by_id = dict((str(row.get("envelope_id", "")).strip(), dict(row)) for row in normalize_signal_message_envelope_rows(envelope_rows) if str(row.get("envelope_id", "")).strip())
    event_rows = normalize_message_delivery_event_rows(existing_delivery_event_rows)
    graphs = dict((str(row.get("graph_id", "")).strip(), dict(row)) for row in list(network_graph_rows or []) if isinstance(row, Mapping) and str(row.get("graph_id", "")).strip())
    loss_rows = loss_policy_rows_by_id(loss_policy_registry)
    routing_policy_rows = _routing_policy_rows_by_id(routing_policy_registry)
    normalized_arrivals = normalize_courier_arrival_rows(courier_arrival_rows)
    arrival_queue_keys = dict(
        (str(row.get("queue_key", "")).strip(), True)
        for row in list(normalized_arrivals or [])
        if str(row.get("queue_key", "")).strip()
    )
    arrival_subject_pairs = dict(
        (
            (str(row.get("envelope_id", "")).strip(), str(row.get("recipient_subject_id", "")).strip()),
            True,
        )
        for row in list(normalized_arrivals or [])
        if str(row.get("envelope_id", "")).strip()
    )
    execution = execute_channel_transport_tick(
        tick=int(tick),
        channels_by_id=channels,
        queue_rows=queue_rows,
        envelope_by_id=envelope_by_id,
        event_rows=event_rows,
        graph_rows_by_id=graphs,
        loss_rows_by_id=loss_rows,
        routing_policy_rows=routing_policy_rows,
        max_cost_units=int(max(0, _as_int(max_cost_units, 0))),
        cost_units_per_delivery=int(max(1, _as_int(cost_units_per_delivery, 1))),
        route_cache_state=route_cache_state,
        resolve_route_fn=_resolve_route_query,
        delivery_state_fn=_delivery_state,
        event_id_fn=deterministic_message_delivery_event_id,
        build_event_fn=build_message_delivery_event,
        courier_arrival_queue_keys=arrival_queue_keys,
        courier_arrival_subject_pairs=arrival_subject_pairs,
        courier_commitment_id_fn=deterministic_courier_commitment_id,
    )
    return {
        "signal_transport_queue_rows": normalize_transport_queue_rows(execution.get("signal_transport_queue_rows")),
        "message_delivery_event_rows": normalize_message_delivery_event_rows(execution.get("message_delivery_event_rows")),
        "processed_queue_keys": _sorted_tokens(execution.get("processed_queue_keys")),
        "deferred_queue_keys": _sorted_tokens(execution.get("deferred_queue_keys")),
        "delivered_rows": sorted(
            (dict(row) for row in list(execution.get("delivered_rows") or []) if isinstance(row, Mapping)),
            key=lambda row: (
                str(row.get("envelope_id", "")),
                str(row.get("recipient_subject_id", "")),
                str(row.get("delivery_event_id", "")),
            ),
        ),
        "budget_outcome": str(execution.get("budget_outcome", "complete")).strip() or "complete",
        "cost_units": int(max(0, _as_int(execution.get("cost_units", 0), 0))),
        "route_cache_state": _as_map(execution.get("route_cache_state")),
        "created_courier_commitment_rows": sorted(
            (dict(row) for row in list(execution.get("created_courier_commitment_rows") or []) if isinstance(row, Mapping)),
            key=lambda row: (
                str(row.get("channel_id", "")),
                str(row.get("envelope_id", "")),
                str(row.get("recipient_subject_id", "")),
                str(row.get("commitment_id", "")),
            ),
        ),
    }


__all__ = [
    "REFUSAL_SIGNAL_INVALID",
    "REFUSAL_SIGNAL_ROUTE_UNAVAILABLE",
    "SignalTransportError",
    "build_knowledge_receipt",
    "build_message_delivery_event",
    "build_signal_channel",
    "build_signal_message_envelope",
    "deterministic_courier_commitment_id",
    "deterministic_knowledge_receipt_id",
    "deterministic_message_delivery_event_id",
    "deterministic_signal_message_envelope_id",
    "encryption_policy_rows_by_id",
    "enqueue_signal_envelope",
    "loss_policy_rows_by_id",
    "normalize_knowledge_receipt_rows",
    "normalize_message_delivery_event_rows",
    "normalize_signal_channel_rows",
    "normalize_signal_message_envelope_rows",
    "normalize_courier_arrival_rows",
    "normalize_transport_queue_rows",
    "process_knowledge_acquire",
    "process_signal_send",
    "process_signal_transport_tick",
    "signal_channel_rows_by_id",
    "signal_channel_type_rows_by_id",
    "tick_signal_transport",
]

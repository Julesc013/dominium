"""Deterministic SIG-1 channel capacity/delay executor."""

from __future__ import annotations

from typing import Callable, Dict, List, Mapping, Tuple

from src.fields import build_field_sample


LARGE_CAPACITY_PER_TICK = 1_000_000_000
FIELD_TAG_MODIFIER_PERMILLE = {
    "tag.signal.attenuation.low": 50,
    "tag.signal.attenuation.medium": 150,
    "tag.signal.attenuation.high": 300,
    "tag.signal.occluded": 250,
    "tag.signal.interference": 200,
}


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


def _queue_sort_key(row: Mapping[str, object]) -> Tuple[str, str, str, str]:
    payload = dict(row or {})
    return (
        str(payload.get("channel_id", "")).strip(),
        str(payload.get("envelope_id", "")).strip(),
        str(payload.get("recipient_subject_id", "")),
        str(payload.get("queue_key", "")),
    )


def _edge_index(graph_row: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for edge in sorted((dict(item) for item in list(graph_row.get("edges") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(edge.get("edge_id", "")).strip()
        if edge_id:
            out[edge_id] = edge
    return out


def _edge_capacity_per_tick(edge_row: Mapping[str, object]) -> int:
    candidates = [
        edge_row.get("capacity"),
        edge_row.get("capacity_per_tick"),
        _as_map(edge_row.get("payload")).get("capacity_per_tick"),
        _as_map(edge_row.get("payload_ref")).get("capacity_per_tick"),
        _as_map(edge_row.get("extensions")).get("capacity_per_tick"),
    ]
    for token in candidates:
        if token is None:
            continue
        value = _as_int(token, 0)
        if value <= 0:
            return 0
        return int(value)
    return int(LARGE_CAPACITY_PER_TICK)


def _edge_delay_ticks(edge_row: Mapping[str, object]) -> int:
    candidates = [
        edge_row.get("delay_ticks"),
        _as_map(edge_row.get("payload")).get("delay_ticks"),
        _as_map(edge_row.get("payload_ref")).get("delay_ticks"),
        _as_map(edge_row.get("extensions")).get("delay_ticks"),
    ]
    for token in candidates:
        if token is None:
            continue
        value = max(0, _as_int(token, 0))
        return int(value)
    return 0


def _path_delay_ticks(*, graph_row: Mapping[str, object], path_edge_ids: List[str]) -> int:
    edge_index = _edge_index(graph_row)
    total = 0
    for edge_id in list(path_edge_ids or []):
        total += _edge_delay_ticks(dict(edge_index.get(str(edge_id).strip()) or {}))
    return int(max(0, total))


def _field_loss_modifier_permille(*, graph_row: Mapping[str, object], path_edge_ids: List[str]) -> int:
    edge_index = _edge_index(graph_row)
    modifier = 0
    for edge_id in list(path_edge_ids or []):
        edge_row = dict(edge_index.get(str(edge_id).strip()) or {})
        tags = _sorted_tokens(edge_row.get("tags"))
        payload_tags = _sorted_tokens(_as_map(edge_row.get("payload")).get("tags"))
        payload_ref_tags = _sorted_tokens(_as_map(edge_row.get("payload_ref")).get("tags"))
        all_tags = sorted(set(tags + payload_tags + payload_ref_tags))
        for tag in all_tags:
            modifier += int(max(0, _as_int(FIELD_TAG_MODIFIER_PERMILLE.get(str(tag), 0), 0)))
    return int(min(900, max(0, modifier)))


def _clamp_permille(value: object, default_value: int = 0) -> int:
    return int(max(0, min(1000, _as_int(value, default_value))))


def _sample_value_permille(sample_row: Mapping[str, object], keys: List[str]) -> int:
    for key in keys:
        if key in sample_row:
            return _clamp_permille(sample_row.get(key), 0)
    fields = _as_map(sample_row.get("fields"))
    for key in keys:
        if key in fields:
            return _clamp_permille(fields.get(key), 0)
    return 0


def _field_sample_cache_key(*, field_id: str, spatial_node_id: str, tick: int) -> str:
    return "{}::{}::{}".format(
        str(field_id).strip(),
        str(spatial_node_id).strip(),
        int(max(0, _as_int(tick, 0))),
    )


def _field_sample_keys(field_id: str) -> List[str]:
    token = str(field_id).strip()
    if token == "field.visibility":
        return ["field.visibility", "visibility_permille", "visibility"]
    if token == "field.radiation":
        return ["field.radiation", "radiation_permille", "radiation"]
    if token == "field.wind":
        return ["field.wind", "wind_permille", "wind"]
    return [token]


def _sample_field_permille(
    *,
    tick: int,
    node_id: str,
    field_id: str,
    row: Mapping[str, object],
    field_sample_cache: Dict[str, dict],
) -> int:
    cache_key = _field_sample_cache_key(
        field_id=str(field_id).strip(),
        spatial_node_id=str(node_id).strip(),
        tick=int(tick),
    )
    cached = _as_map(field_sample_cache.get(cache_key))
    if (
        str(cached.get("field_id", "")).strip() == str(field_id).strip()
        and str(cached.get("spatial_node_id", "")).strip() == str(node_id).strip()
    ):
        return _clamp_permille(cached.get("sampled_value", 0), 0)
    sampled = _sample_value_permille(row, _field_sample_keys(field_id))
    field_sample_cache[cache_key] = build_field_sample(
        field_id=str(field_id).strip(),
        spatial_node_id=str(node_id).strip(),
        tick=int(max(0, _as_int(tick, 0))),
        sampled_value=int(sampled),
        has_cell=True,
        sampled_cell_id=str(node_id).strip(),
        extensions={"source": "signals.transport.channel_executor"},
    )
    return int(sampled)


def _node_field_modifiers(
    *,
    tick: int,
    path_node_ids: List[str],
    field_samples_by_node_id: Mapping[str, object] | None,
    field_sample_cache: Dict[str, dict],
) -> dict:
    samples = dict(field_samples_by_node_id or {})
    visibility = 0
    radiation = 0
    wind = 0
    for node_id in [str(item).strip() for item in list(path_node_ids or []) if str(item).strip()]:
        raw = samples.get(node_id)
        row = _as_map(raw)
        # Allow direct scalar shorthand for visibility-only samples.
        if not row and raw is not None:
            row = {"field.visibility": _clamp_permille(raw, 0)}
        visibility = max(
            int(visibility),
            _sample_field_permille(
                tick=int(tick),
                node_id=node_id,
                field_id="field.visibility",
                row=row,
                field_sample_cache=field_sample_cache,
            ),
        )
        radiation = max(
            int(radiation),
            _sample_field_permille(
                tick=int(tick),
                node_id=node_id,
                field_id="field.radiation",
                row=row,
                field_sample_cache=field_sample_cache,
            ),
        )
        wind = max(
            int(wind),
            _sample_field_permille(
                tick=int(tick),
                node_id=node_id,
                field_id="field.wind",
                row=row,
                field_sample_cache=field_sample_cache,
            ),
        )
    return {
        "field_visibility_modifier_permille": int(visibility),
        "field_radiation_modifier_permille": int(radiation),
        "field_wind_modifier_permille": int(wind),
    }


def _path_has_capacity(
    *,
    graph_id: str,
    graph_row: Mapping[str, object],
    path_edge_ids: List[str],
    edge_usage: Mapping[Tuple[str, str], int],
) -> bool:
    edge_index = _edge_index(graph_row)
    for edge_id in list(path_edge_ids or []):
        edge_token = str(edge_id).strip()
        if not edge_token:
            continue
        edge_row = dict(edge_index.get(edge_token) or {})
        cap = _edge_capacity_per_tick(edge_row)
        used = int(max(0, _as_int(dict(edge_usage).get((str(graph_id), edge_token), 0), 0)))
        if used >= cap:
            return False
    return True


def _consume_path_capacity(
    *,
    graph_id: str,
    path_edge_ids: List[str],
    edge_usage: Dict[Tuple[str, str], int],
) -> None:
    for edge_id in list(path_edge_ids or []):
        edge_token = str(edge_id).strip()
        if not edge_token:
            continue
        key = (str(graph_id), edge_token)
        edge_usage[key] = int(max(0, _as_int(edge_usage.get(key, 0), 0)) + 1)


def execute_channel_transport_tick(
    *,
    tick: int,
    channels_by_id: Mapping[str, dict],
    queue_rows: List[dict],
    envelope_by_id: Mapping[str, dict],
    event_rows: List[dict],
    graph_rows_by_id: Mapping[str, dict],
    loss_rows_by_id: Mapping[str, dict],
    routing_policy_rows: Mapping[str, dict],
    max_cost_units: int,
    cost_units_per_delivery: int,
    route_cache_state: Mapping[str, object] | None,
    resolve_route_fn: Callable[..., dict],
    delivery_state_fn: Callable[..., str],
    event_id_fn: Callable[..., str],
    build_event_fn: Callable[..., dict],
    field_samples_by_node_id: Mapping[str, object] | None = None,
    field_sample_cache_state: Mapping[str, object] | None = None,
    channel_jamming_rows_by_id: Mapping[str, dict] | None = None,
    courier_arrival_queue_keys: Mapping[str, bool] | None = None,
    courier_arrival_subject_pairs: Mapping[Tuple[str, str], bool] | None = None,
    courier_commitment_id_fn: Callable[..., str] | None = None,
) -> dict:
    cost_unit = int(max(1, _as_int(cost_units_per_delivery, 1)))
    max_attempts = int(max(0, _as_int(max_cost_units, 0)) // cost_unit)
    attempts = 0

    channel_attempts: Dict[str, int] = {}
    edge_usage: Dict[Tuple[str, str], int] = {}
    pending_rows: List[dict] = []
    processed_keys: List[str] = []
    deferred_keys: List[str] = []
    delivered_rows: List[dict] = []
    created_courier_commitments_by_id: Dict[str, dict] = {}
    next_event_rows = [dict(row) for row in list(event_rows or []) if isinstance(row, Mapping)]
    event_sequence = int(len(next_event_rows))
    next_route_cache_state = _as_map(route_cache_state)
    next_field_sample_cache_state = {}
    for raw_key, raw_value in dict(field_sample_cache_state or {}).items():
        key_token = str(raw_key).strip()
        if key_token:
            next_field_sample_cache_state[key_token] = _as_map(raw_value)
    arrival_queue_keys = dict((str(key).strip(), bool(value)) for key, value in dict(courier_arrival_queue_keys or {}).items() if str(key).strip())
    arrival_subject_pairs = dict(((str(key[0]).strip(), str(key[1]).strip()), bool(value)) for key, value in dict(courier_arrival_subject_pairs or {}).items() if isinstance(key, tuple) and len(key) == 2 and str(key[0]).strip())

    grouped: Dict[str, List[dict]] = {}
    for queue_row in sorted((dict(row) for row in list(queue_rows or []) if isinstance(row, Mapping)), key=_queue_sort_key):
        channel_id = str(queue_row.get("channel_id", "")).strip()
        grouped.setdefault(channel_id, []).append(queue_row)

    for channel_id in sorted(grouped.keys()):
        channel_row = dict(channels_by_id.get(channel_id) or {})
        channel_cap = int(max(0, _as_int(channel_row.get("capacity_per_tick", 1), 1)))
        for queue_row in sorted(grouped.get(channel_id) or [], key=_queue_sort_key):
            queue_key = str(queue_row.get("queue_key", "")).strip()
            envelope_id = str(queue_row.get("envelope_id", "")).strip()
            envelope_row = dict(envelope_by_id.get(envelope_id) or {})
            if (not channel_row) or (not envelope_row):
                deferred_keys.append(queue_key)
                pending_rows.append(dict(queue_row))
                continue
            remaining_delay = int(max(0, _as_int(queue_row.get("remaining_delay_ticks", 0), 0)))
            if remaining_delay > 0:
                next_row = dict(queue_row)
                next_row["remaining_delay_ticks"] = int(max(0, remaining_delay - 1))
                pending_rows.append(next_row)
                continue

            used_on_channel = int(channel_attempts.get(channel_id, 0))
            if used_on_channel >= channel_cap or attempts >= max_attempts:
                deferred_keys.append(queue_key)
                pending_rows.append(dict(queue_row))
                continue

            queue_ext = _as_map(queue_row.get("extensions"))
            courier_commitment_id = None
            is_courier_channel = str(channel_row.get("channel_type_id", "")).strip() == "channel.courier_route"
            if is_courier_channel:
                courier_commitment_id = str(queue_ext.get("courier_commitment_id", "")).strip() or None
                if courier_commitment_id is None and callable(courier_commitment_id_fn):
                    courier_commitment_id = str(
                        courier_commitment_id_fn(
                            channel_id=channel_id,
                            envelope_id=envelope_id,
                            recipient_subject_id=str(queue_row.get("recipient_subject_id", "")).strip() or None,
                            queue_key=queue_key,
                        )
                    ).strip() or None
                if courier_commitment_id:
                    created_courier_commitments_by_id[courier_commitment_id] = {
                        "commitment_id": courier_commitment_id,
                        "channel_id": channel_id,
                        "envelope_id": envelope_id,
                        "artifact_id": str(envelope_row.get("artifact_id", "")).strip(),
                        "recipient_subject_id": queue_row.get("recipient_subject_id"),
                        "queue_key": queue_key,
                        "created_tick": int(tick),
                        "status": "in_transit",
                    }
                    next_row = dict(queue_row)
                    next_ext = _as_map(next_row.get("extensions"))
                    next_ext["courier_commitment_id"] = courier_commitment_id
                    next_row["extensions"] = next_ext
                    queue_row = next_row
                    queue_ext = next_ext
                recipient_subject_id = str(queue_row.get("recipient_subject_id", "")).strip()
                arrived = bool(arrival_queue_keys.get(queue_key, False)) or bool(arrival_subject_pairs.get((envelope_id, recipient_subject_id), False))
                if not arrived:
                    pending_rows.append(dict(queue_row))
                    continue

            route_initialized = bool(queue_ext.get("route_initialized", False))
            route_details = {
                "route_policy_id": str(queue_ext.get("route_policy_id", "")).strip() or str(_as_map(channel_row.get("extensions")).get("routing_policy_id", "")).strip() or "route.shortest_delay",
                "route_cache_key": queue_ext.get("route_cache_key"),
                "path_edge_ids": [str(item).strip() for item in list(queue_ext.get("path_edge_ids") or []) if str(item).strip()],
                "path_node_ids": [str(item).strip() for item in list(queue_ext.get("path_node_ids") or []) if str(item).strip()],
                "route_unavailable": False,
            }
            if not route_initialized and (not is_courier_channel):
                try:
                    resolved = resolve_route_fn(
                        channel_row=channel_row,
                        queue_row=queue_row,
                        graph_rows_by_id=graph_rows_by_id,
                        routing_policy_rows=routing_policy_rows,
                        route_cache_state=next_route_cache_state,
                    )
                    next_route_cache_state = _as_map(resolved.get("cache_state"))
                    route_details["route_policy_id"] = str(resolved.get("policy_id", "")).strip() or route_details["route_policy_id"]
                    route_details["route_cache_key"] = resolved.get("cache_key")
                    route_details["path_edge_ids"] = [str(item).strip() for item in list(resolved.get("path_edge_ids") or []) if str(item).strip()]
                    route_details["path_node_ids"] = [str(item).strip() for item in list(resolved.get("path_node_ids") or []) if str(item).strip()]
                except Exception:
                    route_details["route_unavailable"] = True
                next_row = dict(queue_row)
                next_ext = _as_map(next_row.get("extensions"))
                next_ext["route_initialized"] = True
                next_ext["route_policy_id"] = route_details.get("route_policy_id")
                next_ext["route_cache_key"] = route_details.get("route_cache_key")
                next_ext["path_edge_ids"] = list(route_details.get("path_edge_ids") or [])
                next_ext["path_node_ids"] = list(route_details.get("path_node_ids") or [])
                next_row["extensions"] = next_ext
                graph_id = str(channel_row.get("network_graph_id", "")).strip()
                graph_row = dict(graph_rows_by_id.get(graph_id) or {})
                path_delay_ticks = int(_path_delay_ticks(graph_row=graph_row, path_edge_ids=list(route_details.get("path_edge_ids") or [])))
                next_ext["path_delay_ticks"] = int(path_delay_ticks)
                if path_delay_ticks > 0:
                    next_row["remaining_delay_ticks"] = int(max(0, path_delay_ticks - 1))
                    pending_rows.append(next_row)
                    continue
                queue_row = next_row
                queue_ext = next_ext

            graph_id = str(channel_row.get("network_graph_id", "")).strip()
            graph_row = dict(graph_rows_by_id.get(graph_id) or {})
            field_loss_modifier_permille = 0
            quality_channel_types = {"channel.wired_basic", "channel.radio_basic", "channel.optical_line_of_sight"}
            if str(channel_row.get("channel_type_id", "")).strip() in quality_channel_types:
                path_edge_ids = list(route_details.get("path_edge_ids") or [])
                path_node_ids = list(route_details.get("path_node_ids") or [])
                tag_loss_modifier_permille = _field_loss_modifier_permille(
                    graph_row=graph_row,
                    path_edge_ids=path_edge_ids,
                )
                node_field_modifiers = _node_field_modifiers(
                    tick=tick,
                    path_node_ids=path_node_ids,
                    field_samples_by_node_id=field_samples_by_node_id,
                    field_sample_cache=next_field_sample_cache_state,
                )
                field_visibility_modifier_permille = int(node_field_modifiers.get("field_visibility_modifier_permille", 0))
                field_radiation_modifier_permille = int(node_field_modifiers.get("field_radiation_modifier_permille", 0))
                field_wind_modifier_permille = int(node_field_modifiers.get("field_wind_modifier_permille", 0))
                field_loss_modifier_permille = int(
                    min(
                        1000,
                        max(
                            0,
                            tag_loss_modifier_permille
                            + (field_visibility_modifier_permille // 2)
                            + (field_radiation_modifier_permille // 4)
                            + (field_wind_modifier_permille // 8),
                        ),
                    )
                )
                queue_ext = _as_map(queue_row.get("extensions"))
                queue_ext["tag_loss_modifier_permille"] = int(tag_loss_modifier_permille)
                queue_ext["field_visibility_modifier_permille"] = int(field_visibility_modifier_permille)
                queue_ext["field_radiation_modifier_permille"] = int(field_radiation_modifier_permille)
                queue_ext["field_wind_modifier_permille"] = int(field_wind_modifier_permille)
                queue_ext["field_loss_modifier_permille"] = int(field_loss_modifier_permille)
                queue_row = dict(queue_row)
                queue_row["extensions"] = queue_ext
            jamming_modifier_permille = 0
            jamming_row = dict((dict(channel_jamming_rows_by_id or {})).get(channel_id) or {})
            if jamming_row:
                start_tick = int(max(0, _as_int(jamming_row.get("start_tick", 0), 0)))
                duration_ticks = int(max(0, _as_int(jamming_row.get("duration_ticks", 0), 0)))
                end_tick = int(max(start_tick, _as_int(jamming_row.get("end_tick", start_tick + duration_ticks), start_tick + duration_ticks)))
                is_active = int(tick) >= int(start_tick) and int(tick) < int(end_tick)
                if is_active:
                    jamming_modifier_permille = int(max(0, _as_int(jamming_row.get("strength_modifier", 0), 0)))
            queue_ext = _as_map(queue_row.get("extensions"))
            queue_ext["jamming_modifier_permille"] = int(min(1000, max(0, jamming_modifier_permille)))
            queue_row = dict(queue_row)
            queue_row["extensions"] = queue_ext
            if (not bool(route_details.get("route_unavailable", False))) and route_details.get("path_edge_ids"):
                if not _path_has_capacity(
                    graph_id=graph_id,
                    graph_row=graph_row,
                    path_edge_ids=list(route_details.get("path_edge_ids") or []),
                    edge_usage=edge_usage,
                ):
                    deferred_keys.append(queue_key)
                    pending_rows.append(dict(queue_row))
                    continue

            loss_policy_id = str(channel_row.get("loss_policy_id", "loss.none")).strip() or "loss.none"
            loss_row = dict(loss_rows_by_id.get(loss_policy_id) or {"loss_policy_id": loss_policy_id, "parameters": {}, "rng_stream_name": None})
            state = str(
                delivery_state_fn(
                    policy_row=loss_row,
                    channel_row=channel_row,
                    queue_row=queue_row,
                    current_tick=tick,
                )
            ).strip() or "lost"
            if bool(route_details.get("route_unavailable", False)):
                state = "lost"

            if (not bool(route_details.get("route_unavailable", False))) and route_details.get("path_edge_ids"):
                _consume_path_capacity(
                    graph_id=graph_id,
                    path_edge_ids=list(route_details.get("path_edge_ids") or []),
                    edge_usage=edge_usage,
                )

            event_id = str(
                event_id_fn(
                    envelope_id=envelope_id,
                    from_node_id=str(queue_row.get("from_node_id", "")).strip(),
                    to_node_id=str(queue_row.get("to_node_id", "")).strip(),
                    delivered_tick=tick,
                    delivery_state=state,
                    sequence=event_sequence,
                )
            ).strip()
            event_sequence += 1
            next_event_rows.append(
                build_event_fn(
                    event_id=event_id,
                    envelope_id=envelope_id,
                    from_node_id=str(queue_row.get("from_node_id", "")).strip(),
                    to_node_id=str(queue_row.get("to_node_id", "")).strip(),
                    delivered_tick=tick,
                    delivery_state=state,
                    extensions={
                        "channel_id": channel_id,
                        "loss_policy_id": loss_policy_id,
                        "recipient_subject_id": queue_row.get("recipient_subject_id"),
                        "route_policy_id": route_details.get("route_policy_id"),
                        "route_cache_key": route_details.get("route_cache_key"),
                        "path_edge_ids": list(route_details.get("path_edge_ids") or []),
                        "path_node_ids": list(route_details.get("path_node_ids") or []),
                        "courier_commitment_id": courier_commitment_id,
                        "field_loss_modifier_permille": int(field_loss_modifier_permille),
                        "tag_loss_modifier_permille": int(_as_int(queue_ext.get("tag_loss_modifier_permille", 0), 0)),
                        "field_visibility_modifier_permille": int(_as_int(queue_ext.get("field_visibility_modifier_permille", 0), 0)),
                        "field_radiation_modifier_permille": int(_as_int(queue_ext.get("field_radiation_modifier_permille", 0), 0)),
                        "field_wind_modifier_permille": int(_as_int(queue_ext.get("field_wind_modifier_permille", 0), 0)),
                        "jamming_modifier_permille": int(_as_int(queue_ext.get("jamming_modifier_permille", 0), 0)),
                        "corrupted_view": bool(state == "corrupted"),
                    },
                )
            )
            attempts += 1
            channel_attempts[channel_id] = used_on_channel + 1
            processed_keys.append(queue_key)
            if state == "delivered":
                delivered_rows.append(
                    {
                        "envelope_id": envelope_id,
                        "artifact_id": str(envelope_row.get("artifact_id", "")).strip(),
                        "sender_subject_id": str(envelope_row.get("sender_subject_id", "")).strip() or None,
                        "recipient_subject_id": queue_row.get("recipient_subject_id"),
                        "delivery_event_id": event_id,
                        "channel_id": channel_id,
                        "envelope_extensions": _as_map(envelope_row.get("extensions")),
                    }
                )

    return {
        "signal_transport_queue_rows": sorted(
            (dict(row) for row in pending_rows if isinstance(row, Mapping)),
            key=_queue_sort_key,
        ),
        "message_delivery_event_rows": list(next_event_rows),
        "processed_queue_keys": _sorted_tokens(processed_keys),
        "deferred_queue_keys": _sorted_tokens(deferred_keys),
        "delivered_rows": sorted(
            (dict(row) for row in delivered_rows if isinstance(row, Mapping)),
            key=lambda row: (
                str(row.get("envelope_id", "")),
                str(row.get("recipient_subject_id", "")),
                str(row.get("delivery_event_id", "")),
            ),
        ),
        "budget_outcome": "degraded" if deferred_keys else "complete",
        "cost_units": int(max(0, attempts * cost_unit)),
        "route_cache_state": dict(next_route_cache_state),
        "field_sample_cache_state": dict(next_field_sample_cache_state),
        "created_courier_commitment_rows": sorted(
            (dict(row) for row in created_courier_commitments_by_id.values()),
            key=lambda row: (
                str(row.get("channel_id", "")),
                str(row.get("envelope_id", "")),
                str(row.get("recipient_subject_id", "")),
                str(row.get("commitment_id", "")),
            ),
        ),
    }

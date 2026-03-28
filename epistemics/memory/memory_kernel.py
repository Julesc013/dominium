"""Deterministic epistemic memory retention/decay/eviction kernel."""

from __future__ import annotations

import copy
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


SOURCE_TICK_BUCKET_SIZE = 32
SUBJECT_KINDS = {"entity", "region", "event", "signal", "custom"}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _string_or_none(value: object) -> str | None:
    token = str(value).strip()
    return token if token else None


def _subject_kind_token(value: object) -> str:
    token = str(value).strip()
    if token in SUBJECT_KINDS:
        return token
    return "custom"


def _default_precision_tag(channel_id: str) -> str:
    token = str(channel_id).strip()
    if token.startswith("ch.truth.overlay"):
        return "coarse"
    if token in (
        "ch.camera.state",
        "ch.core.navigation",
        "ch.nondiegetic.nav",
        "ch.diegetic.map_local",
        "ch.core.entities",
        "ch.nondiegetic.entity_inspector",
    ):
        return "medium"
    return "fine"


def _sort_items(items: List[dict]) -> List[dict]:
    return sorted(
        (dict(row) for row in (items or []) if isinstance(row, dict)),
        key=lambda row: (
            str(row.get("channel_id", "")),
            str(row.get("subject_kind", "")),
            str(row.get("subject_id", "") if row.get("subject_id") is not None else ""),
            _as_int(row.get("source_tick", 0), 0),
            str(row.get("memory_item_id", "")),
        ),
    )


def _memory_item_id(
    owner_subject_id: str,
    channel_id: str,
    subject_kind: str,
    subject_id: str | None,
    source_tick: int,
) -> str:
    source_tick_bucket = int(max(0, int(source_tick)) // SOURCE_TICK_BUCKET_SIZE)
    token = canonical_sha256(
        {
            "owner_subject_id": str(owner_subject_id),
            "channel_id": str(channel_id),
            "subject_kind": str(subject_kind),
            "subject_id": str(subject_id) if subject_id is not None else None,
            "source_tick_bucket": int(source_tick_bucket),
        }
    )
    return "mem.item.{}".format(token[:16])


def _store_id(owner_subject_id: str) -> str:
    token = str(owner_subject_id or "unknown")
    safe = token.replace("\\", ".").replace("/", ".").replace(" ", "_")
    return "memory.store.{}".format(safe)


def _channel_payload(perceived_now: dict, channel_id: str) -> dict:
    if channel_id == "ch.core.time":
        return {
            "time": dict(perceived_now.get("time") or {}),
            "time_state": dict(perceived_now.get("time_state") or {}),
        }
    if channel_id == "ch.camera.state":
        return {"camera_viewpoint": dict(perceived_now.get("camera_viewpoint") or {})}
    if channel_id in ("ch.core.navigation", "ch.nondiegetic.nav"):
        return {"navigation": dict(perceived_now.get("navigation") or {})}
    if channel_id == "ch.core.sites":
        return {"sites": dict(perceived_now.get("sites") or {})}
    if channel_id in ("ch.core.entities", "ch.nondiegetic.entity_inspector"):
        return {
            "entities": dict(perceived_now.get("entities") or {}),
            "observed_entities": list(perceived_now.get("observed_entities") or []),
            "control": dict(perceived_now.get("control") or {}),
        }
    if channel_id == "ch.core.process_log":
        return {"process_log": dict(perceived_now.get("process_log") or {})}
    if channel_id in ("ch.core.performance", "ch.nondiegetic.performance_monitor"):
        return {"performance": dict(perceived_now.get("performance") or {})}
    if channel_id == "ch.watermark.observer_mode":
        return {"watermark": dict(perceived_now.get("watermark") or {})}
    instruments = dict(perceived_now.get("diegetic_instruments") or {})
    if channel_id == "ch.diegetic.compass":
        return {"instrument.compass": dict(instruments.get("instrument.compass") or {})}
    if channel_id == "ch.diegetic.clock":
        return {"instrument.clock": dict(instruments.get("instrument.clock") or {})}
    if channel_id == "ch.diegetic.altimeter":
        return {"instrument.altimeter": dict(instruments.get("instrument.altimeter") or {})}
    if channel_id == "ch.diegetic.map_local":
        return {"instrument.map_local": dict(instruments.get("instrument.map_local") or {})}
    if channel_id == "ch.diegetic.notebook":
        return {"instrument.notebook": dict(instruments.get("instrument.notebook") or {})}
    if channel_id == "ch.diegetic.radio_text":
        return {"instrument.radio_text": dict(instruments.get("instrument.radio_text") or {})}
    truth_overlay = dict(perceived_now.get("truth_overlay") or {})
    if channel_id == "ch.truth.overlay.terrain_height":
        return {"terrain_height_mm": truth_overlay.get("terrain_height_mm")}
    if channel_id == "ch.truth.overlay.anchor_hash":
        return {"state_hash_anchor": truth_overlay.get("state_hash_anchor")}
    return {}


def _event_subject_id(event_row: dict) -> str:
    event_id = str(event_row.get("event_id", "")).strip()
    if event_id:
        return event_id
    return "event.{}".format(canonical_sha256(event_row)[:16])


def _extract_candidates(perceived_now: dict, tick: int) -> List[dict]:
    rows: List[dict] = []
    channel_ids = sorted(set(str(item).strip() for item in (perceived_now.get("channels") or []) if str(item).strip()))
    for channel_id in channel_ids:
        payload = _channel_payload(perceived_now=perceived_now, channel_id=channel_id)
        if channel_id in ("ch.core.entities", "ch.nondiegetic.entity_inspector"):
            entity_rows = sorted(
                (dict(item) for item in (((payload.get("entities") or {}).get("entries")) or []) if isinstance(item, dict)),
                key=lambda row: str(row.get("entity_id", "")),
            )
            if not entity_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "entity",
                        "subject_id": None,
                        "payload": payload,
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
                continue
            for entity_row in entity_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "entity",
                        "subject_id": _string_or_none(entity_row.get("entity_id")),
                        "payload": {"entity": entity_row},
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
            continue

        if channel_id in ("ch.core.navigation", "ch.nondiegetic.nav"):
            hierarchy_rows = sorted(
                (dict(item) for item in (((payload.get("navigation") or {}).get("hierarchy")) or []) if isinstance(item, dict)),
                key=lambda row: (
                    str(row.get("kind", "")),
                    str(row.get("object_id", "")),
                    str(row.get("parent_id", "")),
                ),
            )
            if not hierarchy_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "region",
                        "subject_id": None,
                        "payload": payload,
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
                continue
            for nav_row in hierarchy_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "region",
                        "subject_id": _string_or_none(nav_row.get("object_id")),
                        "payload": {"navigation_row": nav_row},
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
            continue

        if channel_id == "ch.diegetic.map_local":
            map_rows = sorted(
                (
                    dict(item)
                    for item in (((payload.get("instrument.map_local") or {}).get("reading") or {}).get("entries") or [])
                    if isinstance(item, dict)
                ),
                key=lambda row: (
                    str(row.get("region_key", "")),
                    _as_int(row.get("last_seen_tick", 0), 0),
                ),
            )
            if not map_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "region",
                        "subject_id": None,
                        "payload": payload,
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
                continue
            for map_row in map_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "region",
                        "subject_id": _string_or_none(map_row.get("region_key")),
                        "payload": {"map_row": map_row},
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
            continue

        if channel_id == "ch.diegetic.notebook":
            notebook_rows = sorted(
                (
                    dict(item)
                    for item in (((payload.get("instrument.notebook") or {}).get("reading") or {}).get("entries") or [])
                    if isinstance(item, dict)
                ),
                key=lambda row: (
                    _as_int(row.get("created_tick", 0), 0),
                    str(row.get("entry_id", "")),
                ),
            )
            if not notebook_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "event",
                        "subject_id": None,
                        "payload": payload,
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
                continue
            for notebook_row in notebook_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "event",
                        "subject_id": _string_or_none(notebook_row.get("entry_id")),
                        "payload": {"notebook_entry": notebook_row},
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
            continue

        if channel_id == "ch.diegetic.radio_text":
            message_rows = sorted(
                (
                    dict(item)
                    for item in (((payload.get("instrument.radio_text") or {}).get("reading") or {}).get("messages") or [])
                    if isinstance(item, dict)
                ),
                key=lambda row: (
                    _as_int(row.get("created_tick", 0), 0),
                    str(row.get("message_id", "")),
                ),
            )
            if not message_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "signal",
                        "subject_id": None,
                        "payload": payload,
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
                continue
            for message_row in message_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "signal",
                        "subject_id": _string_or_none(message_row.get("message_id")),
                        "payload": {"radio_message": message_row},
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
            continue

        if channel_id == "ch.core.process_log":
            event_rows = sorted(
                (dict(item) for item in (((payload.get("process_log") or {}).get("entries")) or []) if isinstance(item, dict)),
                key=lambda row: (
                    _as_int(row.get("tick", 0), 0),
                    str(row.get("process_id", "")),
                    str(row.get("outcome", "")),
                ),
            )
            if not event_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "event",
                        "subject_id": None,
                        "payload": payload,
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
                continue
            for event_row in event_rows:
                rows.append(
                    {
                        "channel_id": channel_id,
                        "subject_kind": "event",
                        "subject_id": _event_subject_id(event_row),
                        "payload": {"event": event_row},
                        "precision_tag": _default_precision_tag(channel_id),
                        "source_tick": int(tick),
                    }
                )
            continue

        rows.append(
            {
                "channel_id": channel_id,
                "subject_kind": "signal",
                "subject_id": _string_or_none(channel_id),
                "payload": payload,
                "precision_tag": _default_precision_tag(channel_id),
                "source_tick": int(tick),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("channel_id", "")),
            str(row.get("subject_kind", "")),
            str(row.get("subject_id", "") if row.get("subject_id") is not None else ""),
            canonical_sha256(dict(row.get("payload") or {})),
        ),
    )


def _select_rule(rule_rows: List[dict], channel_id: str, subject_kind: str) -> dict:
    matches: List[Tuple[int, int, int, str, dict]] = []
    for row in (rule_rows or []):
        if not isinstance(row, dict):
            continue
        row_channel = str(row.get("channel_id", "*")).strip() or "*"
        row_kind = str(row.get("subject_kind", "*")).strip() or "*"
        if row_channel not in (str(channel_id), "*"):
            continue
        if row_kind not in (str(subject_kind), "*"):
            continue
        channel_exact = 1 if row_channel == str(channel_id) else 0
        kind_exact = 1 if row_kind == str(subject_kind) else 0
        score = channel_exact + kind_exact
        matches.append(
            (
                -int(score),
                -int(channel_exact),
                -int(kind_exact),
                str(row.get("rule_id", "")),
                dict(row),
            )
        )
    if not matches:
        return {}
    matches.sort(key=lambda row: (row[0], row[1], row[2], row[3]))
    return dict(matches[0][4])


def _ttl_for(decay_model: dict, channel_id: str, subject_kind: str) -> int | None:
    rule = _select_rule(list(decay_model.get("ttl_rules") or []), channel_id=channel_id, subject_kind=subject_kind)
    if not rule:
        return None
    ttl_value = rule.get("ttl_ticks")
    if ttl_value is None:
        return None
    return max(0, _as_int(ttl_value, 0))


def _refresh_on_observed(decay_model: dict, channel_id: str, subject_kind: str) -> bool:
    rule = _select_rule(list(decay_model.get("refresh_rules") or []), channel_id=channel_id, subject_kind=subject_kind)
    if not rule:
        return True
    return bool(rule.get("refresh_on_observed", True))


def _coerce_existing_items(previous_store: dict) -> List[dict]:
    items = previous_store.get("items")
    if isinstance(items, list):
        out = []
        for row in items:
            if not isinstance(row, dict):
                continue
            out.append(
                {
                    "memory_item_id": str(row.get("memory_item_id", "")),
                    "owner_subject_id": str(row.get("owner_subject_id", "")),
                    "source_tick": _as_int(row.get("source_tick", 0), 0),
                    "last_refresh_tick": _as_int(row.get("last_refresh_tick", 0), 0),
                    "channel_id": str(row.get("channel_id", "")),
                    "subject_kind": _subject_kind_token(row.get("subject_kind", "custom")),
                    "subject_id": _string_or_none(row.get("subject_id")),
                    "payload": copy.deepcopy(dict(row.get("payload") or {})),
                    "precision_tag": str(row.get("precision_tag", "coarse")) or "coarse",
                    "ttl_ticks": row.get("ttl_ticks") if row.get("ttl_ticks") is None else max(0, _as_int(row.get("ttl_ticks", 0), 0)),
                    "extensions": copy.deepcopy(dict(row.get("extensions") or {})),
                }
            )
        return out

    # Backward-compatibility for legacy entries-only memory state.
    entries = previous_store.get("entries")
    if not isinstance(entries, list):
        return []
    converted = []
    for row in sorted((dict(item) for item in entries if isinstance(item, dict)), key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("channel_id", "")))):
        tick = _as_int(row.get("tick", 0), 0)
        channel_id = str(row.get("channel_id", "")).strip()
        payload_hash = str(row.get("payload_hash", "")).strip()
        if not channel_id:
            continue
        converted.append(
            {
                "memory_item_id": _memory_item_id(
                    owner_subject_id=str(previous_store.get("owner_subject_id", "")),
                    channel_id=channel_id,
                    subject_kind="signal",
                    subject_id=channel_id,
                    source_tick=tick,
                ),
                "owner_subject_id": str(previous_store.get("owner_subject_id", "")),
                "source_tick": int(tick),
                "last_refresh_tick": int(tick),
                "channel_id": channel_id,
                "subject_kind": "signal",
                "subject_id": channel_id,
                "payload": {"legacy_payload_hash": payload_hash},
                "precision_tag": _default_precision_tag(channel_id),
                "ttl_ticks": None,
                "extensions": {"legacy_entry_conversion": True},
            }
        )
    return converted


def _decay_items(items: List[dict], tick_delta: int) -> List[dict]:
    delta = max(0, _as_int(tick_delta, 0))
    if delta == 0:
        return [dict(row) for row in items]
    out = []
    for row in items:
        ttl = row.get("ttl_ticks")
        if ttl is None:
            out.append(dict(row))
            continue
        remaining = max(0, _as_int(ttl, 0) - delta)
        if remaining <= 0:
            continue
        next_row = dict(row)
        next_row["ttl_ticks"] = int(remaining)
        out.append(next_row)
    return out


def _eviction_rank(row: dict, eviction_rule: dict) -> Tuple[int, int, str]:
    algorithm = str(eviction_rule.get("algorithm_id", "evict.oldest_first")).strip() or "evict.oldest_first"
    source_tick = _as_int(row.get("source_tick", 0), 0)
    item_id = str(row.get("memory_item_id", ""))
    if algorithm == "evict.lowest_priority":
        by_channel = dict(eviction_rule.get("priority_by_channel") or {})
        by_kind = dict(eviction_rule.get("priority_by_subject_kind") or {})
        channel_priority = _as_int(by_channel.get(str(row.get("channel_id", "")), 0), 0)
        kind_priority = _as_int(by_kind.get(str(row.get("subject_kind", "")), 0), 0)
        total = int(channel_priority + kind_priority)
        return (int(total), int(source_tick), str(item_id))
    return (int(source_tick), int(source_tick), str(item_id))


def _apply_eviction(items: List[dict], max_items: int, eviction_rule: dict) -> List[dict]:
    cap = max(0, _as_int(max_items, 0))
    if cap <= 0:
        return []
    working = [dict(row) for row in items]
    if len(working) <= cap:
        return working
    overflow = len(working) - cap
    ranked = sorted(working, key=lambda row: _eviction_rank(row, eviction_rule=eviction_rule))
    evicted_ids = set(str(row.get("memory_item_id", "")) for row in ranked[:overflow])
    kept = [dict(row) for row in working if str(row.get("memory_item_id", "")) not in evicted_ids]
    return kept[:cap]


def memory_store_hash(store_payload: dict) -> str:
    payload = dict(store_payload or {})
    payload.pop("store_hash", None)
    return canonical_sha256(payload)


def update_memory_store(
    perceived_now: dict,
    owner_subject_id: str,
    retention_policy: dict,
    decay_model: dict,
    eviction_rule: dict,
    previous_store: dict | None,
    tick: int,
) -> Dict[str, object]:
    owner_token = str(owner_subject_id).strip() or "subject.unknown"
    retention_policy_id = str(retention_policy.get("retention_policy_id", "")).strip()
    memory_allowed = bool(retention_policy.get("memory_allowed", False))
    max_items = max(0, _as_int(retention_policy.get("max_memory_items", 0), 0))
    current_tick = max(0, _as_int(tick, 0))

    previous = dict(previous_store or {})
    previous_extensions = dict(previous.get("extensions") or {})
    previous_tick = _as_int(previous_extensions.get("last_tick", current_tick), current_tick)
    tick_delta = max(0, int(current_tick - previous_tick))
    existing_items = _coerce_existing_items(previous_store=previous)

    items = _decay_items(existing_items, tick_delta=tick_delta)
    if not memory_allowed or max_items <= 0:
        items = []
    else:
        indexed: Dict[str, dict] = dict(
            (str(row.get("memory_item_id", "")), dict(row))
            for row in _sort_items(items)
            if str(row.get("memory_item_id", ""))
        )
        candidates = _extract_candidates(perceived_now=dict(perceived_now or {}), tick=int(current_tick))
        for candidate in candidates:
            channel_id = str(candidate.get("channel_id", "")).strip()
            subject_kind = _subject_kind_token(candidate.get("subject_kind"))
            subject_id = _string_or_none(candidate.get("subject_id"))
            ttl_default = _ttl_for(decay_model=decay_model, channel_id=channel_id, subject_kind=subject_kind)
            refresh_on_observed = _refresh_on_observed(decay_model=decay_model, channel_id=channel_id, subject_kind=subject_kind)
            source_tick = _as_int(candidate.get("source_tick", current_tick), current_tick)
            item_id = _memory_item_id(
                owner_subject_id=owner_token,
                channel_id=channel_id,
                subject_kind=subject_kind,
                subject_id=subject_id,
                source_tick=source_tick,
            )
            current = dict(indexed.get(item_id) or {})
            if not current:
                indexed[item_id] = {
                    "memory_item_id": item_id,
                    "owner_subject_id": owner_token,
                    "source_tick": int(source_tick),
                    "last_refresh_tick": int(current_tick),
                    "channel_id": channel_id,
                    "subject_kind": subject_kind,
                    "subject_id": subject_id,
                    "payload": copy.deepcopy(dict(candidate.get("payload") or {})),
                    "precision_tag": str(candidate.get("precision_tag", _default_precision_tag(channel_id))),
                    "ttl_ticks": ttl_default,
                    "extensions": {
                        "source_tick_bucket": int(max(0, int(source_tick)) // SOURCE_TICK_BUCKET_SIZE),
                    },
                }
                continue
            refreshed = dict(current)
            refreshed["channel_id"] = channel_id
            refreshed["subject_kind"] = subject_kind
            refreshed["subject_id"] = subject_id
            refreshed["payload"] = copy.deepcopy(dict(candidate.get("payload") or {}))
            refreshed["precision_tag"] = str(candidate.get("precision_tag", refreshed.get("precision_tag", _default_precision_tag(channel_id))))
            if refresh_on_observed:
                refreshed["last_refresh_tick"] = int(current_tick)
                refreshed["ttl_ticks"] = ttl_default
            indexed[item_id] = refreshed

        items = [dict(row) for row in indexed.values()]
        items = [
            dict(row)
            for row in items
            if row.get("ttl_ticks") is None or _as_int(row.get("ttl_ticks", 0), 0) > 0
        ]
        items = _apply_eviction(
            items=items,
            max_items=int(max_items),
            eviction_rule=dict(eviction_rule or {}),
        )

    items = _sort_items(items)
    memory_store = {
        "schema_version": "1.0.0",
        "store_id": _store_id(owner_token),
        "owner_subject_id": owner_token,
        "retention_policy_id": retention_policy_id,
        "items": items,
        "store_hash": "",
        "extensions": {
            "memory_allowed": bool(memory_allowed),
            "decay_model_id": str(decay_model.get("decay_model_id", "")).strip(),
            "eviction_rule_id": str(eviction_rule.get("eviction_rule_id", "")).strip(),
            "deterministic_eviction_rule_id": str(retention_policy.get("deterministic_eviction_rule_id", "")).strip()
            or str(retention_policy.get("eviction_rule_id", "")).strip(),
            "last_tick": int(current_tick),
            "source_tick_bucket_size": int(SOURCE_TICK_BUCKET_SIZE),
        },
    }
    memory_store["store_hash"] = memory_store_hash(memory_store)
    return {
        "result": "complete",
        "memory_store": dict(memory_store),
        "memory_state": dict(memory_store),
    }

"""Deterministic diegetic instrument transform from perceived.now/memory."""

from __future__ import annotations

import copy
from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256


NOTEBOOK_TEXT_MAX = 280
RADIO_TEXT_MAX = 280
MAP_ENTRY_MAX = 128
NOTEBOOK_ENTRY_MAX = 128
RADIO_MESSAGE_MAX = 64


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(items: object) -> List[str]:
    if not isinstance(items, list):
        return []
    return sorted(set(str(item).strip() for item in items if str(item).strip()))


def _norm_dict(payload: object) -> dict:
    return dict(payload) if isinstance(payload, dict) else {}


def _message_rows(rows: object, channel_id: str, max_items: int) -> List[dict]:
    if not isinstance(rows, list):
        return []
    normalized = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        item_channel = str(item.get("channel_id", channel_id)).strip() or str(channel_id)
        if item_channel != str(channel_id):
            continue
        payload = _norm_dict(item.get("payload"))
        message_id = str(item.get("message_id", "")).strip()
        if not message_id:
            digest = canonical_sha256(
                {
                    "author_subject_id": str(item.get("author_subject_id", "")).strip(),
                    "created_tick": _as_int(item.get("created_tick", 0), 0),
                    "channel_id": item_channel,
                    "payload": payload,
                }
            )
            message_id = "{}.{}".format(item_channel, digest[:16])
        normalized.append(
            {
                "schema_version": "1.0.0",
                "message_id": message_id,
                "author_subject_id": str(item.get("author_subject_id", "")).strip() or "origin.unknown",
                "created_tick": max(0, _as_int(item.get("created_tick", 0), 0)),
                "channel_id": item_channel,
                "payload": payload,
                "signature": item.get("signature") if item.get("signature") is None else str(item.get("signature", "")),
                "extensions": _norm_dict(item.get("extensions")),
            }
        )
    normalized = sorted(
        normalized,
        key=lambda item: (
            int(item.get("created_tick", 0)),
            str(item.get("author_subject_id", "")),
            str(item.get("message_id", "")),
            canonical_sha256(dict(item.get("payload") or {})),
        ),
    )
    limit = max(0, int(max_items))
    if limit <= 0:
        return []
    return normalized[-limit:]


def _memory_items(memory_store: dict) -> List[dict]:
    rows = memory_store.get("items")
    if not isinstance(rows, list):
        return []
    return sorted(
        (dict(item) for item in rows if isinstance(item, dict)),
        key=lambda item: (
            str(item.get("channel_id", "")),
            str(item.get("subject_kind", "")),
            str(item.get("subject_id", "") if item.get("subject_id") is not None else ""),
            _as_int(item.get("source_tick", 0), 0),
            str(item.get("memory_item_id", "")),
        ),
    )


def _map_entries_from_memory(memory_store: dict, prior_entries: object) -> List[dict]:
    entries = {}
    for item in _memory_items(memory_store):
        channel_id = str(item.get("channel_id", "")).strip()
        subject_kind = str(item.get("subject_kind", "")).strip()
        if channel_id not in ("ch.core.navigation", "ch.nondiegetic.nav", "ch.diegetic.map_local") and subject_kind != "region":
            continue
        subject_id = str(item.get("subject_id", "") if item.get("subject_id") is not None else "").strip()
        key = subject_id or "region.{}".format(canonical_sha256(item)[:16])
        current = entries.get(key) or {
            "region_key": key,
            "discovered": True,
            "confidence_permille": 0,
            "last_seen_tick": 0,
            "precision_tag": "coarse",
            "terrain_class": None,
        }
        current["discovered"] = True
        current["last_seen_tick"] = max(
            int(current.get("last_seen_tick", 0)),
            _as_int(item.get("last_refresh_tick", item.get("source_tick", 0)), 0),
        )
        current["confidence_permille"] = max(
            int(current.get("confidence_permille", 0)),
            500,
        )
        precision = str(item.get("precision_tag", "")).strip()
        if precision:
            current["precision_tag"] = precision
        payload = _norm_dict(item.get("payload"))
        nav_row = _norm_dict(payload.get("navigation_row"))
        terrain = str(nav_row.get("kind", "")).strip()
        if terrain:
            current["terrain_class"] = terrain
        entries[key] = current

    if isinstance(prior_entries, list):
        for item in prior_entries:
            if not isinstance(item, dict):
                continue
            key = str(item.get("region_key", "")).strip() or str(item.get("tile_key", "")).strip()
            if not key:
                key = "region.{}".format(canonical_sha256(item)[:16])
            current = entries.get(key) or {
                "region_key": key,
                "discovered": bool(item.get("discovered", True)),
                "confidence_permille": max(0, min(1000, _as_int(item.get("confidence_permille", 1000), 1000))),
                "last_seen_tick": max(0, _as_int(item.get("last_seen_tick", 0), 0)),
                "precision_tag": str(item.get("precision_tag", "medium") or "medium"),
                "terrain_class": str(item.get("terrain_class", "")).strip() or None,
            }
            current["confidence_permille"] = max(
                int(current.get("confidence_permille", 0)),
                max(0, min(1000, _as_int(item.get("confidence_permille", 0), 0))),
            )
            current["last_seen_tick"] = max(
                int(current.get("last_seen_tick", 0)),
                max(0, _as_int(item.get("last_seen_tick", 0), 0)),
            )
            entries[key] = current

    ordered = sorted(
        (dict(value) for value in entries.values()),
        key=lambda item: (
            str(item.get("region_key", "")),
            int(item.get("last_seen_tick", 0)),
            int(item.get("confidence_permille", 0)),
            canonical_sha256(item),
        ),
    )
    return ordered[:MAP_ENTRY_MAX]


def _memory_summary_text(item: dict) -> str:
    channel = str(item.get("channel_id", "")).strip()
    subject = str(item.get("subject_id", "") if item.get("subject_id") is not None else "").strip()
    payload = _norm_dict(item.get("payload"))
    keys = sorted(payload.keys())
    if subject:
        return "{} @{}".format(channel or "channel.unknown", subject)[:NOTEBOOK_TEXT_MAX]
    if keys:
        return "{} [{}]".format(channel or "channel.unknown", ",".join(keys))[:NOTEBOOK_TEXT_MAX]
    return (channel or "channel.unknown")[:NOTEBOOK_TEXT_MAX]


def _notebook_entries(memory_store: dict, notes: object) -> List[dict]:
    rows = []
    for item in _memory_items(memory_store):
        subject_kind = str(item.get("subject_kind", "")).strip()
        if subject_kind not in ("event", "entity", "signal"):
            continue
        entry_id = str(item.get("memory_item_id", "")).strip() or "mem.entry.{}".format(canonical_sha256(item)[:16])
        rows.append(
            {
                "entry_id": entry_id,
                "kind": "memory",
                "created_tick": max(0, _as_int(item.get("last_refresh_tick", item.get("source_tick", 0)), 0)),
                "author_subject_id": str(item.get("owner_subject_id", "")).strip() or "subject.unknown",
                "text": _memory_summary_text(item),
            }
        )

    for note in _message_rows(notes, "msg.notebook", NOTEBOOK_ENTRY_MAX):
        payload = _norm_dict(note.get("payload"))
        rows.append(
            {
                "entry_id": str(note.get("message_id", "")),
                "kind": "note",
                "created_tick": max(0, _as_int(note.get("created_tick", 0), 0)),
                "author_subject_id": str(note.get("author_subject_id", "")),
                "text": str(payload.get("text", ""))[:NOTEBOOK_TEXT_MAX],
            }
        )

    rows = sorted(
        rows,
        key=lambda item: (
            int(item.get("created_tick", 0)),
            str(item.get("kind", "")),
            str(item.get("entry_id", "")),
            str(item.get("author_subject_id", "")),
        ),
    )
    return rows[-NOTEBOOK_ENTRY_MAX:]


def _default_instrument_rows(source_rows: object) -> Dict[str, dict]:
    rows = {}
    if isinstance(source_rows, list):
        for row in source_rows:
            if not isinstance(row, dict):
                continue
            assembly_id = str(row.get("assembly_id", "")).strip()
            if not assembly_id:
                continue
            rows[assembly_id] = dict(row)
    defaults = {
        "instrument.altimeter": {"instrument_type": "altimeter", "instrument_type_id": "instr.altimeter"},
        "instrument.clock": {"instrument_type": "clock", "instrument_type_id": "instr.clock"},
        "instrument.compass": {"instrument_type": "compass", "instrument_type_id": "instr.compass"},
        "instrument.map_local": {"instrument_type": "map_local", "instrument_type_id": "instr.map_local"},
        "instrument.notebook": {"instrument_type": "notebook", "instrument_type_id": "instr.notebook"},
        "instrument.radio_text": {"instrument_type": "radio_text", "instrument_type_id": "instr.radio_text"},
    }
    for assembly_id in sorted(defaults.keys()):
        if assembly_id in rows:
            continue
        rows[assembly_id] = {
            "assembly_id": assembly_id,
            "instrument_type": str(defaults[assembly_id]["instrument_type"]),
            "instrument_type_id": str(defaults[assembly_id]["instrument_type_id"]),
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {},
            "state": {},
            "outputs": {},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        }
    return rows


def compute_diegetic_instruments(
    perceived_now: dict,
    memory_store: dict,
    instrument_rows: object,
    requested_channels: object,
    simulation_tick: int,
) -> Dict[str, dict]:
    channels = set(_sorted_tokens(requested_channels))
    camera = _norm_dict(perceived_now.get("camera_viewpoint"))
    time_state = _norm_dict(perceived_now.get("time_state"))
    rows = _default_instrument_rows(instrument_rows)
    out: Dict[str, dict] = {}

    for assembly_id in sorted(rows.keys()):
        row = dict(rows[assembly_id])
        state_payload = _norm_dict(row.get("state"))
        outputs = _norm_dict(row.get("outputs"))
        quality = str(row.get("quality", "nominal")).strip() or "nominal"
        quality_value = max(0, _as_int(row.get("quality_value", 1000), 1000))

        reading: dict = {}
        if assembly_id == "instrument.compass":
            yaw = _as_int(_norm_dict(camera.get("orientation_mdeg")).get("yaw", 0), 0) % 360000
            if "ch.diegetic.compass" in channels:
                reading = {"heading_mdeg": yaw}
            outputs["ch.diegetic.compass"] = dict(reading)
        elif assembly_id == "instrument.clock":
            if "ch.diegetic.clock" in channels:
                reading = {
                    "tick": max(0, int(simulation_tick)),
                    "rate_permille": _as_int(time_state.get("rate_permille", 1000), 1000),
                    "paused": bool(time_state.get("paused", False)),
                }
            outputs["ch.diegetic.clock"] = dict(reading)
        elif assembly_id == "instrument.altimeter":
            altitude_mm = _as_int(_norm_dict(camera.get("position_mm")).get("z", 0), 0)
            if "ch.diegetic.altimeter" in channels:
                reading = {"altitude_mm": altitude_mm}
            outputs["ch.diegetic.altimeter"] = dict(reading)
        elif assembly_id == "instrument.map_local":
            prior_entries = state_payload.get("entries")
            entries = _map_entries_from_memory(memory_store=memory_store, prior_entries=prior_entries)
            state_payload["entries"] = copy.deepcopy(entries)
            if "ch.diegetic.map_local" in channels:
                reading = {
                    "entries": copy.deepcopy(entries),
                    "entry_count": len(entries),
                }
            outputs["ch.diegetic.map_local"] = {
                "entries": copy.deepcopy(entries) if "ch.diegetic.map_local" in channels else [],
                "entry_count": len(entries) if "ch.diegetic.map_local" in channels else 0,
            }
        elif assembly_id == "instrument.notebook":
            notes = state_payload.get("user_notes")
            entries = _notebook_entries(memory_store=memory_store, notes=notes)
            state_payload["user_notes"] = _message_rows(notes, "msg.notebook", NOTEBOOK_ENTRY_MAX)
            if "ch.diegetic.notebook" in channels:
                reading = {
                    "entries": copy.deepcopy(entries),
                    "entry_count": len(entries),
                }
            outputs["ch.diegetic.notebook"] = {
                "entries": copy.deepcopy(entries) if "ch.diegetic.notebook" in channels else [],
                "entry_count": len(entries) if "ch.diegetic.notebook" in channels else 0,
            }
        elif assembly_id == "instrument.radio_text":
            inbox = _message_rows(state_payload.get("inbox"), "msg.radio", RADIO_MESSAGE_MAX)
            state_payload["inbox"] = copy.deepcopy(inbox)
            if "ch.diegetic.radio_text" in channels:
                reading = {
                    "messages": copy.deepcopy(inbox),
                    "message_count": len(inbox),
                }
            outputs["ch.diegetic.radio_text"] = {
                "messages": copy.deepcopy(inbox) if "ch.diegetic.radio_text" in channels else [],
                "message_count": len(inbox) if "ch.diegetic.radio_text" in channels else 0,
            }
        else:
            reading = _norm_dict(row.get("reading"))

        out[assembly_id] = {
            "assembly_id": assembly_id,
            "instrument_type": str(row.get("instrument_type", "")).strip(),
            "instrument_type_id": str(row.get("instrument_type_id", "")).strip(),
            "carrier_agent_id": row.get("carrier_agent_id"),
            "station_site_id": row.get("station_site_id"),
            "reading": reading,
            "state": state_payload,
            "outputs": outputs,
            "quality": quality,
            "quality_value": quality_value,
            "last_update_tick": max(0, _as_int(row.get("last_update_tick", simulation_tick), simulation_tick)),
        }

    return dict((key, out[key]) for key in sorted(out.keys()))


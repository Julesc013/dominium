"""Deterministic process-driven mutation runtime for lab camera/time intents."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from typing import Dict, List, Tuple

from src.reality.ledger import (
    begin_process_accounting,
    emit_exception as ledger_emit_exception,
    finalize_process_accounting,
    last_ledger_hash,
    record_unaccounted_delta,
)
from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import refusal


PROCESS_ENTITLEMENT_DEFAULTS = {
    "process.camera_move": "entitlement.camera_control",
    "process.camera_teleport": "entitlement.teleport",
    "process.agent_move": "entitlement.agent.move",
    "process.agent_rotate": "entitlement.agent.rotate",
    "process.srz_transfer_entity": "entitlement.control.admin",
    "process.control_bind_camera": "entitlement.control.camera",
    "process.control_unbind_camera": "entitlement.control.camera",
    "process.control_possess_agent": "entitlement.control.possess",
    "process.control_release_agent": "entitlement.control.possess",
    "process.control_set_view_lens": "entitlement.control.lens_override",
    "process.faction_create": "entitlement.civ.create_faction",
    "process.faction_dissolve": "entitlement.civ.dissolve_faction",
    "process.affiliation_join": "entitlement.civ.affiliation",
    "process.affiliation_leave": "entitlement.civ.affiliation",
    "process.territory_claim": "entitlement.civ.claim",
    "process.territory_release": "entitlement.civ.claim",
    "process.diplomacy_set_relation": "entitlement.civ.diplomacy",
    "process.cohort_create": "entitlement.civ.admin",
    "process.cohort_expand_to_micro": "entitlement.civ.admin",
    "process.cohort_collapse_from_micro": "entitlement.civ.admin",
    "process.affiliation_change_micro": "entitlement.civ.affiliation",
    "process.order_create": "entitlement.civ.order",
    "process.order_cancel": "entitlement.civ.order",
    "process.order_tick": "entitlement.civ.order",
    "process.cohort_relocate": "entitlement.civ.order",
    "process.demography_tick": "session.boot",
    "process.role_assign": "entitlement.civ.role_assign",
    "process.role_revoke": "entitlement.civ.role_assign",
    "process.camera_bind_target": "entitlement.control.camera",
    "process.camera_unbind_target": "entitlement.control.camera",
    "process.camera_set_view_mode": "entitlement.control.camera",
    "process.camera_set_lens": "entitlement.control.lens_override",
    "process.cosmetic_assign": "entitlement.cosmetic.assign",
    "process.body_move_attempt": "entitlement.control.possess",
    "process.instrument_tick": "session.boot",
    "process.instrument_notebook_add_note": "entitlement.diegetic.notebook_write",
    "process.instrument_radio_send_text": "entitlement.diegetic.radio_use",
    "process.time_control_set_rate": "entitlement.time_control",
    "process.time_pause": "entitlement.time_control",
    "process.time_resume": "entitlement.time_control",
    "process.region_management_tick": "session.boot",
    "process.region_expand": "session.boot",
    "process.region_collapse": "session.boot",
}
PROCESS_PRIVILEGE_DEFAULTS = {
    "process.camera_move": "observer",
    "process.camera_teleport": "operator",
    "process.agent_move": "operator",
    "process.agent_rotate": "operator",
    "process.srz_transfer_entity": "system",
    "process.control_bind_camera": "observer",
    "process.control_unbind_camera": "observer",
    "process.control_possess_agent": "operator",
    "process.control_release_agent": "operator",
    "process.control_set_view_lens": "operator",
    "process.faction_create": "operator",
    "process.faction_dissolve": "operator",
    "process.affiliation_join": "observer",
    "process.affiliation_leave": "observer",
    "process.territory_claim": "operator",
    "process.territory_release": "operator",
    "process.diplomacy_set_relation": "operator",
    "process.cohort_create": "operator",
    "process.cohort_expand_to_micro": "operator",
    "process.cohort_collapse_from_micro": "operator",
    "process.affiliation_change_micro": "observer",
    "process.order_create": "operator",
    "process.order_cancel": "operator",
    "process.order_tick": "operator",
    "process.cohort_relocate": "operator",
    "process.demography_tick": "observer",
    "process.role_assign": "operator",
    "process.role_revoke": "operator",
    "process.camera_bind_target": "observer",
    "process.camera_unbind_target": "observer",
    "process.camera_set_view_mode": "observer",
    "process.camera_set_lens": "operator",
    "process.cosmetic_assign": "operator",
    "process.body_move_attempt": "operator",
    "process.instrument_tick": "observer",
    "process.instrument_notebook_add_note": "observer",
    "process.instrument_radio_send_text": "observer",
    "process.time_control_set_rate": "operator",
    "process.time_pause": "operator",
    "process.time_resume": "operator",
    "process.region_management_tick": "observer",
    "process.region_expand": "observer",
    "process.region_collapse": "observer",
}
PRIVILEGE_RANK = {
    "observer": 0,
    "operator": 1,
    "system": 2,
}
REPO_ROOT_HINT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SOLVER_REGISTRY_REL = "data/registries/solver_registry.json"
DEFAULT_SOLVER_BINDINGS = {
    "collapse_solver_id": "solver.collapse.macro_capsule",
    "expand_solver_id": "solver.expand.local_high_fidelity",
}
CONTROL_PROCESS_IDS = {
    "process.agent_move",
    "process.agent_rotate",
    "process.srz_transfer_entity",
    "process.control_bind_camera",
    "process.control_unbind_camera",
    "process.control_possess_agent",
    "process.control_release_agent",
    "process.control_set_view_lens",
    "process.camera_bind_target",
    "process.camera_unbind_target",
    "process.camera_set_view_mode",
    "process.camera_set_lens",
    "process.cosmetic_assign",
    "process.instrument_notebook_add_note",
    "process.instrument_radio_send_text",
    "process.body_move_attempt",
}
CIV_PROCESS_IDS = {
    "process.faction_create",
    "process.faction_dissolve",
    "process.affiliation_join",
    "process.affiliation_leave",
    "process.territory_claim",
    "process.territory_release",
    "process.diplomacy_set_relation",
    "process.cohort_create",
    "process.cohort_expand_to_micro",
    "process.cohort_collapse_from_micro",
    "process.affiliation_change_micro",
    "process.order_create",
    "process.order_cancel",
    "process.order_tick",
    "process.cohort_relocate",
    "process.demography_tick",
    "process.role_assign",
    "process.role_revoke",
}
CAMERA_REQUIRED_PROCESS_IDS = {
    "process.camera_move",
    "process.camera_teleport",
    "process.control_bind_camera",
    "process.control_unbind_camera",
    "process.control_set_view_lens",
    "process.camera_bind_target",
    "process.camera_unbind_target",
    "process.camera_set_view_mode",
    "process.camera_set_lens",
}
CONTROL_GATE_REASON_MAP = {
    "PROCESS_FORBIDDEN": "refusal.control.law_forbidden",
    "ENTITLEMENT_MISSING": "refusal.control.entitlement_missing",
}
COSMETIC_GATE_REASON_MAP = {
    "PROCESS_FORBIDDEN": "refusal.cosmetic.forbidden",
    "ENTITLEMENT_MISSING": "refusal.cosmetic.forbidden",
}
CIV_GATE_REASON_MAP = {
    "PROCESS_FORBIDDEN": "refusal.civ.law_forbidden",
    "ENTITLEMENT_MISSING": "refusal.civ.entitlement_missing",
}
DEFAULT_COSMETIC_ID = "cosmetic.default.pill"
DEFAULT_RENDER_PROXY_ID = "render.proxy.pill_default"
CONTROLLER_ACTIONS_BY_TYPE = {
    "admin": [
        "control.action.bind_camera",
        "control.action.unbind_camera",
        "control.action.possess_agent",
        "control.action.release_agent",
        "control.action.set_view_lens",
        "control.action.assign_cosmetic",
    ],
    "ai_policy": [
        "control.action.possess_agent",
        "control.action.release_agent",
    ],
    "player_input": [
        "control.action.bind_camera",
        "control.action.unbind_camera",
        "control.action.possess_agent",
        "control.action.release_agent",
    ],
    "script": [
        "control.action.bind_camera",
        "control.action.unbind_camera",
        "control.action.possess_agent",
        "control.action.release_agent",
        "control.action.set_view_lens",
        "control.action.assign_cosmetic",
    ],
    "spectator": [
        "control.action.bind_camera",
        "control.action.unbind_camera",
    ],
}
DIEGETIC_NOTE_MAX_CHARS = 280
DIEGETIC_RADIO_MAX_CHARS = 280
DIEGETIC_NOTEBOOK_MAX_ITEMS = 128
DIEGETIC_RADIO_MAX_ITEMS = 64
DIEGETIC_MAP_MAX_ITEMS = 128
INSTRUMENT_TYPE_ID_BY_TYPE = {
    "altimeter": "instr.altimeter",
    "clock": "instr.clock",
    "compass": "instr.compass",
    "map_local": "instr.map_local",
    "notebook": "instr.notebook",
    "radio_text": "instr.radio_text",
}
INSTRUMENT_TYPE_BY_ID = dict((value, key) for key, value in INSTRUMENT_TYPE_ID_BY_TYPE.items())

CONSERVATION_DEFAULT_QUANTITY_ID = "quantity.mass_energy_total"
CONSERVATION_DEFAULT_DOMAIN_ID = "domain.reality"
CONSERVATION_CONTROL_DOMAIN_ID = "domain.control"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(items: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (items or []) if str(item).strip()))


def _ordered_unique_tokens(items: List[object]) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for item in list(items or []):
        token = str(item).strip()
        if not token or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def _vector3_int(payload: object, field_name: str) -> Dict[str, int] | None:
    if not isinstance(payload, dict):
        return None
    if "x" not in payload or "y" not in payload or "z" not in payload:
        return None
    return {
        "x": _as_int(payload.get("x", 0), 0),
        "y": _as_int(payload.get("y", 0), 0),
        "z": _as_int(payload.get("z", 0), 0),
    }


def _angles_int(payload: object) -> Dict[str, int] | None:
    if not isinstance(payload, dict):
        return None
    if "yaw" not in payload or "pitch" not in payload or "roll" not in payload:
        return None
    return {
        "yaw": _as_int(payload.get("yaw", 0), 0),
        "pitch": _as_int(payload.get("pitch", 0), 0),
        "roll": _as_int(payload.get("roll", 0), 0),
    }


def _require_camera_main(state: dict) -> Dict[str, object]:
    rows = state.get("camera_assemblies")
    if not isinstance(rows, list):
        return refusal(
            "PROCESS_INPUT_INVALID",
            "universe state is missing camera_assemblies list",
            "Initialize session with camera.main assembly before process execution.",
            {"field": "camera_assemblies"},
            "$.camera_assemblies",
        )
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == "camera.main":
            return {"result": "complete", "camera": row}
    return refusal(
        "PROCESS_INPUT_INVALID",
        "universe state camera.main assembly is missing",
        "Initialize camera.main through session bootstrap tooling.",
        {"assembly_id": "camera.main"},
        "$.camera_assemblies",
    )


def _ensure_time_control(state: dict) -> dict:
    payload = state.get("time_control")
    if not isinstance(payload, dict):
        payload = {"rate_permille": 1000, "paused": False, "accumulator_permille": 0}
        state["time_control"] = payload
    payload["rate_permille"] = max(0, _as_int(payload.get("rate_permille", 1000), 1000))
    payload["paused"] = bool(payload.get("paused", False))
    payload["accumulator_permille"] = max(0, _as_int(payload.get("accumulator_permille", 0), 0))
    return payload


def _ensure_simulation_time(state: dict) -> dict:
    payload = state.get("simulation_time")
    if not isinstance(payload, dict):
        payload = {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"}
        state["simulation_time"] = payload
    payload["tick"] = max(0, _as_int(payload.get("tick", 0), 0))
    payload["timestamp_utc"] = str(payload.get("timestamp_utc", "1970-01-01T00:00:00Z"))
    return payload


def _ensure_instrument_assemblies(state: dict) -> List[dict]:
    rows = state.get("instrument_assemblies")
    if not isinstance(rows, list):
        rows = []
    by_id = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("assembly_id", "")).strip()
        if token:
            by_id[token] = dict(row)
    defaults = {
        "instrument.altimeter": {
            "assembly_id": "instrument.altimeter",
            "instrument_type": "altimeter",
            "instrument_type_id": "instr.altimeter",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {"altitude_mm": 0},
            "state": {},
            "outputs": {"ch.diegetic.altimeter": {"altitude_mm": 0}},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        "instrument.clock": {
            "assembly_id": "instrument.clock",
            "instrument_type": "clock",
            "instrument_type_id": "instr.clock",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {"tick": 0, "rate_permille": 1000, "paused": False},
            "state": {},
            "outputs": {"ch.diegetic.clock": {"tick": 0, "rate_permille": 1000, "paused": False}},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        "instrument.compass": {
            "assembly_id": "instrument.compass",
            "instrument_type": "compass",
            "instrument_type_id": "instr.compass",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {"heading_mdeg": 0},
            "state": {},
            "outputs": {"ch.diegetic.compass": {"heading_mdeg": 0}},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        "instrument.map_local": {
            "assembly_id": "instrument.map_local",
            "instrument_type": "map_local",
            "instrument_type_id": "instr.map_local",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {"entries": []},
            "state": {"entries": []},
            "outputs": {"ch.diegetic.map_local": {"entries": []}},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        "instrument.notebook": {
            "assembly_id": "instrument.notebook",
            "instrument_type": "notebook",
            "instrument_type_id": "instr.notebook",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {"entries": []},
            "state": {"user_notes": []},
            "outputs": {"ch.diegetic.notebook": {"entries": []}},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        "instrument.radio_text": {
            "assembly_id": "instrument.radio_text",
            "instrument_type": "radio_text",
            "instrument_type_id": "instr.radio_text",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {"messages": []},
            "state": {"inbox": []},
            "outputs": {"ch.diegetic.radio_text": {"messages": []}},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
    }
    for assembly_id in sorted(defaults.keys()):
        if assembly_id not in by_id:
            by_id[assembly_id] = dict(defaults[assembly_id])
            continue
        row = dict(by_id[assembly_id])
        row["assembly_id"] = assembly_id
        row["instrument_type"] = str(row.get("instrument_type", defaults[assembly_id]["instrument_type"])) or defaults[assembly_id]["instrument_type"]
        row["instrument_type_id"] = str(row.get("instrument_type_id", defaults[assembly_id]["instrument_type_id"])) or defaults[assembly_id]["instrument_type_id"]
        row["carrier_agent_id"] = None if row.get("carrier_agent_id") is None else str(row.get("carrier_agent_id", "")).strip() or None
        row["station_site_id"] = None if row.get("station_site_id") is None else str(row.get("station_site_id", "")).strip() or None
        reading = row.get("reading")
        row["reading"] = dict(reading) if isinstance(reading, dict) else dict(defaults[assembly_id]["reading"])
        state_payload = row.get("state")
        row["state"] = dict(state_payload) if isinstance(state_payload, dict) else dict(defaults[assembly_id]["state"])
        outputs_payload = row.get("outputs")
        row["outputs"] = dict(outputs_payload) if isinstance(outputs_payload, dict) else dict(defaults[assembly_id]["outputs"])
        row["quality"] = str(row.get("quality", "nominal")) or "nominal"
        row["quality_value"] = max(0, _as_int(row.get("quality_value", defaults[assembly_id]["quality_value"]), defaults[assembly_id]["quality_value"]))
        row["last_update_tick"] = max(0, _as_int(row.get("last_update_tick", 0), 0))
        by_id[assembly_id] = row
    normalized = [dict(by_id[key]) for key in sorted(by_id.keys())]
    state["instrument_assemblies"] = normalized
    return normalized


def _author_subject_id(authority_context: dict) -> str:
    peer_id = str(authority_context.get("peer_id", "")).strip()
    if peer_id:
        return "peer.{}".format(peer_id)
    origin = str(authority_context.get("authority_origin", "")).strip()
    if origin:
        return "origin.{}".format(origin)
    return "origin.unknown"


def _instrument_row_by_id(rows: List[dict], assembly_id: str) -> dict:
    token = str(assembly_id).strip()
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == token:
            return row
    return {}


def _map_entries_sorted(rows: object, max_items: int = DIEGETIC_MAP_MAX_ITEMS) -> List[dict]:
    if not isinstance(rows, list):
        return []
    normalized = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        region_key = str(item.get("region_key", "")).strip()
        if not region_key:
            region_key = str(item.get("tile_key", "")).strip()
        if not region_key:
            region_key = "region.{}".format(canonical_sha256(item)[:16])
        normalized.append(
            {
                "region_key": region_key,
                "discovered": bool(item.get("discovered", True)),
                "confidence_permille": max(0, min(1000, _as_int(item.get("confidence_permille", 1000), 1000))),
                "last_seen_tick": max(0, _as_int(item.get("last_seen_tick", 0), 0)),
                "precision_tag": str(item.get("precision_tag", "medium") or "medium"),
                "terrain_class": str(item.get("terrain_class", "")).strip() or None,
            }
        )
    normalized = sorted(
        normalized,
        key=lambda item: (
            str(item.get("region_key", "")),
            int(item.get("last_seen_tick", 0)),
            int(item.get("confidence_permille", 0)),
            canonical_sha256(item),
        ),
    )
    limit = max(0, int(max_items))
    if limit > 0:
        normalized = normalized[:limit]
    else:
        normalized = []
    return normalized


def _message_rows_sorted(rows: object, channel_id: str, max_items: int) -> List[dict]:
    if not isinstance(rows, list):
        return []
    normalized = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        item_channel = str(item.get("channel_id", "")).strip()
        if item_channel and item_channel != str(channel_id):
            continue
        payload = item.get("payload")
        payload_obj = dict(payload) if isinstance(payload, dict) else {}
        message_id = str(item.get("message_id", "")).strip()
        if not message_id:
            digest = canonical_sha256(
                {
                    "author_subject_id": str(item.get("author_subject_id", "")).strip(),
                    "created_tick": _as_int(item.get("created_tick", 0), 0),
                    "channel_id": str(channel_id),
                    "payload": payload_obj,
                }
            )
            message_id = "{}.{}".format(str(channel_id), digest[:16]).replace("msg.", "msg.")
        normalized.append(
            {
                "schema_version": "1.0.0",
                "message_id": message_id,
                "author_subject_id": str(item.get("author_subject_id", "")).strip() or "origin.unknown",
                "created_tick": max(0, _as_int(item.get("created_tick", 0), 0)),
                "channel_id": str(channel_id),
                "payload": payload_obj,
                "signature": item.get("signature") if item.get("signature") is None else str(item.get("signature", "")),
                "extensions": dict(item.get("extensions") or {}) if isinstance(item.get("extensions"), dict) else {},
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
    if limit > 0:
        return normalized[-limit:]
    return []


def _is_sha256_hex(token: object) -> bool:
    text = str(token or "").strip()
    if len(text) != 64:
        return False
    for char in text:
        if char.lower() not in "0123456789abcdef":
            return False
    return True


def _ensure_agent_states(state: dict) -> List[dict]:
    rows = state.get("agent_states")
    if not isinstance(rows, list):
        rows = []
    normalized = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("agent_id", ""))):
        agent_id = str(row.get("agent_id", "")).strip() or str(row.get("entity_id", "")).strip()
        if not agent_id:
            continue
        state_hash = str(row.get("state_hash", "")).strip()
        if not _is_sha256_hex(state_hash):
            state_hash = canonical_sha256({"agent_id": agent_id})
        orientation = _angles_int(row.get("orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
        normalized.append(
            {
                "agent_id": agent_id,
                "state_hash": state_hash,
                "body_id": row.get("body_id") if row.get("body_id") is None else str(row.get("body_id", "")).strip(),
                "owner_peer_id": row.get("owner_peer_id")
                if row.get("owner_peer_id") is None
                else str(row.get("owner_peer_id", "")).strip(),
                "controller_id": row.get("controller_id")
                if row.get("controller_id") is None
                else str(row.get("controller_id", "")).strip(),
                "shard_id": str(row.get("shard_id", "")).strip(),
                "intent_scope_id": row.get("intent_scope_id")
                if row.get("intent_scope_id") is None
                else str(row.get("intent_scope_id", "")).strip(),
                "parent_cohort_id": row.get("parent_cohort_id")
                if row.get("parent_cohort_id") is None
                else str(row.get("parent_cohort_id", "")).strip(),
                "location_ref": row.get("location_ref")
                if row.get("location_ref") is None
                else str(row.get("location_ref", "")).strip(),
                "orientation_mdeg": {
                    "yaw": _as_int((orientation or {}).get("yaw", 0), 0),
                    "pitch": _as_int((orientation or {}).get("pitch", 0), 0),
                    "roll": _as_int((orientation or {}).get("roll", 0), 0),
                },
            }
        )
    state["agent_states"] = normalized
    return normalized


def _ensure_controller_assemblies(state: dict) -> List[dict]:
    rows = state.get("controller_assemblies")
    if not isinstance(rows, list):
        rows = []
    normalized = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
        assembly_id = str(row.get("assembly_id", "")).strip()
        if not assembly_id:
            continue
        normalized.append(
            {
                "assembly_id": assembly_id,
                "controller_type": str(row.get("controller_type", "script")).strip() or "script",
                "owner_peer_id": row.get("owner_peer_id") if row.get("owner_peer_id") is None else str(row.get("owner_peer_id", "")).strip(),
                "allowed_actions": _sorted_tokens(list(row.get("allowed_actions") or [])),
                "binding_ids": _sorted_tokens(list(row.get("binding_ids") or [])),
                "status": str(row.get("status", "active")).strip() or "active",
            }
        )
    state["controller_assemblies"] = normalized
    return normalized


def _ensure_control_bindings(state: dict) -> List[dict]:
    rows = state.get("control_bindings")
    if not isinstance(rows, list):
        rows = []
    normalized = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("binding_id", ""))):
        binding_id = str(row.get("binding_id", "")).strip()
        controller_id = str(row.get("controller_id", "")).strip()
        binding_type = str(row.get("binding_type", "")).strip()
        target_id = str(row.get("target_id", "")).strip()
        if not binding_id or not controller_id or not binding_type or not target_id:
            continue
        normalized.append(
            {
                "binding_id": binding_id,
                "controller_id": controller_id,
                "binding_type": binding_type,
                "target_id": target_id,
                "created_tick": max(0, _as_int(row.get("created_tick", 0), 0)),
                "active": bool(row.get("active", True)),
                "required_entitlements": _sorted_tokens(list(row.get("required_entitlements") or [])),
            }
        )
    state["control_bindings"] = normalized
    return normalized


def _controller_actions_for_type(controller_type: str) -> List[str]:
    token = str(controller_type).strip()
    rows = CONTROLLER_ACTIONS_BY_TYPE.get(token)
    if not isinstance(rows, list):
        rows = CONTROLLER_ACTIONS_BY_TYPE.get("script") or []
    return _sorted_tokens(list(rows))


def _find_controller(controllers: List[dict], controller_id: str) -> dict:
    token = str(controller_id).strip()
    for row in controllers:
        if str(row.get("assembly_id", "")).strip() == token:
            return row
    return {}


def _upsert_controller(
    controllers: List[dict],
    controller_id: str,
    controller_type: str,
    owner_peer_id: object,
) -> dict:
    token = str(controller_id).strip()
    existing = _find_controller(controllers, token)
    normalized_owner = owner_peer_id if owner_peer_id is None else str(owner_peer_id).strip()
    controller_type_token = str(controller_type).strip() or "script"
    if existing:
        existing["controller_type"] = controller_type_token
        existing["owner_peer_id"] = normalized_owner
        existing["allowed_actions"] = _controller_actions_for_type(controller_type_token)
        existing["status"] = str(existing.get("status", "active")).strip() or "active"
        return existing
    created = {
        "assembly_id": token,
        "controller_type": controller_type_token,
        "owner_peer_id": normalized_owner,
        "allowed_actions": _controller_actions_for_type(controller_type_token),
        "binding_ids": [],
        "status": "active",
    }
    controllers.append(created)
    return created


def _binding_id(controller_id: str, binding_type: str, target_id: str) -> str:
    digest = canonical_sha256(
        {
            "controller_id": str(controller_id).strip(),
            "binding_type": str(binding_type).strip(),
            "target_id": str(target_id).strip(),
        }
    )
    return "binding.control.{}".format(digest[:24])


def _find_binding(bindings: List[dict], binding_id: str) -> dict:
    token = str(binding_id).strip()
    for row in bindings:
        if str(row.get("binding_id", "")).strip() == token:
            return row
    return {}


def _required_entitlements_for_binding(binding_type: str) -> List[str]:
    token = str(binding_type).strip()
    if token == "camera":
        return ["entitlement.control.camera"]
    if token == "possess":
        return ["entitlement.control.possess"]
    return []


def _sync_controller_binding_ids(controllers: List[dict], bindings: List[dict]) -> None:
    active_by_controller: Dict[str, List[str]] = {}
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        if not bool(binding.get("active", True)):
            continue
        controller_id = str(binding.get("controller_id", "")).strip()
        binding_id = str(binding.get("binding_id", "")).strip()
        if not controller_id or not binding_id:
            continue
        active_by_controller.setdefault(controller_id, []).append(binding_id)
    for controller in controllers:
        controller_id = str(controller.get("assembly_id", "")).strip()
        controller["binding_ids"] = _sorted_tokens(list(active_by_controller.get(controller_id, [])))


def _store_control_state(state: dict, controllers: List[dict], bindings: List[dict]) -> None:
    _sync_controller_binding_ids(controllers=controllers, bindings=bindings)
    state["controller_assemblies"] = sorted(
        (
            dict(item)
            for item in controllers
            if isinstance(item, dict) and str(item.get("assembly_id", "")).strip()
        ),
        key=lambda item: str(item.get("assembly_id", "")),
    )
    state["control_bindings"] = sorted(
        (
            dict(item)
            for item in bindings
            if isinstance(item, dict)
            and str(item.get("binding_id", "")).strip()
            and str(item.get("controller_id", "")).strip()
            and str(item.get("binding_type", "")).strip()
            and str(item.get("target_id", "")).strip()
        ),
        key=lambda item: str(item.get("binding_id", "")),
    )


def _camera_exists(state: dict, camera_id: str) -> bool:
    token = str(camera_id).strip()
    rows = state.get("camera_assemblies")
    if not isinstance(rows, list):
        return False
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == token:
            return True
    return False


def _camera_row(state: dict, camera_id: str) -> dict:
    token = str(camera_id).strip()
    rows = state.get("camera_assemblies")
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == token:
            return row
    return {}


def _camera_defaults(camera_row: dict) -> None:
    if not isinstance(camera_row, dict):
        return
    if "view_mode_id" not in camera_row or not str(camera_row.get("view_mode_id", "")).strip():
        camera_row["view_mode_id"] = "view.free.lab"
    if "binding_id" not in camera_row:
        camera_row["binding_id"] = None
    if "owner_peer_id" not in camera_row:
        camera_row["owner_peer_id"] = None
    if "target_id" not in camera_row:
        camera_row["target_id"] = None
    if "target_type" not in camera_row or not str(camera_row.get("target_type", "")).strip():
        camera_row["target_type"] = "none"
    if "offset_params" not in camera_row or not isinstance(camera_row.get("offset_params"), dict):
        camera_row["offset_params"] = _camera_binding_offset({})


def _view_mode_entries(navigation_indices: dict | None) -> Dict[str, dict]:
    rows: Dict[str, dict] = {}
    if not isinstance(navigation_indices, dict):
        return rows
    payload = navigation_indices.get("view_mode_registry")
    if not isinstance(payload, dict):
        return rows
    for item in payload.get("view_modes") or []:
        if not isinstance(item, dict):
            continue
        view_mode_id = str(item.get("view_mode_id", "")).strip()
        if view_mode_id:
            rows[view_mode_id] = dict(item)
    return rows


def _camera_binding_offset(offset_payload: object) -> Dict[str, int]:
    payload = dict(offset_payload) if isinstance(offset_payload, dict) else {}
    return {
        "x_mm": _as_int(payload.get("x_mm", 0), 0),
        "y_mm": _as_int(payload.get("y_mm", 0), 0),
        "z_mm": _as_int(payload.get("z_mm", 0), 0),
        "yaw_mdeg": _as_int(payload.get("yaw_mdeg", 0), 0),
        "pitch_mdeg": _as_int(payload.get("pitch_mdeg", 0), 0),
        "roll_mdeg": _as_int(payload.get("roll_mdeg", 0), 0),
    }


def _replication_policy_tag(policy_context: dict | None) -> str:
    if not isinstance(policy_context, dict):
        return ""
    token = str(policy_context.get("replication_policy_id", "")).strip()
    mapping = {
        "policy.net.lockstep": "lockstep",
        "policy.net.server_authoritative": "authoritative",
        "policy.net.srz_hybrid": "hybrid",
    }
    if token in mapping:
        return mapping[token]
    if token in ("lockstep", "authoritative", "hybrid"):
        return token
    return ""


def _camera_target_exists(
    state: dict,
    target_type: str,
    target_id: str,
    navigation_indices: dict | None,
) -> bool:
    token_type = str(target_type).strip()
    token_id = str(target_id).strip()
    if token_type == "none":
        return True
    if not token_id:
        return False
    if token_type == "agent":
        return bool(_find_agent(agent_rows=_ensure_agent_states(state), agent_id=token_id))
    if token_type == "body":
        return bool(_find_body(body_rows=_ensure_body_assemblies(state), body_id=token_id))
    if token_type == "site":
        maps = _navigation_maps(navigation_indices)
        return token_id in set((maps.get("sites") or {}).keys())
    return False


def _is_embodied_target(state: dict, target_type: str, target_id: str) -> bool:
    token_type = str(target_type).strip()
    token_id = str(target_id).strip()
    if not token_id:
        return False
    if token_type == "body":
        return bool(_find_body(body_rows=_ensure_body_assemblies(state), body_id=token_id))
    if token_type == "agent":
        agent = _find_agent(agent_rows=_ensure_agent_states(state), agent_id=token_id)
        if not agent:
            return False
        body_id = _agent_body_id(agent_row=agent, body_rows=_ensure_body_assemblies(state), agent_id=token_id)
        return bool(body_id)
    return False


def _view_mode_allowed_in_replication(view_mode: dict, policy_context: dict | None) -> bool:
    allowed = _sorted_tokens(list((view_mode or {}).get("allowed_in_policies") or []))
    if not allowed:
        return True
    token = _replication_policy_tag(policy_context)
    if not token:
        return True
    return token in set(allowed)


def _camera_target_owner_shard(
    state: dict,
    target_type: str,
    target_id: str,
    shard_map: dict,
    navigation_indices: dict | None,
) -> str:
    token_type = str(target_type).strip()
    token_id = str(target_id).strip()
    if not token_id:
        return ""
    if token_type == "agent":
        agent = _find_agent(agent_rows=_ensure_agent_states(state), agent_id=token_id)
        return str((agent or {}).get("shard_id", "")).strip() or _owner_shard_for_object(shard_map=shard_map, object_id=token_id)
    if token_type == "body":
        body = _find_body(body_rows=_ensure_body_assemblies(state), body_id=token_id)
        owner_agent_id = str((body or {}).get("owner_agent_id", "")).strip()
        return (
            str((body or {}).get("shard_id", "")).strip()
            or _owner_shard_for_object(shard_map=shard_map, object_id=owner_agent_id or token_id)
        )
    if token_type == "site":
        maps = _navigation_maps(navigation_indices)
        site = dict((maps.get("sites") or {}).get(token_id) or {})
        object_id = str(site.get("object_id", "")).strip()
        return _owner_shard_for_object(shard_map=shard_map, object_id=object_id or token_id)
    return ""


def _ensure_faction_assemblies(state: dict) -> List[dict]:
    rows = state.get("faction_assemblies")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("faction_id", ""))):
        faction_id = str(row.get("faction_id", "")).strip() or str(row.get("assembly_id", "")).strip()
        if not faction_id:
            continue
        status = str(row.get("status", "active")).strip() or "active"
        if status not in ("active", "dissolved"):
            status = "active"
        diplomatic_relations = row.get("diplomatic_relations")
        relation_map: Dict[str, str] = {}
        if isinstance(diplomatic_relations, dict):
            for peer_id in sorted(diplomatic_relations.keys()):
                peer_token = str(peer_id).strip()
                relation_token = str(diplomatic_relations.get(peer_id, "")).strip()
                if peer_token and relation_token:
                    relation_map[peer_token] = relation_token
        normalized.append(
            {
                "faction_id": faction_id,
                "human_name": str(row.get("human_name", "")).strip() or faction_id,
                "description": str(row.get("description", "")).strip(),
                "created_tick": max(0, _as_int(row.get("created_tick", 0), 0)),
                "founder_agent_id": row.get("founder_agent_id")
                if row.get("founder_agent_id") is None
                else str(row.get("founder_agent_id", "")).strip() or None,
                "governance_type_id": str(row.get("governance_type_id", "gov.none")).strip() or "gov.none",
                "territory_ids": _sorted_tokens(list(row.get("territory_ids") or [])),
                "diplomatic_relations": relation_map,
                "status": status,
                "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
            }
        )
    state["faction_assemblies"] = normalized
    return normalized


def _ensure_affiliations(state: dict) -> List[dict]:
    rows = state.get("affiliations")
    if not isinstance(rows, list):
        rows = []
    by_subject: Dict[str, dict] = {}
    for row in sorted(
        (item for item in rows if isinstance(item, dict)),
        key=lambda item: (
            str(item.get("subject_id", "")),
            _as_int(item.get("joined_tick", 0), 0),
            str(item.get("faction_id", "")),
            str(item.get("role_id", "")),
        ),
    ):
        subject_id = str(row.get("subject_id", "")).strip()
        if not subject_id:
            continue
        faction_value = row.get("faction_id")
        faction_id = None if faction_value is None else str(faction_value).strip() or None
        by_subject[subject_id] = {
            "subject_id": subject_id,
            "faction_id": faction_id,
            "joined_tick": max(0, _as_int(row.get("joined_tick", 0), 0)),
            "role_id": str(row.get("role_id", "role.member")).strip() or "role.member",
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    normalized = [dict(by_subject[token]) for token in sorted(by_subject.keys())]
    state["affiliations"] = normalized
    return normalized


def _ensure_territory_assemblies(state: dict) -> List[dict]:
    rows = state.get("territory_assemblies")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("territory_id", ""))):
        territory_id = str(row.get("territory_id", "")).strip()
        if not territory_id:
            continue
        claim_status = str(row.get("claim_status", "unclaimed")).strip() or "unclaimed"
        if claim_status not in ("unclaimed", "claimed", "contested"):
            claim_status = "unclaimed"
        owner = row.get("owner_faction_id")
        owner_faction_id = None if owner is None else str(owner).strip() or None
        normalized.append(
            {
                "territory_id": territory_id,
                "region_scope": dict(row.get("region_scope") or {}) if isinstance(row.get("region_scope"), dict) else {},
                "owner_faction_id": owner_faction_id,
                "claim_status": claim_status,
                "created_tick": max(0, _as_int(row.get("created_tick", 0), 0)),
                "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
            }
        )
    state["territory_assemblies"] = normalized
    return normalized


def _canonical_faction_pair(faction_a: str, faction_b: str) -> Tuple[str, str]:
    left = str(faction_a).strip()
    right = str(faction_b).strip()
    if left <= right:
        return left, right
    return right, left


def _ensure_diplomatic_relations(state: dict) -> List[dict]:
    rows = state.get("diplomatic_relations")
    if not isinstance(rows, list):
        rows = []
    by_pair: Dict[Tuple[str, str], dict] = {}
    for row in sorted(
        (item for item in rows if isinstance(item, dict)),
        key=lambda item: (
            str(item.get("faction_a", "")),
            str(item.get("faction_b", "")),
            _as_int(item.get("updated_tick", 0), 0),
            str(item.get("relation_state", "")),
        ),
    ):
        faction_a = str(row.get("faction_a", "")).strip()
        faction_b = str(row.get("faction_b", "")).strip()
        if not faction_a or not faction_b or faction_a == faction_b:
            continue
        left, right = _canonical_faction_pair(faction_a=faction_a, faction_b=faction_b)
        by_pair[(left, right)] = {
            "faction_a": left,
            "faction_b": right,
            "relation_state": str(row.get("relation_state", "neutral")).strip() or "neutral",
            "updated_tick": max(0, _as_int(row.get("updated_tick", 0), 0)),
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    normalized = [dict(by_pair[key]) for key in sorted(by_pair.keys())]
    state["diplomatic_relations"] = normalized
    return normalized


def _ensure_cohort_assemblies(state: dict) -> List[dict]:
    rows = state.get("cohort_assemblies")
    if not isinstance(rows, list):
        rows = state.get("cohort_states")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("cohort_id", ""))):
        cohort_id = str(row.get("cohort_id", "")).strip() or str(row.get("subject_id", "")).strip()
        if not cohort_id:
            continue
        size = max(0, _as_int(row.get("size", 0), 0))
        faction_raw = row.get("faction_id")
        territory_raw = row.get("territory_id")
        faction_id = None if faction_raw is None else str(faction_raw).strip() or None
        territory_id = None if territory_raw is None else str(territory_raw).strip() or None
        refinement_state = str(row.get("refinement_state", "macro")).strip() or "macro"
        if refinement_state not in ("macro", "micro", "mixed"):
            refinement_state = "macro"
        normalized.append(
            {
                "cohort_id": cohort_id,
                "size": int(size),
                "faction_id": faction_id,
                "territory_id": territory_id,
                "location_ref": str(row.get("location_ref", "")).strip(),
                "demographic_tags": dict(row.get("demographic_tags") or {}) if isinstance(row.get("demographic_tags"), dict) else {},
                "skill_distribution": dict(row.get("skill_distribution") or {})
                if isinstance(row.get("skill_distribution"), dict)
                else {},
                "refinement_state": refinement_state,
                "created_tick": max(0, _as_int(row.get("created_tick", 0), 0)),
                "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
            }
        )
    state["cohort_assemblies"] = normalized
    return normalized


def _normalize_order_status(token: object) -> str:
    value = str(token or "").strip() or "created"
    if value not in ("created", "queued", "executing", "completed", "failed", "refused", "cancelled"):
        return "created"
    return value


def _ensure_order_assemblies(state: dict) -> List[dict]:
    rows = state.get("order_assemblies")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("order_id", ""))):
        order_id = str(row.get("order_id", "")).strip()
        if not order_id:
            continue
        target_kind = str(row.get("target_kind", "")).strip()
        if target_kind not in ("agent", "cohort", "faction", "territory"):
            target_kind = "cohort"
        normalized.append(
            {
                "order_id": order_id,
                "order_type_id": str(row.get("order_type_id", "")).strip(),
                "issuer_subject_id": str(row.get("issuer_subject_id", "")).strip(),
                "target_kind": target_kind,
                "target_id": str(row.get("target_id", "")).strip(),
                "created_tick": max(0, _as_int(row.get("created_tick", 0), 0)),
                "last_update_tick": max(0, _as_int(row.get("last_update_tick", row.get("created_tick", 0)), 0)),
                "status": _normalize_order_status(row.get("status", "created")),
                "priority": max(0, _as_int(row.get("priority", 0), 0)),
                "payload": dict(row.get("payload") or {}) if isinstance(row.get("payload"), dict) else {},
                "required_entitlements": _sorted_tokens(list(row.get("required_entitlements") or [])),
                "refusal": dict(row.get("refusal") or {}) if isinstance(row.get("refusal"), dict) else None,
                "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
            }
        )
    state["order_assemblies"] = normalized
    return normalized


def _queue_id_for_owner(owner_kind: str, owner_id: str) -> str:
    kind = str(owner_kind).strip() or "global"
    token = str(owner_id).strip() or "global"
    return "queue.{}.{}".format(kind, token)


def _ensure_order_queue_assemblies(state: dict) -> List[dict]:
    rows = state.get("order_queue_assemblies")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("queue_id", ""))):
        queue_id = str(row.get("queue_id", "")).strip()
        if not queue_id:
            continue
        owner_kind = str(row.get("owner_kind", "")).strip()
        if owner_kind not in ("faction", "controller", "cohort", "global"):
            owner_kind = "global"
        owner_id = str(row.get("owner_id", "")).strip()
        if not owner_id:
            owner_id = "global"
        normalized.append(
            {
                "queue_id": queue_id,
                "owner_kind": owner_kind,
                "owner_id": owner_id,
                "order_ids": _ordered_unique_tokens(list(row.get("order_ids") or [])),
                "last_update_tick": max(0, _as_int(row.get("last_update_tick", 0), 0)),
                "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
            }
        )
    state["order_queue_assemblies"] = normalized
    return normalized


def _ensure_institution_assemblies(state: dict) -> List[dict]:
    rows = state.get("institution_assemblies")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("institution_id", ""))):
        institution_id = str(row.get("institution_id", "")).strip()
        if not institution_id:
            continue
        faction_value = row.get("faction_id")
        faction_id = None if faction_value is None else str(faction_value).strip() or None
        status = str(row.get("status", "active")).strip() or "active"
        if status not in ("active", "dissolved"):
            status = "active"
        normalized.append(
            {
                "institution_id": institution_id,
                "institution_type_id": str(row.get("institution_type_id", "")).strip(),
                "faction_id": faction_id,
                "status": status,
                "created_tick": max(0, _as_int(row.get("created_tick", 0), 0)),
                "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
            }
        )
    state["institution_assemblies"] = normalized
    return normalized


def _ensure_role_assignment_assemblies(state: dict) -> List[dict]:
    rows = state.get("role_assignment_assemblies")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("assignment_id", ""))):
        assignment_id = str(row.get("assignment_id", "")).strip()
        if not assignment_id:
            continue
        normalized.append(
            {
                "assignment_id": assignment_id,
                "institution_id": str(row.get("institution_id", "")).strip(),
                "subject_id": str(row.get("subject_id", "")).strip(),
                "role_id": str(row.get("role_id", "")).strip(),
                "granted_entitlements": _sorted_tokens(list(row.get("granted_entitlements") or [])),
                "created_tick": max(0, _as_int(row.get("created_tick", 0), 0)),
                "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
            }
        )
    state["role_assignment_assemblies"] = normalized
    return normalized


def _find_cohort(cohort_rows: List[dict], cohort_id: str) -> dict:
    token = str(cohort_id).strip()
    for row in cohort_rows:
        if str(row.get("cohort_id", "")).strip() == token:
            return row
    return {}


def _find_order(order_rows: List[dict], order_id: str) -> dict:
    token = str(order_id).strip()
    for row in order_rows:
        if str(row.get("order_id", "")).strip() == token:
            return row
    return {}


def _find_order_queue(queue_rows: List[dict], queue_id: str) -> dict:
    token = str(queue_id).strip()
    for row in queue_rows:
        if str(row.get("queue_id", "")).strip() == token:
            return row
    return {}


def _find_institution(institution_rows: List[dict], institution_id: str) -> dict:
    token = str(institution_id).strip()
    for row in institution_rows:
        if str(row.get("institution_id", "")).strip() == token:
            return row
    return {}


def _find_role_assignment(role_assignment_rows: List[dict], assignment_id: str) -> dict:
    token = str(assignment_id).strip()
    for row in role_assignment_rows:
        if str(row.get("assignment_id", "")).strip() == token:
            return row
    return {}


def _find_faction(faction_rows: List[dict], faction_id: str) -> dict:
    token = str(faction_id).strip()
    for row in faction_rows:
        if str(row.get("faction_id", "")).strip() == token:
            return row
    return {}


def _find_affiliation(affiliation_rows: List[dict], subject_id: str) -> dict:
    token = str(subject_id).strip()
    for row in affiliation_rows:
        if str(row.get("subject_id", "")).strip() == token:
            return row
    return {}


def _find_territory(territory_rows: List[dict], territory_id: str) -> dict:
    token = str(territory_id).strip()
    for row in territory_rows:
        if str(row.get("territory_id", "")).strip() == token:
            return row
    return {}


def _authority_peer_token(authority_context: dict) -> str:
    peer_id = str(authority_context.get("peer_id", "")).strip()
    if peer_id:
        return peer_id
    return str(authority_context.get("authority_origin", "")).strip()


def _civ_admin_override(authority_context: dict) -> bool:
    entitlements = _sorted_tokens(list(authority_context.get("entitlements") or []))
    if "entitlement.control.admin" in set(entitlements):
        return True
    if "entitlement.civ.admin" in set(entitlements):
        return True
    return False


def _faction_owner_peer_id(faction_row: dict) -> str:
    ext = dict(faction_row.get("extensions") or {}) if isinstance(faction_row.get("extensions"), dict) else {}
    return str(ext.get("owner_peer_id", "")).strip()


def _source_registry_rows(registry_rel: str, entry_key: str, id_key: str) -> Dict[str, dict]:
    abs_path = os.path.join(REPO_ROOT_HINT, registry_rel.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    record = payload.get("record")
    if not isinstance(record, dict):
        return {}
    rows = record.get(entry_key)
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(id_key, ""))):
        token = str(row.get(id_key, "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _governance_type_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "governance_type_registry")
    rows = _registry_rows_by_id(payload, "governance_types", "governance_type_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/governance_type_registry.json",
        entry_key="governance_types",
        id_key="governance_type_id",
    )


def _diplomatic_state_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "diplomatic_state_registry")
    rows = _registry_rows_by_id(payload, "states", "relation_state")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/diplomatic_state_registry.json",
        entry_key="states",
        id_key="relation_state",
    )


def _cohort_mapping_policy_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "cohort_mapping_policy_registry")
    rows = _registry_rows_by_id(payload, "policies", "mapping_policy_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/cohort_mapping_policy_registry.json",
        entry_key="policies",
        id_key="mapping_policy_id",
    )


def _order_type_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "order_type_registry")
    rows = _registry_rows_by_id(payload, "order_types", "order_type_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/order_type_registry.json",
        entry_key="order_types",
        id_key="order_type_id",
    )


def _role_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "role_registry")
    rows = _registry_rows_by_id(payload, "roles", "role_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/role_registry.json",
        entry_key="roles",
        id_key="role_id",
    )


def _institution_type_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "institution_type_registry")
    rows = _registry_rows_by_id(payload, "institution_types", "institution_type_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/institution_type_registry.json",
        entry_key="institution_types",
        id_key="institution_type_id",
    )


def _demography_policy_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "demography_policy_registry")
    rows = _registry_rows_by_id(payload, "policies", "demography_policy_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/demography_policy_registry.json",
        entry_key="policies",
        id_key="demography_policy_id",
    )


def _death_model_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "death_model_registry")
    rows = _registry_rows_by_id(payload, "death_models", "death_model_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/death_model_registry.json",
        entry_key="death_models",
        id_key="death_model_id",
    )


def _birth_model_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "birth_model_registry")
    rows = _registry_rows_by_id(payload, "birth_models", "birth_model_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/birth_model_registry.json",
        entry_key="birth_models",
        id_key="birth_model_id",
    )


def _migration_model_rows(policy_context: dict | None) -> Dict[str, dict]:
    payload = _policy_payload(policy_context, "migration_model_registry")
    rows = _registry_rows_by_id(payload, "migration_models", "migration_model_id")
    if rows:
        return rows
    return _source_registry_rows(
        registry_rel="data/registries/migration_model_registry.json",
        entry_key="migration_models",
        id_key="migration_model_id",
    )


def _parameter_bundle_rows(policy_context: dict | None) -> Dict[str, dict]:
    if isinstance(policy_context, dict):
        payload = policy_context.get("parameter_bundle_registry")
        if isinstance(payload, dict):
            rows = _registry_rows_by_id(payload, "bundles", "parameter_bundle_id")
            if rows:
                return rows
        rows = policy_context.get("parameter_bundles")
        if isinstance(rows, list):
            out: Dict[str, dict] = {}
            for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("parameter_bundle_id", ""))):
                token = str(row.get("parameter_bundle_id", "")).strip()
                if token:
                    out[token] = dict(row)
            if out:
                return out
    abs_path = os.path.join(REPO_ROOT_HINT, "data", "registries", "parameter_bundles.json")
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    record = payload.get("record")
    if not isinstance(record, dict):
        return {}
    rows = record.get("bundles")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("parameter_bundle_id", ""))):
        token = str(row.get("parameter_bundle_id", "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _active_parameter_bundle(policy_context: dict | None) -> dict:
    if not isinstance(policy_context, dict):
        return {}
    bundle_id = str(policy_context.get("parameter_bundle_id", "")).strip()
    if not bundle_id:
        return {}
    rows = _parameter_bundle_rows(policy_context)
    return dict(rows.get(bundle_id) or {})


def _cohort_policy_id(cohort_row: dict, fallback: str = "") -> str:
    token = str(cohort_row.get("mapping_policy_id", "")).strip()
    if token:
        return token
    extensions = dict(cohort_row.get("extensions") or {}) if isinstance(cohort_row.get("extensions"), dict) else {}
    token = str(extensions.get("mapping_policy_id", "")).strip()
    if token:
        return token
    return str(fallback).strip()


def _deterministic_cohort_id(faction_id: object, location_ref: object, created_tick: int, size_bucket: int) -> str:
    digest = canonical_sha256(
        {
            "faction_id": str(faction_id or "").strip(),
            "location_ref": str(location_ref or "").strip(),
            "created_tick": int(created_tick),
            "size_bucket": int(size_bucket),
        }
    )
    return "cohort.{}".format(digest[:16])


def _cohort_seed_material(
    cohort_id: str,
    tick: int,
    policy_context: dict | None,
    mapping_policy_id: str,
    interest_region_id: str,
) -> str:
    pack_lock_hash = ""
    if isinstance(policy_context, dict):
        pack_lock_hash = str(policy_context.get("pack_lock_hash", "")).strip()
    digest = canonical_sha256(
        {
            "cohort_id": str(cohort_id).strip(),
            "tick": int(tick),
            "pack_lock_hash": pack_lock_hash,
            "mapping_policy_id": str(mapping_policy_id).strip(),
            "interest_region_id": str(interest_region_id).strip(),
        }
    )
    return "seed.cohort.{}".format(digest[:24])


def _deterministic_location_distance_mm(source_ref: str, destination_ref: str) -> int:
    source_token = str(source_ref).strip()
    destination_token = str(destination_ref).strip()
    if not source_token or not destination_token or source_token == destination_token:
        return 0
    digest = canonical_sha256({"source": source_token, "destination": destination_token})
    return 1 + (int(digest[:8], 16) % 100000)


def _migration_distance_bands(migration_model: dict) -> List[dict]:
    extensions = dict(migration_model.get("extensions") or {}) if isinstance(migration_model.get("extensions"), dict) else {}
    rows = extensions.get("distance_bands_mm")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        max_distance_mm = max(0, _as_int(row.get("max_distance_mm", 0), 0))
        travel_ticks = max(0, _as_int(row.get("travel_ticks", 0), 0))
        normalized.append(
            {
                "max_distance_mm": int(max_distance_mm),
                "travel_ticks": int(travel_ticks),
            }
        )
    return sorted(normalized, key=lambda item: (int(item.get("max_distance_mm", 0)), int(item.get("travel_ticks", 0))))


def _migration_travel_ticks(
    migration_model: dict,
    source_ref: str,
    destination_ref: str,
    delay_multiplier: float,
) -> int:
    if str(source_ref).strip() == str(destination_ref).strip():
        return 0
    travel_time_policy_id = str(migration_model.get("travel_time_policy_id", "")).strip()
    extensions = dict(migration_model.get("extensions") or {}) if isinstance(migration_model.get("extensions"), dict) else {}
    if bool(extensions.get("instant", False)) or travel_time_policy_id == "travel.instant":
        return 0
    distance_mm = _deterministic_location_distance_mm(source_ref=source_ref, destination_ref=destination_ref)
    bands = _migration_distance_bands(migration_model)
    base_ticks = 0
    for row in bands:
        if distance_mm <= int(row.get("max_distance_mm", 0)):
            base_ticks = int(row.get("travel_ticks", 0))
            break
    if not bands:
        base_ticks = 0
    elif base_ticks <= 0:
        base_ticks = int(bands[-1].get("travel_ticks", 0))
    multiplier = max(0.0, float(delay_multiplier))
    return max(0, int(math.floor(float(base_ticks) * multiplier)))


def _apply_pending_cohort_arrivals(cohort_rows: List[dict], current_tick: int) -> List[str]:
    arrived: List[str] = []
    for cohort_row in sorted((item for item in cohort_rows if isinstance(item, dict)), key=lambda item: str(item.get("cohort_id", ""))):
        extensions = dict(cohort_row.get("extensions") or {}) if isinstance(cohort_row.get("extensions"), dict) else {}
        migration = dict(extensions.get("migration") or {}) if isinstance(extensions.get("migration"), dict) else {}
        pending_destination = str(migration.get("pending_destination", "")).strip()
        in_transit_until_tick = max(0, _as_int(migration.get("in_transit_until_tick", 0), 0))
        if not pending_destination or int(current_tick) < int(in_transit_until_tick):
            continue
        cohort_row["location_ref"] = pending_destination
        migration["in_transit"] = False
        migration["pending_destination"] = ""
        migration["in_transit_until_tick"] = 0
        migration["last_completed_destination"] = pending_destination
        migration["arrived_tick"] = int(current_tick)
        extensions["migration"] = migration
        cohort_row["extensions"] = extensions
        arrived.append(str(cohort_row.get("cohort_id", "")).strip())
    return sorted(set(token for token in arrived if token))


def _cohort_relocate_internal(
    *,
    cohort_row: dict,
    destination: str,
    migration_model_id: str,
    migration_model_rows: Dict[str, dict],
    current_tick: int,
    migration_delay_multiplier: float,
) -> Dict[str, object]:
    model = dict(migration_model_rows.get(str(migration_model_id).strip()) or {})
    if not model:
        return refusal(
            "refusal.civ.migration_model_missing",
            "migration_model_id '{}' is not registered".format(str(migration_model_id).strip()),
            "Use migration_model_id from migration_model_registry.",
            {"migration_model_id": str(migration_model_id).strip()},
            "$.intent.inputs.migration_model_id",
        )
    source_ref = str(cohort_row.get("location_ref", "")).strip()
    destination_ref = str(destination).strip()
    travel_ticks = _migration_travel_ticks(
        migration_model=model,
        source_ref=source_ref,
        destination_ref=destination_ref,
        delay_multiplier=float(migration_delay_multiplier),
    )
    extensions = dict(cohort_row.get("extensions") or {}) if isinstance(cohort_row.get("extensions"), dict) else {}
    migration = dict(extensions.get("migration") or {}) if isinstance(extensions.get("migration"), dict) else {}
    migration["migration_model_id"] = str(migration_model_id).strip()
    migration["source_location_ref"] = source_ref
    migration["requested_destination"] = destination_ref
    migration["requested_tick"] = int(current_tick)
    migration["travel_ticks"] = int(travel_ticks)
    if int(travel_ticks) <= 0:
        cohort_row["location_ref"] = destination_ref
        migration["in_transit"] = False
        migration["pending_destination"] = ""
        migration["in_transit_until_tick"] = 0
        migration["last_completed_destination"] = destination_ref
        migration["arrived_tick"] = int(current_tick)
    else:
        migration["in_transit"] = True
        migration["pending_destination"] = destination_ref
        migration["in_transit_until_tick"] = int(current_tick) + int(travel_ticks)
        migration["arrived_tick"] = 0
    extensions["migration"] = migration
    extensions["last_relocate_tick"] = int(current_tick)
    extensions["last_relocate_destination"] = destination_ref
    extensions["last_relocate_model_id"] = str(migration_model_id).strip()
    cohort_row["extensions"] = extensions
    return {
        "result": "complete",
        "migration_model_id": str(migration_model_id).strip(),
        "travel_ticks": int(travel_ticks),
        "arrival_tick": int(current_tick) + int(travel_ticks),
        "in_transit": bool(int(travel_ticks) > 0),
        "source_location_ref": source_ref,
        "destination": destination_ref,
    }


def _deterministic_faction_id(founder_agent_id: object, created_tick: int) -> str:
    digest = canonical_sha256(
        {
            "founder_agent_id": str(founder_agent_id or "").strip(),
            "created_tick": int(created_tick),
        }
    )
    return "faction.{}".format(digest[:16])


def _order_sort_key(order_row: dict) -> Tuple[int, int, str]:
    return (
        -max(0, _as_int(order_row.get("priority", 0), 0)),
        max(0, _as_int(order_row.get("created_tick", 0), 0)),
        str(order_row.get("order_id", "")),
    )


def _effective_civ_entitlements(
    state: dict,
    authority_context: dict,
    *,
    subject_id: str = "",
) -> List[str]:
    entitlements = set(_sorted_tokens(list(authority_context.get("entitlements") or [])))
    subject_token = str(subject_id).strip() or _author_subject_id(authority_context)
    role_rows = _ensure_role_assignment_assemblies(state)
    for row in role_rows:
        if str(row.get("subject_id", "")).strip() != subject_token:
            continue
        for entitlement_id in _sorted_tokens(list(row.get("granted_entitlements") or [])):
            entitlements.add(str(entitlement_id))
    return sorted(entitlements)


def _order_queue_owner(state: dict, target_kind: str, target_id: str, inputs: dict) -> Tuple[str, str]:
    kind = str(target_kind).strip()
    token = str(target_id).strip()
    if kind == "faction" and token:
        return "faction", token
    if kind == "cohort" and token:
        return "cohort", token
    if kind == "agent" and token:
        agent = _find_agent(_ensure_agent_states(state), token)
        if isinstance(agent, dict) and agent:
            parent_cohort_id = str(agent.get("parent_cohort_id", "")).strip()
            if parent_cohort_id:
                return "cohort", parent_cohort_id
            controller_id = str(agent.get("controller_id", "")).strip()
            if controller_id:
                return "controller", controller_id
    controller_id = str((inputs or {}).get("controller_id", "")).strip()
    if controller_id:
        return "controller", controller_id
    return "global", "global"


def _order_target_shards(state: dict, target_kind: str, target_id: str, shard_map: dict) -> List[str]:
    kind = str(target_kind).strip()
    token = str(target_id).strip()
    if not token:
        return []
    if kind == "cohort":
        row = _find_cohort(_ensure_cohort_assemblies(state), token)
        if isinstance(row, dict) and row:
            return _sorted_tokens([_cohort_owner_shard_id(row, shard_map)])
        return []
    if kind == "agent":
        row = _find_agent(_ensure_agent_states(state), token)
        if isinstance(row, dict) and row:
            shard_id = str(row.get("shard_id", "")).strip() or _owner_shard_for_object(shard_map, token)
            return _sorted_tokens([shard_id]) if shard_id else []
        return []
    if kind == "territory":
        shard_id = _owner_shard_for_object(shard_map, token)
        return _sorted_tokens([shard_id]) if shard_id else []
    if kind == "faction":
        cohort_rows = _ensure_cohort_assemblies(state)
        out: List[str] = []
        for row in cohort_rows:
            if str(row.get("faction_id", "")).strip() != token:
                continue
            owner = _cohort_owner_shard_id(row, shard_map)
            if owner:
                out.append(owner)
        return _sorted_tokens(out)
    return []


def _upsert_order_queue(queue_rows: List[dict], owner_kind: str, owner_id: str, current_tick: int) -> dict:
    queue_id = _queue_id_for_owner(owner_kind, owner_id)
    row = _find_order_queue(queue_rows=queue_rows, queue_id=queue_id)
    if row:
        row["owner_kind"] = str(owner_kind).strip() or "global"
        row["owner_id"] = str(owner_id).strip() or "global"
        row["last_update_tick"] = int(current_tick)
        if not isinstance(row.get("extensions"), dict):
            row["extensions"] = {}
        return row
    row = {
        "queue_id": queue_id,
        "owner_kind": str(owner_kind).strip() or "global",
        "owner_id": str(owner_id).strip() or "global",
        "order_ids": [],
        "last_update_tick": int(current_tick),
        "extensions": {},
    }
    queue_rows.append(row)
    return row


def _refresh_queue_order_ids(queue_row: dict, order_rows: List[dict]) -> None:
    order_map = {}
    for row in order_rows:
        order_id = str((row or {}).get("order_id", "")).strip()
        if order_id:
            order_map[order_id] = row
    active_status = {"created", "queued", "executing"}
    queued_ids = []
    for order_id in _ordered_unique_tokens(list((queue_row or {}).get("order_ids") or [])):
        row = order_map.get(order_id)
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).strip() not in active_status:
            continue
        queued_ids.append(order_id)
    queue_row["order_ids"] = sorted(
        set(queued_ids),
        key=lambda order_id: _order_sort_key(dict(order_map.get(order_id) or {"order_id": order_id})),
    )


def _remove_order_from_all_queues(queue_rows: List[dict], order_id: str) -> None:
    token = str(order_id).strip()
    if not token:
        return
    for row in queue_rows:
        if not isinstance(row, dict):
            continue
        row["order_ids"] = [entry for entry in _ordered_unique_tokens(list(row.get("order_ids") or [])) if entry != token]


def _run_order_tick(
    *,
    state: dict,
    order_rows: List[dict],
    queue_rows: List[dict],
    cohorts: List[dict],
    agents: List[dict],
    current_tick: int,
    authority_context: dict,
    policy_context: dict | None,
    max_orders_override: int | None = None,
) -> Dict[str, object]:
    budget = max(
        1,
        _as_int(
            max_orders_override if max_orders_override is not None else (policy_context or {}).get("order_tick_budget", 8),
            8,
        ),
    )
    order_type_map = _order_type_rows(policy_context)
    shard_map = dict((policy_context or {}).get("shard_map") or {})
    active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
    affiliations = _ensure_affiliations(state)
    faction_rows = _ensure_faction_assemblies(state)
    migration_model_map = _migration_model_rows(policy_context)
    bundle_params = dict((_active_parameter_bundle(policy_context).get("parameters") or {}))
    migration_delay_multiplier = max(
        0.0,
        _as_float(bundle_params.get("civ.migration.delay_multiplier", 1.0), 1.0),
    )

    processed_ids: List[str] = []
    completed_ids: List[str] = []
    failed_ids: List[str] = []

    def _fail(order_row: dict, code: str, reason: str, extra: dict | None = None) -> None:
        order_id = str(order_row.get("order_id", "")).strip()
        order_row["status"] = "failed"
        payload = {"code": str(code), "reason": str(reason)}
        if isinstance(extra, dict) and extra:
            payload.update(dict(extra))
        order_row["refusal"] = payload
        order_row["last_update_tick"] = int(current_tick)
        failed_ids.append(order_id)
        _remove_order_from_all_queues(queue_rows=queue_rows, order_id=order_id)

    for queue_row in queue_rows:
        _refresh_queue_order_ids(queue_row=queue_row, order_rows=order_rows)

    queued = [
        row
        for row in sorted((item for item in order_rows if isinstance(item, dict)), key=_order_sort_key)
        if str(row.get("status", "")).strip() in {"created", "queued", "executing"}
    ]
    for order_row in queued:
        if len(processed_ids) >= int(budget):
            break
        order_id = str(order_row.get("order_id", "")).strip()
        if not order_id:
            continue
        processed_ids.append(order_id)
        order_row["status"] = "executing"
        order_row["last_update_tick"] = int(current_tick)
        order_type_id = str(order_row.get("order_type_id", "")).strip()
        target_kind = str(order_row.get("target_kind", "")).strip()
        target_id = str(order_row.get("target_id", "")).strip()
        payload = dict(order_row.get("payload") or {}) if isinstance(order_row.get("payload"), dict) else {}
        order_type_row = dict(order_type_map.get(order_type_id) or {})
        if not order_type_row:
            _fail(order_row, "PROCESS_INPUT_INVALID", "order_type_not_registered", {"order_type_id": order_type_id})
            continue

        target_shards = _order_target_shards(state=state, target_kind=target_kind, target_id=target_id, shard_map=shard_map)
        if active_shard_id and target_shards:
            if len(target_shards) > 1 or active_shard_id not in set(target_shards):
                _fail(
                    order_row,
                    "refusal.civ.order_cross_shard_not_supported",
                    "target_shard_span_unsupported",
                    {"active_shard_id": active_shard_id, "target_shards": list(target_shards)},
                )
                continue

        if order_type_id in ("order.move", "order.migrate"):
            destination = str(payload.get("destination", "") or payload.get("site_id", "") or payload.get("region_id", "")).strip()
            if not destination:
                _fail(order_row, "PROCESS_INPUT_INVALID", "destination_missing")
                continue
            if target_kind == "cohort":
                cohort_row = _find_cohort(cohort_rows=cohorts, cohort_id=target_id)
                if not cohort_row:
                    _fail(order_row, "refusal.control.target_invalid", "cohort_missing", {"target_id": target_id})
                    continue
                if order_type_id == "order.migrate":
                    migration_model_id = str(payload.get("migration_model_id", "")).strip() or "demo.migration.instant"
                    relocate_result = _cohort_relocate_internal(
                        cohort_row=cohort_row,
                        destination=destination,
                        migration_model_id=migration_model_id,
                        migration_model_rows=migration_model_map,
                        current_tick=int(current_tick),
                        migration_delay_multiplier=float(migration_delay_multiplier),
                    )
                    if str(relocate_result.get("result", "")) != "complete":
                        refusal_payload = dict(relocate_result.get("refusal") or {})
                        _fail(
                            order_row,
                            str(refusal_payload.get("reason_code", "refusal.civ.migration_model_missing")),
                            str(refusal_payload.get("reason", "migration_model_missing")),
                            {"migration_model_id": migration_model_id},
                        )
                        continue
                else:
                    cohort_row["location_ref"] = destination
            elif target_kind == "faction":
                moved = 0
                migration_failed = False
                for cohort_row in sorted(cohorts, key=lambda item: str(item.get("cohort_id", ""))):
                    if str(cohort_row.get("faction_id", "")).strip() != target_id:
                        continue
                    if order_type_id == "order.migrate":
                        migration_model_id = str(payload.get("migration_model_id", "")).strip() or "demo.migration.instant"
                        relocate_result = _cohort_relocate_internal(
                            cohort_row=cohort_row,
                            destination=destination,
                            migration_model_id=migration_model_id,
                            migration_model_rows=migration_model_map,
                            current_tick=int(current_tick),
                            migration_delay_multiplier=float(migration_delay_multiplier),
                        )
                        if str(relocate_result.get("result", "")) != "complete":
                            refusal_payload = dict(relocate_result.get("refusal") or {})
                            _fail(
                                order_row,
                                str(refusal_payload.get("reason_code", "refusal.civ.migration_model_missing")),
                                str(refusal_payload.get("reason", "migration_model_missing")),
                                {"migration_model_id": migration_model_id},
                            )
                            migration_failed = True
                            break
                    else:
                        cohort_row["location_ref"] = destination
                    moved += 1
                if migration_failed:
                    continue
                if moved <= 0:
                    _fail(order_row, "refusal.control.target_invalid", "faction_has_no_cohorts", {"target_id": target_id})
                    continue
            else:
                _fail(
                    order_row,
                    "refusal.civ.order_requires_pathing_not_supported",
                    "micro_pathing_not_implemented",
                    {"target_kind": target_kind},
                )
                continue
            order_row["status"] = "completed"
            order_row["last_update_tick"] = int(current_tick)
            completed_ids.append(order_id)
            _remove_order_from_all_queues(queue_rows=queue_rows, order_id=order_id)
            continue

        if order_type_id == "order.assimilate":
            issuer_subject_id = str(order_row.get("issuer_subject_id", "")).strip()
            effective_entitlements = set(
                _effective_civ_entitlements(
                    state=state,
                    authority_context=authority_context,
                    subject_id=issuer_subject_id,
                )
            )
            if "entitlement.civ.assimilate" not in effective_entitlements:
                _fail(order_row, "refusal.civ.entitlement_missing", "entitlement.civ.assimilate required")
                continue
            faction_id = str(payload.get("target_faction_id", "")).strip()
            if faction_id and not _find_faction(faction_rows=faction_rows, faction_id=faction_id):
                _fail(order_row, "refusal.civ.claim_forbidden", "target_faction_missing", {"target_faction_id": faction_id})
                continue
            if target_kind == "cohort":
                cohort_row = _find_cohort(cohort_rows=cohorts, cohort_id=target_id)
                if not cohort_row:
                    _fail(order_row, "refusal.control.target_invalid", "cohort_missing")
                    continue
                cohort_row["faction_id"] = faction_id or None
                _apply_affiliation_change(
                    affiliation_rows=affiliations,
                    subject_id=target_id,
                    faction_id=faction_id or None,
                    current_tick=int(current_tick),
                )
            elif target_kind == "agent":
                if not _find_agent(agent_rows=agents, agent_id=target_id):
                    _fail(order_row, "refusal.control.target_invalid", "agent_missing")
                    continue
                _apply_affiliation_change(
                    affiliation_rows=affiliations,
                    subject_id=target_id,
                    faction_id=faction_id or None,
                    current_tick=int(current_tick),
                )
            order_row["status"] = "completed"
            order_row["last_update_tick"] = int(current_tick)
            completed_ids.append(order_id)
            _remove_order_from_all_queues(queue_rows=queue_rows, order_id=order_id)
            continue

        if order_type_id == "order.communicate":
            text = str(payload.get("text", "") or payload.get("message", "") or payload.get("notes", "")).strip()
            if not text:
                _fail(order_row, "PROCESS_INPUT_INVALID", "message_text_missing")
                continue
            recipient_subject_id = str(payload.get("to", "") or target_id).strip()
            message_payload = {"to": recipient_subject_id, "text": text}
            message_id = "msg.radio.{}".format(
                canonical_sha256(
                    {
                        "order_id": order_id,
                        "created_tick": int(current_tick),
                        "payload": message_payload,
                    }
                )[:16]
            )
            extensions = dict(order_row.get("extensions") or {}) if isinstance(order_row.get("extensions"), dict) else {}
            extensions["message_artifact"] = {
                "message_id": message_id,
                "author_subject_id": str(order_row.get("issuer_subject_id", "")),
                "created_tick": int(current_tick),
                "channel_id": "msg.radio",
                "payload": message_payload,
            }
            order_row["extensions"] = extensions
            order_row["status"] = "completed"
            order_row["last_update_tick"] = int(current_tick)
            completed_ids.append(order_id)
            _remove_order_from_all_queues(queue_rows=queue_rows, order_id=order_id)
            continue

        if order_type_id == "order.build_plan":
            blueprint_id = str(payload.get("blueprint_id", "")).strip()
            site_id = str(payload.get("site_id", "")).strip()
            plan_id = "plan.{}".format(
                canonical_sha256(
                    {
                        "order_id": order_id,
                        "target_id": target_id,
                        "blueprint_id": blueprint_id,
                        "site_id": site_id,
                        "created_tick": int(current_tick),
                    }
                )[:16]
            )
            extensions = dict(order_row.get("extensions") or {}) if isinstance(order_row.get("extensions"), dict) else {}
            extensions["plan_artifact"] = {
                "plan_id": plan_id,
                "order_id": order_id,
                "target_id": target_id,
                "blueprint_id": blueprint_id,
                "site_id": site_id,
                "notes": str(payload.get("notes", "")),
                "created_tick": int(current_tick),
                "status": "planned",
            }
            order_row["extensions"] = extensions
            order_row["status"] = "completed"
            order_row["last_update_tick"] = int(current_tick)
            completed_ids.append(order_id)
            _remove_order_from_all_queues(queue_rows=queue_rows, order_id=order_id)
            continue

        _fail(
            order_row,
            "refusal.civ.order_requires_pathing_not_supported",
            "order_executor_stub_missing",
            {"order_type_id": order_type_id},
        )

    for queue_row in queue_rows:
        _refresh_queue_order_ids(queue_row=queue_row, order_rows=order_rows)
    return {
        "processed_order_ids": list(processed_ids),
        "completed_order_ids": list(completed_ids),
        "failed_order_ids": list(failed_ids),
    }


def _persist_civ_state(
    state: dict,
    faction_rows: List[dict],
    affiliation_rows: List[dict],
    territory_rows: List[dict],
    diplomatic_rows: List[dict],
    cohort_rows: List[dict] | None = None,
    order_rows: List[dict] | None = None,
    queue_rows: List[dict] | None = None,
    institution_rows: List[dict] | None = None,
    role_assignment_rows: List[dict] | None = None,
) -> None:
    state["faction_assemblies"] = [dict(row) for row in list(faction_rows or []) if isinstance(row, dict)]
    state["affiliations"] = [dict(row) for row in list(affiliation_rows or []) if isinstance(row, dict)]
    state["territory_assemblies"] = [dict(row) for row in list(territory_rows or []) if isinstance(row, dict)]
    state["diplomatic_relations"] = [dict(row) for row in list(diplomatic_rows or []) if isinstance(row, dict)]
    if cohort_rows is not None:
        state["cohort_assemblies"] = [dict(row) for row in list(cohort_rows or []) if isinstance(row, dict)]
    if order_rows is not None:
        state["order_assemblies"] = [dict(row) for row in list(order_rows or []) if isinstance(row, dict)]
    if queue_rows is not None:
        state["order_queue_assemblies"] = [dict(row) for row in list(queue_rows or []) if isinstance(row, dict)]
    if institution_rows is not None:
        state["institution_assemblies"] = [dict(row) for row in list(institution_rows or []) if isinstance(row, dict)]
    if role_assignment_rows is not None:
        state["role_assignment_assemblies"] = [
            dict(row) for row in list(role_assignment_rows or []) if isinstance(row, dict)
        ]
    _ensure_faction_assemblies(state)
    _ensure_affiliations(state)
    _ensure_territory_assemblies(state)
    _ensure_diplomatic_relations(state)
    _ensure_cohort_assemblies(state)
    _ensure_order_assemblies(state)
    _ensure_order_queue_assemblies(state)
    _ensure_institution_assemblies(state)
    _ensure_role_assignment_assemblies(state)


def _subject_exists(state: dict, subject_id: str) -> bool:
    token = str(subject_id).strip()
    if not token:
        return False
    if _find_agent(agent_rows=_ensure_agent_states(state), agent_id=token):
        return True
    if _find_cohort(cohort_rows=_ensure_cohort_assemblies(state), cohort_id=token):
        return True
    return False


def _require_faction_owner_authority(faction_row: dict, authority_context: dict) -> Dict[str, object]:
    owner_peer_id = _faction_owner_peer_id(faction_row)
    if not owner_peer_id:
        return {"result": "complete"}
    if _civ_admin_override(authority_context):
        return {"result": "complete"}
    caller_peer_id = _authority_peer_token(authority_context)
    if caller_peer_id and caller_peer_id == owner_peer_id:
        return {"result": "complete"}
    return refusal(
        "refusal.civ.ownership_violation",
        "caller peer '{}' cannot mutate faction owned by '{}'".format(caller_peer_id or "<unknown>", owner_peer_id),
        "Use authority context owned by faction owner or grant admin override entitlement.",
        {
            "owner_peer_id": owner_peer_id,
            "caller_peer_id": caller_peer_id or "<unknown>",
            "faction_id": str(faction_row.get("faction_id", "")),
        },
        "$.authority_context.peer_id",
    )


def _add_faction_territory(faction_row: dict, territory_id: str) -> None:
    rows = _sorted_tokens(list(faction_row.get("territory_ids") or []))
    token = str(territory_id).strip()
    if token and token not in rows:
        rows.append(token)
    faction_row["territory_ids"] = _sorted_tokens(rows)


def _drop_faction_territory(faction_row: dict, territory_id: str) -> None:
    token = str(territory_id).strip()
    if not token:
        return
    rows = [str(item).strip() for item in (faction_row.get("territory_ids") or []) if str(item).strip() and str(item).strip() != token]
    faction_row["territory_ids"] = _sorted_tokens(rows)


def _ensure_body_assemblies(state: dict) -> List[dict]:
    rows = state.get("body_assemblies")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
        assembly_id = str(row.get("assembly_id", "")).strip()
        if not assembly_id:
            continue
        shape_type = str(row.get("shape_type", "capsule")).strip() or "capsule"
        if shape_type not in ("capsule", "aabb", "convex_hull"):
            shape_type = "capsule"
        params_raw = row.get("shape_parameters")
        if not isinstance(params_raw, dict):
            params_raw = row.get("parameters")
        params = dict(params_raw) if isinstance(params_raw, dict) else {}
        half_extents = _vector3_int(params.get("half_extents_mm"), "half_extents_mm") or {"x": 0, "y": 0, "z": 0}
        position = _vector3_int(row.get("transform_mm"), "transform_mm")
        if position is None:
            position = _vector3_int(row.get("position_mm"), "position_mm")
        velocity = _vector3_int(row.get("velocity_mm_per_tick"), "velocity_mm_per_tick") or {"x": 0, "y": 0, "z": 0}
        orientation = _angles_int(row.get("orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
        normalized.append(
            {
                "assembly_id": assembly_id,
                "owner_assembly_id": str(row.get("owner_assembly_id", "")).strip() or assembly_id,
                "owner_agent_id": row.get("owner_agent_id")
                if row.get("owner_agent_id") is None
                else str(row.get("owner_agent_id", "")).strip(),
                "shard_id": str(row.get("shard_id", "")).strip() or "shard.0",
                "shape_type": shape_type,
                "shape_parameters": {
                    "radius_mm": max(0, _as_int(params.get("radius_mm", 0), 0)),
                    "height_mm": max(0, _as_int(params.get("height_mm", 0), 0)),
                    "half_extents_mm": {
                        "x": max(0, _as_int(half_extents.get("x", 0), 0)),
                        "y": max(0, _as_int(half_extents.get("y", 0), 0)),
                        "z": max(0, _as_int(half_extents.get("z", 0), 0)),
                    },
                    "vertex_ref_id": str(params.get("vertex_ref_id", "")).strip(),
                },
                "collision_layer": str(row.get("collision_layer", "layer.default")).strip() or "layer.default",
                "dynamic": bool(row.get("dynamic", False)),
                "ghost": bool(row.get("ghost", False)),
                "transform_mm": {
                    "x": _as_int((position or {}).get("x", 0), 0),
                    "y": _as_int((position or {}).get("y", 0), 0),
                    "z": _as_int((position or {}).get("z", 0), 0),
                },
                "orientation_mdeg": {
                    "yaw": _as_int((orientation or {}).get("yaw", 0), 0),
                    "pitch": _as_int((orientation or {}).get("pitch", 0), 0),
                    "roll": _as_int((orientation or {}).get("roll", 0), 0),
                },
                "velocity_mm_per_tick": {
                    "x": _as_int((velocity or {}).get("x", 0), 0),
                    "y": _as_int((velocity or {}).get("y", 0), 0),
                    "z": _as_int((velocity or {}).get("z", 0), 0),
                },
            }
        )
    state["body_assemblies"] = normalized
    return normalized


def _ensure_collision_state(state: dict) -> dict:
    payload = state.get("collision_state")
    if not isinstance(payload, dict):
        payload = {}
    payload = {
        "last_tick_resolved_pairs": _sorted_tokens(list(payload.get("last_tick_resolved_pairs") or [])),
        "last_tick_unresolved_pairs": _sorted_tokens(list(payload.get("last_tick_unresolved_pairs") or [])),
        "last_tick_pair_count": max(0, _as_int(payload.get("last_tick_pair_count", 0), 0)),
        "last_tick_anchor": str(payload.get("last_tick_anchor", "")),
    }
    state["collision_state"] = payload
    return payload


def _find_body(body_rows: List[dict], body_id: str) -> dict:
    token = str(body_id).strip()
    for row in body_rows:
        if str(row.get("assembly_id", "")).strip() == token:
            return row
    return {}


def _find_agent(agent_rows: List[dict], agent_id: str) -> dict:
    token = str(agent_id).strip()
    for row in agent_rows:
        if str(row.get("agent_id", "")).strip() == token:
            return row
    return {}


def _active_possession_binding(bindings: List[dict], agent_id: str) -> dict:
    token = str(agent_id).strip()
    for row in sorted((item for item in bindings if isinstance(item, dict)), key=lambda item: str(item.get("binding_id", ""))):
        if str(row.get("binding_type", "")).strip() != "possess":
            continue
        if not bool(row.get("active", True)):
            continue
        if str(row.get("target_id", "")).strip() != token:
            continue
        return row
    return {}


def _agent_body_id(agent_row: dict, body_rows: List[dict], agent_id: str) -> str:
    token = str((agent_row or {}).get("body_id", "")).strip()
    if token:
        return token
    agent_token = str(agent_id).strip()
    for row in sorted((item for item in body_rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
        owner_agent = str(row.get("owner_agent_id", "")).strip()
        owner_assembly = str(row.get("owner_assembly_id", "")).strip()
        if owner_agent == agent_token or owner_assembly == agent_token:
            body_id = str(row.get("assembly_id", "")).strip()
            if body_id:
                return body_id
    return ""


def _movement_world_delta(local_delta: dict, yaw_mdeg: int) -> Dict[str, int]:
    local = _vector3_int(local_delta, "move_vector_local") or {"x": 0, "y": 0, "z": 0}
    yaw_norm = int(yaw_mdeg) % 360000
    quadrant = int((yaw_norm + 45000) // 90000) % 4
    x = int(local["x"])
    y = int(local["y"])
    z = int(local["z"])
    if quadrant == 0:
        return {"x": x, "y": y, "z": z}
    if quadrant == 1:
        return {"x": -y, "y": x, "z": z}
    if quadrant == 2:
        return {"x": -x, "y": -y, "z": z}
    return {"x": y, "y": -x, "z": z}


def _movement_context(
    agents: List[dict],
    controllers: List[dict],
    bindings: List[dict],
    agent_id: str,
    inputs: dict,
    authority_context: dict,
) -> Dict[str, object]:
    agent = _find_agent(agent_rows=agents, agent_id=agent_id)
    if not agent:
        return refusal(
            "refusal.control.target_invalid",
            "agent '{}' does not exist".format(str(agent_id)),
            "Use an agent_id present in universe_state.agent_states.",
            {"agent_id": str(agent_id)},
            "$.intent.inputs.agent_id",
        )
    entitlements = _sorted_tokens(list(authority_context.get("entitlements") or []))
    admin_override = "entitlement.control.admin" in set(entitlements)
    controller_id = str(inputs.get("controller_id", "")).strip()
    if not controller_id:
        controller_id = str(agent.get("controller_id", "")).strip()
    if not controller_id:
        bound = _active_possession_binding(bindings=bindings, agent_id=agent_id)
        controller_id = str(bound.get("controller_id", "")).strip()
    controller = _find_controller(controllers=controllers, controller_id=controller_id) if controller_id else {}
    if controller_id and not controller and not admin_override:
        return refusal(
            "refusal.agent.ownership_violation",
            "controller '{}' was not found for movement request".format(controller_id),
            "Bind a valid controller before issuing movement or rotate intents.",
            {"agent_id": str(agent_id), "controller_id": controller_id},
            "$.intent.inputs.controller_id",
        )
    if not controller_id and not admin_override:
        return refusal(
            "refusal.agent.ownership_violation",
            "movement requires active possession binding or controller_id",
            "Possess the agent first or issue movement with entitlement.control.admin.",
            {"agent_id": str(agent_id)},
            "$.intent.inputs",
        )

    claimed_owner = str(inputs.get("owner_peer_id", "")).strip()
    controller_owner = str((controller or {}).get("owner_peer_id", "")).strip()
    agent_owner = str(agent.get("owner_peer_id", "")).strip()
    if not agent_owner and controller_owner:
        agent_owner = controller_owner
    if not admin_override:
        if controller_owner and agent_owner and controller_owner != agent_owner:
            return refusal(
                "refusal.agent.ownership_violation",
                "controller owner and agent owner mismatch for movement request",
                "Keep controller.owner_peer_id and agent.owner_peer_id aligned or use admin override.",
                {
                    "agent_id": str(agent_id),
                    "controller_id": controller_id,
                    "agent_owner_peer_id": agent_owner,
                    "controller_owner_peer_id": controller_owner,
                },
                "$.intent.inputs.agent_id",
            )
        if claimed_owner and agent_owner and claimed_owner != agent_owner:
            return refusal(
                "refusal.agent.ownership_violation",
                "claimed owner_peer_id does not match agent owner",
                "Send owner_peer_id matching agent.owner_peer_id or remove owner_peer_id claim.",
                {"agent_id": str(agent_id), "owner_peer_id": claimed_owner, "agent_owner_peer_id": agent_owner},
                "$.intent.inputs.owner_peer_id",
            )
    return {
        "result": "complete",
        "agent": agent,
        "controller": controller,
        "controller_id": controller_id,
        "owner_peer_id": claimed_owner or agent_owner or controller_owner,
        "admin_override": bool(admin_override),
    }


def _refresh_agent_state_hash(agent_row: dict, body_row: dict | None) -> None:
    body = dict(body_row or {})
    payload = {
        "agent_id": str(agent_row.get("agent_id", "")).strip(),
        "body_id": str(agent_row.get("body_id", "")).strip(),
        "owner_peer_id": str(agent_row.get("owner_peer_id", "")).strip(),
        "controller_id": str(agent_row.get("controller_id", "")).strip(),
        "shard_id": str(agent_row.get("shard_id", "")).strip(),
        "orientation_mdeg": dict(agent_row.get("orientation_mdeg") or {"yaw": 0, "pitch": 0, "roll": 0}),
        "body_transform_mm": dict(body.get("transform_mm") or {}),
        "body_orientation_mdeg": dict(body.get("orientation_mdeg") or {}),
    }
    agent_row["state_hash"] = canonical_sha256(payload)


def _shape_half_extents_mm(body_row: dict) -> Dict[str, int]:
    params = dict(body_row.get("shape_parameters") or {})
    shape_type = str(body_row.get("shape_type", "")).strip()
    if shape_type == "aabb":
        half_extents = _vector3_int(params.get("half_extents_mm"), "half_extents_mm") or {"x": 0, "y": 0, "z": 0}
        return {
            "x": max(0, _as_int(half_extents.get("x", 0), 0)),
            "y": max(0, _as_int(half_extents.get("y", 0), 0)),
            "z": max(0, _as_int(half_extents.get("z", 0), 0)),
        }
    radius = max(0, _as_int(params.get("radius_mm", 0), 0))
    height = max(0, _as_int(params.get("height_mm", 0), 0))
    return {
        "x": radius,
        "y": radius,
        "z": max(radius, radius + int(height // 2)),
    }


def _shape_aabb_mm(body_row: dict) -> dict:
    center = _vector3_int(body_row.get("transform_mm"), "transform_mm") or {"x": 0, "y": 0, "z": 0}
    half = _shape_half_extents_mm(body_row)
    return {
        "min_x": int(center["x"]) - int(half["x"]),
        "max_x": int(center["x"]) + int(half["x"]),
        "min_y": int(center["y"]) - int(half["y"]),
        "max_y": int(center["y"]) + int(half["y"]),
        "min_z": int(center["z"]) - int(half["z"]),
        "max_z": int(center["z"]) + int(half["z"]),
    }


def _broadphase_pairs(body_rows: List[dict], cell_size_mm: int = 2000) -> List[Tuple[str, str]]:
    cell_size = max(1, _as_int(cell_size_mm, 2000))
    by_id = {
        str(row.get("assembly_id", "")).strip(): dict(row)
        for row in body_rows
        if isinstance(row, dict) and str(row.get("assembly_id", "")).strip()
    }
    grid: Dict[Tuple[int, int, int], List[str]] = {}
    for body_id in sorted(by_id.keys()):
        row = by_id[body_id]
        aabb = _shape_aabb_mm(row)
        min_cx = int(math.floor(int(aabb["min_x"]) / float(cell_size)))
        max_cx = int(math.floor(int(aabb["max_x"]) / float(cell_size)))
        min_cy = int(math.floor(int(aabb["min_y"]) / float(cell_size)))
        max_cy = int(math.floor(int(aabb["max_y"]) / float(cell_size)))
        min_cz = int(math.floor(int(aabb["min_z"]) / float(cell_size)))
        max_cz = int(math.floor(int(aabb["max_z"]) / float(cell_size)))
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                for cz in range(min_cz, max_cz + 1):
                    key = (int(cx), int(cy), int(cz))
                    grid.setdefault(key, []).append(body_id)

    pair_set = set()
    for cell_key in sorted(grid.keys()):
        cell_ids = _sorted_tokens(list(grid.get(cell_key) or []))
        for left_index, left_id in enumerate(cell_ids):
            for right_id in cell_ids[left_index + 1 :]:
                if left_id == right_id:
                    continue
                pair = tuple(sorted((left_id, right_id)))
                pair_set.add(pair)
    return sorted(list(pair_set), key=lambda item: (str(item[0]), str(item[1])))


def _shape_pair_supported(shape_a: str, shape_b: str) -> bool:
    pair = tuple(sorted((str(shape_a), str(shape_b))))
    return pair in (
        ("aabb", "aabb"),
        ("aabb", "capsule"),
        ("capsule", "capsule"),
    )


def _overlap_mtv_aabb_proxy(body_a: dict, body_b: dict) -> Dict[str, int] | None:
    center_a = _vector3_int(body_a.get("transform_mm"), "transform_mm") or {"x": 0, "y": 0, "z": 0}
    center_b = _vector3_int(body_b.get("transform_mm"), "transform_mm") or {"x": 0, "y": 0, "z": 0}
    half_a = _shape_half_extents_mm(body_a)
    half_b = _shape_half_extents_mm(body_b)
    dx = int(center_b["x"]) - int(center_a["x"])
    dy = int(center_b["y"]) - int(center_a["y"])
    dz = int(center_b["z"]) - int(center_a["z"])
    overlap_x = int(half_a["x"]) + int(half_b["x"]) - abs(int(dx))
    overlap_y = int(half_a["y"]) + int(half_b["y"]) - abs(int(dy))
    overlap_z = int(half_a["z"]) + int(half_b["z"]) - abs(int(dz))
    if overlap_x <= 0 or overlap_y <= 0 or overlap_z <= 0:
        return None
    candidates = [
        ("x", int(overlap_x), int(dx), 0),
        ("y", int(overlap_y), int(dy), 1),
        ("z", int(overlap_z), int(dz), 2),
    ]
    axis, overlap, delta, _ = sorted(candidates, key=lambda row: (int(row[1]), int(row[3])))[0]
    direction = -1 if int(delta) >= 0 else 1
    mtv = {"x": 0, "y": 0, "z": 0}
    mtv[str(axis)] = int(direction) * int(overlap)
    return mtv


def _pair_id(body_id_a: str, body_id_b: str) -> str:
    left = str(body_id_a).strip()
    right = str(body_id_b).strip()
    if left <= right:
        return "{}::{}".format(left, right)
    return "{}::{}".format(right, left)


def _owner_shard_for_object(shard_map: dict, object_id: str) -> str:
    token = str(object_id).strip()
    if not token:
        return ""
    indexed = dict(shard_map.get("object_owner") or {})
    owner = str(indexed.get(token, "")).strip()
    if owner:
        return owner
    rows = shard_map.get("shards")
    if not isinstance(rows, list):
        return ""
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("shard_id", ""))):
        shard_id = str(row.get("shard_id", "")).strip()
        scope = row.get("region_scope")
        if not shard_id or not isinstance(scope, dict):
            continue
        object_ids = _sorted_tokens(list(scope.get("object_ids") or []))
        if token in object_ids:
            return shard_id
    return ""


def _cohort_owner_shard_id(cohort_row: dict, shard_map: dict) -> str:
    token = str((cohort_row or {}).get("location_ref", "")).strip()
    if not token:
        token = str((cohort_row or {}).get("cohort_id", "")).strip()
    return _owner_shard_for_object(shard_map=shard_map, object_id=token) or "shard.0"


def _cohort_micro_agents(agent_rows: List[dict], cohort_id: str) -> List[dict]:
    token = str(cohort_id).strip()
    if not token:
        return []
    out = []
    for row in sorted((item for item in agent_rows if isinstance(item, dict)), key=lambda item: str(item.get("agent_id", ""))):
        if str(row.get("parent_cohort_id", "")).strip() == token:
            out.append(row)
    return out


def _cohort_refinement_state(total_size: int, expanded_count: int) -> str:
    total = max(0, int(total_size))
    expanded = max(0, int(expanded_count))
    if expanded <= 0:
        return "macro"
    if expanded >= total:
        return "micro"
    return "mixed"


def _apply_affiliation_change(
    affiliation_rows: List[dict],
    subject_id: str,
    faction_id: str | None,
    current_tick: int,
) -> dict:
    row = _find_affiliation(affiliation_rows=affiliation_rows, subject_id=subject_id)
    if not row:
        row = {
            "subject_id": str(subject_id).strip(),
            "faction_id": faction_id,
            "joined_tick": int(current_tick),
            "role_id": "role.member",
            "extensions": {},
        }
        affiliation_rows.append(row)
    else:
        row["faction_id"] = faction_id
        row["joined_tick"] = int(current_tick)
        row["role_id"] = str(row.get("role_id", "role.member")).strip() or "role.member"
        if not isinstance(row.get("extensions"), dict):
            row["extensions"] = {}
    return row


def _expand_cohort_to_micro_internal(
    state: dict,
    cohort_row: dict,
    cohort_rows: List[dict],
    affiliation_rows: List[dict],
    interest_region_id: str,
    max_micro_agents: int,
    mapping_policy_id: str,
    policy_context: dict | None,
    current_tick: int,
    deterministic_seed: str,
) -> Dict[str, object]:
    del cohort_rows
    mapping_rows = _cohort_mapping_policy_rows(policy_context)
    mapping_policy = dict(mapping_rows.get(str(mapping_policy_id).strip()) or {})
    spawn_distribution_rules = dict(mapping_policy.get("spawn_distribution_rules") or {})
    anonymous_micro_agents = bool(mapping_policy.get("anonymous_micro_agents", False))
    identity_exposure = str(spawn_distribution_rules.get("identity_exposure", "")).strip()
    if not identity_exposure:
        identity_exposure = "anonymous_unless_entitled" if anonymous_micro_agents else "standard"
    agents = _ensure_agent_states(state)
    cohort_id = str(cohort_row.get("cohort_id", "")).strip()
    cohort_size = max(0, _as_int(cohort_row.get("size", 0), 0))
    target_micro = min(
        max(0, int(max_micro_agents)),
        int(cohort_size),
    )
    current_micro_rows = _cohort_micro_agents(agent_rows=agents, cohort_id=cohort_id)
    current_micro = len(current_micro_rows)
    needed = max(0, int(target_micro) - int(current_micro))
    created_ids: List[str] = []
    if needed > 0:
        existing_ids = set(str(row.get("agent_id", "")).strip() for row in agents if isinstance(row, dict))
        owner_shard = _cohort_owner_shard_id(cohort_row=cohort_row, shard_map=dict((policy_context or {}).get("shard_map") or {}))
        cohort_faction = cohort_row.get("faction_id")
        faction_id = None if cohort_faction is None else str(cohort_faction).strip() or None
        for slot in range(int(current_micro), int(current_micro + needed)):
            agent_id = "agent.{}".format(canonical_sha256({"cohort_id": cohort_id, "slot": int(slot)})[:24])
            if agent_id in existing_ids:
                continue
            existing_ids.add(agent_id)
            location_seed = _stable_positive_int("{}|{}".format(deterministic_seed, slot), 1_000_000, minimum=0)
            agent_row = {
                "agent_id": agent_id,
                "state_hash": canonical_sha256(
                    {
                        "agent_id": agent_id,
                        "cohort_id": cohort_id,
                        "slot": int(slot),
                        "seed": deterministic_seed,
                    }
                ),
                "body_id": None,
                "owner_peer_id": None,
                "controller_id": None,
                "shard_id": owner_shard,
                "intent_scope_id": None,
                "parent_cohort_id": cohort_id,
                "location_ref": str(interest_region_id).strip() or str(cohort_row.get("location_ref", "")).strip(),
                "orientation_mdeg": {"yaw": int(location_seed % 360_000), "pitch": 0, "roll": 0},
            }
            agents.append(agent_row)
            created_ids.append(agent_id)
            _apply_affiliation_change(
                affiliation_rows=affiliation_rows,
                subject_id=agent_id,
                faction_id=faction_id,
                current_tick=int(current_tick),
            )
    agents = sorted(
        (dict(item) for item in agents if isinstance(item, dict)),
        key=lambda item: str(item.get("agent_id", "")),
    )
    state["agent_states"] = agents
    _ensure_affiliations(state)
    final_micro_rows = _cohort_micro_agents(agent_rows=agents, cohort_id=cohort_id)
    final_micro = len(final_micro_rows)
    cohort_row["refinement_state"] = _cohort_refinement_state(total_size=cohort_size, expanded_count=final_micro)
    extensions = dict(cohort_row.get("extensions") or {}) if isinstance(cohort_row.get("extensions"), dict) else {}
    extensions["mapping_policy_id"] = mapping_policy_id
    extensions["anonymous_micro_agents"] = bool(anonymous_micro_agents)
    extensions["identity_exposure"] = identity_exposure
    extensions["expanded_micro_count"] = int(final_micro)
    extensions["last_interest_region_id"] = str(interest_region_id).strip()
    extensions["last_refinement_tick"] = int(current_tick)
    extensions["last_refinement_seed"] = str(deterministic_seed)
    cohort_row["extensions"] = extensions
    return {
        "result": "complete",
        "cohort_id": cohort_id,
        "expanded_micro_count": int(final_micro),
        "created_agent_ids": _sorted_tokens(created_ids),
    }


def _collapse_cohort_from_micro_internal(
    state: dict,
    cohort_row: dict,
    affiliation_rows: List[dict],
    current_tick: int,
) -> Dict[str, object]:
    agents = _ensure_agent_states(state)
    cohort_id = str(cohort_row.get("cohort_id", "")).strip()
    micro_rows = _cohort_micro_agents(agent_rows=agents, cohort_id=cohort_id)
    micro_ids = _sorted_tokens([str(row.get("agent_id", "")).strip() for row in micro_rows if str(row.get("agent_id", "")).strip()])
    extensions = dict(cohort_row.get("extensions") or {}) if isinstance(cohort_row.get("extensions"), dict) else {}
    expanded_before = max(0, _as_int(extensions.get("expanded_micro_count", len(micro_ids)), len(micro_ids)))
    prior_size = max(0, _as_int(cohort_row.get("size", 0), 0))
    macro_remainder = max(0, int(prior_size) - int(expanded_before))
    new_size = int(macro_remainder) + len(micro_ids)

    faction_counts: Dict[str, int] = {}
    for subject_id in micro_ids:
        row = _find_affiliation(affiliation_rows=affiliation_rows, subject_id=subject_id)
        token = ""
        if isinstance(row, dict):
            raw = row.get("faction_id")
            token = "" if raw is None else str(raw).strip()
        faction_counts[token] = int(faction_counts.get(token, 0)) + 1
    if faction_counts:
        best_faction = sorted(faction_counts.items(), key=lambda item: (-int(item[1]), str(item[0])))[0][0]
        cohort_row["faction_id"] = best_faction or None

    remaining_agents = [
        dict(row)
        for row in agents
        if isinstance(row, dict) and str(row.get("agent_id", "")).strip() not in set(micro_ids)
    ]
    state["agent_states"] = sorted(remaining_agents, key=lambda item: str(item.get("agent_id", "")))
    state["affiliations"] = sorted(
        [
            dict(row)
            for row in affiliation_rows
            if isinstance(row, dict) and str(row.get("subject_id", "")).strip() not in set(micro_ids)
        ],
        key=lambda row: str(row.get("subject_id", "")),
    )
    cohort_row["size"] = int(new_size)
    cohort_row["refinement_state"] = "macro"
    extensions["expanded_micro_count"] = 0
    extensions["last_collapse_tick"] = int(current_tick)
    extensions["collapsed_micro_count"] = len(micro_ids)
    cohort_row["extensions"] = extensions
    return {
        "result": "complete",
        "cohort_id": cohort_id,
        "collapsed_agent_ids": micro_ids,
        "size": int(new_size),
    }


def _resolve_body_collisions(
    state: dict,
    moved_body_id: str,
    ghost_collisions_enabled: bool,
    policy_context: dict | None,
) -> Dict[str, object]:
    bodies = _ensure_body_assemblies(state)
    by_id = {
        str(row.get("assembly_id", "")).strip(): row
        for row in bodies
        if isinstance(row, dict) and str(row.get("assembly_id", "")).strip()
    }
    pairs = _broadphase_pairs(list(by_id.values()))
    collidable_pairs: List[str] = []
    resolved_pairs: List[str] = []
    unresolved_pairs: List[str] = []

    policy = dict(policy_context or {})
    shard_map = dict(policy.get("shard_map") or {})
    active_shard_id = str(policy.get("active_shard_id", "")).strip()
    allow_cross_shard_collision = bool(policy.get("allow_cross_shard_collision", False))

    for left_id, right_id in pairs:
        body_a = by_id.get(str(left_id))
        body_b = by_id.get(str(right_id))
        if not isinstance(body_a, dict) or not isinstance(body_b, dict):
            continue
        if str(body_a.get("collision_layer", "")).strip() != str(body_b.get("collision_layer", "")).strip():
            continue
        if (bool(body_a.get("ghost", False)) or bool(body_b.get("ghost", False))) and not bool(ghost_collisions_enabled):
            continue
        shape_a = str(body_a.get("shape_type", "")).strip()
        shape_b = str(body_b.get("shape_type", "")).strip()
        if not _shape_pair_supported(shape_a=shape_a, shape_b=shape_b):
            continue

        pair_id = _pair_id(left_id, right_id)
        collidable_pairs.append(pair_id)
        if (
            active_shard_id
            and (str(moved_body_id).strip() in (str(left_id), str(right_id)))
            and not allow_cross_shard_collision
        ):
            owner_a = str(body_a.get("shard_id", "")).strip() or _owner_shard_for_object(
                shard_map=shard_map,
                object_id=str(body_a.get("owner_assembly_id", left_id)),
            )
            owner_b = str(body_b.get("shard_id", "")).strip() or _owner_shard_for_object(
                shard_map=shard_map,
                object_id=str(body_b.get("owner_assembly_id", right_id)),
            )
            if owner_a and owner_b and owner_a != owner_b:
                return refusal(
                    "refusal.control.cross_shard_collision_forbidden",
                    "collision pair '{}' spans shards '{}' and '{}'".format(pair_id, owner_a, owner_b),
                    "Keep colliding bodies in one shard or enable allow_cross_shard_collision policy.",
                    {
                        "pair_id": pair_id,
                        "owner_shard_a": owner_a,
                        "owner_shard_b": owner_b,
                        "active_shard_id": active_shard_id,
                    },
                    "$.intent.inputs.body_id",
                )

        mtv = _overlap_mtv_aabb_proxy(body_a=body_a, body_b=body_b)
        if mtv is None:
            continue

        dynamic_a = bool(body_a.get("dynamic", False)) and not bool(body_a.get("ghost", False))
        dynamic_b = bool(body_b.get("dynamic", False)) and not bool(body_b.get("ghost", False))
        a_transform = _vector3_int(body_a.get("transform_mm"), "transform_mm") or {"x": 0, "y": 0, "z": 0}
        b_transform = _vector3_int(body_b.get("transform_mm"), "transform_mm") or {"x": 0, "y": 0, "z": 0}
        if dynamic_a and dynamic_b:
            for axis in ("x", "y", "z"):
                full = int(mtv[axis])
                a_step = int(full // 2)
                b_step = int(-(full - a_step))
                a_transform[axis] = int(a_transform[axis]) + int(a_step)
                b_transform[axis] = int(b_transform[axis]) + int(b_step)
            body_a["transform_mm"] = dict(a_transform)
            body_b["transform_mm"] = dict(b_transform)
            resolved_pairs.append(pair_id)
        elif dynamic_a and not dynamic_b:
            for axis in ("x", "y", "z"):
                a_transform[axis] = int(a_transform[axis]) + int(mtv[axis])
            body_a["transform_mm"] = dict(a_transform)
            resolved_pairs.append(pair_id)
        elif dynamic_b and not dynamic_a:
            for axis in ("x", "y", "z"):
                b_transform[axis] = int(b_transform[axis]) - int(mtv[axis])
            body_b["transform_mm"] = dict(b_transform)
            resolved_pairs.append(pair_id)
        else:
            unresolved_pairs.append(pair_id)

    for pair_id in _sorted_tokens(collidable_pairs):
        left_id, right_id = pair_id.split("::", 1)
        body_a = by_id.get(str(left_id))
        body_b = by_id.get(str(right_id))
        if not isinstance(body_a, dict) or not isinstance(body_b, dict):
            continue
        if _overlap_mtv_aabb_proxy(body_a=body_a, body_b=body_b) is not None:
            unresolved_pairs.append(pair_id)

    collision_state = _ensure_collision_state(state)
    collision_state["last_tick_resolved_pairs"] = _sorted_tokens(list(resolved_pairs))
    collision_state["last_tick_unresolved_pairs"] = _sorted_tokens(list(unresolved_pairs))
    collision_state["last_tick_pair_count"] = len(_sorted_tokens(collidable_pairs))
    collision_state["last_tick_anchor"] = canonical_sha256(
        {
            "pair_count": int(collision_state["last_tick_pair_count"]),
            "resolved": list(collision_state["last_tick_resolved_pairs"]),
            "unresolved": list(collision_state["last_tick_unresolved_pairs"]),
        }
    )
    state["collision_state"] = collision_state
    state["body_assemblies"] = sorted(
        (
            dict(item)
            for item in by_id.values()
            if isinstance(item, dict) and str(item.get("assembly_id", "")).strip()
        ),
        key=lambda item: str(item.get("assembly_id", "")),
    )
    if bool(policy.get("strict_contracts", False)) and collision_state["last_tick_unresolved_pairs"]:
        return refusal(
            "refusal.contract.no_penetration_violation",
            "collision resolution left unresolved overlap pairs",
            "Reduce movement delta or increase separation before applying movement in strict contract mode.",
            {
                "unresolved_pairs": list(collision_state["last_tick_unresolved_pairs"]),
            },
            "$.body_assemblies",
        )
    return {
        "result": "complete",
        "resolved_pairs": list(collision_state["last_tick_resolved_pairs"]),
        "unresolved_pairs": list(collision_state["last_tick_unresolved_pairs"]),
        "pair_count": int(collision_state["last_tick_pair_count"]),
        "collision_anchor": str(collision_state["last_tick_anchor"]),
    }


def _apply_body_move_attempt(
    state: dict,
    body_rows: List[dict],
    inputs: dict,
    policy_context: dict | None,
    *,
    body_id_override: str = "",
    delta_override: dict | None = None,
    dt_ticks_override: int | None = None,
    orientation_delta_override: dict | None = None,
    ghost_collisions_enabled_override: bool | None = None,
) -> Dict[str, object]:
    body_id = str(body_id_override or inputs.get("body_id", "")).strip()
    if not body_id:
        body_id = str(inputs.get("target_body_id", "")).strip()
    if not body_id:
        return refusal(
            "PROCESS_INPUT_INVALID",
            "process.body_move_attempt requires body_id",
            "Provide body_id and delta_transform_mm in the process inputs.",
            {"process_id": "process.body_move_attempt"},
            "$.intent.inputs.body_id",
        )
    body = _find_body(body_rows=body_rows, body_id=body_id)
    if not body:
        return refusal(
            "refusal.control.target_invalid",
            "body '{}' does not exist".format(body_id),
            "Use a body_id present in universe_state.body_assemblies.",
            {"body_id": body_id},
            "$.intent.inputs.body_id",
        )
    if not bool(body.get("dynamic", False)):
        return refusal(
            "refusal.control.target_invalid",
            "body '{}' is static and cannot be moved by process.body_move_attempt".format(body_id),
            "Set body.dynamic=true or use a static placement process.",
            {"body_id": body_id},
            "$.intent.inputs.body_id",
        )
    delta = delta_override if isinstance(delta_override, dict) else _vector3_int(inputs.get("delta_transform_mm"), "delta_transform_mm")
    if delta is None:
        delta = _vector3_int(inputs.get("delta_local_mm"), "delta_local_mm")
    dt_ticks = max(1, _as_int(inputs.get("dt_ticks", 1), 1))
    if dt_ticks_override is not None:
        dt_ticks = max(1, _as_int(dt_ticks_override, 1))
    if delta is None:
        return refusal(
            "PROCESS_INPUT_INVALID",
            "process.body_move_attempt requires delta_transform_mm{x,y,z}",
            "Provide integer delta_transform_mm and optional dt_ticks.",
            {"process_id": "process.body_move_attempt"},
            "$.intent.inputs.delta_transform_mm",
        )
    orientation_delta = (
        orientation_delta_override
        if isinstance(orientation_delta_override, dict)
        else _angles_int(inputs.get("delta_orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
    )
    if not isinstance(orientation_delta, dict):
        orientation_delta = {"yaw": 0, "pitch": 0, "roll": 0}
    ghost_collisions_enabled = bool(inputs.get("ghost_collisions_enabled", False))
    if ghost_collisions_enabled_override is not None:
        ghost_collisions_enabled = bool(ghost_collisions_enabled_override)

    transform = _vector3_int(body.get("transform_mm"), "transform_mm") or {"x": 0, "y": 0, "z": 0}
    orientation = _angles_int(body.get("orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
    velocity = _vector3_int(body.get("velocity_mm_per_tick"), "velocity_mm_per_tick") or {"x": 0, "y": 0, "z": 0}
    transform["x"] = int(transform["x"]) + int(delta["x"]) * int(dt_ticks)
    transform["y"] = int(transform["y"]) + int(delta["y"]) * int(dt_ticks)
    transform["z"] = int(transform["z"]) + int(delta["z"]) * int(dt_ticks)
    orientation["yaw"] = int(orientation["yaw"]) + int(_as_int(orientation_delta.get("yaw", 0), 0))
    orientation["pitch"] = int(orientation["pitch"]) + int(_as_int(orientation_delta.get("pitch", 0), 0))
    orientation["roll"] = int(orientation["roll"]) + int(_as_int(orientation_delta.get("roll", 0), 0))
    velocity["x"] = int(delta["x"])
    velocity["y"] = int(delta["y"])
    velocity["z"] = int(delta["z"])
    body["transform_mm"] = transform
    body["orientation_mdeg"] = orientation
    body["velocity_mm_per_tick"] = velocity

    if bool(body.get("ghost", False)) and not ghost_collisions_enabled:
        collision_state = _ensure_collision_state(state)
        collision_state["last_tick_pair_count"] = 0
        collision_state["last_tick_resolved_pairs"] = []
        collision_state["last_tick_unresolved_pairs"] = []
        collision_state["last_tick_anchor"] = canonical_sha256(
            {
                "pair_count": 0,
                "resolved": [],
                "unresolved": [],
            }
        )
        state["collision_state"] = collision_state
        state["body_assemblies"] = sorted(
            (dict(item) for item in body_rows if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
    else:
        resolved = _resolve_body_collisions(
            state=state,
            moved_body_id=body_id,
            ghost_collisions_enabled=ghost_collisions_enabled,
            policy_context=policy_context,
        )
        if resolved.get("result") != "complete":
            return resolved
    return {
        "result": "complete",
        "body_id": body_id,
        "dt_ticks": int(dt_ticks),
        "delta_transform_mm": {
            "x": int(delta["x"]),
            "y": int(delta["y"]),
            "z": int(delta["z"]),
        },
        "final_transform_mm": dict(body.get("transform_mm") or {"x": 0, "y": 0, "z": 0}),
        "final_orientation_mdeg": dict(body.get("orientation_mdeg") or {"yaw": 0, "pitch": 0, "roll": 0}),
        "final_velocity_mm_per_tick": dict(body.get("velocity_mm_per_tick") or {"x": 0, "y": 0, "z": 0}),
    }


def _control_gate_refusal(gate_payload: dict, reason_map: dict | None = None) -> dict:
    payload = dict(gate_payload or {})
    refusal_payload = dict(payload.get("refusal") or {})
    reason_code = str(refusal_payload.get("reason_code", "")).strip()
    map_payload = dict(reason_map if isinstance(reason_map, dict) else CONTROL_GATE_REASON_MAP)
    mapped = str(map_payload.get(reason_code, "")).strip()
    if not mapped:
        return payload
    refusal_payload["reason_code"] = mapped
    payload["refusal"] = refusal_payload
    rows = payload.get("errors")
    if isinstance(rows, list):
        updated = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            changed = dict(row)
            changed["code"] = mapped
            updated.append(changed)
        payload["errors"] = updated
    return payload


def _append_history_anchor(state: dict, tick: int, log_index: int) -> None:
    rows = state.get("history_anchors")
    if not isinstance(rows, list):
        rows = []
        state["history_anchors"] = rows
    rows.append("history.anchor.tick.{}.log.{}".format(int(tick), int(log_index)))


def _advance_time(state: dict, steps: int = 1) -> None:
    sim = _ensure_simulation_time(state)
    control = _ensure_time_control(state)
    for _ in range(max(0, int(steps))):
        if bool(control.get("paused", False)):
            continue
        rate = max(0, _as_int(control.get("rate_permille", 1000), 1000))
        accumulator = max(0, _as_int(control.get("accumulator_permille", 0), 0))
        total = accumulator + rate
        delta = int(total // 1000)
        control["accumulator_permille"] = int(total % 1000)
        sim["tick"] = int(sim.get("tick", 0)) + delta


def _entitlement_requirement(process_id: str, law_profile: dict) -> str:
    by_law = law_profile.get("process_entitlement_requirements")
    if isinstance(by_law, dict):
        token = str(by_law.get(process_id, "")).strip()
        if token:
            return token
    return str(PROCESS_ENTITLEMENT_DEFAULTS.get(process_id, "")).strip()


def _privilege_requirement(process_id: str, law_profile: dict) -> str:
    by_law = law_profile.get("process_privilege_requirements")
    if isinstance(by_law, dict):
        token = str(by_law.get(process_id, "")).strip()
        if token:
            return token
    return str(PROCESS_PRIVILEGE_DEFAULTS.get(process_id, "observer"))


def _gate_process(process_id: str, law_profile: dict, authority_context: dict) -> Dict[str, object]:
    allowed = _sorted_tokens(list(law_profile.get("allowed_processes") or []))
    forbidden = _sorted_tokens(list(law_profile.get("forbidden_processes") or []))
    if process_id in forbidden or process_id not in allowed:
        return refusal(
            "PROCESS_FORBIDDEN",
            "process '{}' is not allowed by law profile '{}'".format(process_id, str(law_profile.get("law_profile_id", ""))),
            "Select an allowed process for the active LawProfile.",
            {
                "process_id": process_id,
                "law_profile_id": str(law_profile.get("law_profile_id", "")),
            },
            "$.intent.process_id",
        )

    required_entitlement = _entitlement_requirement(process_id, law_profile)
    entitlements = _sorted_tokens(list(authority_context.get("entitlements") or []))
    if required_entitlement and required_entitlement not in entitlements:
        return refusal(
            "ENTITLEMENT_MISSING",
            "missing required entitlement '{}' for process '{}'".format(required_entitlement, process_id),
            "Grant the required entitlement or remove the process from the intent script.",
            {
                "process_id": process_id,
                "missing_entitlement": required_entitlement,
            },
            "$.authority_context.entitlements",
        )

    required_privilege = _privilege_requirement(process_id, law_profile)
    authority_privilege = str(authority_context.get("privilege_level", "")).strip() or "observer"
    have_rank = int(PRIVILEGE_RANK.get(authority_privilege, -1))
    need_rank = int(PRIVILEGE_RANK.get(required_privilege, -1))
    if have_rank < need_rank:
        return refusal(
            "PRIVILEGE_INSUFFICIENT",
            "privilege '{}' is insufficient for process '{}' (requires '{}')".format(
                authority_privilege,
                process_id,
                required_privilege,
            ),
            "Use an authority context with sufficient privilege level.",
            {
                "process_id": process_id,
                "required_privilege": required_privilege,
                "authority_privilege": authority_privilege,
            },
            "$.authority_context.privilege_level",
        )
    return {"result": "complete"}


def _log_process(state: dict, process_id: str, intent_id: str, authority_origin: str, inputs: dict) -> str:
    rows = state.get("process_log")
    if not isinstance(rows, list):
        rows = []
        state["process_log"] = rows
    sim = _ensure_simulation_time(state)
    log_index = len(rows)
    input_hash = canonical_sha256(
        {
            "intent_id": str(intent_id),
            "process_id": str(process_id),
            "inputs": dict(inputs or {}),
        }
    )
    state_hash_anchor = canonical_sha256(state)
    rows.append(
        {
            "log_index": int(log_index),
            "process_id": str(process_id),
            "intent_id": str(intent_id),
            "authority_origin": str(authority_origin),
            "input_hash": input_hash,
            "state_hash_anchor": state_hash_anchor,
            "tick": int(sim.get("tick", 0)),
            "rng_usage": [],
        }
    )
    _append_history_anchor(state, int(sim.get("tick", 0)), int(log_index))
    return state_hash_anchor


def _begin_conservation_process(policy_context: dict | None, process_id: str) -> None:
    if not isinstance(policy_context, dict):
        return
    begin_process_accounting(policy_context=policy_context, process_id=str(process_id))


def _ledger_emit_exception(
    policy_context: dict | None,
    *,
    quantity_id: str,
    delta: int,
    exception_type_id: str,
    domain_id: str,
    process_id: str,
    reason_code: str,
    evidence: List[str] | None = None,
) -> None:
    if not isinstance(policy_context, dict):
        return
    ledger_emit_exception(
        policy_context=policy_context,
        quantity_id=str(quantity_id),
        delta=int(_as_int(delta, 0)),
        exception_type_id=str(exception_type_id),
        domain_id=str(domain_id),
        process_id=str(process_id),
        reason_code=str(reason_code),
        evidence=list(evidence or []),
    )


def _record_unaccounted_conservation_delta(
    policy_context: dict | None,
    *,
    quantity_id: str,
    delta: int,
) -> None:
    if not isinstance(policy_context, dict):
        return
    record_unaccounted_delta(
        policy_context=policy_context,
        quantity_id=str(quantity_id),
        delta=int(_as_int(delta, 0)),
    )


def _finalize_conservation_process(
    state: dict,
    process_id: str,
    policy_context: dict | None,
) -> Dict[str, object]:
    if not isinstance(policy_context, dict):
        return {"result": "complete", "ledger_hash": ""}
    tick = int((_ensure_simulation_time(state)).get("tick", 0))
    finalized = finalize_process_accounting(
        policy_context=policy_context,
        tick=int(tick),
        process_id=str(process_id),
    )
    if str(finalized.get("result", "")) != "complete":
        reason_code = str(finalized.get("reason_code", "refusal.conservation_unaccounted")).strip() or "refusal.conservation_unaccounted"
        details = dict(finalized.get("details") or {})
        quantity_id = str(details.get("quantity_id", "")).strip()
        hints = [str(item).strip() for item in list(finalized.get("remediation_hints") or []) if str(item).strip()]
        remediation = "; ".join(hints) if hints else "enable exception type in physics profile; switch contract set; use meta-law override in private universe"
        relevant = {
            "process_id": str(process_id),
            "contract_set_id": str(((dict(policy_context).get("conservation_runtime_by_shard") or {}).get(str(dict(policy_context).get("active_shard_id", "shard.0"))) or {}).get("contract_set_id", "")),
        }
        if quantity_id:
            relevant["quantity_id"] = quantity_id
        if details:
            relevant["net_delta"] = str(details.get("net_delta", ""))
            relevant["tolerance"] = str(details.get("tolerance", ""))
        return refusal(
            reason_code,
            "conservation contract rejected process accounting",
            remediation,
            relevant,
            "$.conservation",
        )
    return {
        "result": "complete",
        "ledger_hash": str(finalized.get("ledger_hash", "")),
        "ledger": dict(finalized.get("ledger") or {}),
    }


def _finalize_conservation_or_refusal(
    state: dict,
    process_id: str,
    policy_context: dict | None,
) -> Dict[str, object]:
    finalized = _finalize_conservation_process(
        state=state,
        process_id=process_id,
        policy_context=policy_context,
    )
    if str(finalized.get("result", "")) != "complete":
        return finalized
    active_shard_id = ""
    if isinstance(policy_context, dict):
        active_shard_id = str(policy_context.get("active_shard_id", "")).strip()
    ledger_hash = str(finalized.get("ledger_hash", "")).strip()
    if not ledger_hash:
        ledger_hash = str(last_ledger_hash(policy_context=policy_context, shard_id=active_shard_id)).strip()
    return {
        "result": "complete",
        "ledger_hash": ledger_hash,
    }


def _navigation_maps(navigation_indices: dict | None) -> Dict[str, dict]:
    astro = {}
    sites = {}
    ephemeris = {}
    terrain_tiles = {}
    view_modes = {}
    if isinstance(navigation_indices, dict):
        astro_payload = navigation_indices.get("astronomy_catalog_index")
        if isinstance(astro_payload, dict):
            for item in astro_payload.get("entries") or []:
                if not isinstance(item, dict):
                    continue
                object_id = str(item.get("object_id", "")).strip()
                if object_id:
                    astro[object_id] = dict(item)
        site_payload = navigation_indices.get("site_registry_index")
        if isinstance(site_payload, dict):
            for item in site_payload.get("sites") or []:
                if not isinstance(item, dict):
                    continue
                site_id = str(item.get("site_id", "")).strip()
                if site_id:
                    sites[site_id] = dict(item)
        ephemeris_payload = navigation_indices.get("ephemeris_registry")
        if isinstance(ephemeris_payload, dict):
            for item in ephemeris_payload.get("tables") or []:
                if not isinstance(item, dict):
                    continue
                body_id = str(item.get("body_id", "")).strip()
                if body_id:
                    ephemeris[body_id] = dict(item)
        terrain_payload = navigation_indices.get("terrain_tile_registry")
        if isinstance(terrain_payload, dict):
            for item in terrain_payload.get("tiles") or []:
                if not isinstance(item, dict):
                    continue
                tile_id = str(item.get("tile_id", "")).strip()
                if tile_id:
                    terrain_tiles[tile_id] = dict(item)
        view_mode_payload = navigation_indices.get("view_mode_registry")
        if isinstance(view_mode_payload, dict):
            for item in view_mode_payload.get("view_modes") or []:
                if not isinstance(item, dict):
                    continue
                view_mode_id = str(item.get("view_mode_id", "")).strip()
                if view_mode_id:
                    view_modes[view_mode_id] = dict(item)
    return {
        "objects": astro,
        "sites": sites,
        "ephemeris": ephemeris,
        "terrain_tiles": terrain_tiles,
        "view_modes": view_modes,
    }


def _as_float(value: object, default_value: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default_value)


def _site_position_to_local_mm(site_row: dict, object_row: dict | None) -> Dict[str, int] | None:
    position = site_row.get("position")
    if not isinstance(position, dict):
        return None
    representation = str(position.get("representation", "")).strip()
    if representation == "local_xyz_mm":
        return _vector3_int(position.get("local_xyz_mm"), "local_xyz_mm")
    if representation == "lat_lon_alt":
        lat_lon_alt = position.get("lat_lon_alt")
        if not isinstance(lat_lon_alt, dict):
            return None
        lat_rad = _as_float(lat_lon_alt.get("lat_deg_x1e6", 0), 0.0) / 1_000_000.0
        lon_rad = _as_float(lat_lon_alt.get("lon_deg_x1e6", 0), 0.0) / 1_000_000.0
        alt_mm = _as_int(lat_lon_alt.get("alt_mm", 0), 0)
        radius_mm = 0
        if isinstance(object_row, dict):
            bounds = object_row.get("bounds")
            if isinstance(bounds, dict):
                radius_mm = _as_int(bounds.get("sphere_radius_mm", 0), 0)
            if radius_mm <= 0:
                physical = object_row.get("physical_params")
                if isinstance(physical, dict):
                    radius_km = _as_float(physical.get("mean_radius_km", 0.0), 0.0)
                    radius_mm = int(radius_km * 1_000_000.0)
        radius = float(max(1, radius_mm + alt_mm))
        # Deterministic coarse conversion with integer-fixed output.
        import math

        lat = math.radians(lat_rad)
        lon = math.radians(lon_rad)
        x = int(round(radius * math.cos(lat) * math.cos(lon)))
        y = int(round(radius * math.cos(lat) * math.sin(lon)))
        z = int(round(radius * math.sin(lat)))
        return {"x": x, "y": y, "z": z}
    return None


def _resolve_teleport_target(inputs: dict, navigation_indices: dict | None) -> Dict[str, object]:
    direct_frame_id = str(inputs.get("target_frame_id", "")).strip() or str(inputs.get("frame_id", "")).strip()
    direct_position = _vector3_int(inputs.get("position_mm"), "position_mm")
    direct_orientation = _angles_int(inputs.get("orientation_mdeg"))

    target_site_id = str(inputs.get("target_site_id", "")).strip()
    target_object_id = str(inputs.get("target_object_id", "")).strip()
    maps = _navigation_maps(navigation_indices)
    object_map = maps.get("objects") or {}
    site_map = maps.get("sites") or {}
    ephemeris_map = maps.get("ephemeris") or {}

    if target_site_id:
        if not site_map:
            return refusal(
                "REGISTRY_MISSING",
                "site registry index is unavailable for target_site_id resolution",
                "Compile registries and ensure build/registries/site.registry.index.json is present.",
                {"target_site_id": target_site_id},
                "$.intent.inputs.target_site_id",
            )
        site_row = site_map.get(target_site_id)
        if not isinstance(site_row, dict):
            return refusal(
                "TARGET_NOT_FOUND",
                "target_site_id '{}' was not found in site registry index".format(target_site_id),
                "Use a site_id listed in build/registries/site.registry.index.json.",
                {"target_site_id": target_site_id},
                "$.intent.inputs.target_site_id",
            )
        site_object_id = str(site_row.get("object_id", "")).strip()
        object_row = object_map.get(site_object_id) if site_object_id else None
        site_position = _site_position_to_local_mm(site_row, object_row if isinstance(object_row, dict) else None)
        if site_position is None:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "target_site_id '{}' has unsupported position representation".format(target_site_id),
                "Fix site entry position to a supported deterministic representation.",
                {"target_site_id": target_site_id},
                "$.intent.inputs.target_site_id",
            )
        return {
            "result": "complete",
            "frame_id": str(site_row.get("frame_id", "")).strip(),
            "position_mm": site_position,
            "orientation_mdeg": direct_orientation or {"yaw": 0, "pitch": 0, "roll": 0},
            "resolution_source": "site",
            "resolved_id": target_site_id,
        }

    if target_object_id:
        if not object_map:
            return refusal(
                "REGISTRY_MISSING",
                "astronomy catalog index is unavailable for target_object_id resolution",
                "Compile registries and ensure build/registries/astronomy.catalog.index.json is present.",
                {"target_object_id": target_object_id},
                "$.intent.inputs.target_object_id",
            )
        object_row = object_map.get(target_object_id)
        if not isinstance(object_row, dict):
            return refusal(
                "TARGET_NOT_FOUND",
                "target_object_id '{}' was not found in astronomy catalog index".format(target_object_id),
                "Use an object_id listed in build/registries/astronomy.catalog.index.json.",
                {"target_object_id": target_object_id},
                "$.intent.inputs.target_object_id",
            )
        frame_id = str(object_row.get("frame_id", "")).strip()
        bounds = object_row.get("bounds")
        radius_mm = 0
        if isinstance(bounds, dict):
            radius_mm = _as_int(bounds.get("sphere_radius_mm", 0), 0)
        if radius_mm <= 0:
            physical = object_row.get("physical_params")
            if isinstance(physical, dict):
                radius_km = _as_float(physical.get("mean_radius_km", 0.0), 0.0)
                radius_mm = int(radius_km * 1_000_000.0)
        default_distance = max(1000, int(radius_mm * 2) if radius_mm > 0 else 1_000_000)
        ephemeris_row = ephemeris_map.get(target_object_id)
        base_position = {"x": 0, "y": 0, "z": 0}
        if isinstance(ephemeris_row, dict):
            samples = ephemeris_row.get("samples")
            if isinstance(samples, list):
                sample_rows = [item for item in samples if isinstance(item, dict)]
                if sample_rows:
                    sample_rows = sorted(sample_rows, key=lambda item: _as_int(item.get("tick", 0), 0))
                    position = sample_rows[0].get("position_mm")
                    if isinstance(position, dict):
                        base_position = {
                            "x": _as_int(position.get("x", 0), 0),
                            "y": _as_int(position.get("y", 0), 0),
                            "z": _as_int(position.get("z", 0), 0),
                        }
        return {
            "result": "complete",
            "frame_id": frame_id or "frame.unknown",
            "position_mm": {
                "x": int(base_position["x"]),
                "y": int(base_position["y"]),
                "z": int(base_position["z"]) + int(default_distance),
            },
            "orientation_mdeg": direct_orientation or {"yaw": 0, "pitch": 0, "roll": 0},
            "resolution_source": "object",
            "resolved_id": target_object_id,
        }

    if not direct_frame_id or direct_position is None or direct_orientation is None:
        return refusal(
            "PROCESS_INPUT_INVALID",
            "process.camera_teleport requires target_site_id, target_object_id, or direct target_frame_id/frame_id with position/orientation",
            "Provide one deterministic teleport target path.",
            {"process_id": "process.camera_teleport"},
            "$.intent.inputs",
        )
    return {
        "result": "complete",
        "frame_id": direct_frame_id,
        "position_mm": direct_position,
        "orientation_mdeg": direct_orientation,
        "resolution_source": "direct",
        "resolved_id": "",
    }


def _policy_payload(policy_context: dict | None, key: str) -> dict:
    if not isinstance(policy_context, dict):
        return {}
    row = policy_context.get(key)
    if not isinstance(row, dict):
        return {}
    return row


def _registry_rows_by_id(registry_payload: dict, key: str, id_key: str) -> Dict[str, dict]:
    rows = registry_payload.get(key)
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(id_key, ""))):
        token = str(row.get(id_key, "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _policy_id_from_context(policy_context: dict | None) -> str:
    if not isinstance(policy_context, dict):
        return ""
    direct = str(policy_context.get("cosmetic_policy_id", "")).strip()
    if direct:
        return direct
    control_policy = dict(policy_context.get("control_policy") or {})
    from_control = str(control_policy.get("cosmetic_policy_id", "")).strip()
    if from_control:
        return from_control
    server_profile = dict(policy_context.get("server_profile") or {})
    from_profile = str((server_profile.get("extensions") or {}).get("cosmetic_policy_id", "")).strip()
    if from_profile:
        return from_profile
    server_policy = dict(policy_context.get("server_policy") or {})
    return str((server_policy.get("extensions") or {}).get("cosmetic_policy_id", "")).strip()


def _resolve_cosmetic_policy(policy_context: dict | None) -> Dict[str, object]:
    policy_registry = _policy_payload(policy_context, "cosmetic_policy_registry")
    policies = _registry_rows_by_id(policy_registry, "policies", "policy_id")
    policy_id = _policy_id_from_context(policy_context)
    if not policy_id:
        return refusal(
            "refusal.cosmetic.forbidden",
            "cosmetic assignment requires an explicit cosmetic policy id",
            "Configure control/server policy with a cosmetic_policy_id before assigning cosmetics.",
            {"policy_id": "<missing>"},
            "$.intent.inputs.cosmetic_id",
        )
    policy = dict(policies.get(policy_id) or {})
    if not policy:
        return refusal(
            "refusal.cosmetic.forbidden",
            "cosmetic policy '{}' is unavailable in compiled registry".format(policy_id),
            "Add cosmetic policy to cosmetic_policy.registry.json and rebuild registries.",
            {"policy_id": policy_id},
            "$.intent.inputs.cosmetic_id",
        )
    return {"result": "complete", "policy": policy}


def _representation_state(policy_context: dict | None) -> dict:
    if not isinstance(policy_context, dict):
        return {"assignments": {}, "events": []}
    state = policy_context.get("representation_state")
    if not isinstance(state, dict):
        state = {}
        policy_context["representation_state"] = state
    assignments = state.get("assignments")
    if not isinstance(assignments, dict):
        assignments = {}
    events = state.get("events")
    if not isinstance(events, list):
        events = []
    state["assignments"] = dict(
        (str(key).strip(), dict(value))
        for key, value in sorted(assignments.items(), key=lambda item: str(item[0]))
        if str(key).strip() and isinstance(value, dict)
    )
    state["events"] = sorted(
        (dict(item) for item in events if isinstance(item, dict)),
        key=lambda item: (
            int(item.get("applied_tick", 0) or 0),
            str(item.get("target_agent_id", "")),
            str(item.get("cosmetic_id", "")),
            str(item.get("assignment_id", "")),
        ),
    )
    return state


def _cosmetic_pack_id(cosmetic_row: dict) -> str:
    ext = dict(cosmetic_row.get("extensions") or {})
    return str(ext.get("pack_id", "")).strip()


def _load_solver_registry(policy_context: dict | None) -> Dict[str, object]:
    if isinstance(policy_context, dict):
        embedded = policy_context.get("solver_registry")
        if isinstance(embedded, dict):
            return {"result": "complete", "payload": dict(embedded), "source": "policy_context"}

    solver_path = os.path.join(REPO_ROOT_HINT, SOLVER_REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(solver_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return refusal(
            "refusal.solver_unbound",
            "solver registry is unavailable for structural transition checks",
            "Provide policy_context.solver_registry or restore data/registries/solver_registry.json.",
            {"registry_path": SOLVER_REGISTRY_REL},
            "$.solver_registry",
        )
    if not isinstance(payload, dict):
        return refusal(
            "refusal.solver_unbound",
            "solver registry payload has invalid root shape",
            "Fix solver registry JSON root to an object with records[].",
            {"registry_path": SOLVER_REGISTRY_REL},
            "$.solver_registry",
        )
    return {"result": "complete", "payload": payload, "source": "registry_file"}


def _solver_row_by_id(payload: dict, solver_id: str) -> dict:
    rows = payload.get("records")
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("solver_id", ""))):
        token = str(row.get("solver_id", "")).strip()
        if token == str(solver_id).strip():
            return dict(row)
    return {}


def _check_solver_binding_for_transition(policy_context: dict | None, transition_name: str) -> Dict[str, object]:
    loaded = _load_solver_registry(policy_context)
    if loaded.get("result") != "complete":
        return loaded

    payload = dict(loaded.get("payload") or {})
    solver_bindings = dict(DEFAULT_SOLVER_BINDINGS)
    if isinstance(policy_context, dict):
        row = policy_context.get("solver_bindings")
        if isinstance(row, dict):
            for key in ("collapse_solver_id", "expand_solver_id"):
                token = str(row.get(key, "")).strip()
                if token:
                    solver_bindings[key] = token

    binding_key = "collapse_solver_id" if str(transition_name) == "collapse" else "expand_solver_id"
    solver_id = str(solver_bindings.get(binding_key, "")).strip()
    solver_row = _solver_row_by_id(payload, solver_id=solver_id)
    if not solver_row:
        return refusal(
            "refusal.solver_unbound",
            "solver '{}' is missing for transition '{}'".format(solver_id, transition_name),
            "Add/restore the requested solver row in solver_registry.json.",
            {"solver_id": solver_id, "transition": str(transition_name)},
            "$.solver_registry.records",
        )

    domain_ids = sorted(set(str(item).strip() for item in (solver_row.get("domain_ids") or []) if str(item).strip()))
    contract_ids = sorted(set(str(item).strip() for item in (solver_row.get("contract_ids") or []) if str(item).strip()))
    transition_support = sorted(
        set(str(item).strip() for item in (solver_row.get("transition_support") or []) if str(item).strip())
    )
    if not domain_ids or not contract_ids:
        return refusal(
            "refusal.solver_unbound",
            "solver '{}' is missing structural domain/contract bindings".format(solver_id),
            "Declare non-empty domain_ids and contract_ids for the solver row.",
            {"solver_id": solver_id},
            "$.solver_registry.records",
        )
    if str(transition_name).strip() not in transition_support:
        return refusal(
            "refusal.contract_violation",
            "solver '{}' does not support transition '{}'".format(solver_id, transition_name),
            "Select a solver whose transition_support includes '{}'.".format(transition_name),
            {"solver_id": solver_id, "transition": str(transition_name)},
            "$.solver_registry.records",
        )

    return {
        "result": "complete",
        "trace": {
            "solver_id": solver_id,
            "transition": str(transition_name),
            "domain_ids": domain_ids,
            "contract_ids": contract_ids,
            "transition_support": transition_support,
            "source": str(loaded.get("source", "")),
        },
    }


def _tier_rank(token: str) -> int:
    value = str(token).strip()
    if value == "coarse":
        return 0
    if value == "medium":
        return 1
    if value == "fine":
        return 2
    return -1


def _tier_tokens() -> List[str]:
    return ["coarse", "medium", "fine"]


def _stable_positive_int(token: str, modulo: int, minimum: int = 0) -> int:
    digest = hashlib.sha256(str(token).encode("utf-8")).hexdigest()
    value = int(digest[:16], 16)
    out = int(value % max(1, int(modulo)))
    if out < int(minimum):
        return int(minimum)
    return out


def _camera_distance_mm(state: dict) -> int:
    camera_result = _require_camera_main(state)
    if camera_result.get("result") != "complete":
        return 0
    camera = camera_result.get("camera")
    if not isinstance(camera, dict):
        return 0
    position = _vector3_int(camera.get("position_mm"), "position_mm") or {"x": 0, "y": 0, "z": 0}
    return abs(int(position["x"])) + abs(int(position["y"])) + abs(int(position["z"]))


def _astronomy_entries(navigation_indices: dict | None) -> List[dict]:
    if not isinstance(navigation_indices, dict):
        return []
    payload = navigation_indices.get("astronomy_catalog_index")
    if not isinstance(payload, dict):
        return []
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return []
    out = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        object_id = str(item.get("object_id", "")).strip()
        if not object_id:
            continue
        out.append(dict(item))
    return sorted(out, key=lambda item: str(item.get("object_id", "")))


def _interest_rule(activation_policy: dict, kind: str) -> dict:
    rules = activation_policy.get("interest_radius_rules")
    if not isinstance(rules, list):
        return {}
    exact = None
    wildcard = None
    for item in rules:
        if not isinstance(item, dict):
            continue
        token = str(item.get("kind", "")).strip()
        if token == str(kind).strip():
            exact = dict(item)
            break
        if token == "*":
            wildcard = dict(item)
    return exact or wildcard or {}


def _tier_from_distance(
    fidelity_policy: dict,
    distance_mm: int,
    kind: str,
    previous_tier: str,
) -> str:
    tiers = []
    for item in fidelity_policy.get("tiers") or []:
        if not isinstance(item, dict):
            continue
        tier_id = str(item.get("tier_id", "")).strip()
        if tier_id not in _tier_tokens():
            continue
        tiers.append(
            {
                "tier_id": tier_id,
                "max_distance_mm": max(0, _as_int(item.get("max_distance_mm", 0), 0)),
            }
        )
    if not tiers:
        return "coarse"
    tiers = sorted(tiers, key=lambda row: (int(row.get("max_distance_mm", 0)), str(row.get("tier_id", ""))))
    chosen = str(tiers[-1].get("tier_id", "coarse"))
    for row in tiers:
        if int(distance_mm) <= int(row.get("max_distance_mm", 0)):
            chosen = str(row.get("tier_id", "coarse"))
            break

    minimum_by_kind = fidelity_policy.get("minimum_tier_by_kind")
    minimum_tier = ""
    if isinstance(minimum_by_kind, dict):
        minimum_tier = str(minimum_by_kind.get(kind, "")).strip() or str(minimum_by_kind.get("*", "")).strip()
    if minimum_tier in _tier_tokens() and _tier_rank(chosen) < _tier_rank(minimum_tier):
        chosen = minimum_tier

    if str(previous_tier).strip() in _tier_tokens():
        switching = fidelity_policy.get("switching_rules")
        if isinstance(switching, dict):
            upgrade_h = max(0, _as_int(switching.get("upgrade_hysteresis_mm", 0), 0))
            degrade_h = max(0, _as_int(switching.get("degrade_hysteresis_mm", 0), 0))
        else:
            upgrade_h = 0
            degrade_h = 0
        previous_rank = _tier_rank(previous_tier)
        chosen_rank = _tier_rank(chosen)
        max_by_tier = {str(row.get("tier_id", "")): int(row.get("max_distance_mm", 0)) for row in tiers}
        if chosen_rank > previous_rank:
            # Upgrade (finer) only if distance is sufficiently inside the new tier threshold.
            threshold = int(max_by_tier.get(chosen, 0))
            if int(distance_mm) + int(upgrade_h) > threshold:
                chosen = str(previous_tier)
        elif chosen_rank < previous_rank:
            # Degrade (coarser) only after leaving previous tier plus hysteresis margin.
            prev_threshold = int(max_by_tier.get(str(previous_tier), 0))
            if int(distance_mm) <= prev_threshold + int(degrade_h):
                chosen = str(previous_tier)
    return chosen if chosen in _tier_tokens() else "coarse"


def _tier_entity_target(fidelity_policy: dict, tier: str) -> int:
    for item in fidelity_policy.get("tiers") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("tier_id", "")).strip() != str(tier).strip():
            continue
        return max(0, _as_int(item.get("micro_entities_target", 0), 0))
    return 0


def _tier_weight(budget_policy: dict, tier: str) -> int:
    weights = budget_policy.get("tier_compute_weights")
    if not isinstance(weights, dict):
        return 0
    return max(0, _as_int(weights.get(str(tier), 0), 0))


def _apply_roi_cohort_refinement(
    state: dict,
    policy_context: dict | None,
    active_region_ids: List[str],
    budget_max_entities: int,
    current_tick: int,
) -> Dict[str, object]:
    cohort_rows = _ensure_cohort_assemblies(state)
    if not cohort_rows:
        return {"result": "complete", "cohort_refinement": []}

    mapping_rows = _cohort_mapping_policy_rows(policy_context)
    if not mapping_rows:
        return refusal(
            "refusal.civ.policy_missing",
            "cohort mapping policy registry is unavailable",
            "Compile cohort_mapping_policy_registry and provide it via policy_context.",
            {"registry": "cohort_mapping_policy_registry"},
            "$.policy_context.cohort_mapping_policy_registry",
        )

    shard_map = dict((policy_context or {}).get("shard_map") or {})
    active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
    active_set = set(_sorted_tokens(active_region_ids))
    camera_distance = _camera_distance_mm(state)
    affiliation_rows = _ensure_affiliations(state)
    decisions: List[dict] = []

    for cohort_row in sorted(cohort_rows, key=lambda row: str(row.get("cohort_id", ""))):
        cohort_id = str(cohort_row.get("cohort_id", "")).strip()
        location_ref = str(cohort_row.get("location_ref", "")).strip()
        if not cohort_id:
            continue
        micro_rows = _cohort_micro_agents(agent_rows=_ensure_agent_states(state), cohort_id=cohort_id)
        expanded_count = len(micro_rows)
        if location_ref in active_set:
            continue
        if expanded_count <= 0:
            continue
        collapsed = _collapse_cohort_from_micro_internal(
            state=state,
            cohort_row=cohort_row,
            affiliation_rows=affiliation_rows,
            current_tick=int(current_tick),
        )
        if collapsed.get("result") != "complete":
            return collapsed
        decisions.append(
            {
                "cohort_id": cohort_id,
                "location_ref": location_ref,
                "action": "collapse",
                "collapsed_count": len(list(collapsed.get("collapsed_agent_ids") or [])),
            }
        )

    candidates = []
    for cohort_row in cohort_rows:
        cohort_id = str(cohort_row.get("cohort_id", "")).strip()
        location_ref = str(cohort_row.get("location_ref", "")).strip()
        if not cohort_id or not location_ref or location_ref not in active_set:
            continue
        faction_id = str(cohort_row.get("faction_id", "")).strip()
        size = max(0, _as_int(cohort_row.get("size", 0), 0))
        anchor_mm = _stable_positive_int("cohort|{}".format(location_ref), 4096, minimum=0) * 1000
        distance_quantized = max(0, abs(int(camera_distance) - int(anchor_mm)) // 1000)
        candidates.append(
            (
                str(cohort_id),
                str(faction_id),
                int(size),
                int(distance_quantized),
            )
        )
    candidates = sorted(candidates, key=lambda row: (row[0], row[1], row[2], row[3]))

    for cohort_id, _faction_id, _size, _distance in candidates:
        cohort_row = _find_cohort(cohort_rows=cohort_rows, cohort_id=cohort_id)
        if not cohort_row:
            continue
        mapping_policy_id = _cohort_policy_id(cohort_row=cohort_row, fallback="")
        if not mapping_policy_id:
            return refusal(
                "refusal.civ.policy_missing",
                "cohort '{}' has no mapping policy id".format(cohort_id),
                "Set cohort.extensions.mapping_policy_id to a registered mapping policy.",
                {"cohort_id": cohort_id},
                "$.cohort_assemblies",
            )
        mapping_policy = dict(mapping_rows.get(mapping_policy_id) or {})
        if not mapping_policy:
            return refusal(
                "refusal.civ.policy_missing",
                "mapping policy '{}' is not registered".format(mapping_policy_id),
                "Use a mapping_policy_id from cohort_mapping_policy_registry.",
                {"cohort_id": cohort_id, "mapping_policy_id": mapping_policy_id},
                "$.cohort_assemblies",
            )
        owner_shard = _cohort_owner_shard_id(cohort_row=cohort_row, shard_map=shard_map)
        if active_shard_id and owner_shard and owner_shard != active_shard_id:
            return refusal(
                "refusal.civ.cohort_cross_shard_forbidden",
                "cohort '{}' belongs to shard '{}' but active shard is '{}'".format(cohort_id, owner_shard, active_shard_id),
                "Route refinement to owning shard or perform deterministic transfer first.",
                {"cohort_id": cohort_id, "owner_shard_id": owner_shard, "active_shard_id": active_shard_id},
                "$.policy_context.active_shard_id",
            )

        cohort_size = max(0, _as_int(cohort_row.get("size", 0), 0))
        policy_max = max(0, _as_int(mapping_policy.get("max_micro_agents_per_cohort", cohort_size), cohort_size))
        desired_target = min(int(cohort_size), int(policy_max))
        current_micro = len(_cohort_micro_agents(agent_rows=_ensure_agent_states(state), cohort_id=cohort_id))
        current_total_micro = len(
            [
                row
                for row in _ensure_agent_states(state)
                if isinstance(row, dict) and str(row.get("parent_cohort_id", "")).strip()
            ]
        )
        available_budget = max(0, int(budget_max_entities) - int(current_total_micro))
        additional_needed = max(0, int(desired_target) - int(current_micro))
        additional_allowed = min(int(additional_needed), int(available_budget))
        target_micro = int(current_micro + additional_allowed)
        deterministic_seed = _cohort_seed_material(
            cohort_id=cohort_id,
            tick=int(current_tick),
            policy_context=policy_context,
            mapping_policy_id=mapping_policy_id,
            interest_region_id=str(cohort_row.get("location_ref", "")).strip(),
        )
        expanded = _expand_cohort_to_micro_internal(
            state=state,
            cohort_row=cohort_row,
            cohort_rows=cohort_rows,
            affiliation_rows=affiliation_rows,
            interest_region_id=str(cohort_row.get("location_ref", "")).strip(),
            max_micro_agents=int(target_micro),
            mapping_policy_id=mapping_policy_id,
            policy_context=policy_context,
            current_tick=int(current_tick),
            deterministic_seed=deterministic_seed,
        )
        if expanded.get("result") != "complete":
            return expanded
        decisions.append(
            {
                "cohort_id": cohort_id,
                "location_ref": str(cohort_row.get("location_ref", "")).strip(),
                "action": "expand",
                "mapping_policy_id": mapping_policy_id,
                "seed": deterministic_seed,
                "target_micro_agents": int(target_micro),
                "expanded_micro_count": int(expanded.get("expanded_micro_count", 0)),
                "partial": bool(int(target_micro) < int(desired_target)),
                "created_agent_ids": list(expanded.get("created_agent_ids") or []),
            }
        )

    state["cohort_assemblies"] = sorted(
        (dict(row) for row in cohort_rows if isinstance(row, dict)),
        key=lambda row: str(row.get("cohort_id", "")),
    )
    state["affiliations"] = sorted(
        (dict(row) for row in affiliation_rows if isinstance(row, dict)),
        key=lambda row: str(row.get("subject_id", "")),
    )
    return {"result": "complete", "cohort_refinement": decisions}


def _total_conserved_mass(state: dict) -> int:
    total = 0
    for row in state.get("macro_capsules") or []:
        if not isinstance(row, dict):
            continue
        conserved = row.get("conserved_quantities")
        if isinstance(conserved, dict):
            total += max(0, _as_int(conserved.get("mass_stub", 0), 0))
    for row in state.get("micro_regions") or []:
        if not isinstance(row, dict):
            continue
        total += max(0, _as_int(row.get("mass_stub", 0), 0))
    return total


def _degrade_one_tier(current_tier: str, degrade_order: List[str]) -> str:
    token = str(current_tier).strip()
    if token not in degrade_order:
        return token
    idx = degrade_order.index(token)
    if idx + 1 >= len(degrade_order):
        return token
    next_tier = str(degrade_order[idx + 1]).strip()
    return next_tier if next_tier in _tier_tokens() else token


def _region_management_tick(
    state: dict,
    navigation_indices: dict | None,
    policy_context: dict | None,
    process_id: str = "process.region_management_tick",
    forced_expand_region_ids: List[str] | None = None,
    forced_collapse_region_ids: List[str] | None = None,
    forced_expand_tiers: Dict[str, str] | None = None,
) -> Dict[str, object]:
    activation_policy = _policy_payload(policy_context, "activation_policy")
    budget_policy = _policy_payload(policy_context, "budget_policy")
    fidelity_policy = _policy_payload(policy_context, "fidelity_policy")
    if not activation_policy or not budget_policy or not fidelity_policy:
        return refusal(
            "REGISTRY_MISSING",
            "region management policies are unavailable",
            "Ensure activation/budget/fidelity policy registries are compiled and selected in SessionSpec.",
            {"process_id": "process.region_management_tick"},
            "$.policy_context",
        )

    entries = _astronomy_entries(navigation_indices)
    if not entries:
        return refusal(
            "REGISTRY_MISSING",
            "astronomy catalog index entries are unavailable for region management",
            "Compile astronomy catalog registry and retry.",
            {"process_id": "process.region_management_tick"},
            "$.navigation_indices",
        )

    simulation = _ensure_simulation_time(state)
    current_tick = int(simulation.get("tick", 0) or 0)

    interest_rows = state.get("interest_regions")
    if not isinstance(interest_rows, list):
        interest_rows = []
    interest_by_region = {}
    for item in interest_rows:
        if not isinstance(item, dict):
            continue
        region_id = str(item.get("region_id", "")).strip()
        if not region_id:
            continue
        interest_by_region[region_id] = dict(item)

    capsule_rows = state.get("macro_capsules")
    if not isinstance(capsule_rows, list):
        capsule_rows = []
    capsule_by_object = {}
    for item in capsule_rows:
        if not isinstance(item, dict):
            continue
        object_id = str(item.get("covers_object_id", "")).strip()
        if not object_id:
            continue
        capsule_by_object[object_id] = dict(item)

    micro_rows = state.get("micro_regions")
    if not isinstance(micro_rows, list):
        micro_rows = []
    micro_by_region = {}
    for item in micro_rows:
        if not isinstance(item, dict):
            continue
        region_id = str(item.get("region_id", "")).strip()
        if not region_id:
            continue
        micro_by_region[region_id] = dict(item)

    for entry in entries:
        object_id = str(entry.get("object_id", "")).strip()
        if not object_id:
            continue
        region_id = "region.{}".format(object_id)
        if region_id not in interest_by_region:
            interest_by_region[region_id] = {
                "region_id": region_id,
                "anchor_object_id": object_id,
                "active": False,
                "current_fidelity_tier": "coarse",
                "last_transition_tick": 0,
            }
        if object_id not in capsule_by_object:
            mass_stub = 100 + _stable_positive_int(object_id, 9000, minimum=0)
            capsule_by_object[object_id] = {
                "capsule_id": "capsule.{}".format(object_id),
                "covers_object_id": object_id,
                "conserved_quantities": {
                    "mass_stub": int(mass_stub),
                    "entity_count": 0,
                },
                "fidelity_representation": {
                    "tier": "macro",
                    "summary": "macro_only",
                },
                "collapsed_micro_state_hash": canonical_sha256({"region_id": region_id, "state": "macro"}),
            }

    mass_before = _total_conserved_mass(
        {
            "macro_capsules": list(capsule_by_object.values()),
            "micro_regions": list(micro_by_region.values()),
        }
    )

    camera_distance = _camera_distance_mm(state)
    hysteresis = dict(activation_policy.get("hysteresis") or {})
    enter_margin = max(0, _as_int(hysteresis.get("enter_margin_mm", 0), 0))
    exit_margin = max(0, _as_int(hysteresis.get("exit_margin_mm", 0), 0))

    candidates = []
    for entry in entries:
        object_id = str(entry.get("object_id", "")).strip()
        kind = str(entry.get("kind", "")).strip()
        region_id = "region.{}".format(object_id)
        row = interest_by_region.get(region_id) or {}
        was_active = bool(row.get("active", False))
        previous_tier = str(row.get("current_fidelity_tier", "coarse")).strip() or "coarse"
        rule = _interest_rule(activation_policy=activation_policy, kind=kind)
        if not rule:
            continue
        priority = max(0, _as_int(rule.get("priority", 0), 0))
        activation_distance = max(0, _as_int(rule.get("activation_distance_mm", 0), 0))
        deactivation_distance = max(0, _as_int(rule.get("deactivation_distance_mm", 0), 0))
        spacing = max(1, _as_int(rule.get("anchor_spacing_mm", 1), 1))
        anchor_mm = _stable_positive_int(object_id, 1024, minimum=0) * int(spacing)
        distance_mm = abs(int(camera_distance) - int(anchor_mm))
        threshold = deactivation_distance + exit_margin if was_active else activation_distance + enter_margin
        if distance_mm > threshold:
            continue
        desired_tier = _tier_from_distance(
            fidelity_policy=fidelity_policy,
            distance_mm=distance_mm,
            kind=kind,
            previous_tier=previous_tier,
        )
        candidates.append(
            {
                "region_id": region_id,
                "object_id": object_id,
                "kind": kind,
                "priority": int(priority),
                "distance_mm": int(distance_mm),
                "tier": desired_tier,
            }
        )

    candidates = sorted(candidates, key=lambda item: (int(item.get("priority", 0)), str(item.get("object_id", ""))))
    max_regions = max(0, _as_int(budget_policy.get("max_regions_micro", 0), 0))
    selected = {}
    priority_map = {}
    for item in candidates[:max_regions]:
        region_id = str(item.get("region_id", ""))
        selected[region_id] = str(item.get("tier", "coarse"))
        priority_map[region_id] = int(item.get("priority", 0))

    max_compute = max(0, _as_int(budget_policy.get("max_compute_units_per_tick", 0), 0))
    max_entities = max(0, _as_int(budget_policy.get("max_entities_micro", 0), 0))
    entity_weight = max(0, _as_int(budget_policy.get("entity_compute_weight", 0), 0))

    def budget_usage(selection: Dict[str, str]) -> Dict[str, int]:
        tier_sum = 0
        entity_sum = 0
        for region_id in sorted(selection.keys()):
            tier = str(selection.get(region_id, "coarse"))
            tier_sum += _tier_weight(budget_policy, tier)
            entity_sum += _tier_entity_target(fidelity_policy, tier)
        compute_units = int(tier_sum + (entity_sum * entity_weight))
        return {
            "compute_units": compute_units,
            "entity_count": int(entity_sum),
        }

    usage = budget_usage(selected)
    fallback = str(budget_policy.get("fallback_behavior", "degrade_fidelity")).strip()
    budget_outcome = "ok"

    if usage["compute_units"] > max_compute or usage["entity_count"] > max_entities:
        if fallback == "refuse":
            return refusal(
                "BUDGET_EXCEEDED",
                "region management exceeded budget policy limits",
                "Lower requested fidelity/region count or use a budget policy with higher limits.",
                {
                    "budget_policy_id": str(budget_policy.get("policy_id", "")),
                    "compute_units_used": str(usage["compute_units"]),
                    "max_compute_units_per_tick": str(max_compute),
                },
                "$.budget_policy",
            )

        switching = fidelity_policy.get("switching_rules")
        if isinstance(switching, dict):
            degrade_order = [str(item).strip() for item in (switching.get("degrade_order") or []) if str(item).strip()]
        else:
            degrade_order = []
        if degrade_order != ["fine", "medium", "coarse"]:
            degrade_order = ["fine", "medium", "coarse"]

        changed = False
        while usage["compute_units"] > max_compute or usage["entity_count"] > max_entities:
            step_changed = False
            for region_id in sorted(selected.keys(), key=lambda rid: (int(priority_map.get(rid, 0)), str(rid)), reverse=True):
                current_tier = str(selected.get(region_id, "coarse"))
                next_tier = _degrade_one_tier(current_tier, degrade_order)
                if next_tier == current_tier:
                    continue
                selected[region_id] = next_tier
                step_changed = True
                changed = True
                usage = budget_usage(selected)
                if usage["compute_units"] <= max_compute and usage["entity_count"] <= max_entities:
                    break
            if not step_changed:
                break
        if changed:
            budget_outcome = "degraded"

        if usage["compute_units"] > max_compute or usage["entity_count"] > max_entities:
            for region_id in sorted(selected.keys(), key=lambda rid: (int(priority_map.get(rid, 0)), str(rid)), reverse=True):
                del selected[region_id]
                usage = budget_usage(selected)
                if usage["compute_units"] <= max_compute and usage["entity_count"] <= max_entities:
                    break
            budget_outcome = "capped"

    current_active = {}
    for region_id, row in interest_by_region.items():
        if bool(row.get("active", False)):
            current_active[region_id] = str(row.get("current_fidelity_tier", "coarse"))
    desired_active = dict(selected)
    forced_expand_ids = _sorted_tokens(list(forced_expand_region_ids or []))
    forced_collapse_ids = _sorted_tokens(list(forced_collapse_region_ids or []))
    forced_tiers = dict(forced_expand_tiers or {})
    for region_id in forced_collapse_ids + forced_expand_ids:
        if region_id not in interest_by_region:
            return refusal(
                "refusal.control.target_invalid",
                "region '{}' is not known to region management".format(region_id),
                "Use a region_id produced by deterministic region mapping (region.<object_id>).",
                {"region_id": region_id},
                "$.intent.inputs.region_id",
            )
    for region_id in forced_collapse_ids:
        desired_active.pop(region_id, None)
    for region_id in forced_expand_ids:
        forced_tier = str(forced_tiers.get(region_id, "")).strip()
        if forced_tier not in _tier_tokens():
            forced_tier = str(desired_active.get(region_id, "") or current_active.get(region_id, "")).strip() or "coarse"
        if forced_tier not in _tier_tokens():
            forced_tier = "coarse"
        desired_active[region_id] = forced_tier
    usage = budget_usage(desired_active)
    if usage["compute_units"] > max_compute or usage["entity_count"] > max_entities:
        return refusal(
            "BUDGET_EXCEEDED",
            "forced region transition exceeds deterministic budget envelope",
            "Reduce forced expand set or use a budget policy with higher limits.",
            {
                "forced_expand_region_ids": ",".join(forced_expand_ids),
                "compute_units_used": str(usage["compute_units"]),
                "max_compute_units_per_tick": str(max_compute),
            },
            "$.budget_policy",
        )

    collapse_ids = sorted(
        region_id
        for region_id in current_active.keys()
        if region_id not in desired_active or str(desired_active.get(region_id, "")) != str(current_active.get(region_id, ""))
    )
    expand_ids = sorted(
        region_id
        for region_id in desired_active.keys()
        if region_id not in current_active or str(desired_active.get(region_id, "")) != str(current_active.get(region_id, ""))
    )
    solver_binding_trace: List[dict] = []
    if collapse_ids:
        collapse_check = _check_solver_binding_for_transition(policy_context=policy_context, transition_name="collapse")
        if collapse_check.get("result") != "complete":
            return collapse_check
        solver_binding_trace.append(dict(collapse_check.get("trace") or {}))
    if expand_ids:
        expand_check = _check_solver_binding_for_transition(policy_context=policy_context, transition_name="expand")
        if expand_check.get("result") != "complete":
            return expand_check
        solver_binding_trace.append(dict(expand_check.get("trace") or {}))

    for region_id in collapse_ids:
        row = interest_by_region.get(region_id) or {}
        object_id = str(row.get("anchor_object_id", "")).strip()
        micro = micro_by_region.pop(region_id, None)
        if isinstance(micro, dict):
            capsule = capsule_by_object.get(object_id)
            if isinstance(capsule, dict):
                conserved = dict(capsule.get("conserved_quantities") or {})
                conserved["mass_stub"] = int(conserved.get("mass_stub", 0) or 0) + max(0, _as_int(micro.get("mass_stub", 0), 0))
                conserved["entity_count"] = max(0, _as_int(micro.get("entity_count", 0), 0))
                capsule["conserved_quantities"] = conserved
                capsule["fidelity_representation"] = {"tier": "macro", "summary": "collapsed"}
                capsule["collapsed_micro_state_hash"] = canonical_sha256(micro)
                capsule_by_object[object_id] = capsule
        row["active"] = False
        row["current_fidelity_tier"] = "coarse"
        row["last_transition_tick"] = int(current_tick)
        interest_by_region[region_id] = row

    for region_id in expand_ids:
        row = interest_by_region.get(region_id) or {}
        object_id = str(row.get("anchor_object_id", "")).strip()
        desired_tier = str(desired_active.get(region_id, "coarse"))
        capsule = capsule_by_object.get(object_id) or {}
        conserved = dict(capsule.get("conserved_quantities") or {})
        mass_stub = max(0, _as_int(conserved.get("mass_stub", 0), 0))
        if mass_stub == 0:
            mass_stub = 100 + _stable_positive_int(object_id, 9000, minimum=0)
        entity_target = _tier_entity_target(fidelity_policy, desired_tier)
        micro_by_region[region_id] = {
            "region_id": region_id,
            "object_id": object_id,
            "fidelity_tier": desired_tier,
            "entity_count": int(entity_target),
            "mass_stub": int(mass_stub),
        }
        conserved["mass_stub"] = 0
        conserved["entity_count"] = 0
        capsule["conserved_quantities"] = conserved
        capsule["fidelity_representation"] = {"tier": "expanded", "summary": "micro:{}".format(desired_tier)}
        capsule_by_object[object_id] = capsule
        row["active"] = True
        row["current_fidelity_tier"] = desired_tier
        row["last_transition_tick"] = int(current_tick)
        interest_by_region[region_id] = row

    for region_id in sorted(desired_active.keys()):
        if region_id in expand_ids:
            continue
        # Ensure stable tier mirror for unchanged active regions.
        row = interest_by_region.get(region_id) or {}
        row["active"] = True
        row["current_fidelity_tier"] = str(desired_active.get(region_id, "coarse"))
        interest_by_region[region_id] = row

    state["interest_regions"] = sorted(
        (dict(item) for item in interest_by_region.values()),
        key=lambda item: str(item.get("region_id", "")),
    )
    state["macro_capsules"] = sorted(
        (dict(item) for item in capsule_by_object.values()),
        key=lambda item: str(item.get("capsule_id", "")),
    )
    state["micro_regions"] = sorted(
        (dict(item) for item in micro_by_region.values()),
        key=lambda item: str(item.get("region_id", "")),
    )

    mass_after = _total_conserved_mass(state)
    mass_delta = int(mass_after) - int(mass_before)
    if collapse_ids or expand_ids:
        _ledger_emit_exception(
            policy_context=policy_context,
            quantity_id=CONSERVATION_DEFAULT_QUANTITY_ID,
            delta=int(mass_delta),
            exception_type_id="exception.numeric_error_budget",
            domain_id=CONSERVATION_DEFAULT_DOMAIN_ID,
            process_id=str(process_id),
            reason_code="conservation.lod.quantization",
            evidence=[
                "mass_before={}".format(int(mass_before)),
                "mass_after={}".format(int(mass_after)),
                "collapsed_regions={}".format(len(collapse_ids)),
                "expanded_regions={}".format(len(expand_ids)),
            ],
        )
    elif int(mass_delta) != 0:
        _record_unaccounted_conservation_delta(
            policy_context=policy_context,
            quantity_id=CONSERVATION_DEFAULT_QUANTITY_ID,
            delta=int(mass_delta),
        )

    tier_counts = {"coarse": 0, "medium": 0, "fine": 0}
    for tier in desired_active.values():
        token = str(tier).strip()
        if token in tier_counts:
            tier_counts[token] += 1
    previous_performance = state.get("performance_state")
    if not isinstance(previous_performance, dict):
        previous_performance = {}
    prior_solver_trace = list(previous_performance.get("solver_binding_trace") or [])

    performance_state = {
        "budget_policy_id": str(budget_policy.get("policy_id", "")),
        "fidelity_policy_id": str(fidelity_policy.get("policy_id", "")),
        "activation_policy_id": str(activation_policy.get("policy_id", "")),
        "compute_units_used": int(usage["compute_units"]),
        "max_compute_units_per_tick": int(max_compute),
        "budget_outcome": str(budget_outcome),
        "active_region_count": int(len(desired_active)),
        "fidelity_tier_counts": tier_counts,
        "transition_log": list(previous_performance.get("transition_log") or []),
        "solver_binding_trace": prior_solver_trace,
    }
    for row in sorted(
        (item for item in solver_binding_trace if isinstance(item, dict)),
        key=lambda item: (str(item.get("transition", "")), str(item.get("solver_id", ""))),
    ):
        performance_state["solver_binding_trace"].append(dict(row))
    performance_state["transition_log"].append(
        {
            "tick": int(current_tick),
            "budget_outcome": str(budget_outcome),
            "compute_units_used": int(usage["compute_units"]),
            "active_regions": sorted(desired_active.keys()),
        }
    )
    terrain_map = _navigation_maps(navigation_indices).get("terrain_tiles") or {}
    terrain_rows = sorted(
        (dict(item) for item in terrain_map.values() if isinstance(item, dict)),
        key=lambda item: (
            _as_int(item.get("z", 0), 0),
            _as_int(item.get("x", 0), 0),
            _as_int(item.get("y", 0), 0),
            str(item.get("tile_id", "")),
        ),
    )
    desired_tile_count = min(len(terrain_rows), int(len(desired_active)))
    selected_terrain_tiles = [str(item.get("tile_id", "")) for item in terrain_rows[:desired_tile_count] if str(item.get("tile_id", "")).strip()]
    state["performance_state"] = performance_state
    cohort_refinement_result = _apply_roi_cohort_refinement(
        state=state,
        policy_context=policy_context,
        active_region_ids=sorted(desired_active.keys()),
        budget_max_entities=max_entities,
        current_tick=current_tick,
    )
    if cohort_refinement_result.get("result") != "complete":
        return cohort_refinement_result
    cohort_refinement = sorted(
        (dict(item) for item in list(cohort_refinement_result.get("cohort_refinement") or []) if isinstance(item, dict)),
        key=lambda item: (
            str(item.get("cohort_id", "")),
            str(item.get("action", "")),
            str(item.get("location_ref", "")),
        ),
    )

    return {
        "result": "complete",
        "budget_outcome": str(budget_outcome),
        "compute_units_used": int(usage["compute_units"]),
        "active_regions": sorted(desired_active.keys()),
        "collapsed_regions": collapse_ids,
        "expanded_regions": expand_ids,
        "forced_expand_region_ids": forced_expand_ids,
        "forced_collapse_region_ids": forced_collapse_ids,
        "selected_terrain_tiles": selected_terrain_tiles,
        "cohort_refinement": cohort_refinement,
    }


def _registry_payloads_for_lod(
    navigation_indices: dict | None,
    policy_context: dict | None,
) -> dict:
    payloads: Dict[str, dict] = {}
    if isinstance(navigation_indices, dict):
        for key, value in sorted(navigation_indices.items(), key=lambda item: str(item[0])):
            if isinstance(value, dict):
                payloads[str(key)] = dict(value)
    if isinstance(policy_context, dict):
        keys = (
            "epistemic_policy_registry",
            "retention_policy_registry",
            "decay_model_registry",
            "eviction_rule_registry",
            "perception_interest_policy_registry",
            "view_mode_registry",
            "instrument_type_registry",
            "calibration_model_registry",
            "render_proxy_registry",
            "cosmetic_registry",
            "cosmetic_policy_registry",
            "representation_state",
        )
        for key in keys:
            row = policy_context.get(key)
            if isinstance(row, dict):
                payloads[str(key)] = dict(row)
    return payloads


def _default_lod_lens(
    state: dict,
    law_profile: dict,
    lod_observation: dict,
    epistemic_policy: dict,
) -> dict:
    explicit_lens = lod_observation.get("lens")
    if isinstance(explicit_lens, dict):
        required = ("lens_id", "lens_type", "required_entitlements", "epistemic_constraints")
        if all(token in explicit_lens for token in required):
            lens = dict(explicit_lens)
            channels = lens.get("observation_channels")
            if not isinstance(channels, list) or not channels:
                lens["observation_channels"] = _sorted_tokens(list(epistemic_policy.get("allowed_observation_channels") or []))
            return lens

    lens_id = str(lod_observation.get("lens_id", "")).strip()
    if not lens_id:
        allowed_lenses = _sorted_tokens(list(law_profile.get("allowed_lenses") or []))
        lens_id = allowed_lenses[0] if allowed_lenses else ""
    if not lens_id:
        camera_rows = list(state.get("camera_assemblies") or [])
        for row in sorted((item for item in camera_rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
            candidate = str(row.get("lens_id", "")).strip()
            if candidate:
                lens_id = candidate
                break
    lens_type = str(lod_observation.get("lens_type", "")).strip() or "diegetic"
    channels = _sorted_tokens(list(lod_observation.get("observation_channels") or []))
    if not channels:
        channels = _sorted_tokens(list(epistemic_policy.get("allowed_observation_channels") or []))
    if not channels:
        channels = ["ch.core.time", "ch.camera.state", "ch.core.entities"]
    return {
        "lens_id": lens_id or "lens.diegetic.sensor",
        "lens_type": lens_type,
        "required_entitlements": _sorted_tokens(list(lod_observation.get("required_entitlements") or [])),
        "observation_channels": channels,
        "epistemic_constraints": dict(
            lod_observation.get("epistemic_constraints")
            if isinstance(lod_observation.get("epistemic_constraints"), dict)
            else {"visibility_policy": "sensor_limited", "max_resolution_tier": 1}
        ),
    }


def _normalized_lod_authority_context(authority_context: dict, law_profile: dict) -> dict:
    scope = dict(authority_context.get("epistemic_scope") or {})
    if not scope:
        scope = {"scope_id": "scope.runtime", "visibility_level": "diegetic"}
    return {
        "authority_origin": str(authority_context.get("authority_origin", "")).strip() or "client",
        "experience_id": str(authority_context.get("experience_id", "")).strip() or "profile.runtime",
        "law_profile_id": str(authority_context.get("law_profile_id", "")).strip()
        or str(law_profile.get("law_profile_id", "")).strip()
        or "law.runtime",
        "entitlements": _sorted_tokens(list(authority_context.get("entitlements") or [])),
        "epistemic_scope": scope,
        "privilege_level": str(authority_context.get("privilege_level", "")).strip() or "observer",
    }


def _normalized_lod_law_profile(law_profile: dict, lens_id: str) -> dict:
    out = dict(law_profile or {})
    allowed_lenses = _sorted_tokens(list(out.get("allowed_lenses") or []))
    if lens_id and lens_id not in set(allowed_lenses):
        allowed_lenses.append(lens_id)
        allowed_lenses = sorted(set(allowed_lenses))
    out["allowed_lenses"] = allowed_lenses
    epistemic_limits = out.get("epistemic_limits")
    if not isinstance(epistemic_limits, dict):
        out["epistemic_limits"] = {}
    return out


def _observe_lod_snapshot(
    state: dict,
    law_profile: dict,
    authority_context: dict,
    navigation_indices: dict | None,
    policy_context: dict | None,
    lod_observation: dict,
    memory_state: dict | None,
) -> Dict[str, object]:
    from .observation import observe_truth

    explicit_epistemic_policy = dict(lod_observation.get("epistemic_policy") or {})
    explicit_retention_policy = dict(lod_observation.get("retention_policy") or {})
    lens = _default_lod_lens(
        state=state,
        law_profile=law_profile,
        lod_observation=lod_observation,
        epistemic_policy=explicit_epistemic_policy,
    )
    normalized_law = _normalized_lod_law_profile(law_profile=law_profile, lens_id=str(lens.get("lens_id", "")))
    normalized_authority = _normalized_lod_authority_context(authority_context=authority_context, law_profile=normalized_law)
    observed = observe_truth(
        truth_model={
            "schema_version": "1.0.0",
            "universe_state": copy.deepcopy(state if isinstance(state, dict) else {}),
            "registry_payloads": _registry_payloads_for_lod(
                navigation_indices=navigation_indices,
                policy_context=policy_context,
            ),
        },
        lens=lens,
        law_profile=normalized_law,
        authority_context=normalized_authority,
        viewpoint_id=str(lod_observation.get("viewpoint_id", "viewpoint.lod.invariance")).strip() or "viewpoint.lod.invariance",
        epistemic_policy=explicit_epistemic_policy if explicit_epistemic_policy else None,
        retention_policy=explicit_retention_policy if explicit_retention_policy else None,
        memory_state=dict(memory_state or {}),
        perception_interest_limit=_as_int(lod_observation.get("perception_interest_limit", 0), 0) or None,
    )
    return dict(observed if isinstance(observed, dict) else {})


def _memory_item_ids(perceived_model: dict) -> List[str]:
    memory = dict(perceived_model.get("memory") or {})
    rows = memory.get("items")
    if not isinstance(rows, list):
        return []
    return _sorted_tokens(
        [
            str(row.get("memory_item_id", "")).strip()
            for row in rows
            if isinstance(row, dict)
        ]
    )


def _lod_sensitive_key_paths(payload: object, prefix: str = "$") -> List[str]:
    suspicious = ("hidden_inventory", "internal_state", "micro_solver", "native_precision")
    rows: List[str] = []
    if isinstance(payload, dict):
        for key in sorted(payload.keys()):
            token = str(key)
            path = "{}.{}".format(prefix, token)
            lowered = token.lower()
            if any(marker in lowered for marker in suspicious):
                rows.append(path)
            rows.extend(_lod_sensitive_key_paths(payload.get(key), prefix=path))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            rows.extend(_lod_sensitive_key_paths(item, prefix="{}[{}]".format(prefix, index)))
    return rows


def _entity_entry_map(perceived_model: dict) -> Dict[str, dict]:
    entities = dict(perceived_model.get("entities") or {})
    rows = entities.get("entries")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("entity_id", ""))):
        token = str(row.get("entity_id", "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _lod_invariance_delta(
    before_perceived: dict,
    after_perceived: dict,
    allowed_new_channels: List[str],
    allowed_new_entity_ids: List[str],
) -> Dict[str, object]:
    before_channels = set(_sorted_tokens(list(before_perceived.get("channels") or [])))
    after_channels = set(_sorted_tokens(list(after_perceived.get("channels") or [])))
    allowed_channel_set = set(_sorted_tokens(list(allowed_new_channels or [])))
    new_channels = sorted(after_channels - before_channels - allowed_channel_set)

    before_entities = _entity_entry_map(before_perceived)
    after_entities = _entity_entry_map(after_perceived)
    allowed_entities = set(_sorted_tokens(list(allowed_new_entity_ids or [])))
    new_entities = sorted(set(after_entities.keys()) - set(before_entities.keys()) - allowed_entities)
    changed_entities = sorted(
        entity_id
        for entity_id in sorted(set(after_entities.keys()) & set(before_entities.keys()))
        if canonical_sha256(dict(after_entities.get(entity_id) or {}))
        != canonical_sha256(dict(before_entities.get(entity_id) or {}))
    )
    precision_gain = canonical_sha256(dict(before_perceived.get("camera_viewpoint") or {})) != canonical_sha256(
        dict(after_perceived.get("camera_viewpoint") or {})
    )
    sensitive_paths = sorted(set(_lod_sensitive_key_paths(after_perceived)))
    invariant_ok = (
        not new_channels
        and not new_entities
        and not changed_entities
        and not precision_gain
        and not sensitive_paths
    )
    return {
        "invariant_ok": bool(invariant_ok),
        "before_hash": canonical_sha256(before_perceived),
        "after_hash": canonical_sha256(after_perceived),
        "new_channels": list(new_channels),
        "new_entities": list(new_entities),
        "changed_entities": list(changed_entities),
        "precision_gain": bool(precision_gain),
        "sensitive_paths": list(sensitive_paths),
    }


def _append_lod_invariance_log(state: dict, row: dict) -> None:
    performance_state = state.get("performance_state")
    if not isinstance(performance_state, dict):
        performance_state = {}
    log_rows = performance_state.get("lod_invariance_log")
    if not isinstance(log_rows, list):
        log_rows = []
    log_rows.append(dict(row))
    performance_state["lod_invariance_log"] = sorted(
        (dict(item) for item in log_rows if isinstance(item, dict)),
        key=lambda item: (
            int(item.get("tick", 0) or 0),
            str(item.get("process_id", "")),
            str(item.get("region_id", "")),
            str(item.get("before_hash", "")),
            str(item.get("after_hash", "")),
        ),
    )
    state["performance_state"] = performance_state


def _run_region_transition_with_lod_invariance(
    state: dict,
    process_id: str,
    inputs: dict,
    law_profile: dict,
    authority_context: dict,
    navigation_indices: dict | None,
    policy_context: dict | None,
) -> Dict[str, object]:
    region_id = str(inputs.get("region_id", "") or inputs.get("target_region_id", "")).strip()
    if not region_id:
        return refusal(
            "PROCESS_INPUT_INVALID",
            "{} requires region_id".format(process_id),
            "Provide intent.inputs.region_id formatted as region.<object_id>.",
            {"process_id": process_id},
            "$.intent.inputs.region_id",
        )
    desired_tier = str(inputs.get("desired_tier", "")).strip() or "coarse"
    if desired_tier not in _tier_tokens():
        desired_tier = "coarse"
    strict_contracts = bool((policy_context or {}).get("strict_contracts", False))
    enforce_lod_invariance = bool(inputs.get("enforce_lod_invariance", True))
    lod_observation = dict(inputs.get("lod_observation") or {})
    before_observation = {}
    after_observation = {}
    memory_state = dict(lod_observation.get("memory_state") or {})
    if enforce_lod_invariance:
        before_observation = _observe_lod_snapshot(
            state=state,
            law_profile=law_profile,
            authority_context=authority_context,
            navigation_indices=navigation_indices,
            policy_context=policy_context,
            lod_observation=lod_observation,
            memory_state=memory_state,
        )
        if str(before_observation.get("result", "")) == "complete":
            memory_state = dict(before_observation.get("memory_state") or {})
        elif strict_contracts:
            return dict(before_observation)

    forced_expand_ids = [region_id] if process_id == "process.region_expand" else []
    forced_collapse_ids = [region_id] if process_id == "process.region_collapse" else []
    forced_tiers = {region_id: desired_tier} if process_id == "process.region_expand" else {}
    tick_result = _region_management_tick(
        state=state,
        navigation_indices=navigation_indices,
        policy_context=policy_context,
        process_id=process_id,
        forced_expand_region_ids=forced_expand_ids,
        forced_collapse_region_ids=forced_collapse_ids,
        forced_expand_tiers=forced_tiers,
    )
    if str(tick_result.get("result", "")) != "complete":
        return tick_result

    lod_summary = {
        "status": "skipped",
        "before_hash": "",
        "after_hash": "",
        "new_channels": [],
        "new_entities": [],
        "changed_entities": [],
        "precision_gain": False,
        "sensitive_paths": [],
        "missing_memory_item_ids": [],
    }
    if enforce_lod_invariance and str(before_observation.get("result", "")) == "complete":
        after_observation = _observe_lod_snapshot(
            state=state,
            law_profile=law_profile,
            authority_context=authority_context,
            navigation_indices=navigation_indices,
            policy_context=policy_context,
            lod_observation=lod_observation,
            memory_state=memory_state,
        )
        if str(after_observation.get("result", "")) != "complete":
            if strict_contracts:
                return dict(after_observation)
        else:
            after_perceived = dict(after_observation.get("perceived_model") or {})
            if bool(inputs.get("test_force_lod_information_gain", False)) or bool(
                (policy_context or {}).get("test_force_lod_information_gain", False)
            ):
                entities_payload = dict(after_perceived.get("entities") or {})
                extensions_payload = dict(entities_payload.get("extensions") or {})
                extensions_payload["micro_internal_state"] = "forced.test.leak"
                entities_payload["extensions"] = extensions_payload
                after_perceived["entities"] = entities_payload

            delta = _lod_invariance_delta(
                before_perceived=dict(before_observation.get("perceived_model") or {}),
                after_perceived=after_perceived,
                allowed_new_channels=_sorted_tokens(list(lod_observation.get("allowed_new_channels") or [])),
                allowed_new_entity_ids=_sorted_tokens(list(lod_observation.get("allowed_new_entity_ids") or [])),
            )
            missing_memory_item_ids: List[str] = []
            if process_id == "process.region_collapse":
                before_memory = set(
                    _memory_item_ids(dict(before_observation.get("perceived_model") or {}))
                )
                after_memory = set(_memory_item_ids(after_perceived))
                missing_memory_item_ids = sorted(before_memory - after_memory)
            violation = (not bool(delta.get("invariant_ok", False))) or bool(missing_memory_item_ids)
            lod_summary = {
                "status": "violation" if violation else "ok",
                "before_hash": str(delta.get("before_hash", "")),
                "after_hash": str(delta.get("after_hash", "")),
                "new_channels": list(delta.get("new_channels") or []),
                "new_entities": list(delta.get("new_entities") or []),
                "changed_entities": list(delta.get("changed_entities") or []),
                "precision_gain": bool(delta.get("precision_gain", False)),
                "sensitive_paths": list(delta.get("sensitive_paths") or []),
                "missing_memory_item_ids": list(missing_memory_item_ids),
            }
            _append_lod_invariance_log(
                state=state,
                row={
                    "tick": int((_ensure_simulation_time(state)).get("tick", 0)),
                    "process_id": process_id,
                    "region_id": region_id,
                    "status": str(lod_summary.get("status", "")),
                    "before_hash": str(lod_summary.get("before_hash", "")),
                    "after_hash": str(lod_summary.get("after_hash", "")),
                    "new_channels": list(lod_summary.get("new_channels") or []),
                    "new_entities": list(lod_summary.get("new_entities") or []),
                    "changed_entities": list(lod_summary.get("changed_entities") or []),
                    "precision_gain": bool(lod_summary.get("precision_gain", False)),
                    "missing_memory_item_ids": list(lod_summary.get("missing_memory_item_ids") or []),
                },
            )
            if violation and strict_contracts:
                return refusal(
                    "refusal.ep.lod_information_gain",
                    "solver-tier transition exposed epistemic information beyond allowed policy envelope",
                    "Apply redaction/precision rules or adjust entitlements before expand/collapse transition.",
                    {
                        "process_id": process_id,
                        "region_id": region_id,
                        "new_channels": ",".join(list(lod_summary.get("new_channels") or [])),
                        "new_entities": ",".join(list(lod_summary.get("new_entities") or [])),
                        "missing_memory_item_ids": ",".join(list(lod_summary.get("missing_memory_item_ids") or [])),
                    },
                    "$.perceived_model",
                )

    return {
        "result": "complete",
        "tick_result": tick_result,
        "lod_invariance": lod_summary,
        "region_id": region_id,
        "forced_tier": desired_tier if process_id == "process.region_expand" else "",
    }


def execute_intent(
    state: dict,
    intent: dict,
    law_profile: dict,
    authority_context: dict,
    navigation_indices: dict | None = None,
    policy_context: dict | None = None,
) -> Dict[str, object]:
    """Commit-phase process mutation primitive used by SRZ scheduler."""
    if not isinstance(intent, dict):
        return refusal(
            "PROCESS_INPUT_INVALID",
            "intent must be an object",
            "Provide an intent object with intent_id, process_id, and inputs.",
            {"field": "intent"},
            "$.intent",
        )
    intent_id = str(intent.get("intent_id", "")).strip()
    process_id = str(intent.get("process_id", "")).strip()
    inputs = intent.get("inputs")
    if not intent_id:
        return refusal(
            "PROCESS_INPUT_INVALID",
            "intent_id is required",
            "Set a stable intent_id string for each script step.",
            {"field": "intent_id"},
            "$.intent.intent_id",
        )
    if not process_id:
        return refusal(
            "PROCESS_INPUT_INVALID",
            "process_id is required",
            "Set process_id to one of the supported process IDs.",
            {"field": "process_id"},
            "$.intent.process_id",
        )
    if not isinstance(inputs, dict):
        return refusal(
            "PROCESS_INPUT_INVALID",
            "inputs must be an object",
            "Provide process inputs as a JSON object.",
            {"field": "inputs"},
            "$.intent.inputs",
        )

    gate = _gate_process(process_id, law_profile, authority_context)
    if gate.get("result") != "complete":
        if process_id == "process.cosmetic_assign":
            return _control_gate_refusal(gate, reason_map=COSMETIC_GATE_REASON_MAP)
        if process_id in CIV_PROCESS_IDS:
            return _control_gate_refusal(gate, reason_map=CIV_GATE_REASON_MAP)
        if process_id in CONTROL_PROCESS_IDS:
            return _control_gate_refusal(gate)
        return gate

    camera: dict = {}
    if process_id in CAMERA_REQUIRED_PROCESS_IDS:
        camera_result = _require_camera_main(state)
        if camera_result.get("result") != "complete":
            return camera_result
        camera = camera_result.get("camera")
        if not isinstance(camera, dict):
            return refusal(
                "PROCESS_INPUT_INVALID",
                "camera payload is invalid",
                "Initialize camera.main in universe state.",
                {"assembly_id": "camera.main"},
                "$.camera_assemblies",
            )
    agents = _ensure_agent_states(state)
    controllers = _ensure_controller_assemblies(state)
    bindings = _ensure_control_bindings(state)
    bodies = _ensure_body_assemblies(state)
    cohorts = _ensure_cohort_assemblies(state)
    order_rows = _ensure_order_assemblies(state)
    queue_rows = _ensure_order_queue_assemblies(state)
    institution_rows = _ensure_institution_assemblies(state)
    role_assignment_rows = _ensure_role_assignment_assemblies(state)
    _ensure_collision_state(state)
    current_tick = int((_ensure_simulation_time(state)).get("tick", 0))
    arrived_cohort_ids = _apply_pending_cohort_arrivals(cohorts, current_tick)
    result_metadata: Dict[str, object] = {}
    skip_state_log = False
    _begin_conservation_process(policy_context=policy_context, process_id=process_id)

    if process_id == "process.camera_move":
        delta = _vector3_int(inputs.get("delta_local_mm"), "delta_local_mm")
        dt_ticks = _as_int(inputs.get("dt_ticks", 0), 0)
        if delta is None or dt_ticks < 1:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.camera_move requires delta_local_mm and dt_ticks>=1",
                "Provide integer delta_local_mm{x,y,z} and dt_ticks in the intent inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        pos = _vector3_int(camera.get("position_mm"), "position_mm") or {"x": 0, "y": 0, "z": 0}
        velocity = _vector3_int(camera.get("velocity_mm_per_tick"), "velocity_mm_per_tick") or {"x": 0, "y": 0, "z": 0}
        pos["x"] += int(delta["x"]) * int(dt_ticks)
        pos["y"] += int(delta["y"]) * int(dt_ticks)
        pos["z"] += int(delta["z"]) * int(dt_ticks)
        velocity["x"] = int(delta["x"])
        velocity["y"] = int(delta["y"])
        velocity["z"] = int(delta["z"])
        camera["position_mm"] = pos
        camera["velocity_mm_per_tick"] = velocity
        _advance_time(state, steps=int(dt_ticks))
    elif process_id == "process.camera_teleport":
        resolved_target = _resolve_teleport_target(inputs=inputs, navigation_indices=navigation_indices)
        if resolved_target.get("result") != "complete":
            return resolved_target
        camera["frame_id"] = str(resolved_target.get("frame_id", ""))
        camera["position_mm"] = dict(resolved_target.get("position_mm") or {"x": 0, "y": 0, "z": 0})
        camera["orientation_mdeg"] = dict(resolved_target.get("orientation_mdeg") or {"yaw": 0, "pitch": 0, "roll": 0})
        camera["velocity_mm_per_tick"] = {"x": 0, "y": 0, "z": 0}
        _ledger_emit_exception(
            policy_context=policy_context,
            quantity_id=CONSERVATION_DEFAULT_QUANTITY_ID,
            delta=0,
            exception_type_id="exception.meta_law_override",
            domain_id=CONSERVATION_CONTROL_DOMAIN_ID,
            process_id=process_id,
            reason_code="control.teleport.override",
            evidence=[
                "target_frame_id={}".format(str(resolved_target.get("frame_id", ""))),
            ],
        )
        _advance_time(state, steps=1)
    elif process_id == "process.agent_move":
        agent_id = str(inputs.get("agent_id", "") or inputs.get("target_agent_id", "") or inputs.get("target_id", "")).strip()
        if not agent_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.agent_move requires agent_id",
                "Provide agent_id and move_vector_local in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.agent_id",
            )
        move_ctx = _movement_context(
            agents=agents,
            controllers=controllers,
            bindings=bindings,
            agent_id=agent_id,
            inputs=dict(inputs),
            authority_context=authority_context,
        )
        if move_ctx.get("result") != "complete":
            return move_ctx
        agent = move_ctx.get("agent")
        if not isinstance(agent, dict):
            return refusal(
                "refusal.control.target_invalid",
                "agent payload is invalid for movement",
                "Ensure agent_id resolves to an object in universe_state.agent_states.",
                {"agent_id": agent_id},
                "$.intent.inputs.agent_id",
            )
        body_id = _agent_body_id(agent_row=agent, body_rows=bodies, agent_id=agent_id)
        if not body_id:
            return refusal(
                "refusal.agent.unembodied",
                "agent '{}' has no embodied body_id".format(agent_id),
                "Attach a body assembly to this agent before issuing movement intents.",
                {"agent_id": agent_id},
                "$.intent.inputs.agent_id",
            )
        body = _find_body(body_rows=bodies, body_id=body_id)
        if not body:
            return refusal(
                "refusal.agent.unembodied",
                "agent '{}' body '{}' is missing".format(agent_id, body_id),
                "Create body assembly and set agent.body_id before movement.",
                {"agent_id": agent_id, "body_id": body_id},
                "$.intent.inputs.agent_id",
            )
        local_move = _vector3_int(inputs.get("move_vector_local"), "move_vector_local")
        if local_move is None:
            local_move = _vector3_int(inputs.get("delta_local_mm"), "delta_local_mm")
        if local_move is None:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.agent_move requires move_vector_local{x,y,z}",
                "Provide integer move_vector_local payload for kinematic movement.",
                {"process_id": process_id},
                "$.intent.inputs.move_vector_local",
            )
        speed_scalar = max(0, min(10000, _as_int(inputs.get("speed_scalar", 1000), 1000)))
        dt_ticks = max(1, _as_int(inputs.get("tick_duration", inputs.get("dt_ticks", 1)), 1))
        scaled_local = {
            "x": int(int(local_move["x"]) * int(speed_scalar) // 1000),
            "y": int(int(local_move["y"]) * int(speed_scalar) // 1000),
            "z": int(int(local_move["z"]) * int(speed_scalar) // 1000),
        }
        orientation = _angles_int(agent.get("orientation_mdeg")) or _angles_int(body.get("orientation_mdeg")) or {
            "yaw": 0,
            "pitch": 0,
            "roll": 0,
        }
        world_delta = _movement_world_delta(local_delta=scaled_local, yaw_mdeg=_as_int(orientation.get("yaw", 0), 0))
        policy_payload = dict(policy_context or {})
        shard_map = dict(policy_payload.get("shard_map") or {})
        active_shard_id = str(policy_payload.get("active_shard_id", "")).strip()
        owner_shard_id = (
            str(agent.get("shard_id", "")).strip()
            or str(body.get("shard_id", "")).strip()
            or _owner_shard_for_object(shard_map=shard_map, object_id=agent_id)
            or _owner_shard_for_object(shard_map=shard_map, object_id=body_id)
        )
        if active_shard_id and owner_shard_id and owner_shard_id != active_shard_id:
            return refusal(
                "refusal.agent.boundary_cross_forbidden",
                "agent movement owner shard '{}' does not match active shard '{}'".format(owner_shard_id, active_shard_id),
                "Route movement intent to owning shard or run explicit SRZ transfer process first.",
                {"agent_id": agent_id, "owner_shard_id": owner_shard_id, "active_shard_id": active_shard_id},
                "$.intent.inputs.agent_id",
            )
        moved = _apply_body_move_attempt(
            state=state,
            body_rows=bodies,
            inputs=dict(inputs),
            policy_context=policy_context,
            body_id_override=body_id,
            delta_override=world_delta,
            dt_ticks_override=int(dt_ticks),
        )
        if moved.get("result") != "complete":
            return moved
        # body_move_attempt can rebuild state.body_assemblies; reload to avoid stale pre-collision rows.
        bodies = _ensure_body_assemblies(state)
        refreshed_body = _find_body(body_rows=bodies, body_id=body_id)
        controller_id = str(move_ctx.get("controller_id", "")).strip()
        owner_peer_id = str(move_ctx.get("owner_peer_id", "")).strip()
        if owner_peer_id:
            agent["owner_peer_id"] = owner_peer_id
        if controller_id:
            agent["controller_id"] = controller_id
        agent["body_id"] = body_id
        shard_id = owner_shard_id or str((refreshed_body or {}).get("shard_id", "")).strip() or "shard.0"
        agent["shard_id"] = shard_id
        if isinstance(refreshed_body, dict):
            refreshed_body["owner_agent_id"] = agent_id
            refreshed_body["shard_id"] = shard_id
        _refresh_agent_state_hash(agent_row=agent, body_row=refreshed_body if isinstance(refreshed_body, dict) else None)
        state["agent_states"] = sorted((dict(item) for item in agents if isinstance(item, dict)), key=lambda item: str(item.get("agent_id", "")))
        state["body_assemblies"] = sorted(
            (dict(item) for item in bodies if isinstance(item, dict) and str(item.get("assembly_id", "")).strip()),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        result_metadata = {
            "agent_id": agent_id,
            "body_id": body_id,
            "movement_delta_mm": dict(world_delta),
            "movement_distance_mm": int(abs(int(world_delta["x"])) + abs(int(world_delta["y"])) + abs(int(world_delta["z"]))),
            "dt_ticks": int(dt_ticks),
        }
        _advance_time(state, steps=int(dt_ticks))
    elif process_id == "process.agent_rotate":
        agent_id = str(inputs.get("agent_id", "") or inputs.get("target_agent_id", "") or inputs.get("target_id", "")).strip()
        if not agent_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.agent_rotate requires agent_id",
                "Provide agent_id with yaw_delta/pitch_delta/roll_delta.",
                {"process_id": process_id},
                "$.intent.inputs.agent_id",
            )
        move_ctx = _movement_context(
            agents=agents,
            controllers=controllers,
            bindings=bindings,
            agent_id=agent_id,
            inputs=dict(inputs),
            authority_context=authority_context,
        )
        if move_ctx.get("result") != "complete":
            return move_ctx
        agent = move_ctx.get("agent")
        if not isinstance(agent, dict):
            return refusal(
                "refusal.control.target_invalid",
                "agent payload is invalid for rotation",
                "Ensure agent_id resolves to an object in universe_state.agent_states.",
                {"agent_id": agent_id},
                "$.intent.inputs.agent_id",
            )
        orientation = _angles_int(agent.get("orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
        delta_payload = _angles_int(inputs.get("delta_orientation_mdeg")) or {
            "yaw": _as_int(inputs.get("yaw_delta", 0), 0),
            "pitch": _as_int(inputs.get("pitch_delta", 0), 0),
            "roll": _as_int(inputs.get("roll_delta", 0), 0),
        }
        orientation["yaw"] = int(orientation["yaw"]) + int(_as_int(delta_payload.get("yaw", 0), 0))
        orientation["pitch"] = int(orientation["pitch"]) + int(_as_int(delta_payload.get("pitch", 0), 0))
        orientation["roll"] = int(orientation["roll"]) + int(_as_int(delta_payload.get("roll", 0), 0))
        agent["orientation_mdeg"] = dict(orientation)
        controller_id = str(move_ctx.get("controller_id", "")).strip()
        owner_peer_id = str(move_ctx.get("owner_peer_id", "")).strip()
        if controller_id:
            agent["controller_id"] = controller_id
        if owner_peer_id:
            agent["owner_peer_id"] = owner_peer_id
        body_id = _agent_body_id(agent_row=agent, body_rows=bodies, agent_id=agent_id)
        if body_id:
            body = _find_body(body_rows=bodies, body_id=body_id)
            if isinstance(body, dict):
                body["orientation_mdeg"] = dict(orientation)
                body["owner_agent_id"] = agent_id
            agent["body_id"] = body_id
            _refresh_agent_state_hash(agent_row=agent, body_row=body if isinstance(body, dict) else None)
        else:
            _refresh_agent_state_hash(agent_row=agent, body_row=None)
        result_metadata = {
            "agent_id": agent_id,
            "rotation_delta_mdeg": {
                "yaw": int(_as_int(delta_payload.get("yaw", 0), 0)),
                "pitch": int(_as_int(delta_payload.get("pitch", 0), 0)),
                "roll": int(_as_int(delta_payload.get("roll", 0), 0)),
            },
        }
        state["agent_states"] = sorted((dict(item) for item in agents if isinstance(item, dict)), key=lambda item: str(item.get("agent_id", "")))
        state["body_assemblies"] = sorted(
            (dict(item) for item in bodies if isinstance(item, dict) and str(item.get("assembly_id", "")).strip()),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        _advance_time(state, steps=1)
    elif process_id == "process.srz_transfer_entity":
        agent_id = str(inputs.get("agent_id", "") or inputs.get("target_agent_id", "")).strip()
        target_shard_id = str(inputs.get("target_shard_id", "")).strip()
        if not agent_id or not target_shard_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.srz_transfer_entity requires agent_id and target_shard_id",
                "Provide explicit agent_id and target_shard_id for deterministic SRZ transfer.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        policy_payload = dict(policy_context or {})
        control_policy = dict(policy_payload.get("control_policy") or {})
        allow_transfer = bool(policy_payload.get("allow_srz_transfer", False) or control_policy.get("allow_srz_transfer", False))
        if not allow_transfer:
            return refusal(
                "refusal.agent.boundary_cross_forbidden",
                "SRZ transfer is disabled by active control policy",
                "Enable control_policy.allow_srz_transfer in server policy or keep movement inside one shard.",
                {"agent_id": agent_id, "target_shard_id": target_shard_id},
                "$.intent.inputs.target_shard_id",
            )
        shard_map = dict(policy_payload.get("shard_map") or {})
        shard_rows = shard_map.get("shards")
        if isinstance(shard_rows, list):
            known_shards = _sorted_tokens(list((row or {}).get("shard_id", "") for row in shard_rows if isinstance(row, dict)))
            if target_shard_id not in known_shards:
                return refusal(
                    "refusal.net.shard_target_invalid",
                    "target_shard_id '{}' is not declared by active shard map".format(target_shard_id),
                    "Select target_shard_id present in shard_map.registry entries.",
                    {"target_shard_id": target_shard_id},
                    "$.intent.inputs.target_shard_id",
                )
        agent = _find_agent(agent_rows=agents, agent_id=agent_id)
        if not agent:
            return refusal(
                "refusal.control.target_invalid",
                "agent '{}' does not exist for SRZ transfer".format(agent_id),
                "Provide an existing agent_id before requesting SRZ transfer.",
                {"agent_id": agent_id},
                "$.intent.inputs.agent_id",
            )
        body_id = _agent_body_id(agent_row=agent, body_rows=bodies, agent_id=agent_id)
        agent["shard_id"] = target_shard_id
        agent["body_id"] = body_id or agent.get("body_id")
        body = _find_body(body_rows=bodies, body_id=body_id) if body_id else {}
        if isinstance(body, dict) and body:
            body["shard_id"] = target_shard_id
            body["owner_agent_id"] = agent_id
        _refresh_agent_state_hash(agent_row=agent, body_row=body if isinstance(body, dict) else None)
        state["agent_states"] = sorted((dict(item) for item in agents if isinstance(item, dict)), key=lambda item: str(item.get("agent_id", "")))
        state["body_assemblies"] = sorted(
            (dict(item) for item in bodies if isinstance(item, dict) and str(item.get("assembly_id", "")).strip()),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        _advance_time(state, steps=1)
    elif process_id in ("process.control_bind_camera", "process.camera_bind_target"):
        legacy = str(process_id) == "process.control_bind_camera"
        controller_id = str(inputs.get("controller_id", "")).strip()
        camera_id = str(inputs.get("camera_id", "")).strip() or "camera.main"
        if legacy and not str(inputs.get("camera_id", "")).strip():
            camera_id = str(inputs.get("target_id", "")).strip() or "camera.main"
        target_type = str(inputs.get("target_type", "none")).strip() or "none"
        target_id: str | None = None
        if legacy:
            target_type = "none"
            target_id = None
        else:
            raw_target_id = inputs.get("target_id")
            if raw_target_id is not None and str(raw_target_id).strip():
                target_id = str(raw_target_id).strip()
        if not controller_id or not camera_id:
            return refusal(
                "refusal.view.target_invalid",
                "{} requires controller_id and camera_id".format(process_id),
                "Provide controller_id and camera_id in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if not _camera_exists(state=state, camera_id=camera_id):
            return refusal(
                "refusal.view.target_invalid",
                "camera target '{}' does not exist".format(camera_id),
                "Bind to an existing camera assembly id.",
                {"camera_id": camera_id},
                "$.intent.inputs.camera_id",
            )
        if target_type not in ("agent", "body", "site", "none"):
            return refusal(
                "refusal.view.target_invalid",
                "target_type '{}' is unsupported".format(target_type),
                "Use target_type in {agent,body,site,none}.",
                {"target_type": target_type},
                "$.intent.inputs.target_type",
            )
        if target_type != "none" and not str(target_id or "").strip():
            return refusal(
                "refusal.view.target_invalid",
                "target_id is required when target_type is '{}'".format(target_type),
                "Provide target_id for non-none camera bindings.",
                {"target_type": target_type},
                "$.intent.inputs.target_id",
            )
        if not _camera_target_exists(
            state=state,
            target_type=target_type,
            target_id=str(target_id or ""),
            navigation_indices=navigation_indices,
        ):
            return refusal(
                "refusal.view.target_invalid",
                "camera target does not exist for type '{}' and id '{}'".format(target_type, str(target_id or "")),
                "Select an existing camera target or use target_type='none'.",
                {"target_type": target_type, "target_id": str(target_id or "")},
                "$.intent.inputs.target_id",
            )

        camera_row = _camera_row(state=state, camera_id=camera_id)
        _camera_defaults(camera_row)
        view_mode_id = str(inputs.get("view_mode_id", "")).strip() or str(camera_row.get("view_mode_id", "view.free.lab")).strip()
        control_policy = dict((policy_context or {}).get("control_policy") or {})
        allowed_view_modes = _sorted_tokens(list(control_policy.get("allowed_view_modes") or []))
        if allowed_view_modes and view_mode_id not in allowed_view_modes:
            return refusal(
                "refusal.view.mode_forbidden",
                "view mode '{}' is forbidden by active control policy".format(view_mode_id),
                "Select a view mode listed in control_policy.allowed_view_modes.",
                {"view_mode_id": view_mode_id},
                "$.intent.inputs.view_mode_id",
            )
        view_modes = _view_mode_entries(navigation_indices)
        if not view_modes:
            maps = _navigation_maps(navigation_indices)
            view_modes = dict(maps.get("view_modes") or {})
        view_mode = dict(view_modes.get(view_mode_id) or {})
        if not view_mode:
            return refusal(
                "refusal.view.mode_forbidden",
                "view mode '{}' is not declared in view mode registry".format(view_mode_id),
                "Use a view_mode_id present in view_mode.registry.json.",
                {"view_mode_id": view_mode_id},
                "$.intent.inputs.view_mode_id",
            )
        if not _view_mode_allowed_in_replication(view_mode=view_mode, policy_context=policy_context):
            return refusal(
                "refusal.view.mode_forbidden",
                "view mode '{}' is not permitted for active replication policy".format(view_mode_id),
                "Choose a view mode allowed by view_mode.allowed_in_policies.",
                {"view_mode_id": view_mode_id, "replication_policy": _replication_policy_tag(policy_context)},
                "$.intent.inputs.view_mode_id",
            )
        mode_entitlements = _sorted_tokens(list(view_mode.get("required_entitlements") or []))
        caller_entitlements = _sorted_tokens(list(authority_context.get("entitlements") or []))
        missing_mode_entitlements = [token for token in mode_entitlements if token not in caller_entitlements]
        if missing_mode_entitlements:
            return refusal(
                "refusal.view.entitlement_missing",
                "camera bind requires additional entitlements for view mode '{}'".format(view_mode_id),
                "Grant missing entitlements or choose a less privileged view mode.",
                {"missing_entitlements": ",".join(sorted(missing_mode_entitlements))},
                "$.authority_context.entitlements",
            )
        if bool(view_mode.get("requires_embodiment", False)) and not _is_embodied_target(
            state=state,
            target_type=target_type,
            target_id=str(target_id or ""),
        ):
            return refusal(
                "refusal.view.requires_embodiment",
                "view mode '{}' requires embodied target".format(view_mode_id),
                "Bind camera to embodied agent/body or choose a non-embodiment-required view mode.",
                {"view_mode_id": view_mode_id, "target_type": target_type, "target_id": str(target_id or "")},
                "$.intent.inputs",
            )
        shard_map = dict((policy_context or {}).get("shard_map") or {})
        active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
        control_policy = dict((policy_context or {}).get("control_policy") or {})
        allow_cross_shard_follow = bool(control_policy.get("allow_cross_shard_follow", False))
        target_owner_shard = _camera_target_owner_shard(
            state=state,
            target_type=target_type,
            target_id=str(target_id or ""),
            shard_map=shard_map,
            navigation_indices=navigation_indices,
        )
        if active_shard_id and target_owner_shard and target_owner_shard != active_shard_id:
            spectator_pattern = str((view_mode.get("extensions") or {}).get("spectator_pattern", "")).strip()
            if spectator_pattern != "follow_agent" or not allow_cross_shard_follow:
                return refusal(
                    "refusal.view.cross_shard_follow_forbidden",
                    "camera target shard '{}' does not match active shard '{}'".format(target_owner_shard, active_shard_id),
                    "Use same-shard camera target or enable cross-shard spectator follow policy.",
                    {
                        "camera_id": camera_id,
                        "view_mode_id": view_mode_id,
                        "active_shard_id": active_shard_id,
                        "target_shard_id": target_owner_shard,
                    },
                    "$.intent.inputs.target_id",
                )
        allowed_lenses = _sorted_tokens(list(view_mode.get("allowed_lens_ids") or []))
        current_lens = str(camera_row.get("lens_id", "")).strip()
        if allowed_lenses and current_lens and current_lens not in allowed_lenses:
            return refusal(
                "refusal.view.mode_forbidden",
                "camera lens '{}' is not permitted for view mode '{}'".format(current_lens, view_mode_id),
                "Set a lens declared by view_mode.allowed_lens_ids.",
                {"view_mode_id": view_mode_id, "lens_id": current_lens},
                "$.camera_assemblies",
            )
        watermark_policy_id = view_mode.get("watermark_policy_id")
        if watermark_policy_id is not None and str(watermark_policy_id).strip():
            if "entitlement.observer.truth" not in set(caller_entitlements):
                return refusal(
                    "refusal.view.watermark_required",
                    "observer truth view requires entitlement.observer.truth",
                    "Grant entitlement.observer.truth or choose non-observer view mode.",
                    {"view_mode_id": view_mode_id},
                    "$.intent.inputs.view_mode_id",
                )

        controller = _upsert_controller(
            controllers=controllers,
            controller_id=controller_id,
            controller_type=str(inputs.get("controller_type", "script")).strip() or "script",
            owner_peer_id=inputs.get("owner_peer_id", authority_context.get("authority_origin")),
        )
        controller["status"] = "active"
        for row in bindings:
            if str(row.get("binding_type", "")) != "camera":
                continue
            if not bool(row.get("active", True)):
                continue
            if str(row.get("controller_id", "")) == controller_id or str(row.get("target_id", "")) == camera_id:
                row["active"] = False

        binding_id = _binding_id(controller_id=controller_id, binding_type="camera", target_id=camera_id)
        binding = _find_binding(bindings=bindings, binding_id=binding_id)
        if not binding:
            bindings.append(
                {
                    "binding_id": binding_id,
                    "controller_id": controller_id,
                    "binding_type": "camera",
                    "target_id": camera_id,
                    "created_tick": int(current_tick),
                    "active": True,
                    "required_entitlements": _required_entitlements_for_binding("camera"),
                }
            )
        else:
            binding["active"] = True
            binding["created_tick"] = max(0, _as_int(binding.get("created_tick", current_tick), current_tick))
            binding["required_entitlements"] = _required_entitlements_for_binding("camera")
        camera_row["binding_id"] = binding_id
        camera_row["view_mode_id"] = view_mode_id
        camera_row["target_id"] = str(target_id or "").strip() if target_type != "none" else None
        camera_row["target_type"] = target_type
        camera_row["offset_params"] = _camera_binding_offset(inputs.get("offset_params"))
        camera_row["owner_peer_id"] = controller.get("owner_peer_id")

        state["camera_assemblies"] = sorted(
            (dict(item) for item in (state.get("camera_assemblies") or []) if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        _store_control_state(state=state, controllers=controllers, bindings=bindings)
        _advance_time(state, steps=1)
    elif process_id in ("process.control_unbind_camera", "process.camera_unbind_target"):
        controller_id = str(inputs.get("controller_id", "")).strip()
        camera_id = str(inputs.get("camera_id", "") or inputs.get("target_id", "")).strip()
        if not controller_id or not camera_id:
            return refusal(
                "refusal.view.target_invalid",
                "{} requires controller_id and camera_id".format(process_id),
                "Provide controller_id and camera_id in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if not _camera_exists(state=state, camera_id=camera_id):
            return refusal(
                "refusal.view.target_invalid",
                "camera target '{}' does not exist".format(camera_id),
                "Unbind from an existing camera assembly id.",
                {"camera_id": camera_id},
                "$.intent.inputs.camera_id",
            )
        for row in bindings:
            if str(row.get("binding_type", "")) != "camera":
                continue
            if str(row.get("controller_id", "")) != controller_id:
                continue
            if str(row.get("target_id", "")) != camera_id:
                continue
            row["active"] = False
        camera_row = _camera_row(state=state, camera_id=camera_id)
        if camera_row:
            _camera_defaults(camera_row)
            camera_row["binding_id"] = None
            camera_row["target_id"] = None
            camera_row["target_type"] = "none"
            camera_row["offset_params"] = _camera_binding_offset({})
        _store_control_state(state=state, controllers=controllers, bindings=bindings)
        _advance_time(state, steps=1)
    elif process_id == "process.camera_set_view_mode":
        controller_id = str(inputs.get("controller_id", "")).strip()
        camera_id = str(inputs.get("camera_id", "camera.main")).strip() or "camera.main"
        view_mode_id = str(inputs.get("view_mode_id", "")).strip()
        if not controller_id or not view_mode_id:
            return refusal(
                "refusal.view.target_invalid",
                "process.camera_set_view_mode requires controller_id and view_mode_id",
                "Provide controller_id and view_mode_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if not _camera_exists(state=state, camera_id=camera_id):
            return refusal(
                "refusal.view.target_invalid",
                "camera target '{}' does not exist".format(camera_id),
                "Select an existing camera assembly id before changing view mode.",
                {"camera_id": camera_id},
                "$.intent.inputs.camera_id",
            )
        view_modes = _view_mode_entries(navigation_indices)
        mode_row = dict(view_modes.get(view_mode_id) or {})
        if not mode_row:
            return refusal(
                "refusal.view.mode_forbidden",
                "view mode '{}' is not registered".format(view_mode_id),
                "Use a view_mode_id present in view_mode.registry.json.",
                {"view_mode_id": view_mode_id},
                "$.intent.inputs.view_mode_id",
            )
        if not _view_mode_allowed_in_replication(view_mode=mode_row, policy_context=policy_context):
            return refusal(
                "refusal.view.mode_forbidden",
                "view mode '{}' is not permitted for active replication policy".format(view_mode_id),
                "Choose a view mode allowed by view_mode.allowed_in_policies.",
                {"view_mode_id": view_mode_id, "replication_policy": _replication_policy_tag(policy_context)},
                "$.intent.inputs.view_mode_id",
            )
        control_policy = dict((policy_context or {}).get("control_policy") or {})
        allowed_view_modes = _sorted_tokens(list(control_policy.get("allowed_view_modes") or []))
        if allowed_view_modes and view_mode_id not in allowed_view_modes:
            return refusal(
                "refusal.view.mode_forbidden",
                "view mode '{}' is forbidden by active control policy".format(view_mode_id),
                "Select a view mode listed in control_policy.allowed_view_modes.",
                {"view_mode_id": view_mode_id},
                "$.intent.inputs.view_mode_id",
            )
        caller_entitlements = _sorted_tokens(list(authority_context.get("entitlements") or []))
        required_entitlements = _sorted_tokens(list(mode_row.get("required_entitlements") or []))
        missing_entitlements = [token for token in required_entitlements if token not in caller_entitlements]
        if missing_entitlements:
            return refusal(
                "refusal.view.entitlement_missing",
                "view mode '{}' requires additional entitlements".format(view_mode_id),
                "Grant missing entitlements or choose another view mode.",
                {"missing_entitlements": ",".join(sorted(missing_entitlements))},
                "$.authority_context.entitlements",
            )
        watermark_policy_id = str(mode_row.get("watermark_policy_id", "") or "").strip()
        if watermark_policy_id and "entitlement.observer.truth" not in set(caller_entitlements):
            return refusal(
                "refusal.view.watermark_required",
                "observer truth view mode requires entitlement.observer.truth",
                "Grant entitlement.observer.truth or select non-observer view mode.",
                {"view_mode_id": view_mode_id},
                "$.intent.inputs.view_mode_id",
            )

        camera_row = _camera_row(state=state, camera_id=camera_id)
        _camera_defaults(camera_row)
        target_type = str(inputs.get("target_type", camera_row.get("target_type", "none"))).strip() or "none"
        if target_type not in ("agent", "body", "site", "none"):
            return refusal(
                "refusal.view.target_invalid",
                "target_type '{}' is unsupported".format(target_type),
                "Use target_type in {agent,body,site,none}.",
                {"target_type": target_type},
                "$.intent.inputs.target_type",
            )
        target_id = str(inputs.get("target_id", "") or camera_row.get("target_id", "") or "").strip()
        if target_type != "none" and not target_id:
            return refusal(
                "refusal.view.target_invalid",
                "target_id is required when target_type is '{}'".format(target_type),
                "Provide target_id for non-none camera target type.",
                {"target_type": target_type},
                "$.intent.inputs.target_id",
            )
        if not _camera_target_exists(
            state=state,
            target_type=target_type,
            target_id=target_id,
            navigation_indices=navigation_indices,
        ):
            return refusal(
                "refusal.view.target_invalid",
                "camera target does not exist for type '{}' and id '{}'".format(target_type, target_id),
                "Bind camera to an existing target before switching mode.",
                {"target_type": target_type, "target_id": target_id},
                "$.intent.inputs.target_id",
            )
        if bool(mode_row.get("requires_embodiment", False)) and not _is_embodied_target(
            state=state,
            target_type=target_type,
            target_id=target_id,
        ):
            return refusal(
                "refusal.view.requires_embodiment",
                "view mode '{}' requires embodied target".format(view_mode_id),
                "Bind or set an embodied agent/body target before switching mode.",
                {"view_mode_id": view_mode_id, "target_type": target_type, "target_id": target_id},
                "$.intent.inputs.view_mode_id",
            )
        shard_map = dict((policy_context or {}).get("shard_map") or {})
        active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
        allow_cross_shard_follow = bool(control_policy.get("allow_cross_shard_follow", False))
        target_owner_shard = _camera_target_owner_shard(
            state=state,
            target_type=target_type,
            target_id=target_id,
            shard_map=shard_map,
            navigation_indices=navigation_indices,
        )
        if active_shard_id and target_owner_shard and target_owner_shard != active_shard_id:
            spectator_pattern = str((mode_row.get("extensions") or {}).get("spectator_pattern", "")).strip()
            if spectator_pattern != "follow_agent" or not allow_cross_shard_follow:
                return refusal(
                    "refusal.view.cross_shard_follow_forbidden",
                    "camera target shard '{}' does not match active shard '{}'".format(target_owner_shard, active_shard_id),
                    "Use same-shard camera target or enable cross-shard spectator follow policy.",
                    {
                        "camera_id": camera_id,
                        "view_mode_id": view_mode_id,
                        "active_shard_id": active_shard_id,
                        "target_shard_id": target_owner_shard,
                    },
                    "$.intent.inputs.target_id",
                )
        allowed_lenses = _sorted_tokens(list(mode_row.get("allowed_lens_ids") or []))
        current_lens = str(camera_row.get("lens_id", "")).strip()
        if allowed_lenses and current_lens and current_lens not in allowed_lenses:
            return refusal(
                "refusal.view.mode_forbidden",
                "camera lens '{}' is incompatible with requested view mode '{}'".format(current_lens, view_mode_id),
                "Set a compatible lens before switching view mode.",
                {"view_mode_id": view_mode_id, "lens_id": current_lens},
                "$.intent.inputs.view_mode_id",
            )
        _upsert_controller(
            controllers=controllers,
            controller_id=controller_id,
            controller_type=str(inputs.get("controller_type", "script")).strip() or "script",
            owner_peer_id=inputs.get("owner_peer_id", authority_context.get("authority_origin")),
        )
        camera_row["view_mode_id"] = view_mode_id
        camera_row["target_type"] = target_type
        camera_row["target_id"] = target_id if target_type != "none" else None
        state["camera_assemblies"] = sorted(
            (dict(item) for item in (state.get("camera_assemblies") or []) if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        _store_control_state(state=state, controllers=controllers, bindings=bindings)
        _advance_time(state, steps=1)
    elif process_id == "process.control_possess_agent":
        controller_id = str(inputs.get("controller_id", "")).strip()
        agent_id = str(inputs.get("agent_id", "") or inputs.get("target_id", "")).strip()
        if not controller_id or not agent_id:
            return refusal(
                "refusal.control.target_invalid",
                "process.control_possess_agent requires controller_id and agent_id",
                "Provide controller_id and agent_id in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if bool(inputs.get("possession_supported", True)) is False:
            return refusal(
                "refusal.control.possession_not_supported",
                "possession is explicitly disabled for this request payload",
                "Set possession_supported=true or use a process that does not require possession support.",
                {"agent_id": agent_id},
                "$.intent.inputs.possession_supported",
            )

        for row in bindings:
            if str(row.get("binding_type", "")) != "possess":
                continue
            if not bool(row.get("active", True)):
                continue
            if str(row.get("target_id", "")) != agent_id:
                continue
            if str(row.get("controller_id", "")) != controller_id:
                return refusal(
                    "refusal.control.already_possessed",
                    "agent '{}' is already possessed by controller '{}'".format(
                        agent_id,
                        str(row.get("controller_id", "")),
                    ),
                    "Release existing possession before binding a new controller.",
                    {"agent_id": agent_id, "controller_id": str(row.get("controller_id", ""))},
                    "$.intent.inputs.agent_id",
                )

        controller = _upsert_controller(
            controllers=controllers,
            controller_id=controller_id,
            controller_type=str(inputs.get("controller_type", "script")).strip() or "script",
            owner_peer_id=inputs.get("owner_peer_id", authority_context.get("authority_origin")),
        )
        controller["status"] = "active"
        for row in bindings:
            if str(row.get("binding_type", "")) != "possess":
                continue
            if not bool(row.get("active", True)):
                continue
            if str(row.get("controller_id", "")) == controller_id and str(row.get("target_id", "")) != agent_id:
                row["active"] = False

        binding_id = _binding_id(controller_id=controller_id, binding_type="possess", target_id=agent_id)
        binding = _find_binding(bindings=bindings, binding_id=binding_id)
        if not binding:
            bindings.append(
                {
                    "binding_id": binding_id,
                    "controller_id": controller_id,
                    "binding_type": "possess",
                    "target_id": agent_id,
                    "created_tick": int(current_tick),
                    "active": True,
                    "required_entitlements": _required_entitlements_for_binding("possess"),
                }
            )
        else:
            binding["active"] = True
            binding["created_tick"] = max(0, _as_int(binding.get("created_tick", current_tick), current_tick))
            binding["required_entitlements"] = _required_entitlements_for_binding("possess")
        _store_control_state(state=state, controllers=controllers, bindings=bindings)
        _advance_time(state, steps=1)
    elif process_id == "process.control_release_agent":
        controller_id = str(inputs.get("controller_id", "")).strip()
        agent_id = str(inputs.get("agent_id", "") or inputs.get("target_id", "")).strip()
        if not controller_id or not agent_id:
            return refusal(
                "refusal.control.target_invalid",
                "process.control_release_agent requires controller_id and agent_id",
                "Provide controller_id and agent_id in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        for row in bindings:
            if str(row.get("binding_type", "")) != "possess":
                continue
            if str(row.get("controller_id", "")) != controller_id:
                continue
            if str(row.get("target_id", "")) != agent_id:
                continue
            row["active"] = False
        _store_control_state(state=state, controllers=controllers, bindings=bindings)
        _advance_time(state, steps=1)
    elif process_id == "process.faction_create":
        founder_agent_raw = inputs.get("founder_agent_id")
        founder_agent_id = None if founder_agent_raw is None else str(founder_agent_raw).strip() or None
        if founder_agent_id and not _find_agent(agent_rows=agents, agent_id=founder_agent_id):
            return refusal(
                "PROCESS_INPUT_INVALID",
                "founder_agent_id '{}' does not exist".format(founder_agent_id),
                "Provide existing founder_agent_id or null founder_agent_id.",
                {"founder_agent_id": founder_agent_id},
                "$.intent.inputs.founder_agent_id",
            )
        governance_type_id = str(inputs.get("governance_type_id", "gov.none")).strip() or "gov.none"
        governance_rows = _governance_type_rows(policy_context)
        if governance_rows and governance_type_id not in governance_rows:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "governance_type_id '{}' is not registered".format(governance_type_id),
                "Use governance_type_id from governance_type_registry.",
                {"governance_type_id": governance_type_id},
                "$.intent.inputs.governance_type_id",
            )
        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        faction_id = str(inputs.get("faction_id", "")).strip() or _deterministic_faction_id(
            founder_agent_id=founder_agent_id,
            created_tick=current_tick,
        )
        if _find_faction(faction_rows=faction_rows, faction_id=faction_id):
            return refusal(
                "refusal.civ.claim_forbidden",
                "faction_id '{}' already exists".format(faction_id),
                "Use a different founder/tick or provide unique faction_id override.",
                {"faction_id": faction_id},
                "$.intent.inputs.faction_id",
            )
        owner_peer_id = _authority_peer_token(authority_context)
        extensions = dict(inputs.get("extensions") or {}) if isinstance(inputs.get("extensions"), dict) else {}
        if owner_peer_id and "owner_peer_id" not in extensions:
            extensions["owner_peer_id"] = owner_peer_id
        faction_rows.append(
            {
                "faction_id": faction_id,
                "human_name": str(inputs.get("human_name", "")).strip() or faction_id,
                "description": str(inputs.get("description", "")).strip(),
                "created_tick": int(current_tick),
                "founder_agent_id": founder_agent_id,
                "governance_type_id": governance_type_id,
                "territory_ids": [],
                "diplomatic_relations": {},
                "status": "active",
                "extensions": extensions,
            }
        )
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
        )
        result_metadata = {
            "faction_id": faction_id,
            "governance_type_id": governance_type_id,
            "founder_agent_id": founder_agent_id,
        }
        _advance_time(state, steps=1)
    elif process_id == "process.faction_dissolve":
        faction_id = str(inputs.get("faction_id", "")).strip()
        if not faction_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.faction_dissolve requires faction_id",
                "Provide faction_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.faction_id",
            )
        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        faction_row = _find_faction(faction_rows=faction_rows, faction_id=faction_id)
        if not faction_row:
            return refusal(
                "refusal.civ.claim_forbidden",
                "faction '{}' does not exist".format(faction_id),
                "Use existing faction_id for dissolution.",
                {"faction_id": faction_id},
                "$.intent.inputs.faction_id",
            )
        ownership_check = _require_faction_owner_authority(faction_row=faction_row, authority_context=authority_context)
        if ownership_check.get("result") != "complete":
            return ownership_check

        released_territory_ids: List[str] = []
        for territory_row in territory_rows:
            if str(territory_row.get("owner_faction_id", "")).strip() != faction_id:
                continue
            territory_row["owner_faction_id"] = None
            territory_row["claim_status"] = "unclaimed"
            ext = dict(territory_row.get("extensions") or {}) if isinstance(territory_row.get("extensions"), dict) else {}
            if "contested_by_faction_ids" in ext:
                ext.pop("contested_by_faction_ids", None)
            territory_row["extensions"] = ext
            released_territory_ids.append(str(territory_row.get("territory_id", "")).strip())

        cleared_subject_ids: List[str] = []
        for affiliation_row in affiliation_rows:
            if str(affiliation_row.get("faction_id", "")).strip() != faction_id:
                continue
            affiliation_row["faction_id"] = None
            affiliation_row["joined_tick"] = int(current_tick)
            cleared_subject_ids.append(str(affiliation_row.get("subject_id", "")).strip())

        diplomatic_rows = [
            dict(row)
            for row in diplomatic_rows
            if isinstance(row, dict)
            and str(row.get("faction_a", "")).strip() != faction_id
            and str(row.get("faction_b", "")).strip() != faction_id
        ]
        for row in faction_rows:
            row_id = str(row.get("faction_id", "")).strip()
            relation_map = dict(row.get("diplomatic_relations") or {}) if isinstance(row.get("diplomatic_relations"), dict) else {}
            if faction_id in relation_map:
                relation_map.pop(faction_id, None)
            if row_id == faction_id:
                row["status"] = "dissolved"
                row["territory_ids"] = []
                row["diplomatic_relations"] = {}
            else:
                row["diplomatic_relations"] = dict((token, relation_map[token]) for token in sorted(relation_map.keys()))
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
        )
        result_metadata = {
            "faction_id": faction_id,
            "released_territory_ids": _sorted_tokens(released_territory_ids),
            "cleared_subject_ids": _sorted_tokens(cleared_subject_ids),
            "status": "dissolved",
        }
        _advance_time(state, steps=1)
    elif process_id == "process.affiliation_join":
        subject_id = str(inputs.get("subject_id", "")).strip()
        faction_id = str(inputs.get("faction_id", "")).strip()
        if not subject_id or not faction_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.affiliation_join requires subject_id and faction_id",
                "Provide subject_id and faction_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if not _subject_exists(state=state, subject_id=subject_id):
            return refusal(
                "refusal.control.target_invalid",
                "subject '{}' does not exist".format(subject_id),
                "Use subject_id from known agent/cohort records.",
                {"subject_id": subject_id},
                "$.intent.inputs.subject_id",
            )
        caller_peer_id = _authority_peer_token(authority_context)
        admin_override = _civ_admin_override(authority_context)
        subject_agent = _find_agent(agent_rows=agents, agent_id=subject_id)
        subject_owner_peer_id = str((subject_agent or {}).get("owner_peer_id", "")).strip()
        if subject_owner_peer_id and (not admin_override) and caller_peer_id != subject_owner_peer_id:
            return refusal(
                "refusal.civ.ownership_violation",
                "caller peer '{}' cannot mutate subject '{}' owned by '{}'".format(
                    caller_peer_id or "<unknown>",
                    subject_id,
                    subject_owner_peer_id,
                ),
                "Use subject owner authority context or admin override entitlement.",
                {
                    "subject_id": subject_id,
                    "caller_peer_id": caller_peer_id or "<unknown>",
                    "owner_peer_id": subject_owner_peer_id,
                },
                "$.authority_context.peer_id",
            )

        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        faction_row = _find_faction(faction_rows=faction_rows, faction_id=faction_id)
        if not faction_row or str(faction_row.get("status", "")).strip() != "active":
            return refusal(
                "refusal.civ.claim_forbidden",
                "faction '{}' is unavailable for affiliation".format(faction_id),
                "Join an active faction_id.",
                {"faction_id": faction_id},
                "$.intent.inputs.faction_id",
            )
        ownership_check = _require_faction_owner_authority(faction_row=faction_row, authority_context=authority_context)
        if ownership_check.get("result") != "complete":
            return ownership_check

        existing_affiliation = _find_affiliation(affiliation_rows=affiliation_rows, subject_id=subject_id)
        if existing_affiliation and str(existing_affiliation.get("faction_id", "")).strip():
            return refusal(
                "refusal.civ.already_affiliated",
                "subject '{}' is already affiliated with faction '{}'".format(
                    subject_id,
                    str(existing_affiliation.get("faction_id", "")).strip(),
                ),
                "Leave current faction before joining another.",
                {
                    "subject_id": subject_id,
                    "faction_id": str(existing_affiliation.get("faction_id", "")).strip(),
                },
                "$.intent.inputs.subject_id",
            )
        if not existing_affiliation:
            existing_affiliation = {
                "subject_id": subject_id,
                "faction_id": None,
                "joined_tick": int(current_tick),
                "role_id": "role.member",
                "extensions": {},
            }
            affiliation_rows.append(existing_affiliation)
        existing_affiliation["faction_id"] = faction_id
        existing_affiliation["joined_tick"] = int(current_tick)
        existing_affiliation["role_id"] = str(inputs.get("role_id", "role.member")).strip() or "role.member"
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
        )
        result_metadata = {
            "subject_id": subject_id,
            "faction_id": faction_id,
            "role_id": str(existing_affiliation.get("role_id", "")),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.affiliation_leave":
        subject_id = str(inputs.get("subject_id", "")).strip()
        if not subject_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.affiliation_leave requires subject_id",
                "Provide subject_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.subject_id",
            )
        if not _subject_exists(state=state, subject_id=subject_id):
            return refusal(
                "refusal.control.target_invalid",
                "subject '{}' does not exist".format(subject_id),
                "Use subject_id from known agent/cohort records.",
                {"subject_id": subject_id},
                "$.intent.inputs.subject_id",
            )
        caller_peer_id = _authority_peer_token(authority_context)
        admin_override = _civ_admin_override(authority_context)
        subject_agent = _find_agent(agent_rows=agents, agent_id=subject_id)
        subject_owner_peer_id = str((subject_agent or {}).get("owner_peer_id", "")).strip()
        if subject_owner_peer_id and (not admin_override) and caller_peer_id != subject_owner_peer_id:
            return refusal(
                "refusal.civ.ownership_violation",
                "caller peer '{}' cannot clear affiliation for subject '{}' owned by '{}'".format(
                    caller_peer_id or "<unknown>",
                    subject_id,
                    subject_owner_peer_id,
                ),
                "Use subject owner authority context or admin override entitlement.",
                {
                    "subject_id": subject_id,
                    "caller_peer_id": caller_peer_id or "<unknown>",
                    "owner_peer_id": subject_owner_peer_id,
                },
                "$.authority_context.peer_id",
            )
        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        affiliation_row = _find_affiliation(affiliation_rows=affiliation_rows, subject_id=subject_id)
        left_faction_id = ""
        if affiliation_row:
            left_faction_id = str(affiliation_row.get("faction_id", "")).strip()
            affiliation_row["faction_id"] = None
            affiliation_row["joined_tick"] = int(current_tick)
            affiliation_row["role_id"] = str(affiliation_row.get("role_id", "role.member")).strip() or "role.member"
        else:
            affiliation_rows.append(
                {
                    "subject_id": subject_id,
                    "faction_id": None,
                    "joined_tick": int(current_tick),
                    "role_id": "role.member",
                    "extensions": {},
                }
            )
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
        )
        result_metadata = {
            "subject_id": subject_id,
            "left_faction_id": left_faction_id,
        }
        _advance_time(state, steps=1)
    elif process_id == "process.territory_claim":
        faction_id = str(inputs.get("faction_id", "")).strip()
        territory_id = str(inputs.get("territory_id", "")).strip()
        region_scope = dict(inputs.get("region_scope") or {}) if isinstance(inputs.get("region_scope"), dict) else {}
        if not faction_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.territory_claim requires faction_id",
                "Provide faction_id and territory_id or region_scope in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.faction_id",
            )
        if not territory_id and not region_scope:
            return refusal(
                "refusal.civ.territory_invalid",
                "territory claim requires territory_id or region_scope descriptor",
                "Provide territory_id or deterministic region_scope payload.",
                {"faction_id": faction_id},
                "$.intent.inputs",
            )
        if not territory_id:
            territory_id = "territory.{}".format(canonical_sha256(region_scope)[:16])

        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        faction_row = _find_faction(faction_rows=faction_rows, faction_id=faction_id)
        if not faction_row or str(faction_row.get("status", "")).strip() != "active":
            return refusal(
                "refusal.civ.claim_forbidden",
                "faction '{}' cannot claim territory".format(faction_id),
                "Use active faction_id with territory claim entitlement.",
                {"faction_id": faction_id},
                "$.intent.inputs.faction_id",
            )
        ownership_check = _require_faction_owner_authority(faction_row=faction_row, authority_context=authority_context)
        if ownership_check.get("result") != "complete":
            return ownership_check

        territory_row = _find_territory(territory_rows=territory_rows, territory_id=territory_id)
        if not territory_row:
            territory_row = {
                "territory_id": territory_id,
                "region_scope": dict(region_scope),
                "owner_faction_id": None,
                "claim_status": "unclaimed",
                "created_tick": int(current_tick),
                "extensions": {},
            }
            territory_rows.append(territory_row)
        elif (not territory_row.get("region_scope")) and region_scope:
            territory_row["region_scope"] = dict(region_scope)

        owner_before_raw = territory_row.get("owner_faction_id")
        owner_before = "" if owner_before_raw is None else str(owner_before_raw).strip()
        owner_after = owner_before
        claim_status = str(territory_row.get("claim_status", "unclaimed")).strip() or "unclaimed"
        territory_extensions = (
            dict(territory_row.get("extensions") or {}) if isinstance(territory_row.get("extensions"), dict) else {}
        )
        if not owner_before:
            owner_after = faction_id
            claim_status = "claimed"
            territory_extensions.pop("contested_by_faction_ids", None)
        elif owner_before == faction_id:
            owner_after = faction_id
            claim_status = "claimed"
            territory_extensions.pop("contested_by_faction_ids", None)
        else:
            owner_after = sorted([owner_before, faction_id])[0]
            claim_status = "contested"
            contested_by = _sorted_tokens(list(territory_extensions.get("contested_by_faction_ids") or []))
            if owner_before and owner_before not in contested_by:
                contested_by.append(owner_before)
            if faction_id not in contested_by:
                contested_by.append(faction_id)
            territory_extensions["contested_by_faction_ids"] = _sorted_tokens(contested_by)
        territory_row["owner_faction_id"] = owner_after if owner_after else None
        territory_row["claim_status"] = claim_status
        territory_row["extensions"] = territory_extensions

        for row in faction_rows:
            row_id = str(row.get("faction_id", "")).strip()
            if row_id == owner_after:
                _add_faction_territory(row, territory_id=territory_id)
            else:
                _drop_faction_territory(row, territory_id=territory_id)

        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
        )
        result_metadata = {
            "faction_id": faction_id,
            "territory_id": territory_id,
            "claim_status": claim_status,
            "owner_faction_id": owner_after or "",
        }
        _advance_time(state, steps=1)
    elif process_id == "process.territory_release":
        faction_id = str(inputs.get("faction_id", "")).strip()
        territory_id = str(inputs.get("territory_id", "")).strip()
        if not faction_id or not territory_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.territory_release requires faction_id and territory_id",
                "Provide faction_id and territory_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        faction_row = _find_faction(faction_rows=faction_rows, faction_id=faction_id)
        if not faction_row or str(faction_row.get("status", "")).strip() != "active":
            return refusal(
                "refusal.civ.claim_forbidden",
                "faction '{}' cannot release territory".format(faction_id),
                "Use active owning faction for territory release.",
                {"faction_id": faction_id},
                "$.intent.inputs.faction_id",
            )
        ownership_check = _require_faction_owner_authority(faction_row=faction_row, authority_context=authority_context)
        if ownership_check.get("result") != "complete":
            return ownership_check

        territory_row = _find_territory(territory_rows=territory_rows, territory_id=territory_id)
        if not territory_row:
            return refusal(
                "refusal.civ.territory_invalid",
                "territory '{}' does not exist".format(territory_id),
                "Use existing territory_id for release.",
                {"territory_id": territory_id},
                "$.intent.inputs.territory_id",
            )
        owner_faction_raw = territory_row.get("owner_faction_id")
        owner_faction_id = "" if owner_faction_raw is None else str(owner_faction_raw).strip()
        if owner_faction_id != faction_id:
            return refusal(
                "refusal.civ.claim_forbidden",
                "faction '{}' is not owner of territory '{}'".format(faction_id, territory_id),
                "Only owner faction may release a claimed territory.",
                {
                    "faction_id": faction_id,
                    "territory_id": territory_id,
                    "owner_faction_id": owner_faction_id,
                },
                "$.intent.inputs.faction_id",
            )
        territory_row["owner_faction_id"] = None
        territory_row["claim_status"] = "unclaimed"
        territory_extensions = (
            dict(territory_row.get("extensions") or {}) if isinstance(territory_row.get("extensions"), dict) else {}
        )
        territory_extensions.pop("contested_by_faction_ids", None)
        territory_row["extensions"] = territory_extensions
        for row in faction_rows:
            _drop_faction_territory(row, territory_id=territory_id)
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
        )
        result_metadata = {
            "faction_id": faction_id,
            "territory_id": territory_id,
            "claim_status": "unclaimed",
        }
        _advance_time(state, steps=1)
    elif process_id == "process.diplomacy_set_relation":
        faction_a = str(inputs.get("faction_a", "")).strip()
        faction_b = str(inputs.get("faction_b", "")).strip()
        relation_state = str(inputs.get("relation_state", "")).strip()
        if not faction_a or not faction_b or not relation_state or faction_a == faction_b:
            return refusal(
                "refusal.civ.relation_invalid",
                "diplomacy update requires faction_a, faction_b, relation_state and distinct faction ids",
                "Provide valid relation update payload and distinct faction ids.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        relation_rows = _diplomatic_state_rows(policy_context)
        if not relation_rows or relation_state not in relation_rows:
            return refusal(
                "refusal.civ.relation_invalid",
                "relation_state '{}' is not registered".format(relation_state),
                "Use relation_state from diplomatic_state_registry.",
                {"relation_state": relation_state},
                "$.intent.inputs.relation_state",
            )
        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        faction_a_row = _find_faction(faction_rows=faction_rows, faction_id=faction_a)
        faction_b_row = _find_faction(faction_rows=faction_rows, faction_id=faction_b)
        if not faction_a_row or not faction_b_row:
            return refusal(
                "refusal.civ.relation_invalid",
                "faction pair '{}'/'{}' is invalid".format(faction_a, faction_b),
                "Use existing faction ids for diplomacy updates.",
                {"faction_a": faction_a, "faction_b": faction_b},
                "$.intent.inputs",
            )
        if str(faction_a_row.get("status", "")).strip() != "active" or str(faction_b_row.get("status", "")).strip() != "active":
            return refusal(
                "refusal.civ.relation_invalid",
                "diplomacy update requires active factions",
                "Reactivate factions or use active faction ids.",
                {"faction_a": faction_a, "faction_b": faction_b},
                "$.intent.inputs",
            )
        ownership_check = _require_faction_owner_authority(faction_row=faction_a_row, authority_context=authority_context)
        if ownership_check.get("result") != "complete":
            return ownership_check

        left, right = _canonical_faction_pair(faction_a=faction_a, faction_b=faction_b)
        relation_row = {}
        for row in diplomatic_rows:
            if not isinstance(row, dict):
                continue
            if str(row.get("faction_a", "")).strip() == left and str(row.get("faction_b", "")).strip() == right:
                relation_row = row
                break
        if not relation_row:
            relation_row = {
                "faction_a": left,
                "faction_b": right,
                "relation_state": relation_state,
                "updated_tick": int(current_tick),
                "extensions": {},
            }
            diplomatic_rows.append(relation_row)
        relation_row["relation_state"] = relation_state
        relation_row["updated_tick"] = int(current_tick)
        if not isinstance(relation_row.get("extensions"), dict):
            relation_row["extensions"] = {}

        for row in faction_rows:
            faction_id = str(row.get("faction_id", "")).strip()
            relation_map = dict(row.get("diplomatic_relations") or {}) if isinstance(row.get("diplomatic_relations"), dict) else {}
            if faction_id == left:
                relation_map[right] = relation_state
            elif faction_id == right:
                relation_map[left] = relation_state
            row["diplomatic_relations"] = dict((token, relation_map[token]) for token in sorted(relation_map.keys()))

        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
        )
        result_metadata = {
            "faction_a": left,
            "faction_b": right,
            "relation_state": relation_state,
        }
        _advance_time(state, steps=1)
    elif process_id == "process.cohort_create":
        size = _as_int(inputs.get("size", -1), -1)
        if size <= 0:
            return refusal(
                "refusal.civ.invalid_size",
                "cohort creation requires size > 0",
                "Provide positive integer size in intent.inputs.size.",
                {"size": str(size)},
                "$.intent.inputs.size",
            )
        location_ref = str(inputs.get("location_ref", "") or inputs.get("region_id", "")).strip()
        if not location_ref:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.cohort_create requires location_ref",
                "Provide deterministic location_ref (site_id or region_id).",
                {"process_id": process_id},
                "$.intent.inputs.location_ref",
            )
        mapping_policy_id = str(inputs.get("mapping_policy_id", "")).strip()
        policy_rows = _cohort_mapping_policy_rows(policy_context)
        if not mapping_policy_id or mapping_policy_id not in policy_rows:
            return refusal(
                "refusal.civ.policy_missing",
                "cohort mapping policy '{}' is unavailable".format(mapping_policy_id or "<missing>"),
                "Provide mapping_policy_id from cohort_mapping_policy_registry.",
                {"mapping_policy_id": mapping_policy_id or "<missing>"},
                "$.intent.inputs.mapping_policy_id",
            )
        faction_value = inputs.get("faction_id")
        faction_id = None if faction_value is None else str(faction_value).strip() or None
        territory_value = inputs.get("territory_id")
        territory_id = None if territory_value is None else str(territory_value).strip() or None
        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        if faction_id:
            faction_row = _find_faction(faction_rows=faction_rows, faction_id=faction_id)
            if not faction_row or str(faction_row.get("status", "")).strip() != "active":
                return refusal(
                    "refusal.civ.claim_forbidden",
                    "cohort faction '{}' is unavailable".format(faction_id),
                    "Use active faction_id for cohort creation or null faction_id.",
                    {"faction_id": faction_id},
                    "$.intent.inputs.faction_id",
                )
            ownership_check = _require_faction_owner_authority(faction_row=faction_row, authority_context=authority_context)
            if ownership_check.get("result") != "complete":
                return ownership_check
        size_bucket = max(1, int(size))
        cohort_id = str(inputs.get("cohort_id", "")).strip() or _deterministic_cohort_id(
            faction_id=faction_id,
            location_ref=location_ref,
            created_tick=current_tick,
            size_bucket=size_bucket,
        )
        if _find_cohort(cohort_rows=cohorts, cohort_id=cohort_id):
            return refusal(
                "refusal.civ.claim_forbidden",
                "cohort_id '{}' already exists".format(cohort_id),
                "Use a distinct cohort_id or deterministic input tuple.",
                {"cohort_id": cohort_id},
                "$.intent.inputs.cohort_id",
            )
        cohort_row = {
            "cohort_id": cohort_id,
            "size": int(size),
            "faction_id": faction_id,
            "territory_id": territory_id,
            "location_ref": location_ref,
            "demographic_tags": dict(inputs.get("demographic_tags") or {}) if isinstance(inputs.get("demographic_tags"), dict) else {},
            "skill_distribution": dict(inputs.get("skill_distribution") or {})
            if isinstance(inputs.get("skill_distribution"), dict)
            else {},
            "refinement_state": "macro",
            "created_tick": int(current_tick),
            "extensions": {
                "mapping_policy_id": mapping_policy_id,
                "expanded_micro_count": 0,
            },
        }
        cohorts.append(cohort_row)
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
            cohort_rows=cohorts,
        )
        result_metadata = {
            "cohort_id": cohort_id,
            "size": int(size),
            "location_ref": location_ref,
            "mapping_policy_id": mapping_policy_id,
        }
        _advance_time(state, steps=1)
    elif process_id == "process.cohort_expand_to_micro":
        cohort_id = str(inputs.get("cohort_id", "")).strip()
        if not cohort_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.cohort_expand_to_micro requires cohort_id",
                "Provide cohort_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.cohort_id",
            )
        cohort_row = _find_cohort(cohort_rows=cohorts, cohort_id=cohort_id)
        if not cohort_row:
            return refusal(
                "refusal.control.target_invalid",
                "cohort '{}' does not exist".format(cohort_id),
                "Use an existing cohort_id from cohort assemblies.",
                {"cohort_id": cohort_id},
                "$.intent.inputs.cohort_id",
            )
        interest_region_id = str(inputs.get("interest_region_id", "")).strip() or str(cohort_row.get("location_ref", "")).strip()
        mapping_policy_id = _cohort_policy_id(
            cohort_row=cohort_row,
            fallback=str(inputs.get("mapping_policy_id", "")).strip(),
        )
        policy_rows = _cohort_mapping_policy_rows(policy_context)
        mapping_policy = dict(policy_rows.get(mapping_policy_id) or {})
        if not mapping_policy:
            return refusal(
                "refusal.civ.policy_missing",
                "mapping policy '{}' is unavailable".format(mapping_policy_id or "<missing>"),
                "Provide cohort mapping policy registry entry and valid mapping_policy_id.",
                {"mapping_policy_id": mapping_policy_id or "<missing>", "cohort_id": cohort_id},
                "$.intent.inputs.mapping_policy_id",
            )
        requested_max = _as_int(inputs.get("max_micro_agents", -1), -1)
        if requested_max < -1:
            return refusal(
                "refusal.civ.invalid_size",
                "max_micro_agents must be >= 0 when provided",
                "Set max_micro_agents to non-negative integer or omit it.",
                {"max_micro_agents": str(requested_max)},
                "$.intent.inputs.max_micro_agents",
            )
        policy_max = max(0, _as_int(mapping_policy.get("max_micro_agents_per_cohort", 0), 0))
        if requested_max >= 0:
            target_max = min(policy_max, int(requested_max))
        else:
            target_max = int(policy_max)
        shard_map = dict((policy_context or {}).get("shard_map") or {})
        active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
        owner_shard_id = _cohort_owner_shard_id(cohort_row=cohort_row, shard_map=shard_map)
        if active_shard_id and owner_shard_id and owner_shard_id != active_shard_id:
            return refusal(
                "refusal.civ.cohort_cross_shard_forbidden",
                "cohort '{}' belongs to shard '{}' not active shard '{}'".format(cohort_id, owner_shard_id, active_shard_id),
                "Route expansion to owning shard or transfer cohort deterministically first.",
                {"cohort_id": cohort_id, "owner_shard_id": owner_shard_id, "active_shard_id": active_shard_id},
                "$.policy_context.active_shard_id",
            )
        deterministic_seed = _cohort_seed_material(
            cohort_id=cohort_id,
            tick=int(current_tick),
            policy_context=policy_context,
            mapping_policy_id=mapping_policy_id,
            interest_region_id=interest_region_id,
        )
        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        expanded = _expand_cohort_to_micro_internal(
            state=state,
            cohort_row=cohort_row,
            cohort_rows=cohorts,
            affiliation_rows=affiliation_rows,
            interest_region_id=interest_region_id,
            max_micro_agents=max(0, int(target_max)),
            mapping_policy_id=mapping_policy_id,
            policy_context=policy_context,
            current_tick=int(current_tick),
            deterministic_seed=deterministic_seed,
        )
        if expanded.get("result") != "complete":
            return expanded
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
            cohort_rows=cohorts,
        )
        expanded_micro_count = int(expanded.get("expanded_micro_count", 0))
        cohort_size = max(0, _as_int(cohort_row.get("size", 0), 0))
        result_metadata = {
            "cohort_id": cohort_id,
            "interest_region_id": interest_region_id,
            "mapping_policy_id": mapping_policy_id,
            "deterministic_seed": deterministic_seed,
            "expanded_micro_count": expanded_micro_count,
            "partial_expansion": bool(expanded_micro_count < min(cohort_size, max(0, int(target_max)))),
            "created_agent_ids": list(expanded.get("created_agent_ids") or []),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.cohort_collapse_from_micro":
        cohort_id = str(inputs.get("cohort_id", "")).strip()
        if not cohort_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.cohort_collapse_from_micro requires cohort_id",
                "Provide cohort_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.cohort_id",
            )
        cohort_row = _find_cohort(cohort_rows=cohorts, cohort_id=cohort_id)
        if not cohort_row:
            return refusal(
                "refusal.control.target_invalid",
                "cohort '{}' does not exist".format(cohort_id),
                "Use an existing cohort_id from cohort assemblies.",
                {"cohort_id": cohort_id},
                "$.intent.inputs.cohort_id",
            )
        shard_map = dict((policy_context or {}).get("shard_map") or {})
        active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
        owner_shard_id = _cohort_owner_shard_id(cohort_row=cohort_row, shard_map=shard_map)
        if active_shard_id and owner_shard_id and owner_shard_id != active_shard_id:
            return refusal(
                "refusal.civ.cohort_cross_shard_forbidden",
                "cohort '{}' belongs to shard '{}' not active shard '{}'".format(cohort_id, owner_shard_id, active_shard_id),
                "Route collapse to owning shard or transfer cohort deterministically first.",
                {"cohort_id": cohort_id, "owner_shard_id": owner_shard_id, "active_shard_id": active_shard_id},
                "$.policy_context.active_shard_id",
            )
        faction_rows = _ensure_faction_assemblies(state)
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        collapsed = _collapse_cohort_from_micro_internal(
            state=state,
            cohort_row=cohort_row,
            affiliation_rows=affiliation_rows,
            current_tick=int(current_tick),
        )
        if collapsed.get("result") != "complete":
            return collapsed
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
            cohort_rows=cohorts,
        )
        result_metadata = {
            "cohort_id": cohort_id,
            "collapsed_agent_ids": list(collapsed.get("collapsed_agent_ids") or []),
            "size": int(collapsed.get("size", 0)),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.affiliation_change_micro":
        subject_id = str(inputs.get("subject_id", "")).strip()
        if not subject_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.affiliation_change_micro requires subject_id",
                "Provide micro agent subject_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.subject_id",
            )
        subject_row = _find_agent(agent_rows=agents, agent_id=subject_id)
        if not subject_row or not str(subject_row.get("parent_cohort_id", "")).strip():
            return refusal(
                "refusal.control.target_invalid",
                "subject '{}' is not a micro cohort agent".format(subject_id),
                "Use an expanded micro agent id with parent_cohort_id.",
                {"subject_id": subject_id},
                "$.intent.inputs.subject_id",
            )
        faction_value = inputs.get("faction_id")
        faction_id = None if faction_value is None else str(faction_value).strip() or None
        faction_rows = _ensure_faction_assemblies(state)
        if faction_id:
            faction_row = _find_faction(faction_rows=faction_rows, faction_id=faction_id)
            if not faction_row or str(faction_row.get("status", "")).strip() != "active":
                return refusal(
                    "refusal.civ.claim_forbidden",
                    "faction '{}' is unavailable for micro affiliation update".format(faction_id),
                    "Use active faction_id or null to clear affiliation.",
                    {"faction_id": faction_id},
                    "$.intent.inputs.faction_id",
                )
        affiliation_rows = _ensure_affiliations(state)
        territory_rows = _ensure_territory_assemblies(state)
        diplomatic_rows = _ensure_diplomatic_relations(state)
        updated = _apply_affiliation_change(
            affiliation_rows=affiliation_rows,
            subject_id=subject_id,
            faction_id=faction_id,
            current_tick=int(current_tick),
        )
        _persist_civ_state(
            state=state,
            faction_rows=faction_rows,
            affiliation_rows=affiliation_rows,
            territory_rows=territory_rows,
            diplomatic_rows=diplomatic_rows,
            cohort_rows=cohorts,
        )
        result_metadata = {
            "subject_id": subject_id,
            "faction_id": updated.get("faction_id"),
            "joined_tick": int(updated.get("joined_tick", 0)),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.order_create":
        order_type_id = str(inputs.get("order_type_id", "")).strip()
        target_kind = str(inputs.get("target_kind", "")).strip()
        target_id = str(inputs.get("target_id", "")).strip()
        payload = dict(inputs.get("payload") or {}) if isinstance(inputs.get("payload"), dict) else {}
        if not order_type_id or not target_kind or not target_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.order_create requires order_type_id, target_kind, and target_id",
                "Provide deterministic order target fields and payload in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if target_kind not in ("agent", "cohort", "faction", "territory"):
            return refusal(
                "PROCESS_INPUT_INVALID",
                "target_kind '{}' is unsupported".format(target_kind),
                "Use target_kind in {agent,cohort,faction,territory}.",
                {"target_kind": target_kind},
                "$.intent.inputs.target_kind",
            )
        order_type_map = _order_type_rows(policy_context)
        order_type_row = dict(order_type_map.get(order_type_id) or {})
        if not order_type_row:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "order_type_id '{}' is not registered".format(order_type_id),
                "Use order_type_id from order_type_registry.",
                {"order_type_id": order_type_id},
                "$.intent.inputs.order_type_id",
            )
        allowed_target_kinds = _sorted_tokens(list(order_type_row.get("allowed_target_kinds") or []))
        if allowed_target_kinds and target_kind not in set(allowed_target_kinds):
            return refusal(
                "PROCESS_INPUT_INVALID",
                "target_kind '{}' is forbidden for order_type_id '{}'".format(target_kind, order_type_id),
                "Use allowed_target_kinds from order_type_registry for this order.",
                {"order_type_id": order_type_id, "target_kind": target_kind},
                "$.intent.inputs.target_kind",
            )

        target_exists = False
        if target_kind == "agent":
            target_exists = bool(_find_agent(agents, target_id))
        elif target_kind == "cohort":
            target_exists = bool(_find_cohort(cohorts, target_id))
        elif target_kind == "faction":
            target_exists = bool(_find_faction(_ensure_faction_assemblies(state), target_id))
        elif target_kind == "territory":
            target_exists = bool(_find_territory(_ensure_territory_assemblies(state), target_id))
        if not target_exists:
            return refusal(
                "refusal.control.target_invalid",
                "order target '{}' does not exist for kind '{}'".format(target_id, target_kind),
                "Use target ids present in current universe assemblies.",
                {"target_kind": target_kind, "target_id": target_id},
                "$.intent.inputs.target_id",
            )

        issuer_subject_id = str(inputs.get("issuer_subject_id", "")).strip() or _author_subject_id(authority_context)
        effective_entitlements = set(
            _effective_civ_entitlements(
                state=state,
                authority_context=authority_context,
                subject_id=issuer_subject_id,
            )
        )
        required_caps = _sorted_tokens(list(order_type_row.get("required_capabilities") or []))
        missing_caps = [token for token in required_caps if token not in effective_entitlements]
        if missing_caps:
            return refusal(
                "refusal.civ.entitlement_missing",
                "issuer subject is missing order capabilities required by order type",
                "Grant required entitlements or assign a role with delegation before order_create.",
                {"missing_entitlements": ",".join(sorted(missing_caps)), "issuer_subject_id": issuer_subject_id},
                "$.intent.inputs.order_type_id",
            )

        shard_map = dict((policy_context or {}).get("shard_map") or {})
        active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
        target_shards = _order_target_shards(state=state, target_kind=target_kind, target_id=target_id, shard_map=shard_map)
        if active_shard_id and target_shards:
            if len(target_shards) > 1 or active_shard_id not in set(target_shards):
                return refusal(
                    "refusal.civ.order_cross_shard_not_supported",
                    "order target spans unsupported shards for current execution shard",
                    "Route to a single owning shard or split into deterministic per-shard orders.",
                    {
                        "active_shard_id": active_shard_id,
                        "target_shards": list(target_shards),
                        "target_kind": target_kind,
                        "target_id": target_id,
                    },
                    "$.intent.inputs.target_id",
                )

        created_tick = int(current_tick)
        payload_hash = canonical_sha256(payload)
        order_id = str(inputs.get("order_id", "")).strip() or "order.{}".format(
            canonical_sha256(
                {
                    "issuer_subject_id": issuer_subject_id,
                    "target_kind": target_kind,
                    "target_id": target_id,
                    "order_type_id": order_type_id,
                    "created_tick": created_tick,
                    "payload_hash": payload_hash,
                }
            )[:16]
        )
        if _find_order(order_rows=order_rows, order_id=order_id):
            return refusal(
                "refusal.civ.claim_forbidden",
                "order_id '{}' already exists".format(order_id),
                "Use deterministic order id generation or provide a unique override.",
                {"order_id": order_id},
                "$.intent.inputs.order_id",
            )
        priority = max(0, _as_int(inputs.get("priority", order_type_row.get("default_priority", 0)), 0))
        row = {
            "order_id": order_id,
            "order_type_id": order_type_id,
            "issuer_subject_id": issuer_subject_id,
            "target_kind": target_kind,
            "target_id": target_id,
            "created_tick": created_tick,
            "last_update_tick": created_tick,
            "status": "queued",
            "priority": int(priority),
            "payload": dict(payload),
            "required_entitlements": required_caps,
            "refusal": None,
            "extensions": {"payload_hash": payload_hash, "shard_targets": list(target_shards)},
        }
        order_rows.append(row)

        owner_kind, owner_id = _order_queue_owner(state=state, target_kind=target_kind, target_id=target_id, inputs=inputs)
        queue_row = _upsert_order_queue(
            queue_rows=queue_rows,
            owner_kind=owner_kind,
            owner_id=owner_id,
            current_tick=created_tick,
        )
        queue_order_ids = _ordered_unique_tokens(list(queue_row.get("order_ids") or []))
        queue_order_ids.append(order_id)
        queue_row["order_ids"] = queue_order_ids
        _refresh_queue_order_ids(queue_row=queue_row, order_rows=order_rows)

        _persist_civ_state(
            state=state,
            faction_rows=_ensure_faction_assemblies(state),
            affiliation_rows=_ensure_affiliations(state),
            territory_rows=_ensure_territory_assemblies(state),
            diplomatic_rows=_ensure_diplomatic_relations(state),
            cohort_rows=cohorts,
            order_rows=order_rows,
            queue_rows=queue_rows,
            institution_rows=institution_rows,
            role_assignment_rows=role_assignment_rows,
        )
        result_metadata = {
            "order_id": order_id,
            "order_type_id": order_type_id,
            "queue_id": str(queue_row.get("queue_id", "")),
            "status": "queued",
            "priority": int(priority),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.order_cancel":
        order_id = str(inputs.get("order_id", "")).strip()
        if not order_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.order_cancel requires order_id",
                "Provide order_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.order_id",
            )
        order_row = _find_order(order_rows=order_rows, order_id=order_id)
        if not order_row:
            return refusal(
                "refusal.control.target_invalid",
                "order '{}' does not exist".format(order_id),
                "Use order_id from order assemblies.",
                {"order_id": order_id},
                "$.intent.inputs.order_id",
            )
        caller_subject_id = _author_subject_id(authority_context)
        admin_override = _civ_admin_override(authority_context)
        issuer_subject_id = str(order_row.get("issuer_subject_id", "")).strip()
        if (not admin_override) and issuer_subject_id and caller_subject_id != issuer_subject_id:
            return refusal(
                "refusal.civ.ownership_violation",
                "caller subject cannot cancel order created by another issuer",
                "Cancel with issuer authority or use civ admin override entitlement.",
                {
                    "caller_subject_id": caller_subject_id,
                    "issuer_subject_id": issuer_subject_id,
                    "order_id": order_id,
                },
                "$.intent.inputs.order_id",
            )
        order_row["status"] = "refused"
        order_row["last_update_tick"] = int(current_tick)
        order_row["refusal"] = {
            "code": "refusal.civ.order_cancelled",
            "reason": "cancelled_by_issuer_or_admin",
            "issuer_subject_id": caller_subject_id,
            "cancel_tick": int(current_tick),
        }
        _remove_order_from_all_queues(queue_rows=queue_rows, order_id=order_id)
        for queue_row in queue_rows:
            _refresh_queue_order_ids(queue_row=queue_row, order_rows=order_rows)
        _persist_civ_state(
            state=state,
            faction_rows=_ensure_faction_assemblies(state),
            affiliation_rows=_ensure_affiliations(state),
            territory_rows=_ensure_territory_assemblies(state),
            diplomatic_rows=_ensure_diplomatic_relations(state),
            cohort_rows=cohorts,
            order_rows=order_rows,
            queue_rows=queue_rows,
            institution_rows=institution_rows,
            role_assignment_rows=role_assignment_rows,
        )
        result_metadata = {
            "order_id": order_id,
            "status": "refused",
        }
        _advance_time(state, steps=1)
    elif process_id == "process.demography_tick":
        demography_policy_id = str(
            inputs.get("demography_policy_id", "")
            or (policy_context or {}).get("demography_policy_id", "")
            or "demo.policy.none"
        ).strip()
        policy_rows = _demography_policy_rows(policy_context)
        policy_row = dict(policy_rows.get(demography_policy_id) or {})
        if not policy_row:
            return refusal(
                "refusal.civ.demography_policy_missing",
                "demography policy '{}' is not registered".format(demography_policy_id),
                "Use demography_policy_id from demography_policy_registry.",
                {"demography_policy_id": demography_policy_id},
                "$.intent.inputs.demography_policy_id",
            )
        death_model_rows = _death_model_rows(policy_context)
        birth_model_rows = _birth_model_rows(policy_context)
        death_model_id = str(policy_row.get("death_model_id", "")).strip()
        birth_model_id = str(policy_row.get("birth_model_id", "")).strip()
        death_model = dict(death_model_rows.get(death_model_id) or {})
        birth_model = dict(birth_model_rows.get(birth_model_id) or {})
        if not death_model or not birth_model:
            return refusal(
                "refusal.civ.demography_policy_missing",
                "demography policy references missing birth/death models",
                "Ensure demography policy model references exist in birth/death model registries.",
                {
                    "demography_policy_id": demography_policy_id,
                    "death_model_id": death_model_id,
                    "birth_model_id": birth_model_id,
                },
                "$.intent.inputs.demography_policy_id",
            )
        births_enabled = bool(policy_row.get("births_enabled", False))
        law_births_forbidden = (
            law_profile.get("births_enabled_override") is False
            or law_profile.get("births_allowed") is False
            or law_profile.get("demography_births_allowed") is False
        )
        if births_enabled and law_births_forbidden:
            return refusal(
                "refusal.civ.births_forbidden_by_law",
                "births are enabled by demography policy but forbidden by law",
                "Set births_enabled=false in demography policy or allow births in law profile.",
                {
                    "demography_policy_id": demography_policy_id,
                    "law_profile_id": str(law_profile.get("law_profile_id", "")),
                },
                "$.law_profile",
            )
        tick_rate = max(1, _as_int(policy_row.get("tick_rate", 1), 1))
        due = (int(current_tick) % int(tick_rate)) == 0
        bundle = _active_parameter_bundle(policy_context)
        bundle_id = str(bundle.get("parameter_bundle_id", "")).strip() if isinstance(bundle, dict) else ""
        bundle_parameters = dict(bundle.get("parameters") or {}) if isinstance(bundle, dict) else {}
        birth_multiplier = max(0.0, _as_float(bundle_parameters.get("civ.demography.birth_multiplier", 1.0), 1.0))
        death_multiplier = max(0.0, _as_float(bundle_parameters.get("civ.demography.death_multiplier", 1.0), 1.0))
        max_growth_per_interval = max(
            0,
            _as_int(bundle_parameters.get("civ.demography.max_cohort_growth_per_interval", 0), 0),
        )
        cohort_ids = _sorted_tokens(
            list(
                inputs.get("applies_to")
                or inputs.get("cohort_ids")
                or []
            )
        )
        cohort_id_filter = set(cohort_ids)
        shard_map = dict((policy_context or {}).get("shard_map") or {})
        active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
        target_rows: List[dict] = []
        for cohort_row in sorted(cohorts, key=lambda item: str(item.get("cohort_id", ""))):
            cohort_token = str(cohort_row.get("cohort_id", "")).strip()
            if cohort_id_filter and cohort_token not in cohort_id_filter:
                continue
            if active_shard_id:
                owner_shard = _cohort_owner_shard_id(cohort_row=cohort_row, shard_map=shard_map)
                if owner_shard and owner_shard != active_shard_id:
                    continue
            target_rows.append(cohort_row)
        base_birth_rate = max(0.0, _as_float(birth_model.get("base_birth_rate_per_tick", 0.0), 0.0))
        base_death_rate = max(0.0, _as_float(death_model.get("base_death_rate_per_tick", 0.0), 0.0))
        cohort_deltas: List[dict] = []
        total_births = 0
        total_deaths = 0
        if due:
            for cohort_row in target_rows:
                size_before = max(0, _as_int(cohort_row.get("size", 0), 0))
                births = 0
                if births_enabled:
                    births = max(0, int(math.floor(float(size_before) * float(base_birth_rate) * float(birth_multiplier))))
                    if int(max_growth_per_interval) > 0:
                        births = min(int(births), int(max_growth_per_interval))
                deaths = max(0, int(math.floor(float(size_before) * float(base_death_rate) * float(death_multiplier))))
                size_after = max(0, int(size_before) + int(births) - int(deaths))
                cohort_row["size"] = int(size_after)
                extensions = dict(cohort_row.get("extensions") or {}) if isinstance(cohort_row.get("extensions"), dict) else {}
                totals = dict(extensions.get("demography_totals") or {}) if isinstance(extensions.get("demography_totals"), dict) else {}
                totals["births"] = max(0, _as_int(totals.get("births", 0), 0) + int(births))
                totals["deaths"] = max(0, _as_int(totals.get("deaths", 0), 0) + int(deaths))
                extensions["demography_policy_id"] = demography_policy_id
                extensions["demography_last_tick"] = int(current_tick)
                extensions["demography_last_births"] = int(births)
                extensions["demography_last_deaths"] = int(deaths)
                extensions["demography_totals"] = totals
                cohort_row["extensions"] = extensions
                total_births += int(births)
                total_deaths += int(deaths)
                cohort_deltas.append(
                    {
                        "cohort_id": str(cohort_row.get("cohort_id", "")),
                        "size_before": int(size_before),
                        "births": int(births),
                        "deaths": int(deaths),
                        "size_after": int(size_after),
                    }
                )
            _persist_civ_state(
                state=state,
                faction_rows=_ensure_faction_assemblies(state),
                affiliation_rows=_ensure_affiliations(state),
                territory_rows=_ensure_territory_assemblies(state),
                diplomatic_rows=_ensure_diplomatic_relations(state),
                cohort_rows=cohorts,
                order_rows=order_rows,
                queue_rows=queue_rows,
                institution_rows=institution_rows,
                role_assignment_rows=role_assignment_rows,
            )
        result_metadata = {
            "demography_policy_id": demography_policy_id,
            "tick_rate": int(tick_rate),
            "applied": bool(due),
            "processed_cohort_count": len(list(target_rows)),
            "total_births": int(total_births),
            "total_deaths": int(total_deaths),
            "births_enabled": bool(births_enabled),
            "birth_model_id": birth_model_id,
            "death_model_id": death_model_id,
            "parameter_bundle_id": bundle_id,
            "cohort_deltas": cohort_deltas,
        }
        _advance_time(state, steps=1)
    elif process_id == "process.cohort_relocate":
        cohort_id = str(inputs.get("cohort_id", "")).strip()
        destination = str(inputs.get("destination", "") or inputs.get("location_ref", "")).strip()
        if not cohort_id or not destination:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.cohort_relocate requires cohort_id and destination",
                "Provide deterministic cohort_id and destination in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        cohort_row = _find_cohort(cohort_rows=cohorts, cohort_id=cohort_id)
        if not cohort_row:
            return refusal(
                "refusal.control.target_invalid",
                "cohort '{}' does not exist".format(cohort_id),
                "Use an existing cohort_id from cohort assemblies.",
                {"cohort_id": cohort_id},
                "$.intent.inputs.cohort_id",
            )
        shard_map = dict((policy_context or {}).get("shard_map") or {})
        active_shard_id = str((policy_context or {}).get("active_shard_id", "")).strip()
        owner_shard_id = _cohort_owner_shard_id(cohort_row=cohort_row, shard_map=shard_map)
        if active_shard_id and owner_shard_id and owner_shard_id != active_shard_id:
            return refusal(
                "refusal.civ.order_cross_shard_not_supported",
                "cohort relocate must execute on owning shard",
                "Route order to owning shard or split into deterministic per-shard orders.",
                {"cohort_id": cohort_id, "owner_shard_id": owner_shard_id, "active_shard_id": active_shard_id},
                "$.policy_context.active_shard_id",
            )
        if law_profile.get("migration_allowed") is False:
            return refusal(
                "refusal.civ.claim_forbidden",
                "active law profile forbids migration processes",
                "Enable migration in law profile or use a law profile that allows process.cohort_relocate.",
                {"law_profile_id": str(law_profile.get("law_profile_id", ""))},
                "$.law_profile",
            )
        migration_model_id = str(
            inputs.get("migration_model_id", "")
            or (policy_context or {}).get("migration_model_id", "")
            or "demo.migration.instant"
        ).strip()
        migration_model_rows = _migration_model_rows(policy_context)
        bundle = _active_parameter_bundle(policy_context)
        bundle_parameters = dict(bundle.get("parameters") or {}) if isinstance(bundle, dict) else {}
        migration_delay_multiplier = max(
            0.0,
            _as_float(bundle_parameters.get("civ.migration.delay_multiplier", 1.0), 1.0),
        )
        relocate_result = _cohort_relocate_internal(
            cohort_row=cohort_row,
            destination=destination,
            migration_model_id=migration_model_id,
            migration_model_rows=migration_model_rows,
            current_tick=int(current_tick),
            migration_delay_multiplier=float(migration_delay_multiplier),
        )
        if str(relocate_result.get("result", "")) != "complete":
            return relocate_result
        _persist_civ_state(
            state=state,
            faction_rows=_ensure_faction_assemblies(state),
            affiliation_rows=_ensure_affiliations(state),
            territory_rows=_ensure_territory_assemblies(state),
            diplomatic_rows=_ensure_diplomatic_relations(state),
            cohort_rows=cohorts,
            order_rows=order_rows,
            queue_rows=queue_rows,
            institution_rows=institution_rows,
            role_assignment_rows=role_assignment_rows,
        )
        result_metadata = {
            "cohort_id": cohort_id,
            "destination": destination,
            "migration_model_id": str(relocate_result.get("migration_model_id", "")),
            "travel_ticks": int(relocate_result.get("travel_ticks", 0)),
            "arrival_tick": int(relocate_result.get("arrival_tick", int(current_tick))),
            "in_transit": bool(relocate_result.get("in_transit", False)),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.order_tick":
        tick_summary = _run_order_tick(
            state=state,
            order_rows=order_rows,
            queue_rows=queue_rows,
            cohorts=cohorts,
            agents=agents,
            current_tick=int(current_tick),
            authority_context=authority_context,
            policy_context=policy_context,
            max_orders_override=_as_int(inputs.get("max_orders_per_tick", 0), 0) or None,
        )
        _persist_civ_state(
            state=state,
            faction_rows=_ensure_faction_assemblies(state),
            affiliation_rows=_ensure_affiliations(state),
            territory_rows=_ensure_territory_assemblies(state),
            diplomatic_rows=_ensure_diplomatic_relations(state),
            cohort_rows=cohorts,
            order_rows=order_rows,
            queue_rows=queue_rows,
            institution_rows=institution_rows,
            role_assignment_rows=role_assignment_rows,
        )
        result_metadata = {
            "processed_count": len(list(tick_summary.get("processed_order_ids") or [])),
            "processed_order_ids": list(tick_summary.get("processed_order_ids") or []),
            "completed_order_ids": list(tick_summary.get("completed_order_ids") or []),
            "failed_order_ids": list(tick_summary.get("failed_order_ids") or []),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.role_assign":
        if law_profile.get("allow_role_delegation") is False:
            return refusal(
                "refusal.civ.law_forbidden",
                "active law profile forbids role delegation",
                "Enable role delegation in law profile or use direct entitlements.",
                {"law_profile_id": str(law_profile.get("law_profile_id", ""))},
                "$.law_profile.allow_role_delegation",
            )
        subject_id = str(inputs.get("subject_id", "")).strip()
        role_id = str(inputs.get("role_id", "")).strip()
        institution_id = str(inputs.get("institution_id", "")).strip()
        institution_type_id = str(inputs.get("institution_type_id", "inst.band_council")).strip() or "inst.band_council"
        faction_raw = inputs.get("faction_id")
        faction_id = None if faction_raw is None else str(faction_raw).strip() or None
        if not subject_id or not role_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.role_assign requires subject_id and role_id",
                "Provide deterministic subject_id and role_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        role_map = _role_rows(policy_context)
        role_row = dict(role_map.get(role_id) or {})
        if not role_row:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "role_id '{}' is not registered".format(role_id),
                "Use role_id from role_registry.",
                {"role_id": role_id},
                "$.intent.inputs.role_id",
            )
        institution_type_map = _institution_type_rows(policy_context)
        institution_row = _find_institution(institution_rows=institution_rows, institution_id=institution_id) if institution_id else {}
        if not institution_row:
            institution_type_row = dict(institution_type_map.get(institution_type_id) or {})
            if not institution_type_row:
                return refusal(
                    "PROCESS_INPUT_INVALID",
                    "institution_type_id '{}' is not registered".format(institution_type_id),
                    "Use institution_type_id from institution_type_registry.",
                    {"institution_type_id": institution_type_id},
                    "$.intent.inputs.institution_type_id",
                )
            if not institution_id:
                institution_id = "institution.{}".format(
                    canonical_sha256(
                        {
                            "institution_type_id": institution_type_id,
                            "faction_id": faction_id,
                            "created_tick": int(current_tick),
                        }
                    )[:16]
                )
            institution_row = {
                "institution_id": institution_id,
                "institution_type_id": institution_type_id,
                "faction_id": faction_id,
                "status": "active",
                "created_tick": int(current_tick),
                "extensions": {},
            }
            institution_rows.append(institution_row)
        institution_type_id = str(institution_row.get("institution_type_id", "")).strip() or institution_type_id
        institution_type_row = dict(institution_type_map.get(institution_type_id) or {})
        allowed_role_ids = _sorted_tokens(list(institution_type_row.get("allowed_role_ids") or []))
        if allowed_role_ids and role_id not in set(allowed_role_ids):
            return refusal(
                "refusal.civ.relation_invalid",
                "role_id '{}' is not allowed by institution type '{}'".format(role_id, institution_type_id),
                "Choose a role listed in institution_type_registry.allowed_role_ids.",
                {"institution_type_id": institution_type_id, "role_id": role_id},
                "$.intent.inputs.role_id",
            )
        granted_entitlements = _sorted_tokens(list(role_row.get("granted_entitlements") or []))
        delegable = law_profile.get("delegable_entitlements")
        if isinstance(delegable, list) and delegable:
            allowed_delegable = set(_sorted_tokens(list(delegable)))
            granted_entitlements = [token for token in granted_entitlements if token in allowed_delegable]
        disallowed = set(_sorted_tokens(list((policy_context or {}).get("disallowed_role_entitlements") or [])))
        if disallowed:
            granted_entitlements = [token for token in granted_entitlements if token not in disallowed]
        assignment_id = str(inputs.get("assignment_id", "")).strip() or "role_assignment.{}".format(
            canonical_sha256(
                {
                    "institution_id": institution_id,
                    "subject_id": subject_id,
                    "role_id": role_id,
                    "created_tick": int(current_tick),
                }
            )[:16]
        )
        assignment_row = _find_role_assignment(role_assignment_rows=role_assignment_rows, assignment_id=assignment_id)
        if assignment_row:
            assignment_row["institution_id"] = institution_id
            assignment_row["subject_id"] = subject_id
            assignment_row["role_id"] = role_id
            assignment_row["granted_entitlements"] = list(granted_entitlements)
            assignment_row["created_tick"] = int(current_tick)
            if not isinstance(assignment_row.get("extensions"), dict):
                assignment_row["extensions"] = {}
        else:
            role_assignment_rows.append(
                {
                    "assignment_id": assignment_id,
                    "institution_id": institution_id,
                    "subject_id": subject_id,
                    "role_id": role_id,
                    "granted_entitlements": list(granted_entitlements),
                    "created_tick": int(current_tick),
                    "extensions": {},
                }
            )
        affiliation_row = _find_affiliation(affiliation_rows=_ensure_affiliations(state), subject_id=subject_id)
        if isinstance(affiliation_row, dict) and affiliation_row:
            affiliation_row["role_id"] = role_id
        _persist_civ_state(
            state=state,
            faction_rows=_ensure_faction_assemblies(state),
            affiliation_rows=_ensure_affiliations(state),
            territory_rows=_ensure_territory_assemblies(state),
            diplomatic_rows=_ensure_diplomatic_relations(state),
            cohort_rows=cohorts,
            order_rows=order_rows,
            queue_rows=queue_rows,
            institution_rows=institution_rows,
            role_assignment_rows=role_assignment_rows,
        )
        result_metadata = {
            "assignment_id": assignment_id,
            "institution_id": institution_id,
            "subject_id": subject_id,
            "role_id": role_id,
        }
        _advance_time(state, steps=1)
    elif process_id == "process.role_revoke":
        assignment_id = str(inputs.get("assignment_id", "")).strip()
        if not assignment_id:
            subject_id = str(inputs.get("subject_id", "")).strip()
            institution_id = str(inputs.get("institution_id", "")).strip()
            role_id = str(inputs.get("role_id", "")).strip()
            for row in sorted(role_assignment_rows, key=lambda item: str(item.get("assignment_id", ""))):
                if subject_id and str(row.get("subject_id", "")).strip() != subject_id:
                    continue
                if institution_id and str(row.get("institution_id", "")).strip() != institution_id:
                    continue
                if role_id and str(row.get("role_id", "")).strip() != role_id:
                    continue
                assignment_id = str(row.get("assignment_id", "")).strip()
                break
        if not assignment_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.role_revoke requires assignment_id or deterministic match fields",
                "Provide assignment_id or subject_id/institution_id(/role_id).",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        assignment_row = _find_role_assignment(role_assignment_rows=role_assignment_rows, assignment_id=assignment_id)
        if not assignment_row:
            return refusal(
                "refusal.control.target_invalid",
                "role assignment '{}' does not exist".format(assignment_id),
                "Use assignment_id from role_assignment assemblies.",
                {"assignment_id": assignment_id},
                "$.intent.inputs.assignment_id",
            )
        subject_id = str(assignment_row.get("subject_id", "")).strip()
        role_id = str(assignment_row.get("role_id", "")).strip()
        role_assignment_rows[:] = [
            dict(row)
            for row in role_assignment_rows
            if isinstance(row, dict) and str(row.get("assignment_id", "")).strip() != assignment_id
        ]
        affiliation_row = _find_affiliation(affiliation_rows=_ensure_affiliations(state), subject_id=subject_id)
        if isinstance(affiliation_row, dict) and affiliation_row and str(affiliation_row.get("role_id", "")).strip() == role_id:
            affiliation_row["role_id"] = "role.member"
        _persist_civ_state(
            state=state,
            faction_rows=_ensure_faction_assemblies(state),
            affiliation_rows=_ensure_affiliations(state),
            territory_rows=_ensure_territory_assemblies(state),
            diplomatic_rows=_ensure_diplomatic_relations(state),
            cohort_rows=cohorts,
            order_rows=order_rows,
            queue_rows=queue_rows,
            institution_rows=institution_rows,
            role_assignment_rows=role_assignment_rows,
        )
        result_metadata = {
            "assignment_id": assignment_id,
            "subject_id": subject_id,
            "role_id": role_id,
            "revoked": True,
        }
        _advance_time(state, steps=1)
    elif process_id in ("process.control_set_view_lens", "process.camera_set_lens"):
        controller_id = str(inputs.get("controller_id", "")).strip()
        lens_id = str(inputs.get("lens_id", "")).strip()
        camera_id = str(inputs.get("camera_id", "camera.main")).strip() or "camera.main"
        if not controller_id or not lens_id:
            return refusal(
                "refusal.view.target_invalid",
                "{} requires controller_id and lens_id".format(process_id),
                "Provide controller_id and lens_id in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if not _camera_exists(state=state, camera_id=camera_id):
            return refusal(
                "refusal.view.target_invalid",
                "camera target '{}' does not exist".format(camera_id),
                "Select an existing camera assembly id for lens override.",
                {"camera_id": camera_id},
                "$.intent.inputs.camera_id",
            )
        allowed_lenses = _sorted_tokens(list(law_profile.get("allowed_lenses") or []))
        if lens_id not in allowed_lenses:
            return refusal(
                "refusal.control.lens_forbidden",
                "lens '{}' is forbidden by active law profile".format(lens_id),
                "Select a lens listed in law_profile.allowed_lenses.",
                {"lens_id": lens_id, "law_profile_id": str(law_profile.get("law_profile_id", ""))},
                "$.intent.inputs.lens_id",
            )
        entitlements = _sorted_tokens(list(authority_context.get("entitlements") or []))
        if lens_id.startswith("lens.nondiegetic") and "lens.nondiegetic.access" not in entitlements:
            return refusal(
                "refusal.view.entitlement_missing",
                "nondiegetic lens '{}' requires lens.nondiegetic.access entitlement".format(lens_id),
                "Grant lens.nondiegetic.access or use a diegetic lens.",
                {"lens_id": lens_id},
                "$.intent.inputs.lens_id",
            )
        _upsert_controller(
            controllers=controllers,
            controller_id=controller_id,
            controller_type=str(inputs.get("controller_type", "script")).strip() or "script",
            owner_peer_id=inputs.get("owner_peer_id", authority_context.get("authority_origin")),
        )
        camera_rows = state.get("camera_assemblies")
        if not isinstance(camera_rows, list):
            camera_rows = []
        for row in camera_rows:
            if not isinstance(row, dict):
                continue
            if str(row.get("assembly_id", "")).strip() != camera_id:
                continue
            _camera_defaults(row)
            view_mode_id = str(row.get("view_mode_id", "")).strip()
            if view_mode_id:
                view_modes = _view_mode_entries(navigation_indices)
                mode_row = dict(view_modes.get(view_mode_id) or {})
                allowed_lenses = _sorted_tokens(list(mode_row.get("allowed_lens_ids") or []))
                if allowed_lenses and lens_id not in allowed_lenses:
                    return refusal(
                        "refusal.view.mode_forbidden",
                        "lens '{}' is not permitted by active view mode '{}'".format(lens_id, view_mode_id),
                        "Choose a lens listed in view_mode.allowed_lens_ids for current mode.",
                        {"view_mode_id": view_mode_id, "lens_id": lens_id},
                        "$.intent.inputs.lens_id",
                    )
            row["lens_id"] = lens_id
        state["camera_assemblies"] = sorted(
            (dict(item) for item in camera_rows if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        _store_control_state(state=state, controllers=controllers, bindings=bindings)
        _advance_time(state, steps=1)
    elif process_id == "process.cosmetic_assign":
        agent_id = str(inputs.get("agent_id", "") or inputs.get("target_agent_id", "") or inputs.get("target_id", "")).strip()
        cosmetic_id = str(inputs.get("cosmetic_id", "")).strip()
        if not agent_id or not cosmetic_id:
            return refusal(
                "refusal.cosmetic.forbidden",
                "process.cosmetic_assign requires agent_id and cosmetic_id",
                "Provide deterministic agent_id and cosmetic_id in process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        agent_row = _find_agent(agent_rows=agents, agent_id=agent_id)
        if not agent_row:
            return refusal(
                "refusal.cosmetic.forbidden",
                "agent '{}' is not available for cosmetic assignment".format(agent_id),
                "Select an existing agent_id before assigning cosmetics.",
                {"agent_id": agent_id},
                "$.intent.inputs.agent_id",
            )

        cosmetic_registry = _policy_payload(policy_context, "cosmetic_registry")
        cosmetic_rows = _registry_rows_by_id(cosmetic_registry, "cosmetics", "cosmetic_id")
        cosmetic_row = dict(cosmetic_rows.get(cosmetic_id) or {})
        if not cosmetic_row:
            return refusal(
                "refusal.cosmetic.forbidden",
                "cosmetic '{}' is not defined in cosmetic registry".format(cosmetic_id),
                "Use a cosmetic_id from cosmetic.registry.json.",
                {"cosmetic_id": cosmetic_id},
                "$.intent.inputs.cosmetic_id",
            )

        policy_check = _resolve_cosmetic_policy(policy_context)
        if policy_check.get("result") != "complete":
            return policy_check
        cosmetic_policy = dict(policy_check.get("policy") or {})
        policy_id = str(cosmetic_policy.get("policy_id", "")).strip()
        allow_unsigned = bool(cosmetic_policy.get("allow_unsigned_packs", True))
        require_signed = bool(cosmetic_policy.get("require_signed_packs", False))
        allowed_cosmetics = _sorted_tokens(list(cosmetic_policy.get("allowed_cosmetic_ids") or []))
        allowed_pack_ids = _sorted_tokens(list(cosmetic_policy.get("allowed_pack_ids") or []))

        if allowed_cosmetics and cosmetic_id not in set(allowed_cosmetics):
            return refusal(
                "refusal.cosmetic.not_in_whitelist",
                "cosmetic '{}' is not permitted by policy '{}'".format(cosmetic_id, policy_id),
                "Select a cosmetic_id listed in cosmetic policy allow-list.",
                {"policy_id": policy_id, "cosmetic_id": cosmetic_id},
                "$.intent.inputs.cosmetic_id",
            )

        resolved_packs = [
            dict(row)
            for row in list((policy_context or {}).get("resolved_packs") or [])
            if isinstance(row, dict)
        ]
        pack_map = dict(
            (
                str(row.get("pack_id", "")).strip(),
                dict(row),
            )
            for row in sorted(resolved_packs, key=lambda row: str(row.get("pack_id", "")))
            if str(row.get("pack_id", "")).strip()
        )
        pack_id = _cosmetic_pack_id(cosmetic_row)
        if allowed_pack_ids and (not pack_id or pack_id not in set(allowed_pack_ids)):
            return refusal(
                "refusal.cosmetic.not_in_whitelist",
                "cosmetic '{}' pack '{}' is not permitted by policy '{}'".format(
                    cosmetic_id,
                    pack_id or "<missing>",
                    policy_id,
                ),
                "Assign a cosmetic from an allowed pack.",
                {"policy_id": policy_id, "cosmetic_id": cosmetic_id, "pack_id": pack_id or "<missing>"},
                "$.intent.inputs.cosmetic_id",
            )

        pack_row = dict(pack_map.get(pack_id) or {}) if pack_id else {}
        signature_status = str(pack_row.get("signature_status", "")).strip().lower()
        signed_status = signature_status in ("signed", "verified", "official")
        if (require_signed or not allow_unsigned) and not signed_status:
            return refusal(
                "refusal.cosmetic.unsigned_not_allowed",
                "cosmetic '{}' requires signed pack under policy '{}'".format(cosmetic_id, policy_id),
                "Use signed cosmetic packs or relax cosmetic policy on private/casual server profiles.",
                {
                    "policy_id": policy_id,
                    "cosmetic_id": cosmetic_id,
                    "pack_id": pack_id or "<missing>",
                    "signature_status": signature_status or "<missing>",
                },
                "$.intent.inputs.cosmetic_id",
            )

        representation_state = _representation_state(policy_context)
        assignments = dict(representation_state.get("assignments") or {})
        assignment_id = "cosmetic.assignment.{}".format(agent_id)
        assignment_row = {
            "assignment_id": assignment_id,
            "target_agent_id": agent_id,
            "cosmetic_id": cosmetic_id,
            "applied_tick": int(current_tick),
            "authority_origin": str(authority_context.get("authority_origin", "")),
            "policy_id": policy_id,
            "pack_id": pack_id,
        }
        assignments[agent_id] = assignment_row
        representation_state["assignments"] = dict(
            (token, dict(assignments[token]))
            for token in sorted(assignments.keys())
            if str(token).strip()
        )
        events = list(representation_state.get("events") or [])
        events.append(dict(assignment_row))
        representation_state["events"] = sorted(
            (dict(item) for item in events if isinstance(item, dict)),
            key=lambda item: (
                int(item.get("applied_tick", 0) or 0),
                str(item.get("target_agent_id", "")),
                str(item.get("cosmetic_id", "")),
                str(item.get("assignment_id", "")),
            ),
        )
        result_metadata = {
            "assignment_id": assignment_id,
            "target_agent_id": agent_id,
            "cosmetic_id": cosmetic_id,
            "policy_id": policy_id,
            "pack_id": pack_id,
        }
        skip_state_log = True
    elif process_id == "process.body_move_attempt":
        moved = _apply_body_move_attempt(
            state=state,
            body_rows=bodies,
            inputs=dict(inputs),
            policy_context=policy_context,
        )
        if moved.get("result") != "complete":
            return moved
        result_metadata = {
            "body_id": str(moved.get("body_id", "")),
            "movement_delta_mm": dict(moved.get("delta_transform_mm") or {"x": 0, "y": 0, "z": 0}),
            "movement_distance_mm": int(
                abs(_as_int((moved.get("delta_transform_mm") or {}).get("x", 0), 0))
                + abs(_as_int((moved.get("delta_transform_mm") or {}).get("y", 0), 0))
                + abs(_as_int((moved.get("delta_transform_mm") or {}).get("z", 0), 0))
            ),
            "dt_ticks": int(moved.get("dt_ticks", 1)),
        }
        _advance_time(state, steps=int(moved.get("dt_ticks", 1)))
    elif process_id == "process.instrument_tick":
        sim = _ensure_simulation_time(state)
        control = _ensure_time_control(state)
        position = _vector3_int(camera.get("position_mm"), "position_mm") or {"x": 0, "y": 0, "z": 0}
        orientation = _angles_int(camera.get("orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
        heading = int(orientation.get("yaw", 0)) % 360000
        rows = _ensure_instrument_assemblies(state)
        current_tick = int(sim.get("tick", 0))
        for row in rows:
            assembly_id = str(row.get("assembly_id", "")).strip()
            instrument_type = str(row.get("instrument_type", "")).strip()
            instrument_type_id = str(row.get("instrument_type_id", "")).strip()
            if (not instrument_type) and instrument_type_id:
                instrument_type = str(INSTRUMENT_TYPE_BY_ID.get(instrument_type_id, "")).strip()
            if instrument_type and (not instrument_type_id):
                instrument_type_id = str(INSTRUMENT_TYPE_ID_BY_TYPE.get(instrument_type, "")).strip()
            row["instrument_type"] = instrument_type
            row["instrument_type_id"] = instrument_type_id
            state_payload = dict(row.get("state") or {}) if isinstance(row.get("state"), dict) else {}
            outputs_payload = dict(row.get("outputs") or {}) if isinstance(row.get("outputs"), dict) else {}
            if assembly_id == "instrument.compass":
                reading = {"heading_mdeg": heading}
                outputs_payload["ch.diegetic.compass"] = dict(reading)
            elif assembly_id == "instrument.clock":
                reading = {
                    "tick": current_tick,
                    "rate_permille": int(control.get("rate_permille", 1000)),
                    "paused": bool(control.get("paused", False)),
                }
                outputs_payload["ch.diegetic.clock"] = dict(reading)
            elif assembly_id == "instrument.altimeter":
                reading = {"altitude_mm": int(position.get("z", 0))}
                outputs_payload["ch.diegetic.altimeter"] = dict(reading)
            elif assembly_id == "instrument.map_local":
                map_entries = _map_entries_sorted(state_payload.get("entries"), DIEGETIC_MAP_MAX_ITEMS)
                state_payload["entries"] = list(map_entries)
                reading = {
                    "entries": list(map_entries),
                    "entry_count": len(map_entries),
                }
                outputs_payload["ch.diegetic.map_local"] = {
                    "entries": list(map_entries),
                    "entry_count": len(map_entries),
                }
            elif assembly_id == "instrument.notebook":
                notes = _message_rows_sorted(state_payload.get("user_notes"), "msg.notebook", DIEGETIC_NOTEBOOK_MAX_ITEMS)
                state_payload["user_notes"] = list(notes)
                entries = [
                    {
                        "entry_id": str(item.get("message_id", "")),
                        "kind": "note",
                        "created_tick": int(item.get("created_tick", 0)),
                        "author_subject_id": str(item.get("author_subject_id", "")),
                        "text": str((dict(item.get("payload") or {})).get("text", ""))[:DIEGETIC_NOTE_MAX_CHARS],
                    }
                    for item in notes
                ]
                reading = {
                    "entries": entries,
                    "entry_count": len(entries),
                }
                outputs_payload["ch.diegetic.notebook"] = {
                    "entries": entries,
                    "entry_count": len(entries),
                }
            elif assembly_id == "instrument.radio_text":
                inbox = _message_rows_sorted(state_payload.get("inbox"), "msg.radio", DIEGETIC_RADIO_MAX_ITEMS)
                state_payload["inbox"] = list(inbox)
                reading = {
                    "messages": [dict(item) for item in inbox],
                    "message_count": len(inbox),
                }
                outputs_payload["ch.diegetic.radio_text"] = {
                    "messages": [dict(item) for item in inbox],
                    "message_count": len(inbox),
                }
            else:
                reading = dict(row.get("reading") or {})
            row["state"] = state_payload
            row["reading"] = reading
            row["outputs"] = outputs_payload
            row["quality"] = "nominal"
            row["quality_value"] = max(0, _as_int(row.get("quality_value", 1000), 1000))
            row["last_update_tick"] = current_tick
        state["instrument_assemblies"] = sorted(
            (dict(item) for item in rows if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        _advance_time(state, steps=1)
    elif process_id == "process.instrument_notebook_add_note":
        note_text = str(inputs.get("text", "") or inputs.get("note", "")).strip()
        if not note_text:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.instrument_notebook_add_note requires text",
                "Provide note text in intent.inputs.text.",
                {"process_id": process_id},
                "$.intent.inputs.text",
            )
        if len(note_text) > DIEGETIC_NOTE_MAX_CHARS:
            return refusal(
                "refusal.diegetic.message_too_large",
                "notebook note exceeds deterministic character budget",
                "Reduce note payload length to {} characters or less.".format(DIEGETIC_NOTE_MAX_CHARS),
                {"max_chars": DIEGETIC_NOTE_MAX_CHARS},
                "$.intent.inputs.text",
            )
        rows = _ensure_instrument_assemblies(state)
        notebook_row = _instrument_row_by_id(rows, "instrument.notebook")
        if not notebook_row:
            return refusal(
                "refusal.diegetic.radio_forbidden",
                "notebook instrument assembly is unavailable",
                "Enable pack.core.diegetic_instruments and retry.",
                {"assembly_id": "instrument.notebook"},
                "$.universe_state.instrument_assemblies",
            )
        current_tick = int((_ensure_simulation_time(state)).get("tick", 0))
        state_payload = dict(notebook_row.get("state") or {}) if isinstance(notebook_row.get("state"), dict) else {}
        notes = _message_rows_sorted(state_payload.get("user_notes"), "msg.notebook", DIEGETIC_NOTEBOOK_MAX_ITEMS)
        author_subject_id = _author_subject_id(authority_context)
        message_id = "msg.notebook.{}".format(
            canonical_sha256(
                {
                    "author_subject_id": author_subject_id,
                    "created_tick": current_tick,
                    "payload": {"text": note_text},
                }
            )[:16]
        )
        note_message = {
            "schema_version": "1.0.0",
            "message_id": message_id,
            "author_subject_id": author_subject_id,
            "created_tick": current_tick,
            "channel_id": "msg.notebook",
            "payload": {"text": note_text},
            "signature": None,
            "extensions": {
                "controller_id": str(inputs.get("controller_id", "")).strip() or None,
            },
        }
        notes.append(note_message)
        notes = _message_rows_sorted(notes, "msg.notebook", DIEGETIC_NOTEBOOK_MAX_ITEMS)
        state_payload["user_notes"] = list(notes)
        entries = [
            {
                "entry_id": str(item.get("message_id", "")),
                "kind": "note",
                "created_tick": int(item.get("created_tick", 0)),
                "author_subject_id": str(item.get("author_subject_id", "")),
                "text": str((dict(item.get("payload") or {})).get("text", ""))[:DIEGETIC_NOTE_MAX_CHARS],
            }
            for item in notes
        ]
        notebook_row["state"] = state_payload
        notebook_row["reading"] = {
            "entries": entries,
            "entry_count": len(entries),
        }
        outputs_payload = dict(notebook_row.get("outputs") or {}) if isinstance(notebook_row.get("outputs"), dict) else {}
        outputs_payload["ch.diegetic.notebook"] = {
            "entries": entries,
            "entry_count": len(entries),
        }
        notebook_row["outputs"] = outputs_payload
        notebook_row["quality"] = "nominal"
        notebook_row["quality_value"] = max(0, _as_int(notebook_row.get("quality_value", 1000), 1000))
        notebook_row["last_update_tick"] = current_tick
        state["instrument_assemblies"] = sorted(
            (dict(item) for item in rows if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        result_metadata = {
            "message_id": message_id,
            "channel_id": "msg.notebook",
            "entry_count": len(entries),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.instrument_radio_send_text":
        recipient_subject_id = str(
            inputs.get("to", "")
            or inputs.get("recipient_subject_id", "")
            or inputs.get("target_subject_id", "")
        ).strip()
        payload = inputs.get("payload")
        payload_text = ""
        if isinstance(payload, dict):
            payload_text = str(payload.get("text", "")).strip()
        elif payload is not None:
            payload_text = str(payload).strip()
        if not payload_text:
            payload_text = str(inputs.get("text", "")).strip()
        if not recipient_subject_id:
            return refusal(
                "refusal.diegetic.radio_forbidden",
                "radio send requires a recipient subject id",
                "Provide intent.inputs.to or intent.inputs.recipient_subject_id.",
                {"process_id": process_id},
                "$.intent.inputs.to",
            )
        if not payload_text:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.instrument_radio_send_text requires payload text",
                "Provide text payload in intent.inputs.payload.text or intent.inputs.text.",
                {"process_id": process_id},
                "$.intent.inputs.payload",
            )
        if len(payload_text) > DIEGETIC_RADIO_MAX_CHARS:
            return refusal(
                "refusal.diegetic.message_too_large",
                "radio payload exceeds deterministic character budget",
                "Reduce radio payload length to {} characters or less.".format(DIEGETIC_RADIO_MAX_CHARS),
                {"max_chars": DIEGETIC_RADIO_MAX_CHARS},
                "$.intent.inputs.payload",
            )
        rows = _ensure_instrument_assemblies(state)
        radio_row = _instrument_row_by_id(rows, "instrument.radio_text")
        if not radio_row:
            return refusal(
                "refusal.diegetic.radio_forbidden",
                "radio instrument assembly is unavailable",
                "Enable pack.core.diegetic_instruments and retry.",
                {"assembly_id": "instrument.radio_text"},
                "$.universe_state.instrument_assemblies",
            )
        current_tick = int((_ensure_simulation_time(state)).get("tick", 0))
        state_payload = dict(radio_row.get("state") or {}) if isinstance(radio_row.get("state"), dict) else {}
        inbox = _message_rows_sorted(state_payload.get("inbox"), "msg.radio", DIEGETIC_RADIO_MAX_ITEMS)
        author_subject_id = _author_subject_id(authority_context)
        message_payload = {
            "to": recipient_subject_id,
            "text": payload_text,
        }
        message_id = "msg.radio.{}".format(
            canonical_sha256(
                {
                    "author_subject_id": author_subject_id,
                    "recipient_subject_id": recipient_subject_id,
                    "created_tick": current_tick,
                    "payload": message_payload,
                }
            )[:16]
        )
        message = {
            "schema_version": "1.0.0",
            "message_id": message_id,
            "author_subject_id": author_subject_id,
            "created_tick": current_tick,
            "channel_id": "msg.radio",
            "payload": message_payload,
            "signature": None,
            "extensions": {
                "delivery_policy": str(inputs.get("delivery_policy", "same_shard_instant")).strip() or "same_shard_instant",
            },
        }
        inbox.append(message)
        inbox = _message_rows_sorted(inbox, "msg.radio", DIEGETIC_RADIO_MAX_ITEMS)
        state_payload["inbox"] = list(inbox)
        radio_row["state"] = state_payload
        radio_row["reading"] = {
            "messages": [dict(item) for item in inbox],
            "message_count": len(inbox),
        }
        outputs_payload = dict(radio_row.get("outputs") or {}) if isinstance(radio_row.get("outputs"), dict) else {}
        outputs_payload["ch.diegetic.radio_text"] = {
            "messages": [dict(item) for item in inbox],
            "message_count": len(inbox),
        }
        radio_row["outputs"] = outputs_payload
        radio_row["quality"] = "nominal"
        radio_row["quality_value"] = max(0, _as_int(radio_row.get("quality_value", 1000), 1000))
        radio_row["last_update_tick"] = current_tick
        state["instrument_assemblies"] = sorted(
            (dict(item) for item in rows if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        result_metadata = {
            "message_id": message_id,
            "channel_id": "msg.radio",
            "recipient_subject_id": recipient_subject_id,
            "delivered_count": len(inbox),
        }
        _advance_time(state, steps=1)
    elif process_id == "process.time_control_set_rate":
        rate = _as_int(inputs.get("rate_permille", -1), -1)
        if rate < 0 or rate > 10000:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.time_control_set_rate requires rate_permille in [0,10000]",
                "Provide a valid integer rate_permille in the intent inputs.",
                {"process_id": process_id},
                "$.intent.inputs.rate_permille",
            )
        control = _ensure_time_control(state)
        control["rate_permille"] = int(rate)
        if int(rate) == 0:
            control["paused"] = True
        _advance_time(state, steps=1)
    elif process_id == "process.time_pause":
        control = _ensure_time_control(state)
        control["paused"] = True
        _advance_time(state, steps=1)
    elif process_id == "process.time_resume":
        control = _ensure_time_control(state)
        control["paused"] = False
        _advance_time(state, steps=1)
    elif process_id in ("process.region_expand", "process.region_collapse"):
        transition = _run_region_transition_with_lod_invariance(
            state=state,
            process_id=process_id,
            inputs=dict(inputs),
            law_profile=law_profile,
            authority_context=authority_context,
            navigation_indices=navigation_indices,
            policy_context=policy_context,
        )
        if str(transition.get("result", "")) != "complete":
            return transition
        tick_result = dict(transition.get("tick_result") or {})
        lod_summary = dict(transition.get("lod_invariance") or {})
        _advance_time(state, steps=1)
        conservation_result = _finalize_conservation_or_refusal(
            state=state,
            process_id=process_id,
            policy_context=policy_context,
        )
        if str(conservation_result.get("result", "")) != "complete":
            return conservation_result
        state_hash_anchor = _log_process(
            state=state,
            process_id=process_id,
            intent_id=intent_id,
            authority_origin=str(authority_context.get("authority_origin", "")),
            inputs=dict(inputs),
        )
        return {
            "result": "complete",
            "state_hash_anchor": state_hash_anchor,
            "tick": int((_ensure_simulation_time(state)).get("tick", 0)),
            "ledger_hash": str(conservation_result.get("ledger_hash", "")),
            "selected_terrain_tiles": list(tick_result.get("selected_terrain_tiles") or []),
            "active_regions": list(tick_result.get("active_regions") or []),
            "budget_outcome": str(tick_result.get("budget_outcome", "")),
            "forced_expand_region_ids": list(tick_result.get("forced_expand_region_ids") or []),
            "forced_collapse_region_ids": list(tick_result.get("forced_collapse_region_ids") or []),
            "cohort_refinement": list(tick_result.get("cohort_refinement") or []),
            "lod_invariance": lod_summary,
        }
    elif process_id == "process.region_management_tick":
        tick_result = _region_management_tick(
            state=state,
            navigation_indices=navigation_indices,
            policy_context=policy_context,
            process_id=process_id,
        )
        if tick_result.get("result") != "complete":
            return tick_result
        _advance_time(state, steps=1)
        conservation_result = _finalize_conservation_or_refusal(
            state=state,
            process_id=process_id,
            policy_context=policy_context,
        )
        if str(conservation_result.get("result", "")) != "complete":
            return conservation_result
        state_hash_anchor = _log_process(
            state=state,
            process_id=process_id,
            intent_id=intent_id,
            authority_origin=str(authority_context.get("authority_origin", "")),
            inputs=dict(inputs),
        )
        return {
            "result": "complete",
            "state_hash_anchor": state_hash_anchor,
            "tick": int((_ensure_simulation_time(state)).get("tick", 0)),
            "ledger_hash": str(conservation_result.get("ledger_hash", "")),
            "selected_terrain_tiles": list(tick_result.get("selected_terrain_tiles") or []),
            "active_regions": list(tick_result.get("active_regions") or []),
            "budget_outcome": str(tick_result.get("budget_outcome", "")),
            "cohort_refinement": list(tick_result.get("cohort_refinement") or []),
        }
    else:
        return refusal(
            "PROCESS_FORBIDDEN",
            "process '{}' is not implemented in the lab process runtime".format(process_id),
            "Use one of the supported lab process IDs.",
            {"process_id": process_id},
            "$.intent.process_id",
        )

    conservation_result = _finalize_conservation_or_refusal(
        state=state,
        process_id=process_id,
        policy_context=policy_context,
    )
    if str(conservation_result.get("result", "")) != "complete":
        return conservation_result

    if bool(skip_state_log):
        state_hash_anchor = canonical_sha256(state)
    else:
        state_hash_anchor = _log_process(
            state=state,
            process_id=process_id,
            intent_id=intent_id,
            authority_origin=str(authority_context.get("authority_origin", "")),
            inputs=dict(inputs),
        )
    result_payload = {
        "result": "complete",
        "state_hash_anchor": state_hash_anchor,
        "tick": int((_ensure_simulation_time(state)).get("tick", 0)),
        "ledger_hash": str(conservation_result.get("ledger_hash", "")),
    }
    if arrived_cohort_ids:
        result_payload["arrived_cohort_ids"] = list(arrived_cohort_ids)
    if isinstance(result_metadata, dict) and result_metadata:
        result_payload.update(dict(result_metadata))
    return result_payload


def replay_intent_script(
    universe_state: dict,
    law_profile: dict,
    authority_context: dict,
    intents: List[dict],
    navigation_indices: dict | None = None,
    policy_context: dict | None = None,
) -> Dict[str, object]:
    state = copy.deepcopy(universe_state if isinstance(universe_state, dict) else {})
    anchors: List[str] = []
    for step_index, intent in enumerate(list(intents or [])):
        executed = execute_intent(
            state=state,
            intent=intent,
            law_profile=law_profile,
            authority_context=authority_context,
            navigation_indices=navigation_indices,
            policy_context=policy_context,
        )
        if executed.get("result") != "complete":
            refused = dict(executed)
            refused["script_step"] = int(step_index)
            return refused
        anchors.append(str(executed.get("state_hash_anchor", "")))
    return {
        "result": "complete",
        "universe_state": state,
        "state_hash_anchors": anchors,
        "final_state_hash": canonical_sha256(state),
    }

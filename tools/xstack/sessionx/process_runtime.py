"""Deterministic process-driven mutation runtime for lab camera/time intents."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from typing import Dict, List, Tuple

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


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(items: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (items or []) if str(item).strip()))


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
    if int(mass_before) != int(mass_after):
        return refusal(
            "CONSERVATION_VIOLATION",
            "macro/micro transition changed conserved mass_stub total",
            "Inspect region transition ordering and conservation transfer logic.",
            {
                "mass_before": str(mass_before),
                "mass_after": str(mass_after),
            },
            "$.macro_capsules",
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

    return {
        "result": "complete",
        "budget_outcome": str(budget_outcome),
        "compute_units_used": int(usage["compute_units"]),
        "active_regions": sorted(desired_active.keys()),
        "collapsed_regions": collapse_ids,
        "expanded_regions": expand_ids,
        "selected_terrain_tiles": selected_terrain_tiles,
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
    _ensure_collision_state(state)
    current_tick = int((_ensure_simulation_time(state)).get("tick", 0))
    result_metadata: Dict[str, object] = {}
    skip_state_log = False

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
    elif process_id == "process.region_management_tick":
        tick_result = _region_management_tick(
            state=state,
            navigation_indices=navigation_indices,
            policy_context=policy_context,
        )
        if tick_result.get("result") != "complete":
            return tick_result
        _advance_time(state, steps=1)
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
            "selected_terrain_tiles": list(tick_result.get("selected_terrain_tiles") or []),
            "active_regions": list(tick_result.get("active_regions") or []),
            "budget_outcome": str(tick_result.get("budget_outcome", "")),
        }
    else:
        return refusal(
            "PROCESS_FORBIDDEN",
            "process '{}' is not implemented in the lab process runtime".format(process_id),
            "Use one of the supported lab process IDs.",
            {"process_id": process_id},
            "$.intent.process_id",
        )

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
    }
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

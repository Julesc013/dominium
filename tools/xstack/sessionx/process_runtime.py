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
    "process.control_bind_camera": "entitlement.control.camera",
    "process.control_unbind_camera": "entitlement.control.camera",
    "process.control_possess_agent": "entitlement.control.possess",
    "process.control_release_agent": "entitlement.control.possess",
    "process.control_set_view_lens": "entitlement.control.lens_override",
    "process.body_move_attempt": "entitlement.control.possess",
    "process.instrument_tick": "session.boot",
    "process.time_control_set_rate": "entitlement.time_control",
    "process.time_pause": "entitlement.time_control",
    "process.time_resume": "entitlement.time_control",
    "process.region_management_tick": "session.boot",
}
PROCESS_PRIVILEGE_DEFAULTS = {
    "process.camera_move": "observer",
    "process.camera_teleport": "operator",
    "process.control_bind_camera": "observer",
    "process.control_unbind_camera": "observer",
    "process.control_possess_agent": "operator",
    "process.control_release_agent": "operator",
    "process.control_set_view_lens": "operator",
    "process.body_move_attempt": "operator",
    "process.instrument_tick": "observer",
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
    "process.control_bind_camera",
    "process.control_unbind_camera",
    "process.control_possess_agent",
    "process.control_release_agent",
    "process.control_set_view_lens",
    "process.body_move_attempt",
}
CONTROL_GATE_REASON_MAP = {
    "PROCESS_FORBIDDEN": "refusal.control.law_forbidden",
    "ENTITLEMENT_MISSING": "refusal.control.entitlement_missing",
}
CONTROLLER_ACTIONS_BY_TYPE = {
    "admin": [
        "control.action.bind_camera",
        "control.action.unbind_camera",
        "control.action.possess_agent",
        "control.action.release_agent",
        "control.action.set_view_lens",
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
    ],
    "spectator": [
        "control.action.bind_camera",
        "control.action.unbind_camera",
    ],
}


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
        "instrument.compass": {
            "assembly_id": "instrument.compass",
            "instrument_type": "compass",
            "reading": {"heading_mdeg": 0},
            "quality": "nominal",
            "last_update_tick": 0,
        },
        "instrument.clock": {
            "assembly_id": "instrument.clock",
            "instrument_type": "clock",
            "reading": {"tick": 0, "rate_permille": 1000, "paused": False},
            "quality": "nominal",
            "last_update_tick": 0,
        },
        "instrument.altimeter": {
            "assembly_id": "instrument.altimeter",
            "instrument_type": "altimeter",
            "reading": {"altitude_mm": 0},
            "quality": "nominal",
            "last_update_tick": 0,
        },
        "instrument.radio": {
            "assembly_id": "instrument.radio",
            "instrument_type": "radio",
            "reading": {"signal_quality_permille": 1000},
            "quality": "nominal",
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
        reading = row.get("reading")
        row["reading"] = dict(reading) if isinstance(reading, dict) else dict(defaults[assembly_id]["reading"])
        row["quality"] = str(row.get("quality", "nominal")) or "nominal"
        row["last_update_tick"] = max(0, _as_int(row.get("last_update_tick", 0), 0))
        by_id[assembly_id] = row
    normalized = [dict(by_id[key]) for key in sorted(by_id.keys())]
    state["instrument_assemblies"] = normalized
    return normalized


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
            owner_a = _owner_shard_for_object(shard_map=shard_map, object_id=str(body_a.get("owner_assembly_id", left_id)))
            owner_b = _owner_shard_for_object(shard_map=shard_map, object_id=str(body_b.get("owner_assembly_id", right_id)))
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


def _control_gate_refusal(gate_payload: dict) -> dict:
    payload = dict(gate_payload or {})
    refusal_payload = dict(payload.get("refusal") or {})
    reason_code = str(refusal_payload.get("reason_code", "")).strip()
    mapped = str(CONTROL_GATE_REASON_MAP.get(reason_code, "")).strip()
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
    return {"objects": astro, "sites": sites, "ephemeris": ephemeris, "terrain_tiles": terrain_tiles}


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
        if process_id in CONTROL_PROCESS_IDS:
            return _control_gate_refusal(gate)
        return gate

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
    elif process_id == "process.control_bind_camera":
        controller_id = str(inputs.get("controller_id", "")).strip()
        camera_id = str(inputs.get("camera_id", "") or inputs.get("target_id", "")).strip()
        if not controller_id or not camera_id:
            return refusal(
                "refusal.control.target_invalid",
                "process.control_bind_camera requires controller_id and camera_id",
                "Provide controller_id and camera_id in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if not _camera_exists(state=state, camera_id=camera_id):
            return refusal(
                "refusal.control.target_invalid",
                "camera target '{}' does not exist".format(camera_id),
                "Bind to an existing camera assembly id.",
                {"camera_id": camera_id},
                "$.intent.inputs.camera_id",
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
        _store_control_state(state=state, controllers=controllers, bindings=bindings)
        _advance_time(state, steps=1)
    elif process_id == "process.control_unbind_camera":
        controller_id = str(inputs.get("controller_id", "")).strip()
        camera_id = str(inputs.get("camera_id", "") or inputs.get("target_id", "")).strip()
        if not controller_id or not camera_id:
            return refusal(
                "refusal.control.target_invalid",
                "process.control_unbind_camera requires controller_id and camera_id",
                "Provide controller_id and camera_id in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if not _camera_exists(state=state, camera_id=camera_id):
            return refusal(
                "refusal.control.target_invalid",
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
    elif process_id == "process.control_set_view_lens":
        controller_id = str(inputs.get("controller_id", "")).strip()
        lens_id = str(inputs.get("lens_id", "")).strip()
        camera_id = str(inputs.get("camera_id", "camera.main")).strip() or "camera.main"
        if not controller_id or not lens_id:
            return refusal(
                "refusal.control.target_invalid",
                "process.control_set_view_lens requires controller_id and lens_id",
                "Provide controller_id and lens_id in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs",
            )
        if not _camera_exists(state=state, camera_id=camera_id):
            return refusal(
                "refusal.control.target_invalid",
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
                "refusal.control.lens_forbidden",
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
            row["lens_id"] = lens_id
        state["camera_assemblies"] = sorted(
            (dict(item) for item in camera_rows if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
        _store_control_state(state=state, controllers=controllers, bindings=bindings)
        _advance_time(state, steps=1)
    elif process_id == "process.body_move_attempt":
        body_id = str(inputs.get("body_id", "")).strip()
        if not body_id:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.body_move_attempt requires body_id",
                "Provide body_id and delta_transform_mm in the process inputs.",
                {"process_id": process_id},
                "$.intent.inputs.body_id",
            )
        body = _find_body(body_rows=bodies, body_id=body_id)
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
        delta = _vector3_int(inputs.get("delta_transform_mm"), "delta_transform_mm")
        if delta is None:
            delta = _vector3_int(inputs.get("delta_local_mm"), "delta_local_mm")
        dt_ticks = max(1, _as_int(inputs.get("dt_ticks", 1), 1))
        if delta is None:
            return refusal(
                "PROCESS_INPUT_INVALID",
                "process.body_move_attempt requires delta_transform_mm{x,y,z}",
                "Provide integer delta_transform_mm and optional dt_ticks.",
                {"process_id": process_id},
                "$.intent.inputs.delta_transform_mm",
            )
        orientation_delta = _angles_int(inputs.get("delta_orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
        ghost_collisions_enabled = bool(inputs.get("ghost_collisions_enabled", False))

        transform = _vector3_int(body.get("transform_mm"), "transform_mm") or {"x": 0, "y": 0, "z": 0}
        orientation = _angles_int(body.get("orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
        velocity = _vector3_int(body.get("velocity_mm_per_tick"), "velocity_mm_per_tick") or {"x": 0, "y": 0, "z": 0}
        transform["x"] = int(transform["x"]) + int(delta["x"]) * int(dt_ticks)
        transform["y"] = int(transform["y"]) + int(delta["y"]) * int(dt_ticks)
        transform["z"] = int(transform["z"]) + int(delta["z"]) * int(dt_ticks)
        orientation["yaw"] = int(orientation["yaw"]) + int(orientation_delta["yaw"])
        orientation["pitch"] = int(orientation["pitch"]) + int(orientation_delta["pitch"])
        orientation["roll"] = int(orientation["roll"]) + int(orientation_delta["roll"])
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
                (dict(item) for item in bodies if isinstance(item, dict)),
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
        _advance_time(state, steps=int(dt_ticks))
    elif process_id == "process.instrument_tick":
        sim = _ensure_simulation_time(state)
        control = _ensure_time_control(state)
        position = _vector3_int(camera.get("position_mm"), "position_mm") or {"x": 0, "y": 0, "z": 0}
        orientation = _angles_int(camera.get("orientation_mdeg")) or {"yaw": 0, "pitch": 0, "roll": 0}
        heading = int(orientation.get("yaw", 0)) % 360000
        rows = _ensure_instrument_assemblies(state)
        current_tick = int(sim.get("tick", 0))
        for row in rows:
            assembly_id = str(row.get("assembly_id", ""))
            if assembly_id == "instrument.compass":
                row["reading"] = {"heading_mdeg": heading}
            elif assembly_id == "instrument.clock":
                row["reading"] = {
                    "tick": current_tick,
                    "rate_permille": int(control.get("rate_permille", 1000)),
                    "paused": bool(control.get("paused", False)),
                }
            elif assembly_id == "instrument.altimeter":
                row["reading"] = {"altitude_mm": int(position.get("z", 0))}
            elif assembly_id == "instrument.radio":
                row["reading"] = {
                    "signal_quality_permille": 1000,
                    "channel_id": "radio.lab.default",
                }
            row["quality"] = "nominal"
            row["last_update_tick"] = current_tick
        state["instrument_assemblies"] = sorted(
            (dict(item) for item in rows if isinstance(item, dict)),
            key=lambda item: str(item.get("assembly_id", "")),
        )
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
    }


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

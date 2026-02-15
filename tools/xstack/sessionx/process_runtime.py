"""Deterministic process-driven mutation runtime for lab camera/time intents."""

from __future__ import annotations

import copy
import hashlib
from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import refusal


PROCESS_ENTITLEMENT_DEFAULTS = {
    "process.camera_move": "entitlement.camera_control",
    "process.camera_teleport": "entitlement.teleport",
    "process.time_control_set_rate": "entitlement.time_control",
    "process.time_pause": "entitlement.time_control",
    "process.time_resume": "entitlement.time_control",
    "process.region_management_tick": "session.boot",
}
PROCESS_PRIVILEGE_DEFAULTS = {
    "process.camera_move": "observer",
    "process.camera_teleport": "operator",
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
    return {"objects": astro, "sites": sites}


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
        return {
            "result": "complete",
            "frame_id": frame_id or "frame.unknown",
            "position_mm": {"x": 0, "y": 0, "z": default_distance},
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
    }
    performance_state["transition_log"].append(
        {
            "tick": int(current_tick),
            "budget_outcome": str(budget_outcome),
            "compute_units_used": int(usage["compute_units"]),
            "active_regions": sorted(desired_active.keys()),
        }
    )
    state["performance_state"] = performance_state

    return {
        "result": "complete",
        "budget_outcome": str(budget_outcome),
        "compute_units_used": int(usage["compute_units"]),
        "active_regions": sorted(desired_active.keys()),
        "collapsed_regions": collapse_ids,
        "expanded_regions": expand_ids,
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

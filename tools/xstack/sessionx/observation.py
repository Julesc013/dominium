"""Deterministic Observation Kernel v1 for TruthModel -> PerceivedModel derivation."""

from __future__ import annotations

import copy
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import refusal


CHANNEL_ENTITLEMENT_REQUIREMENTS = {
    "ch.nondiegetic.entity_inspector": "entitlement.inspect",
    "ch.nondiegetic.performance_monitor": "entitlement.inspect",
    "ch.truth.overlay.terrain_height": "entitlement.debug_view",
    "ch.truth.overlay.anchor_hash": "entitlement.debug_view",
}


def _sorted_unique(items: List[str]) -> List[str]:
    return sorted(set(str(item).strip() for item in (items or []) if str(item).strip()))


def _required_mapping(payload: dict, keys: Tuple[str, ...], reason_code: str, path: str) -> Dict[str, object]:
    for key in keys:
        if key not in payload:
            return refusal(
                reason_code,
                "required field '{}' is missing".format(key),
                "Provide all required observation input fields before retry.",
                {"field": key},
                path,
            )
    return {"result": "complete"}


def _agent_entity_ids(truth: dict) -> List[str]:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return []
    rows = state.get("agent_states")
    if not isinstance(rows, list):
        return []
    out = []
    for idx, row in enumerate(rows):
        if isinstance(row, dict):
            token = str(row.get("entity_id", "")).strip() or str(row.get("agent_id", "")).strip()
            if token:
                out.append(token)
                continue
        out.append("agent.index.{}".format(idx))
    return sorted(out)


def _simulation_tick(truth: dict) -> int:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return 0
    sim_time = state.get("simulation_time")
    if not isinstance(sim_time, dict):
        return 0
    try:
        return int(sim_time.get("tick", 0) or 0)
    except (TypeError, ValueError):
        return 0


def _registry_payload(truth: dict, key: str) -> dict:
    payloads = truth.get("registry_payloads")
    if not isinstance(payloads, dict):
        return {}
    payload = payloads.get(key)
    if not isinstance(payload, dict):
        return {}
    return payload


def _policy_row(registry_payload: dict, policy_id: str) -> dict:
    rows = registry_payload.get("policies")
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        token = str(row.get("policy_id", "")).strip() or str(row.get("epistemic_policy_id", "")).strip()
        if token == str(policy_id).strip():
            return dict(row)
    return {}


def _resolve_epistemic_policy(
    truth_model: dict,
    law_profile: dict,
    authority_context: dict,
    explicit_policy: dict | None,
) -> Dict[str, object]:
    if isinstance(explicit_policy, dict):
        policy_id = str(explicit_policy.get("epistemic_policy_id", "")).strip() or str(explicit_policy.get("policy_id", "")).strip()
        if policy_id:
            row = dict(explicit_policy)
            row["epistemic_policy_id"] = policy_id
            return {"result": "complete", "policy": row}

    policy_id = str(law_profile.get("epistemic_policy_id", "")).strip()
    scope = authority_context.get("epistemic_scope")
    if not policy_id and isinstance(scope, dict):
        policy_id = str(scope.get("epistemic_policy_id", "")).strip()
    if not policy_id and isinstance(scope, dict):
        policy_id = str(scope.get("scope_id", "")).strip()
    if not policy_id:
        return refusal(
            "refusal.ep.policy_missing",
            "epistemic policy id is missing from law profile and authority context",
            "Declare law_profile.epistemic_policy_id or authority_context.epistemic_scope.epistemic_policy_id.",
            {"law_profile_id": str(law_profile.get("law_profile_id", ""))},
            "$.law_profile.epistemic_policy_id",
        )

    registry_payload = _registry_payload(truth_model, "epistemic_policy_registry")
    rows = registry_payload.get("policies")
    if not isinstance(rows, list):
        return refusal(
            "refusal.ep.policy_missing",
            "epistemic_policy.registry is missing from loaded registry payloads",
            "Compile registries and load epistemic_policy.registry.json before observation.",
            {"epistemic_policy_id": policy_id},
            "$.registry_payloads.epistemic_policy_registry",
        )
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("epistemic_policy_id", ""))):
        token = str(row.get("epistemic_policy_id", "")).strip() or str(row.get("policy_id", "")).strip()
        if token == policy_id:
            payload = dict(row)
            payload["epistemic_policy_id"] = token
            return {"result": "complete", "policy": payload}
    return refusal(
        "refusal.ep.policy_missing",
        "epistemic policy '{}' is not present in registry payloads".format(policy_id),
        "Use a law profile that references a registered epistemic policy.",
        {"epistemic_policy_id": policy_id},
        "$.law_profile.epistemic_policy_id",
    )


def _resolve_retention_policy(
    truth_model: dict,
    epistemic_policy: dict,
    explicit_policy: dict | None,
) -> Dict[str, object]:
    if isinstance(explicit_policy, dict):
        policy_id = str(explicit_policy.get("retention_policy_id", "")).strip() or str(explicit_policy.get("policy_id", "")).strip()
        if policy_id:
            row = dict(explicit_policy)
            row["retention_policy_id"] = policy_id
            return {"result": "complete", "policy": row}

    retention_policy_id = str(epistemic_policy.get("retention_policy_id", "")).strip()
    if not retention_policy_id:
        return refusal(
            "refusal.ep.policy_missing",
            "epistemic policy is missing retention_policy_id",
            "Define retention_policy_id in epistemic_policy registry entry.",
            {"epistemic_policy_id": str(epistemic_policy.get("epistemic_policy_id", ""))},
            "$.epistemic_policy.retention_policy_id",
        )
    registry_payload = _registry_payload(truth_model, "retention_policy_registry")
    rows = registry_payload.get("policies")
    if not isinstance(rows, list):
        return refusal(
            "refusal.ep.policy_missing",
            "retention_policy.registry is missing from loaded registry payloads",
            "Compile registries and load retention_policy.registry.json before observation.",
            {"retention_policy_id": retention_policy_id},
            "$.registry_payloads.retention_policy_registry",
        )
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("retention_policy_id", ""))):
        token = str(row.get("retention_policy_id", "")).strip() or str(row.get("policy_id", "")).strip()
        if token == retention_policy_id:
            payload = dict(row)
            payload["retention_policy_id"] = token
            return {"result": "complete", "policy": payload}
    return refusal(
        "refusal.ep.policy_missing",
        "retention policy '{}' is not present in registry payloads".format(retention_policy_id),
        "Use an epistemic policy that references a registered retention policy.",
        {"retention_policy_id": retention_policy_id},
        "$.epistemic_policy.retention_policy_id",
    )


def _default_lens_channels(lens_type: str) -> List[str]:
    if str(lens_type).strip() == "nondiegetic":
        return [
            "ch.core.time",
            "ch.camera.state",
            "ch.core.navigation",
            "ch.core.sites",
            "ch.core.entities",
            "ch.core.process_log",
            "ch.core.performance",
            "ch.nondiegetic.nav",
            "ch.nondiegetic.entity_inspector",
        ]
    return [
        "ch.core.time",
        "ch.camera.state",
        "ch.diegetic.compass",
        "ch.diegetic.clock",
        "ch.diegetic.altimeter",
        "ch.diegetic.radio",
        "ch.diegetic.map_local",
    ]


def _quantize_int(value: int, step: int) -> int:
    token = int(step) if int(step) > 0 else 1
    number = int(value)
    if number >= 0:
        return int(((number + (token // 2)) // token) * token)
    return int(-(((-number + (token // 2)) // token) * token))


def _camera_distance_mm(camera_viewpoint: dict) -> int:
    position = camera_viewpoint.get("position_mm")
    if not isinstance(position, dict):
        return 0
    x = int(position.get("x", 0) or 0)
    y = int(position.get("y", 0) or 0)
    z = int(position.get("z", 0) or 0)
    return abs(x) + abs(y) + abs(z)


def _precision_rule_for_channel(epistemic_policy: dict, channel_id: str, distance_mm: int) -> dict:
    rows = [
        dict(row)
        for row in (epistemic_policy.get("max_precision_rules") or [])
        if isinstance(row, dict) and str(row.get("channel_id", "")).strip() == str(channel_id).strip()
    ]
    rows = sorted(rows, key=lambda row: (int(row.get("max_distance_mm", 0) or 0), str(row.get("rule_id", ""))))
    if not rows:
        return {}
    for row in rows:
        if int(distance_mm) <= int(row.get("max_distance_mm", 0) or 0):
            return row
    return rows[-1]


def _interest_cull(perceived_model: dict, max_objects: int) -> dict:
    out = copy.deepcopy(dict(perceived_model or {}))
    limit = max(0, int(max_objects))
    if limit < 1:
        out["observed_entities"] = []
        entities = dict(out.get("entities") or {})
        entities["entries"] = []
        out["entities"] = entities
        return out
    selected = sorted(set(str(item).strip() for item in (out.get("observed_entities") or []) if str(item).strip()))[:limit]
    selected_set = set(selected)
    out["observed_entities"] = selected

    entities = dict(out.get("entities") or {})
    entries = entities.get("entries")
    if isinstance(entries, list):
        entities["entries"] = [
            dict(item)
            for item in sorted((row for row in entries if isinstance(row, dict)), key=lambda row: str(row.get("entity_id", "")))
            if str(item.get("entity_id", "")).strip() in selected_set
        ]
    out["entities"] = entities

    navigation = dict(out.get("navigation") or {})
    hierarchy = navigation.get("hierarchy")
    if isinstance(hierarchy, list):
        filtered = []
        for row in sorted((item for item in hierarchy if isinstance(item, dict)), key=lambda item: (str(item.get("kind", "")), str(item.get("object_id", "")))):
            object_id = str(row.get("object_id", "")).strip()
            parent_id = str(row.get("parent_id", "")).strip()
            if object_id in selected_set or parent_id in selected_set:
                filtered.append(dict(row))
        navigation["hierarchy"] = filtered
    out["navigation"] = navigation
    return out


def _channel_payload(perceived_model: dict, channel_id: str) -> dict:
    if channel_id == "ch.core.time":
        return {"time": dict(perceived_model.get("time") or {}), "time_state": dict(perceived_model.get("time_state") or {})}
    if channel_id == "ch.camera.state":
        return {"camera_viewpoint": dict(perceived_model.get("camera_viewpoint") or {})}
    if channel_id in ("ch.core.navigation", "ch.nondiegetic.nav", "ch.diegetic.map_local"):
        return {"navigation": dict(perceived_model.get("navigation") or {})}
    if channel_id == "ch.core.sites":
        return {"sites": dict(perceived_model.get("sites") or {})}
    if channel_id in ("ch.core.entities", "ch.nondiegetic.entity_inspector"):
        return {"entities": dict(perceived_model.get("entities") or {}), "observed_entities": list(perceived_model.get("observed_entities") or [])}
    if channel_id == "ch.core.process_log":
        return {"process_log": dict(perceived_model.get("process_log") or {})}
    if channel_id in ("ch.core.performance", "ch.nondiegetic.performance_monitor"):
        return {"performance": dict(perceived_model.get("performance") or {})}
    instruments = dict(perceived_model.get("diegetic_instruments") or {})
    if channel_id == "ch.diegetic.compass":
        return {"instrument.compass": dict(instruments.get("instrument.compass") or {})}
    if channel_id == "ch.diegetic.clock":
        return {"instrument.clock": dict(instruments.get("instrument.clock") or {})}
    if channel_id == "ch.diegetic.altimeter":
        return {"instrument.altimeter": dict(instruments.get("instrument.altimeter") or {})}
    if channel_id == "ch.diegetic.radio":
        return {"instrument.radio": dict(instruments.get("instrument.radio") or {})}
    truth_overlay = dict(perceived_model.get("truth_overlay") or {})
    if channel_id == "ch.truth.overlay.terrain_height":
        return {"terrain_height_mm": truth_overlay.get("terrain_height_mm")}
    if channel_id == "ch.truth.overlay.anchor_hash":
        return {"state_hash_anchor": truth_overlay.get("state_hash_anchor")}
    return {}


def _apply_channel_filter(perceived_model: dict, requested_channels: List[str]) -> dict:
    out = copy.deepcopy(dict(perceived_model or {}))
    allowed = set(_sorted_unique(list(requested_channels or [])))

    if "ch.camera.state" not in allowed:
        camera = dict(out.get("camera_viewpoint") or {})
        out["camera_viewpoint"] = {
            "assembly_id": str(camera.get("assembly_id", "camera.main")),
            "frame_id": str(camera.get("frame_id", "frame.world")),
        }

    if not ({"ch.core.navigation", "ch.nondiegetic.nav", "ch.diegetic.map_local"} & allowed):
        out["navigation"] = {"hierarchy": [], "search_index": {}, "search_results": [], "selection_summary": "", "ephemeris_tables": [], "terrain_tiles": []}
    if "ch.core.sites" not in allowed:
        out["sites"] = {"entries": [], "search_index": {}}
    if not ({"ch.core.entities", "ch.nondiegetic.entity_inspector"} & allowed):
        out["observed_entities"] = []
        out["entities"] = {"entries": [], "selected_fields": []}
    if not ({"ch.core.process_log", "ch.nondiegetic.performance_monitor"} & allowed):
        out["process_log"] = {"entries": []}
    if not ({"ch.core.performance", "ch.nondiegetic.performance_monitor"} & allowed):
        out["performance"] = {"budget": {"summary": "redacted", "visible": False}, "active_regions": [], "fidelity_tiers": {"coarse": 0, "medium": 0, "fine": 0}}
    if not ({"ch.core.time", "ch.diegetic.clock"} & allowed):
        out["time"] = {"tick": 0, "rate_permille": 0, "paused": True, "summary": "redacted"}
        out["time_state"] = {"tick": 0, "rate_permille": 0, "paused": True}

    instruments = dict(out.get("diegetic_instruments") or {})
    instrument_channels = {
        "instrument.compass": "ch.diegetic.compass",
        "instrument.clock": "ch.diegetic.clock",
        "instrument.altimeter": "ch.diegetic.altimeter",
        "instrument.radio": "ch.diegetic.radio",
    }
    for instrument_id, channel_id in sorted(instrument_channels.items()):
        if channel_id not in allowed:
            instruments[instrument_id] = {}
    out["diegetic_instruments"] = instruments

    truth_overlay = dict(out.get("truth_overlay") or {})
    if "ch.truth.overlay.terrain_height" not in allowed:
        truth_overlay.pop("terrain_height_mm", None)
    if "ch.truth.overlay.anchor_hash" not in allowed:
        truth_overlay.pop("state_hash_anchor", None)
    out["truth_overlay"] = truth_overlay
    out["channels"] = sorted(allowed)
    return out


def _apply_precision_quantization(perceived_model: dict, epistemic_policy: dict, channels: List[str]) -> dict:
    out = copy.deepcopy(dict(perceived_model or {}))
    distance_mm = _camera_distance_mm(dict(out.get("camera_viewpoint") or {}))
    if "ch.camera.state" in channels:
        camera = dict(out.get("camera_viewpoint") or {})
        rule = _precision_rule_for_channel(epistemic_policy=epistemic_policy, channel_id="ch.camera.state", distance_mm=distance_mm)
        if rule:
            position = dict(camera.get("position_mm") or {})
            orientation = dict(camera.get("orientation_mdeg") or {})
            position_step = max(1, int(rule.get("position_quantization_mm", 1) or 1))
            orientation_step = max(1, int(rule.get("orientation_quantization_mdeg", 1) or 1))
            for axis in ("x", "y", "z"):
                if axis in position:
                    position[axis] = _quantize_int(int(position.get(axis, 0) or 0), position_step)
            for axis in ("yaw", "pitch", "roll"):
                if axis in orientation:
                    orientation[axis] = _quantize_int(int(orientation.get(axis, 0) or 0), orientation_step)
            camera["position_mm"] = position
            camera["orientation_mdeg"] = orientation
            out["camera_viewpoint"] = camera
    return out


def _instrument_channel_view(truth: dict, simulation_tick: int) -> dict:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        state = {}
    rows = state.get("instrument_assemblies")
    if not isinstance(rows, list):
        rows = []
    payload = {
        "instrument.compass": {},
        "instrument.clock": {},
        "instrument.altimeter": {},
        "instrument.radio": {},
    }
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
        assembly_id = str(row.get("assembly_id", "")).strip()
        if assembly_id in payload:
            payload[assembly_id] = {
                "reading": copy.deepcopy(row.get("reading")),
                "quality": str(row.get("quality", "")),
                "last_update_tick": int(row.get("last_update_tick", simulation_tick) or simulation_tick),
            }
    return payload


def _update_memory_hook(
    perceived_model: dict,
    retention_policy: dict,
    memory_state: dict | None,
) -> Tuple[dict, dict]:
    state = dict(memory_state or {})
    memory_allowed = bool(retention_policy.get("memory_allowed", False))
    max_items = max(0, int(retention_policy.get("max_memory_items", 0) or 0))
    entries = list(state.get("entries") or [])
    channels = _sorted_unique(list(perceived_model.get("channels") or []))
    tick = int((perceived_model.get("time") or {}).get("tick", 0) or 0)
    if memory_allowed and max_items > 0:
        for channel_id in channels:
            payload = _channel_payload(perceived_model, channel_id)
            entry = {
                "tick": int(tick),
                "channel_id": str(channel_id),
                "payload_hash": canonical_sha256(payload),
            }
            entries.append(entry)
        dedup = []
        seen = set()
        for row in sorted(
            (dict(item) for item in entries if isinstance(item, dict)),
            key=lambda item: (int(item.get("tick", 0) or 0), str(item.get("channel_id", "")), str(item.get("payload_hash", ""))),
        ):
            key = (
                int(row.get("tick", 0) or 0),
                str(row.get("channel_id", "")),
                str(row.get("payload_hash", "")),
            )
            if key in seen:
                continue
            seen.add(key)
            dedup.append(row)
        if len(dedup) > max_items:
            dedup = dedup[-max_items:]
        entries = dedup
    else:
        entries = []
    state["entries"] = list(entries)
    memory_block = {
        "retention_policy_id": str(retention_policy.get("retention_policy_id", "")),
        "memory_allowed": bool(memory_allowed),
        "deterministic_eviction_rule_id": str(retention_policy.get("deterministic_eviction_rule_id", "")),
        "entries": list(entries),
    }
    return memory_block, state


def _navigation_view(truth: dict) -> dict:
    astronomy = _registry_payload(truth, "astronomy_catalog_index")
    ephemeris = _registry_payload(truth, "ephemeris_registry")
    terrain_tiles = _registry_payload(truth, "terrain_tile_registry")
    entries = astronomy.get("entries")
    rows = []
    if isinstance(entries, list):
        for item in entries:
            if not isinstance(item, dict):
                continue
            object_id = str(item.get("object_id", "")).strip()
            if not object_id:
                continue
            rows.append(
                {
                    "object_id": object_id,
                    "parent_id": item.get("parent_id"),
                    "kind": str(item.get("kind", "")).strip(),
                    "frame_id": str(item.get("frame_id", "")).strip(),
                    "search_keys": sorted(
                        set(str(token).strip() for token in (item.get("search_keys") or []) if str(token).strip())
                    ),
                }
            )
    rows = sorted(rows, key=lambda item: (str(item.get("kind", "")), str(item.get("object_id", ""))))
    search_index = astronomy.get("search_index")
    normalized_search = {}
    if isinstance(search_index, dict):
        for key in sorted(search_index.keys()):
            value = search_index.get(key)
            if not isinstance(value, list):
                continue
            normalized_search[str(key)] = sorted(set(str(token).strip() for token in value if str(token).strip()))

    ephemeris_rows = []
    for item in ephemeris.get("tables") or []:
        if not isinstance(item, dict):
            continue
        body_id = str(item.get("body_id", "")).strip()
        if not body_id:
            continue
        sample_count = len(list(item.get("samples") or []))
        ephemeris_rows.append(
            {
                "body_id": body_id,
                "reference_frame": str(item.get("reference_frame", "")).strip(),
                "sample_count": int(sample_count),
            }
        )
    ephemeris_rows = sorted(ephemeris_rows, key=lambda item: str(item.get("body_id", "")))

    terrain_rows = []
    for item in terrain_tiles.get("tiles") or []:
        if not isinstance(item, dict):
            continue
        tile_id = str(item.get("tile_id", "")).strip()
        if not tile_id:
            continue
        terrain_rows.append(
            {
                "tile_id": tile_id,
                "z": int(item.get("z", 0) or 0),
                "x": int(item.get("x", 0) or 0),
                "y": int(item.get("y", 0) or 0),
                "source_id": str(item.get("source_id", "")).strip(),
            }
        )
    terrain_rows = sorted(
        terrain_rows,
        key=lambda item: (int(item.get("z", 0)), int(item.get("x", 0)), int(item.get("y", 0)), str(item.get("tile_id", ""))),
    )
    return {
        "hierarchy": rows,
        "search_index": normalized_search,
        "search_results": [],
        "selection_summary": "",
        "ephemeris_tables": ephemeris_rows,
        "terrain_tiles": terrain_rows,
    }


def _site_view(truth: dict) -> dict:
    site_registry = _registry_payload(truth, "site_registry_index")
    entries = site_registry.get("sites")
    rows = []
    if isinstance(entries, list):
        for item in entries:
            if not isinstance(item, dict):
                continue
            site_id = str(item.get("site_id", "")).strip()
            if not site_id:
                continue
            rows.append(
                {
                    "site_id": site_id,
                    "object_id": str(item.get("object_id", "")).strip(),
                    "kind": str(item.get("kind", "")).strip(),
                    "frame_id": str(item.get("frame_id", "")).strip(),
                }
            )
    rows = sorted(rows, key=lambda item: (str(item.get("object_id", "")), str(item.get("site_id", ""))))
    search_index = site_registry.get("search_index")
    normalized_search = {}
    if isinstance(search_index, dict):
        for key in sorted(search_index.keys()):
            value = search_index.get(key)
            if not isinstance(value, list):
                continue
            normalized_search[str(key)] = sorted(set(str(token).strip() for token in value if str(token).strip()))
    return {
        "entries": rows,
        "search_index": normalized_search,
    }


def _process_log_entries(truth: dict) -> list:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return []
    rows = state.get("process_log")
    if not isinstance(rows, list):
        return []
    out = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "log_index": int(item.get("log_index", 0) or 0),
                "process_id": str(item.get("process_id", "")),
                "intent_id": str(item.get("intent_id", "")),
                "tick": int(item.get("tick", 0) or 0),
                "outcome": "complete",
                "state_hash_anchor": str(item.get("state_hash_anchor", "")),
            }
        )
    return sorted(out, key=lambda item: (int(item.get("log_index", 0)), str(item.get("intent_id", ""))))


def _entity_view(truth: dict, observed_entities: List[str]) -> dict:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return {"entries": [], "selected_fields": []}
    known = sorted(set(str(item).strip() for item in observed_entities if str(item).strip()))
    entries = [{"entity_id": token} for token in known]
    for camera in state.get("camera_assemblies") or []:
        if not isinstance(camera, dict):
            continue
        assembly_id = str(camera.get("assembly_id", "")).strip()
        if not assembly_id:
            continue
        if assembly_id not in known:
            entries.append({"entity_id": assembly_id})
    entries = sorted(entries, key=lambda item: str(item.get("entity_id", "")))
    return {
        "entries": entries,
        "selected_fields": [],
    }


def _camera_main(truth: dict) -> dict:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return {}
    rows = state.get("camera_assemblies")
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() == "camera.main":
            return dict(row)
    return {}


def _time_control(truth: dict) -> dict:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return {"rate_permille": 1000, "paused": False}
    payload = state.get("time_control")
    if not isinstance(payload, dict):
        return {"rate_permille": 1000, "paused": False}
    try:
        rate = int(payload.get("rate_permille", 1000) or 1000)
    except (TypeError, ValueError):
        rate = 1000
    return {
        "rate_permille": max(0, rate),
        "paused": bool(payload.get("paused", False)),
    }


def _performance_view(truth: dict, allow_hidden: bool) -> dict:
    zero_tiers = {
        "coarse": 0,
        "medium": 0,
        "fine": 0,
    }
    if not allow_hidden:
        return {
            "budget": {
                "summary": "redacted",
                "visible": False,
            },
            "active_regions": [],
            "fidelity_tiers": dict(zero_tiers),
        }

    state = truth.get("universe_state")
    if not isinstance(state, dict):
        state = {}
    perf = state.get("performance_state")
    if not isinstance(perf, dict):
        perf = {}
    tier_counts = perf.get("fidelity_tier_counts")
    if not isinstance(tier_counts, dict):
        tier_counts = {}
    normalized_tiers = {
        "coarse": int(tier_counts.get("coarse", 0) or 0),
        "medium": int(tier_counts.get("medium", 0) or 0),
        "fine": int(tier_counts.get("fine", 0) or 0),
    }

    active_rows = []
    regions = state.get("interest_regions")
    if isinstance(regions, list):
        for item in regions:
            if not isinstance(item, dict):
                continue
            if not bool(item.get("active", False)):
                continue
            active_rows.append(
                {
                    "region_id": str(item.get("region_id", "")),
                    "anchor_object_id": str(item.get("anchor_object_id", "")),
                    "fidelity_tier": str(item.get("current_fidelity_tier", "")),
                    "last_transition_tick": int(item.get("last_transition_tick", 0) or 0),
                }
            )
    active_rows = sorted(active_rows, key=lambda row: str(row.get("region_id", "")))
    return {
        "budget": {
            "budget_policy_id": str(perf.get("budget_policy_id", "")),
            "fidelity_policy_id": str(perf.get("fidelity_policy_id", "")),
            "activation_policy_id": str(perf.get("activation_policy_id", "")),
            "compute_units_used": int(perf.get("compute_units_used", 0) or 0),
            "max_compute_units_per_tick": int(perf.get("max_compute_units_per_tick", 0) or 0),
            "budget_outcome": str(perf.get("budget_outcome", "ok")),
            "active_region_count": int(perf.get("active_region_count", len(active_rows)) or 0),
            "summary": "budget={} outcome={} active_regions={}".format(
                int(perf.get("compute_units_used", 0) or 0),
                str(perf.get("budget_outcome", "ok")),
                len(active_rows),
            ),
            "visible": True,
        },
        "active_regions": active_rows,
        "fidelity_tiers": normalized_tiers,
    }


def build_truth_model(
    universe_identity: dict,
    universe_state: dict,
    lockfile_payload: dict,
    identity_path: str,
    state_path: str,
    registry_payloads: dict | None = None,
) -> dict:
    """Build minimal TruthModel payload for deterministic observation derivation."""
    registries = lockfile_payload.get("registries")
    if not isinstance(registries, dict):
        registries = {}
    return {
        "schema_version": "1.0.0",
        "universe_identity_ref": str(identity_path),
        "universe_state_ref": str(state_path),
        "registry_refs": {
            "domain_registry_hash": str(registries.get("domain_registry_hash", "")),
            "law_registry_hash": str(registries.get("law_registry_hash", "")),
            "experience_registry_hash": str(registries.get("experience_registry_hash", "")),
            "lens_registry_hash": str(registries.get("lens_registry_hash", "")),
            "activation_policy_registry_hash": str(registries.get("activation_policy_registry_hash", "")),
            "budget_policy_registry_hash": str(registries.get("budget_policy_registry_hash", "")),
            "fidelity_policy_registry_hash": str(registries.get("fidelity_policy_registry_hash", "")),
            "astronomy_catalog_index_hash": str(registries.get("astronomy_catalog_index_hash", "")),
            "site_registry_index_hash": str(registries.get("site_registry_index_hash", "")),
            "ephemeris_registry_hash": str(registries.get("ephemeris_registry_hash", "")),
            "terrain_tile_registry_hash": str(registries.get("terrain_tile_registry_hash", "")),
            "perception_interest_policy_registry_hash": str(registries.get("perception_interest_policy_registry_hash", "")),
            "epistemic_policy_registry_hash": str(registries.get("epistemic_policy_registry_hash", "")),
            "retention_policy_registry_hash": str(registries.get("retention_policy_registry_hash", "")),
            "ui_registry_hash": str(registries.get("ui_registry_hash", "")),
        },
        "universe_identity": dict(universe_identity),
        "universe_state": dict(universe_state),
        "simulation_tick": _simulation_tick({"universe_state": universe_state}),
        "registry_payloads": dict(registry_payloads or {}),
    }


def observe_truth(
    truth_model: dict,
    lens: dict,
    law_profile: dict,
    authority_context: dict,
    viewpoint_id: str,
    epistemic_policy: dict | None = None,
    retention_policy: dict | None = None,
    memory_state: dict | None = None,
    perception_interest_limit: int | None = None,
) -> Dict[str, object]:
    """Observation Kernel contract: TruthModel x Lens x LawProfile x AuthorityContext -> PerceivedModel."""
    input_check = _required_mapping(
        authority_context,
        ("authority_origin", "experience_id", "law_profile_id", "entitlements", "epistemic_scope", "privilege_level"),
        "AUTHORITY_CONTEXT_INVALID",
        "$.authority_context",
    )
    if input_check.get("result") != "complete":
        return input_check

    lens_check = _required_mapping(
        lens,
        ("lens_id", "lens_type", "required_entitlements", "epistemic_constraints"),
        "LENS_INVALID",
        "$.lens",
    )
    if lens_check.get("result") != "complete":
        return lens_check
    law_check = _required_mapping(law_profile, ("law_profile_id", "allowed_lenses", "epistemic_limits"), "LAW_PROFILE_INVALID", "$.law_profile")
    if law_check.get("result") != "complete":
        return law_check

    lens_id = str(lens.get("lens_id", "")).strip()
    lens_type = str(lens.get("lens_type", "")).strip()
    if lens_type not in ("diegetic", "nondiegetic"):
        return refusal(
            "LENS_INVALID",
            "lens_type must be diegetic or nondiegetic",
            "Fix lens_type in lens contribution payload.",
            {"lens_id": lens_id or "<missing>"},
            "$.lens.lens_type",
        )

    allowed_lenses = _sorted_unique(list(law_profile.get("allowed_lenses") or []))
    if lens_id not in allowed_lenses:
        return refusal(
            "LENS_FORBIDDEN",
            "lens '{}' is not permitted by law profile '{}'".format(
                lens_id,
                str(law_profile.get("law_profile_id", "")),
            ),
            "Select an allowed lens declared by the active LawProfile.",
            {
                "lens_id": lens_id,
                "law_profile_id": str(law_profile.get("law_profile_id", "")),
            },
            "$.lens.lens_id",
        )

    entitlements = _sorted_unique(list(authority_context.get("entitlements") or []))
    required_entitlements = _sorted_unique(list(lens.get("required_entitlements") or []))
    if lens_type == "nondiegetic":
        required_entitlements = _sorted_unique(required_entitlements + ["lens.nondiegetic.access"])
    missing_entitlements = [token for token in required_entitlements if token not in entitlements]
    if missing_entitlements:
        return refusal(
            "ENTITLEMENT_MISSING",
            "authority context missing required lens entitlements",
            "Grant the missing entitlements or select a lens with lower requirements.",
            {
                "lens_id": lens_id,
                "missing_entitlements": ",".join(missing_entitlements),
            },
            "$.authority_context.entitlements",
        )

    scope = authority_context.get("epistemic_scope")
    if not isinstance(scope, dict):
        return refusal(
            "AUTHORITY_CONTEXT_INVALID",
            "epistemic_scope must be an object",
            "Populate authority_context.epistemic_scope in SessionSpec.",
            {"field": "epistemic_scope"},
            "$.authority_context.epistemic_scope",
        )

    policy_result = _resolve_epistemic_policy(
        truth_model=truth_model,
        law_profile=law_profile,
        authority_context=authority_context,
        explicit_policy=epistemic_policy,
    )
    if str(policy_result.get("result", "")) != "complete":
        return policy_result
    active_epistemic_policy = dict(policy_result.get("policy") or {})

    retention_result = _resolve_retention_policy(
        truth_model=truth_model,
        epistemic_policy=active_epistemic_policy,
        explicit_policy=retention_policy,
    )
    if str(retention_result.get("result", "")) != "complete":
        return retention_result
    active_retention_policy = dict(retention_result.get("policy") or {})

    policy_allowed_channels = _sorted_unique(list(active_epistemic_policy.get("allowed_observation_channels") or []))
    policy_forbidden_channels = _sorted_unique(list(active_epistemic_policy.get("forbidden_channels") or []))
    requested_channels = _sorted_unique(list(lens.get("observation_channels") or []))
    if not requested_channels:
        requested_channels = _default_lens_channels(lens_type=lens_type)

    channel_forbidden = sorted(
        token
        for token in requested_channels
        if token in set(policy_forbidden_channels) or token not in set(policy_allowed_channels)
    )
    if channel_forbidden:
        return refusal(
            "refusal.ep.channel_forbidden",
            "requested lens channels are forbidden by active epistemic policy",
            "Select a lens whose observation_channels are allowed by the active epistemic policy.",
            {
                "lens_id": lens_id,
                "epistemic_policy_id": str(active_epistemic_policy.get("epistemic_policy_id", "")),
                "forbidden_channels": ",".join(channel_forbidden),
            },
            "$.lens.observation_channels",
        )

    missing_channel_entitlements = []
    for channel_id in requested_channels:
        entitlement_id = str(CHANNEL_ENTITLEMENT_REQUIREMENTS.get(channel_id, "")).strip()
        if entitlement_id and entitlement_id not in entitlements:
            missing_channel_entitlements.append(entitlement_id)
    missing_channel_entitlements = _sorted_unique(missing_channel_entitlements)
    if missing_channel_entitlements:
        return refusal(
            "refusal.ep.entitlement_missing",
            "authority context missing required channel entitlements",
            "Grant required entitlements or choose a lens with lower channel requirements.",
            {
                "lens_id": lens_id,
                "missing_entitlements": ",".join(missing_channel_entitlements),
            },
            "$.authority_context.entitlements",
        )

    observed_entities = _agent_entity_ids(truth_model)
    simulation_tick = _simulation_tick(truth_model)
    time_control = _time_control(truth_model)
    camera = _camera_main(truth_model)
    epistemic_limits = law_profile.get("epistemic_limits")
    allow_hidden = bool((epistemic_limits or {}).get("allow_hidden_state_access", False)) if isinstance(epistemic_limits, dict) else False
    observed_fields = [
        {
            "field_id": "simulation_time.tick",
            "value": str(simulation_tick),
        }
    ]
    if allow_hidden:
        observed_fields.append(
            {
                "field_id": "time_control.rate_permille",
                "value": str(int(time_control.get("rate_permille", 1000))),
            }
        )
        observed_fields.append(
            {
                "field_id": "time_control.paused",
                "value": "true" if bool(time_control.get("paused", False)) else "false",
            }
        )

    camera_viewpoint = {
        "assembly_id": str(camera.get("assembly_id", "camera.main")),
        "frame_id": str(camera.get("frame_id", "frame.world")),
    }
    if allow_hidden or "ch.camera.state" in requested_channels:
        camera_viewpoint["position_mm"] = dict(camera.get("position_mm") or {"x": 0, "y": 0, "z": 0})
        camera_viewpoint["orientation_mdeg"] = dict(camera.get("orientation_mdeg") or {"yaw": 0, "pitch": 0, "roll": 0})
        camera_viewpoint["lens_id"] = str(camera.get("lens_id", lens_id))
    camera_time = {
        "tick": simulation_tick,
        "rate_permille": int(time_control.get("rate_permille", 1000)),
        "paused": bool(time_control.get("paused", False)),
    }
    navigation = _navigation_view(truth_model)
    sites = _site_view(truth_model)
    process_log = _process_log_entries(truth_model)
    entities = _entity_view(truth_model, observed_entities=observed_entities)
    performance = _performance_view(truth_model, allow_hidden=allow_hidden)
    diegetic_instruments = _instrument_channel_view(truth=truth_model, simulation_tick=simulation_tick)
    state_hash_anchor = canonical_sha256(dict(truth_model.get("universe_state") or {}))
    terrain_height_mm = int((camera_viewpoint.get("position_mm") or {}).get("z", 0) or 0)
    filter_chain = [str(item).strip() for item in (active_epistemic_policy.get("deterministic_filters") or []) if str(item).strip()]
    if not filter_chain:
        filter_chain = [
            "filter.channel_allow_deny.v1",
            "filter.quantize_precision.v1",
            "filter.interest_cull.v1",
        ]

    perceived_model = {
        "schema_version": "1.0.0",
        "viewpoint_id": str(viewpoint_id),
        "lens_id": lens_id,
        "epistemic_scope": {
            "scope_id": str(scope.get("scope_id", "")),
            "visibility_level": str(scope.get("visibility_level", "")),
        },
        "observed_entities": observed_entities,
        "observed_fields": observed_fields,
        "camera_viewpoint": camera_viewpoint,
        "time_state": camera_time,
        "navigation": navigation,
        "sites": sites,
        "entities": entities,
        "process_log": {
            "entries": process_log,
        },
        "diegetic_instruments": diegetic_instruments,
        "truth_overlay": {
            "terrain_height_mm": terrain_height_mm,
            "state_hash_anchor": state_hash_anchor,
        },
        "performance": performance,
        "time": {
            "tick": simulation_tick,
            "rate_permille": int(time_control.get("rate_permille", 1000)),
            "paused": bool(time_control.get("paused", False)),
            "summary": "tick={} rate={} paused={}".format(
                simulation_tick,
                int(time_control.get("rate_permille", 1000)),
                "true" if bool(time_control.get("paused", False)) else "false",
            ),
        },
        "tool": {
            "log": {
                "entries": [],
            }
        },
        "metadata": {
            "simulation_tick": simulation_tick,
            "coordinate_frame": "world.global",
            "lens_type": lens_type,
            "epistemic_policy_id": str(active_epistemic_policy.get("epistemic_policy_id", "")),
            "retention_policy_id": str(active_retention_policy.get("retention_policy_id", "")),
            "deterministic_filter_chain": list(filter_chain),
            "epistemic_visibility_policy": str((lens.get("epistemic_constraints") or {}).get("visibility_policy", "")),
        },
    }
    perceived_model = _apply_channel_filter(
        perceived_model=perceived_model,
        requested_channels=requested_channels,
    )
    perceived_model = _apply_precision_quantization(
        perceived_model=perceived_model,
        epistemic_policy=active_epistemic_policy,
        channels=requested_channels,
    )

    max_objects = 0
    for candidate in (
        perception_interest_limit,
        scope.get("max_objects"),
        scope.get("max_observed_entities"),
    ):
        if candidate is None:
            continue
        try:
            max_objects = max(max_objects, int(candidate))
        except (TypeError, ValueError):
            continue
    if max_objects > 0:
        perceived_model = _interest_cull(perceived_model=perceived_model, max_objects=max_objects)

    memory_block, next_memory_state = _update_memory_hook(
        perceived_model=perceived_model,
        retention_policy=active_retention_policy,
        memory_state=memory_state,
    )
    perceived_model["memory"] = memory_block
    perceived_model_hash_value = canonical_sha256(perceived_model)
    return {
        "result": "complete",
        "perceived_model": perceived_model,
        "perceived_model_hash": perceived_model_hash_value,
        "epistemic_policy_id": str(active_epistemic_policy.get("epistemic_policy_id", "")),
        "retention_policy_id": str(active_retention_policy.get("retention_policy_id", "")),
        "memory_state": next_memory_state,
    }


def perceived_model_hash(payload: dict) -> str:
    """Return deterministic canonical hash for a PerceivedModel payload."""
    return canonical_sha256(payload)

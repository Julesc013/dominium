"""Deterministic Observation Kernel v1 for TruthModel -> PerceivedModel derivation."""

from __future__ import annotations

import copy
from typing import Dict, List, Tuple

from src.diegetics import compute_diegetic_instruments
from src.epistemics.memory import update_memory_store
from src.interior import InteriorError, path_exists
from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import refusal


CHANNEL_ENTITLEMENT_REQUIREMENTS = {
    "ch.nondiegetic.entity_inspector": "entitlement.inspect",
    "ch.nondiegetic.performance_monitor": "entitlement.inspect",
    "ch.truth.overlay.terrain_height": "entitlement.debug_view",
    "ch.truth.overlay.anchor_hash": "entitlement.debug_view",
}
DEFAULT_RENDER_PROXY_ID = "render.proxy.pill_default"
DEFAULT_COSMETIC_ID = "cosmetic.default.pill"


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


def _viewer_graph_portal_entity_ids(truth: dict, interior_occlusion_meta: dict) -> List[str]:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return []
    viewer_graph_id = str((dict(interior_occlusion_meta or {})).get("viewer_graph_id", "")).strip()
    if not viewer_graph_id:
        return []
    graph_rows = [
        dict(item)
        for item in list(state.get("interior_graphs") or [])
        if isinstance(item, dict)
    ]
    graph_row = {}
    for row in sorted(graph_rows, key=lambda item: str(item.get("graph_id", ""))):
        if str(row.get("graph_id", "")).strip() == viewer_graph_id:
            graph_row = dict(row)
            break
    if not graph_row:
        return []
    return [
        "interior.portal.{}".format(token)
        for token in _sorted_unique(list(graph_row.get("portals") or []))
        if str(token).strip()
    ]


def _interior_row_index(rows: object, id_key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(id_key, ""))):
        token = str(row.get(id_key, "")).strip()
        if not token:
            continue
        out[token] = dict(row)
    return out


def _interior_entity_volume_map(state: dict) -> Dict[str, str]:
    out: Dict[str, str] = {}

    explicit_rows = list(state.get("interior_entity_locations") or [])
    for row in sorted(
        (item for item in explicit_rows if isinstance(item, dict)),
        key=lambda item: (
            str(item.get("entity_id", "")),
            str(item.get("agent_id", "")),
            str(item.get("volume_id", "")),
        ),
    ):
        entity_id = (
            str(row.get("entity_id", "")).strip()
            or str(row.get("agent_id", "")).strip()
            or str(row.get("semantic_id", "")).strip()
        )
        volume_id = (
            str(row.get("volume_id", "")).strip()
            or str(row.get("interior_volume_id", "")).strip()
            or str((dict(row.get("extensions") or {})).get("volume_id", "")).strip()
        )
        if entity_id and volume_id:
            out[entity_id] = volume_id

    for row in sorted((item for item in list(state.get("agent_states") or []) if isinstance(item, dict)), key=lambda item: str(item.get("agent_id", ""))):
        entity_id = str(row.get("entity_id", "")).strip() or str(row.get("agent_id", "")).strip()
        ext = dict(row.get("extensions") or {})
        volume_id = (
            str(row.get("interior_volume_id", "")).strip()
            or str(row.get("current_volume_id", "")).strip()
            or str(row.get("volume_id", "")).strip()
            or str(ext.get("interior_volume_id", "")).strip()
            or str(ext.get("volume_id", "")).strip()
        )
        if entity_id and volume_id and entity_id not in out:
            out[entity_id] = volume_id
    return dict((key, out[key]) for key in sorted(out.keys()))


def _viewer_interior_volume_id(*, state: dict, camera: dict, authority_context: dict, entity_volume_by_id: Dict[str, str]) -> str:
    camera_ext = dict(camera.get("extensions") or {})
    for token in (
        str(camera.get("interior_volume_id", "")).strip(),
        str(camera.get("current_volume_id", "")).strip(),
        str(camera.get("volume_id", "")).strip(),
        str(camera_ext.get("interior_volume_id", "")).strip(),
    ):
        if token:
            return token

    scope = dict(authority_context.get("epistemic_scope") or {})
    scope_ext = dict(scope.get("extensions") or {})
    for token in (
        str(scope.get("interior_volume_id", "")).strip(),
        str(scope.get("current_volume_id", "")).strip(),
        str(scope.get("volume_id", "")).strip(),
        str(scope_ext.get("interior_volume_id", "")).strip(),
    ):
        if token:
            return token

    subject_tokens = _sorted_unique(
        [
            str(scope.get("subject_id", "")).strip(),
            str(authority_context.get("subject_id", "")).strip(),
            str(authority_context.get("peer_id", "")).strip(),
        ]
    )
    for subject_id in subject_tokens:
        volume_id = str(entity_volume_by_id.get(subject_id, "")).strip()
        if volume_id:
            return volume_id
    return ""


def _interior_occlusion_bypass_allowed(*, law_profile: dict, lens: dict, lens_type: str) -> bool:
    lens_id = str(lens.get("lens_id", "")).strip()
    limits = dict(law_profile.get("epistemic_limits") or {})
    if lens_id == "lens.nondiegetic.freecam":
        return True
    if str(lens_type).strip() == "nondiegetic" and bool(limits.get("allow_freecam_occlusion_bypass", False)):
        return True
    return bool(limits.get("allow_interior_occlusion_bypass", False))


def _apply_interior_occlusion(
    *,
    truth_model: dict,
    observed_entities: List[str],
    camera: dict,
    lens: dict,
    lens_type: str,
    law_profile: dict,
    authority_context: dict,
) -> Tuple[List[str], dict]:
    state = truth_model.get("universe_state")
    if not isinstance(state, dict):
        return sorted(_sorted_unique(list(observed_entities or []))), {"applied": False, "reason": "no_state"}

    if _interior_occlusion_bypass_allowed(law_profile=law_profile, lens=lens, lens_type=lens_type):
        return sorted(_sorted_unique(list(observed_entities or []))), {"applied": False, "reason": "bypass_allowed"}

    graph_rows = [dict(item) for item in list(state.get("interior_graphs") or []) if isinstance(item, dict)]
    volume_rows = [dict(item) for item in list(state.get("interior_volumes") or []) if isinstance(item, dict)]
    portal_rows = [dict(item) for item in list(state.get("interior_portals") or []) if isinstance(item, dict)]
    if not graph_rows or not volume_rows:
        return sorted(_sorted_unique(list(observed_entities or []))), {"applied": False, "reason": "no_interior_graph"}

    entity_volume_by_id = _interior_entity_volume_map(state)
    viewer_volume_id = _viewer_interior_volume_id(
        state=state,
        camera=dict(camera or {}),
        authority_context=dict(authority_context or {}),
        entity_volume_by_id=entity_volume_by_id,
    )
    if not viewer_volume_id:
        return sorted(_sorted_unique(list(observed_entities or []))), {"applied": False, "reason": "no_viewer_volume"}

    graph_by_id = _interior_row_index(graph_rows, "graph_id")
    graph_for_volume: Dict[str, str] = {}
    for graph_id in sorted(graph_by_id.keys()):
        graph = dict(graph_by_id.get(graph_id) or {})
        volume_ids = _sorted_unique(list(graph.get("volumes") or []))
        for volume_id in volume_ids:
            if volume_id and volume_id not in graph_for_volume:
                graph_for_volume[volume_id] = graph_id

    viewer_graph_id = str(graph_for_volume.get(viewer_volume_id, "")).strip()
    if not viewer_graph_id:
        return sorted(_sorted_unique(list(observed_entities or []))), {"applied": False, "reason": "viewer_not_in_graph"}

    viewer_graph = dict(graph_by_id.get(viewer_graph_id) or {})
    portal_state_rows = list(state.get("interior_portal_state_machines") or [])
    visible = []
    hidden = []
    for entity_id in sorted(_sorted_unique(list(observed_entities or []))):
        entity_volume_id = str(entity_volume_by_id.get(entity_id, "")).strip()
        if not entity_volume_id:
            visible.append(entity_id)
            continue
        if entity_volume_id == viewer_volume_id:
            visible.append(entity_id)
            continue
        entity_graph_id = str(graph_for_volume.get(entity_volume_id, "")).strip()
        if entity_graph_id != viewer_graph_id:
            visible.append(entity_id)
            continue
        try:
            if path_exists(
                graph_row=viewer_graph,
                volume_rows=volume_rows,
                portal_rows=portal_rows,
                from_volume_id=viewer_volume_id,
                to_volume_id=entity_volume_id,
                portal_state_rows=portal_state_rows,
            ):
                visible.append(entity_id)
            else:
                hidden.append(entity_id)
        except InteriorError:
            visible.append(entity_id)

    return sorted(visible), {
        "applied": True,
        "viewer_volume_id": viewer_volume_id,
        "viewer_graph_id": viewer_graph_id,
        "visible_count": len(visible),
        "hidden_count": len(hidden),
        "hidden_entity_ids": list(sorted(hidden))[:64],
    }


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


def _view_mode_registry(truth: dict) -> dict:
    return _registry_payload(truth, "view_mode_registry")


def _observer_watermark_payload(truth: dict, camera: dict) -> dict:
    view_mode_id = str((camera or {}).get("view_mode_id", "")).strip()
    watermark_policy_id = ""
    registry = _view_mode_registry(truth)
    rows = registry.get("view_modes")
    if isinstance(rows, list) and view_mode_id:
        for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("view_mode_id", ""))):
            if str(row.get("view_mode_id", "")).strip() != view_mode_id:
                continue
            watermark_policy_id = str(row.get("watermark_policy_id", "") or "").strip()
            break
    required = bool(watermark_policy_id)
    return {
        "active": bool(required),
        "view_mode_id": view_mode_id,
        "watermark_policy_id": watermark_policy_id,
        "text": "OBSERVER MODE" if required else "",
    }


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


def _resolve_decay_model(
    truth_model: dict,
    retention_policy: dict,
) -> Dict[str, object]:
    decay_model_id = str(retention_policy.get("decay_model_id", "")).strip()
    if not decay_model_id:
        return refusal(
            "refusal.ep.policy_missing",
            "retention policy is missing decay_model_id",
            "Define decay_model_id in retention_policy registry entry.",
            {"retention_policy_id": str(retention_policy.get("retention_policy_id", ""))},
            "$.retention_policy.decay_model_id",
        )
    registry_payload = _registry_payload(truth_model, "decay_model_registry")
    rows = registry_payload.get("decay_models")
    if not isinstance(rows, list):
        return refusal(
            "refusal.ep.policy_missing",
            "decay_model.registry is missing from loaded registry payloads",
            "Compile registries and load decay_model.registry.json before observation.",
            {"decay_model_id": decay_model_id},
            "$.registry_payloads.decay_model_registry",
        )
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("decay_model_id", ""))):
        token = str(row.get("decay_model_id", "")).strip()
        if token != decay_model_id:
            continue
        payload = dict(row)
        payload["decay_model_id"] = token
        return {"result": "complete", "decay_model": payload}
    return refusal(
        "refusal.ep.policy_missing",
        "decay model '{}' is not present in registry payloads".format(decay_model_id),
        "Use a retention policy that references a registered decay model.",
        {"decay_model_id": decay_model_id},
        "$.retention_policy.decay_model_id",
    )


def _resolve_eviction_rule(
    truth_model: dict,
    retention_policy: dict,
    decay_model: dict,
) -> Dict[str, object]:
    eviction_rule_id = (
        str(retention_policy.get("eviction_rule_id", "")).strip()
        or str(retention_policy.get("deterministic_eviction_rule_id", "")).strip()
        or str(decay_model.get("eviction_rule_id", "")).strip()
    )
    if not eviction_rule_id:
        return refusal(
            "refusal.ep.policy_missing",
            "retention policy is missing eviction rule id",
            "Define eviction_rule_id in retention_policy or decay_model registry entry.",
            {"retention_policy_id": str(retention_policy.get("retention_policy_id", ""))},
            "$.retention_policy.eviction_rule_id",
        )
    registry_payload = _registry_payload(truth_model, "eviction_rule_registry")
    rows = registry_payload.get("eviction_rules")
    if not isinstance(rows, list):
        return refusal(
            "refusal.ep.policy_missing",
            "eviction_rule.registry is missing from loaded registry payloads",
            "Compile registries and load eviction_rule.registry.json before observation.",
            {"eviction_rule_id": eviction_rule_id},
            "$.registry_payloads.eviction_rule_registry",
        )
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("eviction_rule_id", ""))):
        token = str(row.get("eviction_rule_id", "")).strip()
        if token != eviction_rule_id:
            continue
        payload = dict(row)
        payload["eviction_rule_id"] = token
        return {"result": "complete", "eviction_rule": payload}
    return refusal(
        "refusal.ep.policy_missing",
        "eviction rule '{}' is not present in registry payloads".format(eviction_rule_id),
        "Use a retention policy that references a registered eviction rule.",
        {"eviction_rule_id": eviction_rule_id},
        "$.retention_policy.eviction_rule_id",
    )


def _memory_owner_subject_id(authority_context: dict, viewpoint_id: str) -> str:
    scope = authority_context.get("epistemic_scope")
    if isinstance(scope, dict):
        scope_subject_id = str(scope.get("subject_id", "")).strip()
        if scope_subject_id:
            return scope_subject_id
        scope_id = str(scope.get("scope_id", "")).strip()
        if scope_id:
            return "scope.{}".format(scope_id)
    peer_id = str(authority_context.get("peer_id", "")).strip()
    if peer_id:
        return "peer.{}".format(peer_id)
    return "viewpoint.{}".format(str(viewpoint_id).strip() or "unknown")


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
        "ch.diegetic.notebook",
        "ch.diegetic.radio_text",
        "ch.diegetic.map_local",
        "ch.diegetic.tool.torque",
        "ch.diegetic.tool.measurement",
        "ch.diegetic.tool.health",
        "ch.diegetic.task.progress",
        "ch.diegetic.task.status",
        "ch.diegetic.pressure_status",
        "ch.diegetic.oxygen_status",
        "ch.diegetic.smoke_alarm",
        "ch.diegetic.flood_alarm",
        "ch.diegetic.door_indicator",
    ]


def _quantize_int(value: int, step: int) -> int:
    token = int(step) if int(step) > 0 else 1
    number = int(value)
    if number >= 0:
        return int(((number + (token // 2)) // token) * token)
    return int(-(((-number + (token // 2)) // token) * token))


def _population_quantization_step(camera_distance_mm: int, has_map_instrument: bool) -> int:
    distance = max(0, int(camera_distance_mm))
    if distance <= 5000:
        step = 10
    elif distance <= 20000:
        step = 25
    elif distance <= 100000:
        step = 50
    else:
        step = 100
    if bool(has_map_instrument):
        step = max(5, step // 2)
    return int(step)


def _population_band(population_value: int) -> str:
    value = max(0, int(population_value))
    if value == 0:
        return "none"
    if value < 100:
        return "dozens"
    if value < 1000:
        return "hundreds"
    return "thousands"


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
        out["populations"] = {
            "entries": [],
            "summary": "cohorts=0 population=none",
            "total_population_estimate": 0,
            "precision_mode": str((dict(out.get("populations") or {})).get("precision_mode", "quantized")),
            "precision_step": int((dict(out.get("populations") or {})).get("precision_step", 100) or 100),
        }
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
    populations = dict(out.get("populations") or {})
    population_entries = populations.get("entries")
    if isinstance(population_entries, list):
        trimmed_entries = [
            dict(item)
            for item in sorted(
                (row for row in population_entries if isinstance(row, dict)),
                key=lambda row: str(row.get("cohort_id", "")),
            )[:limit]
        ]
        populations["entries"] = trimmed_entries
        populations["total_population_estimate"] = int(
            sum(max(0, int(row.get("population_estimate", 0) or 0)) for row in trimmed_entries)
        )
        populations["summary"] = "cohorts={} population={}".format(
            len(trimmed_entries),
            _population_band(int(populations.get("total_population_estimate", 0) or 0)),
        )
    out["populations"] = populations

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
    if channel_id in ("ch.core.navigation", "ch.nondiegetic.nav"):
        return {"navigation": dict(perceived_model.get("navigation") or {})}
    if channel_id == "ch.core.sites":
        return {"sites": dict(perceived_model.get("sites") or {})}
    if channel_id in ("ch.core.entities", "ch.nondiegetic.entity_inspector"):
        return {
            "entities": dict(perceived_model.get("entities") or {}),
            "populations": dict(perceived_model.get("populations") or {}),
            "observed_entities": list(perceived_model.get("observed_entities") or []),
            "control": dict(perceived_model.get("control") or {}),
        }
    if channel_id == "ch.core.process_log":
        return {"process_log": dict(perceived_model.get("process_log") or {})}
    if channel_id in ("ch.core.performance", "ch.nondiegetic.performance_monitor"):
        return {"performance": dict(perceived_model.get("performance") or {})}
    if channel_id == "ch.watermark.observer_mode":
        return {"watermark": dict(perceived_model.get("watermark") or {})}
    instruments = dict(perceived_model.get("diegetic_instruments") or {})
    if channel_id == "ch.diegetic.compass":
        return {"instrument.compass": dict(instruments.get("instrument.compass") or {})}
    if channel_id == "ch.diegetic.clock":
        return {"instrument.clock": dict(instruments.get("instrument.clock") or {})}
    if channel_id == "ch.diegetic.altimeter":
        return {"instrument.altimeter": dict(instruments.get("instrument.altimeter") or {})}
    if channel_id == "ch.diegetic.map_local":
        return {
            "instrument.map_local": dict(instruments.get("instrument.map_local") or {}),
            "populations": dict(perceived_model.get("populations") or {}),
        }
    if channel_id == "ch.diegetic.notebook":
        return {"instrument.notebook": dict(instruments.get("instrument.notebook") or {})}
    if channel_id == "ch.diegetic.radio_text":
        return {"instrument.radio_text": dict(instruments.get("instrument.radio_text") or {})}
    if channel_id == "ch.diegetic.tool.torque":
        return {"instrument.tool.torque": dict(instruments.get("instrument.tool.torque") or {})}
    if channel_id == "ch.diegetic.tool.measurement":
        return {"instrument.tool.measurement": dict(instruments.get("instrument.tool.measurement") or {})}
    if channel_id == "ch.diegetic.tool.health":
        return {"instrument.tool.health": dict(instruments.get("instrument.tool.health") or {})}
    if channel_id == "ch.diegetic.task.progress":
        return {"instrument.task.progress": dict(instruments.get("instrument.task.progress") or {})}
    if channel_id == "ch.diegetic.task.status":
        return {"instrument.task.status": dict(instruments.get("instrument.task.status") or {})}
    if channel_id == "ch.diegetic.pressure_status":
        return {"instrument.interior.pressure": dict(instruments.get("instrument.interior.pressure") or {})}
    if channel_id == "ch.diegetic.oxygen_status":
        return {"instrument.interior.oxygen": dict(instruments.get("instrument.interior.oxygen") or {})}
    if channel_id == "ch.diegetic.smoke_alarm":
        return {"instrument.interior.smoke": dict(instruments.get("instrument.interior.smoke") or {})}
    if channel_id == "ch.diegetic.flood_alarm":
        return {"instrument.interior.flood": dict(instruments.get("instrument.interior.flood") or {})}
    if channel_id == "ch.diegetic.door_indicator":
        return {"instrument.interior.portal_state": dict(instruments.get("instrument.interior.portal_state") or {})}
    if channel_id == "ch.diegetic.interior.alarm":
        return {"instrument.interior.alarm": dict(instruments.get("instrument.interior.alarm") or {})}
    if channel_id == "ch.diegetic.interior.pressure":
        return {"instrument.interior.pressure": dict(instruments.get("instrument.interior.pressure") or {})}
    if channel_id == "ch.diegetic.interior.oxygen":
        return {"instrument.interior.oxygen": dict(instruments.get("instrument.interior.oxygen") or {})}
    if channel_id == "ch.diegetic.interior.smoke_alarm":
        return {"instrument.interior.smoke": dict(instruments.get("instrument.interior.smoke") or {})}
    if channel_id == "ch.diegetic.interior.flood_alarm":
        return {"instrument.interior.flood": dict(instruments.get("instrument.interior.flood") or {})}
    if channel_id == "ch.diegetic.interior.alarm":
        return {"instrument.interior.alarm": dict(instruments.get("instrument.interior.alarm") or {})}
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
        out["entities"] = {"entries": [], "assignments": [], "selected_fields": []}
    if not ({"ch.core.entities", "ch.nondiegetic.entity_inspector", "ch.diegetic.map_local"} & allowed):
        out["populations"] = {
            "entries": [],
            "summary": "redacted",
            "total_population_estimate": 0,
            "precision_mode": "redacted",
            "precision_step": 0,
        }
    if "ch.nondiegetic.entity_inspector" not in allowed:
        out["control"] = {"controllers": [], "bindings": [], "possession_graph": [], "summary": "redacted"}
    if not ({"ch.core.process_log", "ch.nondiegetic.performance_monitor"} & allowed):
        out["process_log"] = {"entries": []}
    if not ({"ch.core.performance", "ch.nondiegetic.performance_monitor"} & allowed):
        out["performance"] = {"budget": {"summary": "redacted", "visible": False}, "active_regions": [], "fidelity_tiers": {"coarse": 0, "medium": 0, "fine": 0}}
    if not ({"ch.core.time", "ch.diegetic.clock"} & allowed):
        out["time"] = {"tick": 0, "rate_permille": 0, "paused": True, "summary": "redacted"}
        out["time_state"] = {"tick": 0, "rate_permille": 0, "paused": True}
    if "ch.watermark.observer_mode" not in allowed:
        out["watermark"] = {
            "active": False,
            "view_mode_id": "",
            "watermark_policy_id": "",
            "text": "",
        }

    instruments = dict(out.get("diegetic_instruments") or {})
    instrument_channels = {
        "instrument.compass": "ch.diegetic.compass",
        "instrument.clock": "ch.diegetic.clock",
        "instrument.altimeter": "ch.diegetic.altimeter",
        "instrument.map_local": "ch.diegetic.map_local",
        "instrument.notebook": "ch.diegetic.notebook",
        "instrument.radio_text": "ch.diegetic.radio_text",
        "instrument.tool.torque": "ch.diegetic.tool.torque",
        "instrument.tool.measurement": "ch.diegetic.tool.measurement",
        "instrument.tool.health": "ch.diegetic.tool.health",
        "instrument.task.progress": "ch.diegetic.task.progress",
        "instrument.task.status": "ch.diegetic.task.status",
        "instrument.interior.portal_state": "ch.diegetic.door_indicator",
        "instrument.interior.pressure": ["ch.diegetic.pressure_status", "ch.diegetic.interior.pressure"],
        "instrument.interior.oxygen": ["ch.diegetic.oxygen_status", "ch.diegetic.interior.oxygen"],
        "instrument.interior.smoke": ["ch.diegetic.smoke_alarm", "ch.diegetic.interior.smoke_alarm"],
        "instrument.interior.flood": ["ch.diegetic.flood_alarm", "ch.diegetic.interior.flood_alarm"],
        "instrument.interior.alarm": "ch.diegetic.interior.alarm",
    }
    for instrument_id, channel_spec in sorted(instrument_channels.items()):
        allowed_channels = (
            _sorted_unique(list(channel_spec))
            if isinstance(channel_spec, list)
            else [str(channel_spec).strip()]
        )
        if not any(token in allowed for token in allowed_channels if token):
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


_LOD_REDACTION_EXACT_KEYS = {
    "exact_hidden_inventory",
    "hidden_inventory",
    "internal_state",
    "internal_stress_state",
    "micro_internal_state",
    "micro_solver_native_payload",
    "native_precision_payload",
}
_LOD_REDACTION_SUBSTRINGS = (
    "hidden_inventory",
    "internal_state",
    "micro_solver",
    "native_precision",
)


def _redact_lod_sensitive_payload(value: object) -> Tuple[object, int]:
    if isinstance(value, dict):
        out: Dict[str, object] = {}
        redacted = 0
        for key in sorted(value.keys()):
            token = str(key)
            lowered = token.lower()
            if lowered in _LOD_REDACTION_EXACT_KEYS or any(snippet in lowered for snippet in _LOD_REDACTION_SUBSTRINGS):
                redacted += 1
                continue
            next_value, nested_redacted = _redact_lod_sensitive_payload(value.get(key))
            out[token] = next_value
            redacted += int(nested_redacted)
        return out, redacted
    if isinstance(value, list):
        rows: List[object] = []
        redacted = 0
        for item in value:
            next_value, nested_redacted = _redact_lod_sensitive_payload(item)
            rows.append(next_value)
            redacted += int(nested_redacted)
        return rows, redacted
    return value, 0


def _apply_lod_invariance_redaction(perceived_model: dict, epistemic_policy: dict, channels: List[str]) -> dict:
    out = copy.deepcopy(dict(perceived_model or {}))
    redacted_payload, redacted_count = _redact_lod_sensitive_payload(out)
    out = dict(redacted_payload if isinstance(redacted_payload, dict) else {})
    metadata = dict(out.get("metadata") or {})
    metadata["lod_redaction_rule_id"] = "filter.lod_epistemic_redaction.v1"
    metadata["lod_redaction_applied"] = True
    metadata["lod_redacted_field_count"] = int(redacted_count)
    metadata["lod_precision_envelope_id"] = str(
        (dict(epistemic_policy.get("extensions") or {})).get("lod_precision_envelope_id", "ep.envelope.default")
    ).strip() or "ep.envelope.default"
    metadata["lod_channel_count"] = int(len(_sorted_unique(list(channels or []))))
    out["metadata"] = metadata
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
        "instrument.map_local": {},
        "instrument.notebook": {},
        "instrument.radio_text": {},
        "instrument.tool.torque": {},
        "instrument.tool.measurement": {},
        "instrument.tool.health": {},
        "instrument.task.progress": {},
        "instrument.task.status": {},
        "instrument.interior.portal_state": {},
        "instrument.interior.pressure": {},
        "instrument.interior.oxygen": {},
        "instrument.interior.smoke": {},
        "instrument.interior.flood": {},
        "instrument.interior.alarm": {},
    }
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
        assembly_id = str(row.get("assembly_id", "")).strip()
        if assembly_id in payload:
            payload[assembly_id] = {
                "assembly_id": assembly_id,
                "reading": copy.deepcopy(row.get("reading")),
                "quality": str(row.get("quality", "")),
                "quality_value": int(row.get("quality_value", 0) or 0),
                "last_update_tick": int(row.get("last_update_tick", simulation_tick) or simulation_tick),
                "state": copy.deepcopy(row.get("state") if isinstance(row.get("state"), dict) else {}),
                "outputs": copy.deepcopy(row.get("outputs") if isinstance(row.get("outputs"), dict) else {}),
                "instrument_type": str(row.get("instrument_type", "")).strip(),
                "instrument_type_id": str(row.get("instrument_type_id", "")).strip(),
            }
    return payload


def _update_memory_hook(
    perceived_model: dict,
    retention_policy: dict,
    decay_model: dict,
    eviction_rule: dict,
    owner_subject_id: str,
    simulation_tick: int,
    memory_state: dict | None,
) -> Tuple[dict, dict]:
    result = update_memory_store(
        perceived_now=dict(perceived_model or {}),
        owner_subject_id=str(owner_subject_id).strip() or "subject.unknown",
        retention_policy=dict(retention_policy or {}),
        decay_model=dict(decay_model or {}),
        eviction_rule=dict(eviction_rule or {}),
        previous_store=dict(memory_state or {}),
        tick=int(simulation_tick),
    )
    if str(result.get("result", "")) != "complete":
        empty_store = {
            "schema_version": "1.0.0",
            "store_id": "memory.store.subject.unknown",
            "owner_subject_id": "subject.unknown",
            "retention_policy_id": str(retention_policy.get("retention_policy_id", "")),
            "items": [],
            "store_hash": canonical_sha256(
                {
                    "owner_subject_id": "subject.unknown",
                    "retention_policy_id": str(retention_policy.get("retention_policy_id", "")),
                    "items": [],
                }
            ),
            "extensions": {
                "memory_allowed": False,
            },
        }
        return empty_store, empty_store
    memory_block = dict(result.get("memory_store") or {})
    state = dict(result.get("memory_state") or {})
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


def _id_index(rows: list, id_keys: Tuple[str, ...]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(id_keys[0], ""))):
        for key in id_keys:
            token = str(row.get(key, "")).strip()
            if token:
                out[token] = dict(row)
    return out


def _representation_indexes(truth: dict) -> Dict[str, Dict[str, dict]]:
    cosmetic_registry = _registry_payload(truth, "cosmetic_registry")
    render_proxy_registry = _registry_payload(truth, "render_proxy_registry")
    cosmetic_rows = list(cosmetic_registry.get("cosmetics") or [])
    render_proxy_rows = list(render_proxy_registry.get("render_proxies") or [])
    return {
        "cosmetics": _id_index(cosmetic_rows, ("cosmetic_id",)),
        "render_proxies": _id_index(render_proxy_rows, ("render_proxy_id",)),
    }


def _representation_assignments(truth: dict) -> Dict[str, dict]:
    payload = _registry_payload(truth, "representation_state")
    assignments = payload.get("assignments")
    if isinstance(assignments, dict):
        out = {}
        for key in sorted(assignments.keys()):
            token = str(key).strip()
            row = assignments.get(key)
            if token and isinstance(row, dict):
                out[token] = dict(row)
        return out
    if isinstance(assignments, list):
        out = {}
        for row in sorted((item for item in assignments if isinstance(item, dict)), key=lambda item: str(item.get("target_agent_id", ""))):
            token = str(row.get("target_agent_id", "")).strip()
            if token:
                out[token] = dict(row)
        return out
    return {}


def _portal_graph_index(state: dict) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for row in sorted(
        (item for item in list(state.get("interior_graphs") or []) if isinstance(item, dict)),
        key=lambda item: str(item.get("graph_id", "")),
    ):
        graph_id = str(row.get("graph_id", "")).strip()
        if not graph_id:
            continue
        for portal_id in _sorted_unique(list(row.get("portals") or [])):
            token = str(portal_id).strip()
            if token and token not in out:
                out[token] = graph_id
    return dict((key, out[key]) for key in sorted(out.keys()))


def _portal_state_index(state: dict) -> Dict[str, str]:
    out: Dict[str, str] = {}
    rows = [
        dict(item)
        for item in list(state.get("interior_portal_state_machines") or [])
        if isinstance(item, dict)
    ]
    for row in sorted(rows, key=lambda item: str(item.get("machine_id", ""))):
        machine_id = str(row.get("machine_id", "")).strip()
        state_id = str(row.get("state_id", "")).strip()
        if machine_id and state_id:
            out[machine_id] = state_id
    return dict((key, out[key]) for key in sorted(out.keys()))


def _portal_surface_rows(portal_row: dict, portal_state_id: str) -> List[dict]:
    portal = dict(portal_row or {})
    portal_id = str(portal.get("portal_id", "")).strip()
    state_id = str(portal_state_id).strip() or "unknown"
    panel_state = "locked" if state_id == "locked" else "ready"
    return sorted(
        [
            {
                "surface_type_id": "surface.handle",
                "compatible_tool_tags": ["tool_tag.operating"],
                "allowed_process_ids": [
                    "process.portal_open",
                    "process.portal_close",
                    "process.portal_lock",
                    "process.portal_unlock",
                ],
                "parameter_schema_id": None,
                "constraints": {
                    "portal_id": portal_id,
                    "state_id": state_id,
                },
                "visibility_policy_id": "visibility.default",
                "local_transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "extensions": {},
            },
            {
                "surface_type_id": "surface.panel",
                "compatible_tool_tags": ["tool_tag.operating"],
                "allowed_process_ids": [
                    "process.vent_activate",
                    "process.portal_seal_breach",
                ],
                "parameter_schema_id": None,
                "constraints": {
                    "portal_id": portal_id,
                    "panel_state": panel_state,
                },
                "visibility_policy_id": "visibility.default",
                "local_transform": {
                    "position_mm": {"x": 250, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "extensions": {},
            },
        ],
        key=lambda item: str(item.get("surface_type_id", "")),
    )


def _entity_view(truth: dict, observed_entities: List[str], interior_occlusion_meta: dict | None = None) -> dict:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return {"entries": [], "selected_fields": []}
    known = sorted(set(str(item).strip() for item in observed_entities if str(item).strip()))
    agent_rows = list(state.get("agent_states") or [])
    body_rows = list(state.get("body_assemblies") or [])
    agent_index = _id_index(agent_rows, ("agent_id", "entity_id"))
    body_index = _id_index(body_rows, ("assembly_id", "body_id"))
    representation_index = _representation_indexes(truth)
    cosmetic_rows = dict(representation_index.get("cosmetics") or {})
    render_proxy_rows = dict(representation_index.get("render_proxies") or {})
    assignments = _representation_assignments(truth)
    portal_rows_by_id = _interior_row_index(state.get("interior_portals"), "portal_id")
    portal_state_by_machine = _portal_state_index(state)
    portal_graph_by_id = _portal_graph_index(state)
    viewer_graph_id = str((dict(interior_occlusion_meta or {})).get("viewer_graph_id", "")).strip()
    entries = []
    assignment_rows = []
    for token in known:
        if token.startswith("interior.portal."):
            portal_id = str(token[len("interior.portal."):]).strip()
            portal = dict(portal_rows_by_id.get(portal_id) or {})
            if not portal:
                continue
            machine_id = str(portal.get("state_machine_id", "")).strip()
            state_id = str(portal_state_by_machine.get(machine_id, "")).strip() or "open"
            graph_id = str(portal_graph_by_id.get(portal_id, "")).strip()
            if viewer_graph_id and graph_id and graph_id != viewer_graph_id:
                continue
            entries.append(
                {
                    "entity_id": token,
                    "semantic_id": token,
                    "entity_kind": "interior_portal",
                    "portal_id": portal_id,
                    "interior_graph_id": graph_id or None,
                    "representation": {
                        "shape_type": "none",
                        "cosmetic_id": DEFAULT_COSMETIC_ID,
                        "render_proxy_id": DEFAULT_RENDER_PROXY_ID,
                        "mesh_ref": "asset.mesh.pill.default",
                        "material_ref": "asset.material.pill.default",
                        "lod_set_ref": None,
                        "fallback_proxy_id": DEFAULT_RENDER_PROXY_ID,
                        "fallback_used": True,
                    },
                    "transform_mm": {"x": 0, "y": 0, "z": 0},
                    "action_surfaces": _portal_surface_rows(portal, state_id),
                    "extensions": {
                        "portal_type_id": str(portal.get("portal_type_id", "")).strip(),
                        "from_volume_id": str(portal.get("from_volume_id", "")).strip(),
                        "to_volume_id": str(portal.get("to_volume_id", "")).strip(),
                        "state_machine_id": machine_id or None,
                        "state_id": state_id,
                    },
                }
            )
            continue
        agent = dict(agent_index.get(token) or {})
        agent_ext = dict(agent.get("extensions") or {}) if isinstance(agent.get("extensions"), dict) else {}
        body_id = str(agent.get("body_id", "") or "").strip()
        body = dict(body_index.get(body_id) or {}) if body_id else {}
        shape_type = str(body.get("shape_type", "")).strip() or "capsule"
        assignment = dict(assignments.get(token) or {})
        cosmetic_id = str(assignment.get("cosmetic_id", "")).strip() or DEFAULT_COSMETIC_ID
        cosmetic = dict(cosmetic_rows.get(cosmetic_id) or {})
        proxy_id = str(cosmetic.get("render_proxy_id", "")).strip() or DEFAULT_RENDER_PROXY_ID
        proxy = dict(render_proxy_rows.get(proxy_id) or {})
        supported_shapes = sorted(
            set(str(item).strip() for item in (proxy.get("supported_body_shapes") or []) if str(item).strip())
        )
        used_fallback = False
        if not proxy or (supported_shapes and shape_type not in set(supported_shapes)):
            proxy_id = DEFAULT_RENDER_PROXY_ID
            proxy = dict(render_proxy_rows.get(proxy_id) or {})
            used_fallback = True
        mesh_ref = str(cosmetic.get("mesh_ref_override") or "").strip() or str(proxy.get("mesh_ref", "")).strip() or "asset.mesh.pill.default"
        material_ref = str(cosmetic.get("material_ref_override") or "").strip() or str(proxy.get("material_ref", "")).strip() or "asset.material.pill.default"
        entry = {
            "entity_id": token,
            "semantic_id": token,
            "entity_kind": "agent",
            "agent_id": str(agent.get("agent_id", "")).strip() or token,
            "body_id": body_id,
            "owner_peer_id": str(agent.get("owner_peer_id", "")).strip() if agent.get("owner_peer_id") is not None else None,
            "representation": {
                "shape_type": shape_type,
                "cosmetic_id": cosmetic_id,
                "render_proxy_id": proxy_id,
                "mesh_ref": mesh_ref,
                "material_ref": material_ref,
                "lod_set_ref": str(proxy.get("lod_set_ref", "")).strip() if proxy.get("lod_set_ref") is not None else None,
                "fallback_proxy_id": DEFAULT_RENDER_PROXY_ID,
                "fallback_used": bool(used_fallback),
            },
            "transform_mm": dict(body.get("transform_mm") or {"x": 0, "y": 0, "z": 0}),
            "extensions": {
                "interior_volume_id": str(agent.get("interior_volume_id", "")).strip() or None,
                "posture": str(agent.get("posture", "")).strip() or None,
                "pose_slot_id": str(agent.get("pose_slot_id", "")).strip() or None,
                "pose_control_binding_ids": _sorted_unique(list(agent_ext.get("pose_control_binding_ids") or [])),
                "pose_granted_process_ids": _sorted_unique(list(agent_ext.get("pose_granted_process_ids") or [])),
                "pose_granted_surface_ids": _sorted_unique(list(agent_ext.get("pose_granted_surface_ids") or [])),
                "occupied_pose_slot_ids": _sorted_unique(list(agent_ext.get("occupied_pose_slot_ids") or [])),
            },
        }
        granted_process_ids = _sorted_unique(list(agent_ext.get("pose_granted_process_ids") or []))
        granted_surface_ids = _sorted_unique(list(agent_ext.get("pose_granted_surface_ids") or []))
        if granted_process_ids and granted_surface_ids:
            entry["action_surfaces"] = [
                {
                    "surface_type_id": "surface.panel",
                    "compatible_tool_tags": ["tool_tag.operating"],
                    "allowed_process_ids": list(granted_process_ids),
                    "parameter_schema_id": None,
                    "constraints": {
                        "control_grant_surface_id": str(surface_id),
                    },
                    "visibility_policy_id": "visibility.default",
                    "local_transform": {
                        "position_mm": {"x": int(index) * 120, "y": 0, "z": 0},
                        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        "scale_permille": 1000,
                    },
                    "extensions": {
                        "control_grant_surface_id": str(surface_id),
                    },
                }
                for index, surface_id in enumerate(granted_surface_ids)
            ]
        entries.append(entry)
        if assignment:
            assignment_rows.append(
                {
                    "assignment_id": str(assignment.get("assignment_id", "")).strip() or "cosmetic.assignment.{}".format(token),
                    "target_agent_id": token,
                    "cosmetic_id": cosmetic_id,
                    "applied_tick": int(assignment.get("applied_tick", 0) or 0),
                    "policy_id": str(assignment.get("policy_id", "")).strip(),
                    "pack_id": str(assignment.get("pack_id", "")).strip(),
                }
            )
    for camera in state.get("camera_assemblies") or []:
        if not isinstance(camera, dict):
            continue
        assembly_id = str(camera.get("assembly_id", "")).strip()
        if not assembly_id:
            continue
        if assembly_id not in known:
            entries.append(
                {
                    "entity_id": assembly_id,
                    "representation": {
                        "shape_type": "none",
                        "cosmetic_id": DEFAULT_COSMETIC_ID,
                        "render_proxy_id": DEFAULT_RENDER_PROXY_ID,
                        "mesh_ref": "asset.mesh.pill.default",
                        "material_ref": "asset.material.pill.default",
                        "lod_set_ref": None,
                        "fallback_proxy_id": DEFAULT_RENDER_PROXY_ID,
                        "fallback_used": True,
                    },
                    "transform_mm": dict(camera.get("position_mm") or {"x": 0, "y": 0, "z": 0}),
                }
            )
    entries = sorted(entries, key=lambda item: str(item.get("entity_id", "")))
    assignment_rows = sorted(
        assignment_rows,
        key=lambda item: (
            str(item.get("target_agent_id", "")),
            str(item.get("assignment_id", "")),
        ),
    )
    return {
        "entries": entries,
        "assignments": assignment_rows,
        "selected_fields": [
            "representation.shape_type",
            "representation.cosmetic_id",
            "representation.render_proxy_id",
        ],
    }


def _population_view(
    truth: dict,
    *,
    camera_viewpoint: dict,
    allow_hidden: bool,
    entitlements: List[str],
    requested_channels: List[str],
) -> dict:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return {
            "entries": [],
            "summary": "cohorts=0 population=none",
            "total_population_estimate": 0,
            "precision_mode": "quantized",
            "precision_step": 100,
        }

    cohort_rows = list(state.get("cohort_assemblies") or [])
    if not isinstance(cohort_rows, list):
        cohort_rows = []
    has_map_instrument = "ch.diegetic.map_local" in set(_sorted_unique(list(requested_channels or [])))
    can_view_exact = bool(allow_hidden) or "entitlement.inspect" in set(_sorted_unique(list(entitlements or [])))
    quant_step = _population_quantization_step(
        camera_distance_mm=_camera_distance_mm(camera_viewpoint),
        has_map_instrument=bool(has_map_instrument),
    )

    entries = []
    total_population_estimate = 0
    anonymous_index = 0
    for row in sorted((item for item in cohort_rows if isinstance(item, dict)), key=lambda item: str(item.get("cohort_id", ""))):
        cohort_id = str(row.get("cohort_id", "")).strip()
        if not cohort_id:
            continue
        size_exact = max(0, int(row.get("size", 0) or 0))
        if can_view_exact:
            estimate = int(size_exact)
        else:
            estimate = int(_quantize_int(size_exact, quant_step))
            if size_exact > 0:
                estimate = max(1, estimate)
        total_population_estimate += int(estimate)
        entry = {
            "faction_id": row.get("faction_id"),
            "territory_id": row.get("territory_id"),
            "location_ref": str(row.get("location_ref", "")).strip(),
            "refinement_state": str(row.get("refinement_state", "macro")).strip() or "macro",
            "population_estimate": int(estimate),
            "population_band": _population_band(estimate),
            "precision_mode": "exact" if can_view_exact else "quantized",
            "precision_step": 1 if can_view_exact else int(quant_step),
        }
        if can_view_exact:
            entry["cohort_id"] = cohort_id
            entry["population_exact"] = int(size_exact)
        else:
            anonymous_index += 1
            entry["population_id"] = "population.anonymous.{}".format(str(int(anonymous_index)).zfill(4))
        entries.append(entry)

    summary = "cohorts={} population={}".format(len(entries), _population_band(total_population_estimate))
    return {
        "entries": entries,
        "summary": summary,
        "total_population_estimate": int(total_population_estimate),
        "precision_mode": "exact" if can_view_exact else "quantized",
        "precision_step": 1 if can_view_exact else int(quant_step),
    }


def _control_view(truth: dict, *, allow_order_visibility: bool = False) -> dict:
    state = truth.get("universe_state")
    if not isinstance(state, dict):
        return {
            "controllers": [],
            "bindings": [],
            "possession_graph": [],
            "orders": [],
            "order_queues": [],
            "institutions": [],
            "role_assignments": [],
            "summary": "",
        }

    controllers = state.get("controller_assemblies")
    if not isinstance(controllers, list):
        controllers = []
    normalized_controllers = []
    for row in controllers:
        if not isinstance(row, dict):
            continue
        controller_id = str(row.get("assembly_id", "")).strip()
        if not controller_id:
            continue
        normalized_controllers.append(
            {
                "controller_id": controller_id,
                "controller_type": str(row.get("controller_type", "")),
                "owner_peer_id": row.get("owner_peer_id"),
                "binding_ids": sorted(
                    set(
                        str(item).strip()
                        for item in (row.get("binding_ids") or [])
                        if str(item).strip()
                    )
                ),
                "status": str(row.get("status", "")),
            }
        )
    normalized_controllers = sorted(normalized_controllers, key=lambda item: str(item.get("controller_id", "")))

    bindings = state.get("control_bindings")
    if not isinstance(bindings, list):
        bindings = []
    normalized_bindings = []
    possession_graph = []
    for row in sorted((item for item in bindings if isinstance(item, dict)), key=lambda item: str(item.get("binding_id", ""))):
        binding_id = str(row.get("binding_id", "")).strip()
        controller_id = str(row.get("controller_id", "")).strip()
        binding_type = str(row.get("binding_type", "")).strip()
        target_id = str(row.get("target_id", "")).strip()
        if not binding_id or not controller_id or not binding_type or not target_id:
            continue
        normalized = {
            "binding_id": binding_id,
            "controller_id": controller_id,
            "binding_type": binding_type,
            "target_id": target_id,
            "created_tick": int(row.get("created_tick", 0) or 0),
            "active": bool(row.get("active", True)),
        }
        normalized_bindings.append(normalized)
        if binding_type == "possess" and bool(normalized.get("active", False)):
            possession_graph.append(
                {
                    "agent_id": target_id,
                    "controller_id": controller_id,
                    "binding_id": binding_id,
                }
            )

    possession_graph = sorted(
        possession_graph,
        key=lambda item: (str(item.get("agent_id", "")), str(item.get("controller_id", ""))),
    )
    summary = "controllers={} active_bindings={} active_possessions={}".format(
        len(normalized_controllers),
        len([row for row in normalized_bindings if bool(row.get("active", False))]),
        len(possession_graph),
    )
    visible_orders: List[dict] = []
    visible_queues: List[dict] = []
    visible_institutions: List[dict] = []
    visible_role_assignments: List[dict] = []
    if bool(allow_order_visibility):
        order_rows = state.get("order_assemblies")
        if isinstance(order_rows, list):
            for row in sorted((item for item in order_rows if isinstance(item, dict)), key=lambda item: str(item.get("order_id", ""))):
                order_id = str(row.get("order_id", "")).strip()
                if not order_id:
                    continue
                visible_orders.append(
                    {
                        "order_id": order_id,
                        "order_type_id": str(row.get("order_type_id", "")).strip(),
                        "issuer_subject_id": str(row.get("issuer_subject_id", "")).strip(),
                        "target_kind": str(row.get("target_kind", "")).strip(),
                        "target_id": str(row.get("target_id", "")).strip(),
                        "status": str(row.get("status", "")).strip(),
                        "priority": int(row.get("priority", 0) or 0),
                        "created_tick": int(row.get("created_tick", 0) or 0),
                    }
                )
        queue_rows = state.get("order_queue_assemblies")
        if isinstance(queue_rows, list):
            for row in sorted((item for item in queue_rows if isinstance(item, dict)), key=lambda item: str(item.get("queue_id", ""))):
                queue_id = str(row.get("queue_id", "")).strip()
                if not queue_id:
                    continue
                visible_queues.append(
                    {
                        "queue_id": queue_id,
                        "owner_kind": str(row.get("owner_kind", "")).strip(),
                        "owner_id": str(row.get("owner_id", "")).strip(),
                        "order_ids": sorted(
                            set(
                                str(item).strip()
                                for item in (row.get("order_ids") or [])
                                if str(item).strip()
                            )
                        ),
                        "last_update_tick": int(row.get("last_update_tick", 0) or 0),
                    }
                )
        institution_rows = state.get("institution_assemblies")
        if isinstance(institution_rows, list):
            for row in sorted((item for item in institution_rows if isinstance(item, dict)), key=lambda item: str(item.get("institution_id", ""))):
                institution_id = str(row.get("institution_id", "")).strip()
                if not institution_id:
                    continue
                visible_institutions.append(
                    {
                        "institution_id": institution_id,
                        "institution_type_id": str(row.get("institution_type_id", "")).strip(),
                        "faction_id": row.get("faction_id"),
                        "status": str(row.get("status", "")).strip(),
                        "created_tick": int(row.get("created_tick", 0) or 0),
                    }
                )
        role_rows = state.get("role_assignment_assemblies")
        if isinstance(role_rows, list):
            for row in sorted((item for item in role_rows if isinstance(item, dict)), key=lambda item: str(item.get("assignment_id", ""))):
                assignment_id = str(row.get("assignment_id", "")).strip()
                if not assignment_id:
                    continue
                visible_role_assignments.append(
                    {
                        "assignment_id": assignment_id,
                        "institution_id": str(row.get("institution_id", "")).strip(),
                        "subject_id": str(row.get("subject_id", "")).strip(),
                        "role_id": str(row.get("role_id", "")).strip(),
                        "granted_entitlements": sorted(
                            set(
                                str(item).strip()
                                for item in (row.get("granted_entitlements") or [])
                                if str(item).strip()
                            )
                        ),
                        "created_tick": int(row.get("created_tick", 0) or 0),
                    }
                )
        summary = "{} visible_orders={} visible_role_assignments={}".format(
            summary,
            len(visible_orders),
            len(visible_role_assignments),
        )
    return {
        "controllers": normalized_controllers,
        "bindings": normalized_bindings,
        "possession_graph": possession_graph,
        "orders": visible_orders,
        "order_queues": visible_queues,
        "institutions": visible_institutions,
        "role_assignments": visible_role_assignments,
        "summary": summary,
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
            "universe_physics_profile_registry_hash": str(registries.get("universe_physics_profile_registry_hash", "")),
            "time_model_registry_hash": str(registries.get("time_model_registry_hash", "")),
            "numeric_precision_policy_registry_hash": str(registries.get("numeric_precision_policy_registry_hash", "")),
            "tier_taxonomy_registry_hash": str(registries.get("tier_taxonomy_registry_hash", "")),
            "boundary_model_registry_hash": str(registries.get("boundary_model_registry_hash", "")),
            "domain_registry_hash": str(registries.get("domain_registry_hash", "")),
            "law_registry_hash": str(registries.get("law_registry_hash", "")),
            "experience_registry_hash": str(registries.get("experience_registry_hash", "")),
            "lens_registry_hash": str(registries.get("lens_registry_hash", "")),
            "control_action_registry_hash": str(registries.get("control_action_registry_hash", "")),
            "control_policy_registry_hash": str(registries.get("control_policy_registry_hash", "")),
            "controller_type_registry_hash": str(registries.get("controller_type_registry_hash", "")),
            "governance_type_registry_hash": str(registries.get("governance_type_registry_hash", "")),
            "diplomatic_state_registry_hash": str(registries.get("diplomatic_state_registry_hash", "")),
            "cohort_mapping_policy_registry_hash": str(registries.get("cohort_mapping_policy_registry_hash", "")),
            "order_type_registry_hash": str(registries.get("order_type_registry_hash", "")),
            "role_registry_hash": str(registries.get("role_registry_hash", "")),
            "institution_type_registry_hash": str(registries.get("institution_type_registry_hash", "")),
            "demography_policy_registry_hash": str(registries.get("demography_policy_registry_hash", "")),
            "death_model_registry_hash": str(registries.get("death_model_registry_hash", "")),
            "birth_model_registry_hash": str(registries.get("birth_model_registry_hash", "")),
            "migration_model_registry_hash": str(registries.get("migration_model_registry_hash", "")),
            "view_mode_registry_hash": str(registries.get("view_mode_registry_hash", "")),
            "view_policy_registry_hash": str(registries.get("view_policy_registry_hash", "")),
            "instrument_type_registry_hash": str(registries.get("instrument_type_registry_hash", "")),
            "calibration_model_registry_hash": str(registries.get("calibration_model_registry_hash", "")),
            "render_proxy_registry_hash": str(registries.get("render_proxy_registry_hash", "")),
            "cosmetic_registry_hash": str(registries.get("cosmetic_registry_hash", "")),
            "cosmetic_policy_registry_hash": str(registries.get("cosmetic_policy_registry_hash", "")),
            "render_primitive_registry_hash": str(registries.get("render_primitive_registry_hash", "")),
            "procedural_material_template_registry_hash": str(
                registries.get("procedural_material_template_registry_hash", "")
            ),
            "label_policy_registry_hash": str(registries.get("label_policy_registry_hash", "")),
            "lod_policy_registry_hash": str(registries.get("lod_policy_registry_hash", "")),
            "representation_rule_registry_hash": str(registries.get("representation_rule_registry_hash", "")),
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
            "decay_model_registry_hash": str(registries.get("decay_model_registry_hash", "")),
            "eviction_rule_registry_hash": str(registries.get("eviction_rule_registry_hash", "")),
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

    camera = _camera_main(truth_model)
    watermark_payload = _observer_watermark_payload(truth=truth_model, camera=camera)
    if bool(watermark_payload.get("active", False)) and "entitlement.observer.truth" not in set(entitlements):
        return refusal(
            "refusal.ep.entitlement_missing",
            "observer truth view mode requires entitlement.observer.truth",
            "Grant entitlement.observer.truth or switch to non-observer view mode.",
            {"view_mode_id": str(watermark_payload.get("view_mode_id", ""))},
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
    memory_allowed = bool(active_retention_policy.get("memory_allowed", False))
    active_decay_model = {}
    active_eviction_rule = {}
    if memory_allowed:
        decay_result = _resolve_decay_model(
            truth_model=truth_model,
            retention_policy=active_retention_policy,
        )
        if str(decay_result.get("result", "")) != "complete":
            return decay_result
        active_decay_model = dict(decay_result.get("decay_model") or {})
        eviction_result = _resolve_eviction_rule(
            truth_model=truth_model,
            retention_policy=active_retention_policy,
            decay_model=active_decay_model,
        )
        if str(eviction_result.get("result", "")) != "complete":
            return eviction_result
        active_eviction_rule = dict(eviction_result.get("eviction_rule") or {})
    else:
        active_decay_model = {
            "decay_model_id": str(active_retention_policy.get("decay_model_id", "")).strip()
            or "ep.decay.none",
            "ttl_rules": [],
            "refresh_rules": [],
            "eviction_rule_id": str(active_retention_policy.get("eviction_rule_id", "")).strip()
            or str(active_retention_policy.get("deterministic_eviction_rule_id", "")).strip()
            or "evict.none",
            "extensions": {
                "memory_disabled": True,
            },
        }
        active_eviction_rule = {
            "eviction_rule_id": str(active_retention_policy.get("eviction_rule_id", "")).strip()
            or str(active_retention_policy.get("deterministic_eviction_rule_id", "")).strip()
            or "evict.none",
            "algorithm_id": "evict.none",
            "priority_by_channel": {},
            "priority_by_subject_kind": {},
            "extensions": {
                "memory_disabled": True,
            },
        }

    policy_allowed_channels = _sorted_unique(list(active_epistemic_policy.get("allowed_observation_channels") or []))
    policy_forbidden_channels = _sorted_unique(list(active_epistemic_policy.get("forbidden_channels") or []))
    requested_channels = _sorted_unique(list(lens.get("observation_channels") or []))
    if not requested_channels:
        requested_channels = _default_lens_channels(lens_type=lens_type)
    if bool(watermark_payload.get("active", False)):
        requested_channels = _sorted_unique(list(requested_channels) + ["ch.watermark.observer_mode"])

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
    observed_entities, interior_occlusion_meta = _apply_interior_occlusion(
        truth_model=truth_model,
        observed_entities=observed_entities,
        camera=camera,
        lens=lens,
        lens_type=lens_type,
        law_profile=law_profile,
        authority_context=authority_context,
    )
    observed_entities = _sorted_unique(
        list(observed_entities) + _viewer_graph_portal_entity_ids(truth_model, interior_occlusion_meta)
    )
    simulation_tick = _simulation_tick(truth_model)
    time_control = _time_control(truth_model)
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
        "view_mode_id": str(camera.get("view_mode_id", "")),
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
    entities = _entity_view(
        truth_model,
        observed_entities=observed_entities,
        interior_occlusion_meta=interior_occlusion_meta,
    )
    populations = _population_view(
        truth_model,
        camera_viewpoint=camera_viewpoint,
        allow_hidden=allow_hidden,
        entitlements=list(entitlements),
        requested_channels=requested_channels,
    )
    control = _control_view(
        truth_model,
        allow_order_visibility=("entitlement.civ.view_orders" in set(entitlements)),
    )
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
        "populations": populations,
        "control": control,
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
            "decay_model_id": str(active_decay_model.get("decay_model_id", "")),
            "eviction_rule_id": str(active_eviction_rule.get("eviction_rule_id", "")),
            "deterministic_filter_chain": list(filter_chain),
            "epistemic_visibility_policy": str((lens.get("epistemic_constraints") or {}).get("visibility_policy", "")),
            "interior_occlusion": dict(interior_occlusion_meta),
        },
        "watermark": watermark_payload,
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
    perceived_model = _apply_lod_invariance_redaction(
        perceived_model=perceived_model,
        epistemic_policy=active_epistemic_policy,
        channels=requested_channels,
    )

    memory_block, next_memory_state = _update_memory_hook(
        perceived_model=perceived_model,
        retention_policy=active_retention_policy,
        decay_model=active_decay_model,
        eviction_rule=active_eviction_rule,
        owner_subject_id=_memory_owner_subject_id(authority_context=authority_context, viewpoint_id=viewpoint_id),
        simulation_tick=simulation_tick,
        memory_state=memory_state,
    )
    instrument_rows = [
        dict(item)
        for item in (dict(perceived_model.get("diegetic_instruments") or {})).values()
        if isinstance(item, dict)
    ]
    perceived_model["diegetic_instruments"] = compute_diegetic_instruments(
        perceived_now=perceived_model,
        memory_store=memory_block,
        instrument_rows=instrument_rows,
        requested_channels=requested_channels,
        simulation_tick=simulation_tick,
    )
    perceived_model = _apply_channel_filter(
        perceived_model=perceived_model,
        requested_channels=requested_channels,
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

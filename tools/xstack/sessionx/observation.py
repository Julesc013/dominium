"""Deterministic Observation Kernel v1 for TruthModel -> PerceivedModel derivation."""

from __future__ import annotations

from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import refusal


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


def _navigation_view(truth: dict) -> dict:
    astronomy = _registry_payload(truth, "astronomy_catalog_index")
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
    return {
        "hierarchy": rows,
        "search_index": normalized_search,
        "search_results": [],
        "selection_summary": "",
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
    law_check = _required_mapping(
        law_profile,
        ("law_profile_id", "allowed_lenses", "epistemic_limits"),
        "LAW_PROFILE_INVALID",
        "$.law_profile",
    )
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
    if allow_hidden:
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
            "epistemic_visibility_policy": str((lens.get("epistemic_constraints") or {}).get("visibility_policy", "")),
        },
    }
    return {
        "result": "complete",
        "perceived_model": perceived_model,
        "perceived_model_hash": canonical_sha256(perceived_model),
    }


def perceived_model_hash(payload: dict) -> str:
    """Return deterministic canonical hash for a PerceivedModel payload."""
    return canonical_sha256(payload)

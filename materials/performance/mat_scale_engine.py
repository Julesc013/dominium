"""Deterministic MAT-10 scale cost/degradation simulation helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from performance.cost_engine import normalize_subsystem_cost_usage
from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_MAT_DEGRADATION_ORDER = (
    "inspection_fidelity_reduce",
    "materialization_cap",
    "construction_parallel_reduce",
    "logistics_batching",
    "maintenance_deferral",
    "creation_refusal",
)

DEFAULT_MAT_SCALE_COST_MODEL = {
    "schema_version": "1.0.0",
    "model_id": "mat.cost_model.default.v1",
    "logistics": {
        "cost_units_per_manifest_processed": 4,
        "cost_units_per_routing_lookup": 2,
    },
    "construction": {
        "cost_units_per_active_step": 5,
        "cost_units_per_ag_node_resolved": 1,
    },
    "decay": {
        "cost_units_per_tracked_asset": 1,
    },
    "materialization": {
        "cost_units_per_micro_part_instance": 2,
    },
    "inspection": {
        "cost_units_per_section_generated": 1,
        "cost_units_per_history_window_tick": 1,
        "section_count_by_fidelity": {"macro": 4, "meso": 8, "micro": 12},
    },
    "reenactment": {
        "cost_units_per_event_processed": 2,
        "fidelity_multiplier": {"macro": 1, "meso": 2, "micro": 4},
    },
    "maintenance": {
        "cost_units_per_low_priority_asset": 1,
    },
    "extensions": {},
}

_FIDELITY_ORDER = ("micro", "meso", "macro")
ZERO_HASH = "0" * 64


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _stable_int(*, seed: int, label: str, index: int, modulus: int) -> int:
    mod = max(1, int(modulus))
    digest = canonical_sha256(
        {
            "seed": int(seed),
            "label": str(label),
            "index": int(index),
            "modulus": int(mod),
        }
    )
    return int(int(digest[:12], 16) % mod)


def _normalize_fidelity(token: object) -> str:
    value = str(token or "").strip().lower() or "macro"
    if value not in _FIDELITY_ORDER:
        return "macro"
    return value


def _degrade_fidelity(token: str) -> str:
    value = _normalize_fidelity(token)
    idx = _FIDELITY_ORDER.index(value)
    if idx + 1 >= len(_FIDELITY_ORDER):
        return value
    return _FIDELITY_ORDER[idx + 1]


def _non_negative_map(payload: Mapping[str, object] | None) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key, value in sorted((dict(payload or {})).items(), key=lambda item: str(item[0])):
        token = str(key).strip()
        if not token:
            continue
        out[token] = max(0, _as_int(value, 0))
    return out


def normalize_mat_scale_cost_model(model_row: Mapping[str, object] | None) -> dict:
    row = dict(DEFAULT_MAT_SCALE_COST_MODEL)
    row.update(dict(model_row or {}))
    inspection = dict(DEFAULT_MAT_SCALE_COST_MODEL["inspection"])
    inspection.update(dict(row.get("inspection") or {}))
    section_count_by_fidelity = dict(DEFAULT_MAT_SCALE_COST_MODEL["inspection"]["section_count_by_fidelity"])
    section_count_by_fidelity.update(_non_negative_map(dict(inspection.get("section_count_by_fidelity") or {})))
    inspection["section_count_by_fidelity"] = {
        "macro": max(1, _as_int(section_count_by_fidelity.get("macro", 4), 4)),
        "meso": max(1, _as_int(section_count_by_fidelity.get("meso", 8), 8)),
        "micro": max(1, _as_int(section_count_by_fidelity.get("micro", 12), 12)),
    }
    reenactment = dict(DEFAULT_MAT_SCALE_COST_MODEL["reenactment"])
    reenactment.update(dict(row.get("reenactment") or {}))
    fidelity_multiplier = dict(DEFAULT_MAT_SCALE_COST_MODEL["reenactment"]["fidelity_multiplier"])
    fidelity_multiplier.update(_non_negative_map(dict(reenactment.get("fidelity_multiplier") or {})))
    reenactment["fidelity_multiplier"] = {
        "macro": max(1, _as_int(fidelity_multiplier.get("macro", 1), 1)),
        "meso": max(1, _as_int(fidelity_multiplier.get("meso", 2), 2)),
        "micro": max(1, _as_int(fidelity_multiplier.get("micro", 4), 4)),
    }
    return {
        "schema_version": "1.0.0",
        "model_id": str(row.get("model_id", "mat.cost_model.default.v1")).strip() or "mat.cost_model.default.v1",
        "logistics": {
            "cost_units_per_manifest_processed": max(
                1, _as_int((dict(row.get("logistics") or {})).get("cost_units_per_manifest_processed", 4), 4)
            ),
            "cost_units_per_routing_lookup": max(
                0, _as_int((dict(row.get("logistics") or {})).get("cost_units_per_routing_lookup", 2), 2)
            ),
        },
        "construction": {
            "cost_units_per_active_step": max(
                1, _as_int((dict(row.get("construction") or {})).get("cost_units_per_active_step", 5), 5)
            ),
            "cost_units_per_ag_node_resolved": max(
                0, _as_int((dict(row.get("construction") or {})).get("cost_units_per_ag_node_resolved", 1), 1)
            ),
        },
        "decay": {
            "cost_units_per_tracked_asset": max(
                0, _as_int((dict(row.get("decay") or {})).get("cost_units_per_tracked_asset", 1), 1)
            ),
        },
        "materialization": {
            "cost_units_per_micro_part_instance": max(
                0, _as_int((dict(row.get("materialization") or {})).get("cost_units_per_micro_part_instance", 2), 2)
            ),
        },
        "inspection": {
            "cost_units_per_section_generated": max(
                0, _as_int(inspection.get("cost_units_per_section_generated", 1), 1)
            ),
            "cost_units_per_history_window_tick": max(
                0, _as_int(inspection.get("cost_units_per_history_window_tick", 1), 1)
            ),
            "section_count_by_fidelity": dict(inspection["section_count_by_fidelity"]),
        },
        "reenactment": {
            "cost_units_per_event_processed": max(
                0, _as_int(reenactment.get("cost_units_per_event_processed", 2), 2)
            ),
            "fidelity_multiplier": dict(reenactment["fidelity_multiplier"]),
        },
        "maintenance": {
            "cost_units_per_low_priority_asset": max(
                0, _as_int((dict(row.get("maintenance") or {})).get("cost_units_per_low_priority_asset", 1), 1)
            ),
        },
        "extensions": dict(row.get("extensions") or {}),
    }


def default_factory_planet_scenario(
    *,
    seed: int,
    factory_complex_count: int,
    logistics_node_count: int,
    active_project_count: int,
    player_count: int,
) -> dict:
    n = max(1, int(factory_complex_count))
    m = max(1, int(logistics_node_count))
    k = max(1, int(active_project_count))
    p = max(1, int(player_count))

    complexes = []
    for idx in range(n):
        lat = _stable_int(seed=seed, label="complex.lat", index=idx, modulus=180_000) - 90_000
        lon = _stable_int(seed=seed, label="complex.lon", index=idx, modulus=360_000) - 180_000
        complexes.append(
            {
                "complex_id": "factory.complex.{:04d}".format(idx),
                "lat_mdeg": int(lat),
                "lon_mdeg": int(lon),
            }
        )
    nodes = []
    for idx in range(m):
        home_idx = int(idx % n)
        nodes.append(
            {
                "node_id": "node.factory.{:05d}".format(idx),
                "complex_id": str(complexes[home_idx]["complex_id"]),
            }
        )
    projects = []
    for idx in range(k):
        complex_id = str(complexes[idx % n]["complex_id"])
        projects.append(
            {
                "project_id": "project.factory.{:05d}".format(idx),
                "complex_id": complex_id,
                "priority": int(idx % 3),
            }
        )
    players = []
    for idx in range(p):
        project = projects[idx % k]
        players.append(
            {
                "player_id": "player.{:05d}".format(idx),
                "target_project_id": str(project["project_id"]),
                "roi_id": "roi.player.{:05d}".format(idx),
                "desired_fidelity": "micro",
            }
        )

    manifests_per_tick = max(1, m // 6)
    routes_per_tick = max(0, manifests_per_tick // 2)
    active_steps = max(1, k // 2)
    ag_nodes_resolved = max(1, k)
    tracked_assets = max(1, n * 16 + k * 8)
    micro_parts_per_player = 64
    maintenance_due = max(1, n * 2)
    reenactment_events = max(1, p // 4)

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.factory_planet.seed_{}".format(int(seed)),
        "seed": int(seed),
        "parameters": {
            "factory_complex_count": int(n),
            "logistics_node_count": int(m),
            "active_project_count": int(k),
            "player_count": int(p),
        },
        "factory_complexes": list(complexes),
        "logistics_nodes": list(nodes),
        "construction_projects": list(projects),
        "players": list(players),
        "workload_template": {
            "logistics_manifests_per_tick": int(manifests_per_tick),
            "logistics_route_lookups_per_tick": int(routes_per_tick),
            "construction_active_steps": int(active_steps),
            "construction_parallel_steps": int(max(1, min(active_steps, 16))),
            "construction_ag_nodes_resolved": int(ag_nodes_resolved),
            "decay_tracked_assets": int(tracked_assets),
            "materialization_micro_parts_per_player": int(micro_parts_per_player),
            "maintenance_low_priority_due_per_tick": int(maintenance_due),
            "inspection_history_window_ticks": 8,
            "inspection_desired_fidelity": "micro",
            "reenactment_events_per_tick": int(reenactment_events),
            "reenactment_desired_fidelity": "meso",
            "project_create_requests_per_tick": max(1, k // 64),
            "manifest_create_requests_per_tick": max(1, m // 64),
            "time_warp_dt_ticks": 1,
            "truth_anchor_interval_ticks": 24,
        },
        "budget_envelopes": [
            {
                "envelope_id": "budget.factory_planet.default",
                "max_solver_cost_units_per_tick": int(max(128, p * 256)),
                "max_inspection_cost_units_per_tick": int(max(32, p * 16)),
                "max_micro_parts_per_roi": 128,
            }
        ],
        "arbitration_policy_id": "arb.equal_share.deterministic",
        "multiplayer_policy_id": "policy.net.server_authoritative",
        "cost_model": normalize_mat_scale_cost_model(DEFAULT_MAT_SCALE_COST_MODEL),
        "extensions": {},
    }
    scenario["deterministic_fingerprint"] = canonical_sha256(dict(scenario, deterministic_fingerprint=""))
    return scenario


def _sorted_players(scenario_row: Mapping[str, object]) -> List[dict]:
    players = list(scenario_row.get("players") or [])
    rows = [dict(row) for row in players if isinstance(row, dict)]
    return sorted(rows, key=lambda row: str(row.get("player_id", "")))


def _budget_envelope_row(
    scenario_row: Mapping[str, object],
    *,
    budget_envelope_id: str | None,
) -> dict:
    envelopes = [dict(row) for row in list(scenario_row.get("budget_envelopes") or []) if isinstance(row, dict)]
    if not envelopes:
        return {
            "envelope_id": "budget.default",
            "max_solver_cost_units_per_tick": 1024,
            "max_inspection_cost_units_per_tick": 128,
            "max_micro_parts_per_roi": 128,
        }
    requested = str(budget_envelope_id or "").strip()
    for row in sorted(envelopes, key=lambda item: str(item.get("envelope_id", ""))):
        if str(row.get("envelope_id", "")).strip() == requested and requested:
            return {
                "envelope_id": str(row.get("envelope_id", "budget.default")).strip() or "budget.default",
                "max_solver_cost_units_per_tick": max(
                    0, _as_int(row.get("max_solver_cost_units_per_tick", 0), 0)
                ),
                "max_inspection_cost_units_per_tick": max(
                    0, _as_int(row.get("max_inspection_cost_units_per_tick", 0), 0)
                ),
                "max_micro_parts_per_roi": max(1, _as_int(row.get("max_micro_parts_per_roi", 1), 1)),
            }
    row = dict(sorted(envelopes, key=lambda item: str(item.get("envelope_id", "")))[0])
    return {
        "envelope_id": str(row.get("envelope_id", "budget.default")).strip() or "budget.default",
        "max_solver_cost_units_per_tick": max(0, _as_int(row.get("max_solver_cost_units_per_tick", 0), 0)),
        "max_inspection_cost_units_per_tick": max(
            0, _as_int(row.get("max_inspection_cost_units_per_tick", 0), 0)
        ),
        "max_micro_parts_per_roi": max(1, _as_int(row.get("max_micro_parts_per_roi", 1), 1)),
    }


def _base_workload_template(scenario_row: Mapping[str, object]) -> dict:
    template = dict(scenario_row.get("workload_template") or {})
    return {
        "logistics_manifests_per_tick": max(0, _as_int(template.get("logistics_manifests_per_tick", 0), 0)),
        "logistics_route_lookups_per_tick": max(
            0, _as_int(template.get("logistics_route_lookups_per_tick", 0), 0)
        ),
        "construction_active_steps": max(0, _as_int(template.get("construction_active_steps", 0), 0)),
        "construction_parallel_steps": max(0, _as_int(template.get("construction_parallel_steps", 0), 0)),
        "construction_ag_nodes_resolved": max(0, _as_int(template.get("construction_ag_nodes_resolved", 0), 0)),
        "decay_tracked_assets": max(0, _as_int(template.get("decay_tracked_assets", 0), 0)),
        "materialization_micro_parts_per_player": max(
            0, _as_int(template.get("materialization_micro_parts_per_player", 0), 0)
        ),
        "maintenance_low_priority_due_per_tick": max(
            0, _as_int(template.get("maintenance_low_priority_due_per_tick", 0), 0)
        ),
        "inspection_history_window_ticks": max(0, _as_int(template.get("inspection_history_window_ticks", 0), 0)),
        "inspection_desired_fidelity": _normalize_fidelity(template.get("inspection_desired_fidelity", "macro")),
        "reenactment_events_per_tick": max(0, _as_int(template.get("reenactment_events_per_tick", 0), 0)),
        "reenactment_desired_fidelity": _normalize_fidelity(template.get("reenactment_desired_fidelity", "macro")),
        "project_create_requests_per_tick": max(
            0, _as_int(template.get("project_create_requests_per_tick", 0), 0)
        ),
        "manifest_create_requests_per_tick": max(
            0, _as_int(template.get("manifest_create_requests_per_tick", 0), 0)
        ),
        "time_warp_dt_ticks": max(1, _as_int(template.get("time_warp_dt_ticks", 1), 1)),
        "truth_anchor_interval_ticks": max(1, _as_int(template.get("truth_anchor_interval_ticks", 1), 1)),
    }


def _workload_for_tick(
    scenario_row: Mapping[str, object],
    *,
    tick: int,
    workload_state: Mapping[str, object] | None,
) -> dict:
    seed = max(0, _as_int(scenario_row.get("seed", 0), 0))
    base = _base_workload_template(scenario_row)
    overrides = dict(workload_state or {})
    out = dict(base)
    for key, value in sorted(overrides.items(), key=lambda item: str(item[0])):
        token = str(key).strip()
        if token not in out:
            continue
        if token.endswith("_fidelity"):
            out[token] = _normalize_fidelity(value)
        else:
            out[token] = max(0, _as_int(value, out[token]))
    manifests = int(out["logistics_manifests_per_tick"])
    wave = 1 + _stable_int(seed=seed, label="workload.wave", index=max(0, int(tick)), modulus=3)
    out["logistics_manifests_per_tick"] = int(max(0, manifests + wave - 2))
    routes = int(out["logistics_route_lookups_per_tick"])
    out["logistics_route_lookups_per_tick"] = int(max(0, routes + (wave // 2)))
    active_steps = int(out["construction_active_steps"])
    parallel_steps = int(out["construction_parallel_steps"])
    out["construction_parallel_steps"] = int(min(max(0, parallel_steps), max(0, active_steps)))
    return out


def _inspection_section_count(
    cost_model: Mapping[str, object],
    *,
    fidelity: str,
) -> int:
    inspection_row = dict(cost_model.get("inspection") or {})
    by_fidelity = dict(inspection_row.get("section_count_by_fidelity") or {})
    return max(1, _as_int(by_fidelity.get(_normalize_fidelity(fidelity), 1), 1))


def _inspection_request_cost(cost_model: Mapping[str, object], *, fidelity: str, history_ticks: int) -> int:
    inspection_row = dict(cost_model.get("inspection") or {})
    per_section = max(0, _as_int(inspection_row.get("cost_units_per_section_generated", 0), 0))
    per_history_tick = max(0, _as_int(inspection_row.get("cost_units_per_history_window_tick", 0), 0))
    section_count = _inspection_section_count(cost_model, fidelity=_normalize_fidelity(fidelity))
    return int(section_count * per_section + max(0, int(history_ticks)) * per_history_tick)


def _time_warp_cost_factor(dt_ticks: int) -> int:
    dt = max(1, _as_int(dt_ticks, 1))
    if dt <= 1:
        return 1
    return max(1, int(dt).bit_length() - 1)


def compute_mat_cost_usage(
    *,
    scenario_row: Mapping[str, object],
    tick: int,
    cost_model_row: Mapping[str, object] | None = None,
    workload_state: Mapping[str, object] | None = None,
    budget_envelope_id: str | None = None,
) -> dict:
    model = normalize_mat_scale_cost_model(cost_model_row or dict(scenario_row.get("cost_model") or {}))
    envelope = _budget_envelope_row(scenario_row, budget_envelope_id=budget_envelope_id)
    workload = _workload_for_tick(scenario_row, tick=tick, workload_state=workload_state)
    players = _sorted_players(scenario_row)
    player_count = max(1, len(players))

    logistics_row = dict(model.get("logistics") or {})
    construction_row = dict(model.get("construction") or {})
    decay_row = dict(model.get("decay") or {})
    materialization_row = dict(model.get("materialization") or {})
    maintenance_row = dict(model.get("maintenance") or {})
    reenactment_row = dict(model.get("reenactment") or {})

    logistics_cost = int(
        max(0, int(workload["logistics_manifests_per_tick"]))
        * max(0, _as_int(logistics_row.get("cost_units_per_manifest_processed", 0), 0))
        + max(0, int(workload["logistics_route_lookups_per_tick"]))
        * max(0, _as_int(logistics_row.get("cost_units_per_routing_lookup", 0), 0))
    )
    construction_cost = int(
        max(0, int(workload["construction_parallel_steps"]))
        * max(0, _as_int(construction_row.get("cost_units_per_active_step", 0), 0))
        + max(0, int(workload["construction_ag_nodes_resolved"]))
        * max(0, _as_int(construction_row.get("cost_units_per_ag_node_resolved", 0), 0))
    )
    decay_cost = int(
        max(0, int(workload["decay_tracked_assets"]))
        * max(0, _as_int(decay_row.get("cost_units_per_tracked_asset", 0), 0))
        * _time_warp_cost_factor(int(workload["time_warp_dt_ticks"]))
    )
    per_player_parts = max(0, int(workload["materialization_micro_parts_per_player"]))
    parts_cap = max(1, int(envelope["max_micro_parts_per_roi"]))
    bounded_per_player = min(per_player_parts, parts_cap)
    materialization_cost = int(
        bounded_per_player
        * player_count
        * max(0, _as_int(materialization_row.get("cost_units_per_micro_part_instance", 0), 0))
    )
    maintenance_cost = int(
        max(0, int(workload["maintenance_low_priority_due_per_tick"]))
        * max(0, _as_int(maintenance_row.get("cost_units_per_low_priority_asset", 0), 0))
    )
    reenactment_multiplier_map = dict(reenactment_row.get("fidelity_multiplier") or {})
    reenactment_cost = int(
        max(0, int(workload["reenactment_events_per_tick"]))
        * max(0, _as_int(reenactment_row.get("cost_units_per_event_processed", 0), 0))
        * max(
            1,
            _as_int(
                reenactment_multiplier_map.get(_normalize_fidelity(workload["reenactment_desired_fidelity"]), 1),
                1,
            ),
        )
    )

    inspection_request_cost = _inspection_request_cost(
        model,
        fidelity=_normalize_fidelity(workload["inspection_desired_fidelity"]),
        history_ticks=max(0, int(workload["inspection_history_window_ticks"])),
    )
    inspection_cost = int(player_count * inspection_request_cost)
    normalized_subsystems = normalize_subsystem_cost_usage(
        subsystem_cost_units={
            "construction": int(construction_cost),
            "decay": int(decay_cost),
            "inspection": int(inspection_cost),
            "logistics": int(logistics_cost),
            "maintenance": int(maintenance_cost),
            "materialization": int(materialization_cost),
            "reenactment": int(reenactment_cost),
        }
    )
    subsystem_cost_units = dict(normalized_subsystems.get("subsystem_cost_units") or {})
    solver_cost = int(
        max(0, _as_int(subsystem_cost_units.get("logistics", 0), 0))
        + max(0, _as_int(subsystem_cost_units.get("construction", 0), 0))
        + max(0, _as_int(subsystem_cost_units.get("decay", 0), 0))
        + max(0, _as_int(subsystem_cost_units.get("materialization", 0), 0))
        + max(0, _as_int(subsystem_cost_units.get("maintenance", 0), 0))
        + max(0, _as_int(subsystem_cost_units.get("reenactment", 0), 0))
    )
    total = int(solver_cost + inspection_cost)
    return {
        "schema_version": "1.0.0",
        "tick": int(max(0, int(tick))),
        "cost_model_id": str(model.get("model_id", "mat.cost_model.default.v1")),
        "budget_envelope_id": str(envelope.get("envelope_id", "")),
        "workload": dict(workload),
        "subsystem_cost_units": subsystem_cost_units,
        "inspection_request_cost_units": int(inspection_request_cost),
        "player_count": int(player_count),
        "solver_cost_units": int(solver_cost),
        "inspection_cost_units": int(inspection_cost),
        "total_cost_units": int(total),
        "max_solver_cost_units_per_tick": int(envelope["max_solver_cost_units_per_tick"]),
        "max_inspection_cost_units_per_tick": int(envelope["max_inspection_cost_units_per_tick"]),
        "solver_cost_exceeded": bool(solver_cost > int(envelope["max_solver_cost_units_per_tick"])),
        "inspection_cost_exceeded": bool(inspection_cost > int(envelope["max_inspection_cost_units_per_tick"])),
        "micro_parts_per_player_effective": int(bounded_per_player),
    }


def _apply_single_degradation_step(
    *,
    step_id: str,
    workload: dict,
    envelope: Mapping[str, object],
) -> dict | None:
    if step_id == "inspection_fidelity_reduce":
        current = _normalize_fidelity(workload.get("inspection_desired_fidelity", "macro"))
        degraded = _degrade_fidelity(current)
        if degraded == current:
            return None
        workload["inspection_desired_fidelity"] = degraded
        return {"step_id": step_id, "field": "inspection_desired_fidelity", "before": current, "after": degraded}

    if step_id == "materialization_cap":
        before = max(0, _as_int(workload.get("materialization_micro_parts_per_player", 0), 0))
        cap = max(1, _as_int(envelope.get("max_micro_parts_per_roi", 1), 1))
        after = before
        if before > cap:
            after = cap
        elif before > 0:
            after = max(0, before // 2)
        if after == before:
            return None
        workload["materialization_micro_parts_per_player"] = after
        return {
            "step_id": step_id,
            "field": "materialization_micro_parts_per_player",
            "before": int(before),
            "after": int(after),
        }

    if step_id == "construction_parallel_reduce":
        before = max(0, _as_int(workload.get("construction_parallel_steps", 0), 0))
        after = max(0, before // 2)
        if after == before:
            return None
        workload["construction_parallel_steps"] = after
        return {
            "step_id": step_id,
            "field": "construction_parallel_steps",
            "before": int(before),
            "after": int(after),
        }

    if step_id == "logistics_batching":
        manifests_before = max(0, _as_int(workload.get("logistics_manifests_per_tick", 0), 0))
        routes_before = max(0, _as_int(workload.get("logistics_route_lookups_per_tick", 0), 0))
        manifests_after = max(0, manifests_before // 2)
        routes_after = max(0, routes_before // 2)
        if manifests_after == manifests_before and routes_after == routes_before:
            return None
        workload["logistics_manifests_per_tick"] = manifests_after
        workload["logistics_route_lookups_per_tick"] = routes_after
        return {
            "step_id": step_id,
            "fields": {
                "logistics_manifests_per_tick": {"before": int(manifests_before), "after": int(manifests_after)},
                "logistics_route_lookups_per_tick": {"before": int(routes_before), "after": int(routes_after)},
            },
        }

    if step_id == "maintenance_deferral":
        before = max(0, _as_int(workload.get("maintenance_low_priority_due_per_tick", 0), 0))
        after = max(0, before // 2)
        if after == before:
            return None
        workload["maintenance_low_priority_due_per_tick"] = after
        return {
            "step_id": step_id,
            "field": "maintenance_low_priority_due_per_tick",
            "before": int(before),
            "after": int(after),
        }

    if step_id == "creation_refusal":
        proj_before = max(0, _as_int(workload.get("project_create_requests_per_tick", 0), 0))
        man_before = max(0, _as_int(workload.get("manifest_create_requests_per_tick", 0), 0))
        if proj_before == 0 and man_before == 0:
            return None
        workload["project_create_requests_per_tick"] = 0
        workload["manifest_create_requests_per_tick"] = 0
        return {
            "step_id": step_id,
            "fields": {
                "project_create_requests_per_tick": {"before": int(proj_before), "after": 0},
                "manifest_create_requests_per_tick": {"before": int(man_before), "after": 0},
            },
        }
    return None


def apply_mat_degradation_policy(
    *,
    scenario_row: Mapping[str, object],
    tick: int,
    cost_model_row: Mapping[str, object] | None = None,
    budget_envelope_id: str | None = None,
    workload_state: Mapping[str, object] | None = None,
    strict_budget: bool = False,
) -> dict:
    model = normalize_mat_scale_cost_model(cost_model_row or dict(scenario_row.get("cost_model") or {}))
    envelope = _budget_envelope_row(scenario_row, budget_envelope_id=budget_envelope_id)
    workload = _workload_for_tick(scenario_row, tick=tick, workload_state=workload_state)

    cost_before = compute_mat_cost_usage(
        scenario_row=scenario_row,
        tick=tick,
        cost_model_row=model,
        workload_state=workload,
        budget_envelope_id=str(envelope.get("envelope_id", "")),
    )
    degraded_events: List[dict] = []
    iterations = 0
    while (
        bool(cost_before.get("solver_cost_exceeded")) or bool(cost_before.get("inspection_cost_exceeded"))
    ) and iterations < 4:
        changed_in_iteration = False
        for step_id in DEFAULT_MAT_DEGRADATION_ORDER:
            if not (
                bool(cost_before.get("solver_cost_exceeded")) or bool(cost_before.get("inspection_cost_exceeded"))
            ):
                break
            event = _apply_single_degradation_step(step_id=step_id, workload=workload, envelope=envelope)
            if event is None:
                continue
            changed_in_iteration = True
            after_cost = compute_mat_cost_usage(
                scenario_row=scenario_row,
                tick=tick,
                cost_model_row=model,
                workload_state=workload,
                budget_envelope_id=str(envelope.get("envelope_id", "")),
            )
            degraded_events.append(
                {
                    "tick": int(max(0, int(tick))),
                    "order": len(degraded_events),
                    "step_id": str(step_id),
                    "details": event,
                    "solver_cost_before": int(cost_before.get("solver_cost_units", 0)),
                    "solver_cost_after": int(after_cost.get("solver_cost_units", 0)),
                    "inspection_cost_before": int(cost_before.get("inspection_cost_units", 0)),
                    "inspection_cost_after": int(after_cost.get("inspection_cost_units", 0)),
                }
            )
            cost_before = after_cost
        iterations += 1
        if not changed_in_iteration:
            break

    exceeded = bool(cost_before.get("solver_cost_exceeded")) or bool(cost_before.get("inspection_cost_exceeded"))
    if exceeded and strict_budget:
        return {
            "result": "refused",
            "reason_code": "refusal.mat_scale.budget_exceeded",
            "tick": int(max(0, int(tick))),
            "budget_envelope_id": str(envelope.get("envelope_id", "")),
            "cost_usage": dict(cost_before),
            "workload": dict(workload),
            "degradation_events": degraded_events,
        }
    return {
        "result": "complete",
        "tick": int(max(0, int(tick))),
        "budget_envelope_id": str(envelope.get("envelope_id", "")),
        "cost_usage": dict(cost_before),
        "workload": dict(workload),
        "degradation_events": degraded_events,
        "budget_outcome": "degraded" if degraded_events else "nominal",
        "bounded": not exceeded,
    }


def _inspection_cache_key(
    *,
    target_id: str,
    desired_fidelity: str,
    truth_hash_anchor: str,
    history_window_ticks: int,
) -> str:
    return canonical_sha256(
        {
            "target_id": str(target_id),
            "desired_fidelity": _normalize_fidelity(desired_fidelity),
            "truth_hash_anchor": str(truth_hash_anchor),
            "history_window_ticks": max(0, int(history_window_ticks)),
        }
    )


def _inspection_budget_share(
    *,
    players: List[dict],
    max_inspection_cost_units_per_tick: int,
) -> Dict[str, int]:
    sorted_players = sorted(players, key=lambda row: str(row.get("player_id", "")))
    count = max(1, len(sorted_players))
    total = max(0, int(max_inspection_cost_units_per_tick))
    base_share = int(total // count)
    remainder = int(total % count)
    shares: Dict[str, int] = {}
    for index, row in enumerate(sorted_players):
        player_id = str(row.get("player_id", "")).strip() or "player.unknown"
        shares[player_id] = int(base_share + (1 if index < remainder else 0))
    return shares


def _truth_anchor_for_tick(
    *,
    scenario_row: Mapping[str, object],
    tick: int,
    prior_hash_anchor: str,
    truth_anchor_interval_ticks: int,
) -> str:
    interval = max(1, _as_int(truth_anchor_interval_ticks, 1))
    if tick > 0 and (tick % interval) != 0:
        return str(prior_hash_anchor)
    return canonical_sha256(
        {
            "scenario_id": str(scenario_row.get("scenario_id", "")),
            "tick": int(max(0, int(tick))),
            "prior_hash_anchor": str(prior_hash_anchor),
        }
    )


def run_stress_simulation(
    *,
    scenario_row: Mapping[str, object],
    tick_count: int,
    budget_envelope_id: str | None = None,
    arbitration_policy_id: str | None = None,
    multiplayer_policy_id: str | None = None,
    strict_budget: bool = False,
) -> dict:
    scenario = dict(scenario_row or {})
    model = normalize_mat_scale_cost_model(dict(scenario.get("cost_model") or {}))
    envelope = _budget_envelope_row(scenario, budget_envelope_id=budget_envelope_id)
    players = _sorted_players(scenario)
    ticks = max(0, _as_int(tick_count, 0))
    arbitration_id = str(arbitration_policy_id or scenario.get("arbitration_policy_id", "")).strip()
    if not arbitration_id:
        arbitration_id = "arb.equal_share.deterministic"
    multiplayer_id = str(multiplayer_policy_id or scenario.get("multiplayer_policy_id", "")).strip()
    if not multiplayer_id:
        multiplayer_id = "policy.net.server_authoritative"

    cache: Dict[str, str] = {}
    cache_hits = 0
    cache_misses = 0
    tick_reports: List[dict] = []
    all_degradation_events: List[dict] = []
    hash_anchor_stream: List[str] = []
    run_meta_notes: List[dict] = []
    prior_tick_hash_anchor = ZERO_HASH
    prior_truth_hash_anchor = ZERO_HASH
    prior_workload_state: Dict[str, object] = {}
    bounded = True

    for tick in range(ticks):
        tick_truth_anchor = _truth_anchor_for_tick(
            scenario_row=scenario,
            tick=tick,
            prior_hash_anchor=prior_truth_hash_anchor,
            truth_anchor_interval_ticks=_base_workload_template(scenario)["truth_anchor_interval_ticks"],
        )
        degraded = apply_mat_degradation_policy(
            scenario_row=scenario,
            tick=tick,
            cost_model_row=model,
            budget_envelope_id=str(envelope.get("envelope_id", "")),
            workload_state=prior_workload_state,
            strict_budget=bool(strict_budget),
        )
        if str(degraded.get("result", "")) != "complete":
            bounded = False
            tick_reports.append(
                {
                    "tick": int(tick),
                    "result": "refused",
                    "reason_code": str(degraded.get("reason_code", "refusal.mat_scale.budget_exceeded")),
                    "cost_usage": dict(degraded.get("cost_usage") or {}),
                    "degradation_events": list(degraded.get("degradation_events") or []),
                }
            )
            break

        workload = dict(degraded.get("workload") or {})
        cost_usage = dict(degraded.get("cost_usage") or {})
        degradation_events = [dict(row) for row in list(degraded.get("degradation_events") or []) if isinstance(row, dict)]
        all_degradation_events.extend(degradation_events)
        for event in degradation_events:
            run_meta_notes.append(
                {
                    "tick": int(tick),
                    "kind": "degradation",
                    "step_id": str(event.get("step_id", "")),
                    "order": int(event.get("order", 0) or 0),
                }
            )

        shares = _inspection_budget_share(
            players=players,
            max_inspection_cost_units_per_tick=int(envelope.get("max_inspection_cost_units_per_tick", 0)),
        )
        player_reports: List[dict] = []
        effective_fidelity = _normalize_fidelity(workload.get("inspection_desired_fidelity", "macro"))
        history_ticks = max(0, _as_int(workload.get("inspection_history_window_ticks", 0), 0))
        request_cost = _inspection_request_cost(model, fidelity=effective_fidelity, history_ticks=history_ticks)
        inspection_realized_cost = 0
        for row in players:
            player_id = str(row.get("player_id", "")).strip() or "player.unknown"
            target_id = str(row.get("target_project_id", "")).strip() or str(row.get("roi_id", "target.unknown"))
            key = _inspection_cache_key(
                target_id=target_id,
                desired_fidelity=effective_fidelity,
                truth_hash_anchor=tick_truth_anchor,
                history_window_ticks=history_ticks,
            )
            share = max(0, _as_int(shares.get(player_id, 0), 0))
            cache_hit = key in cache
            if cache_hit:
                cache_hits += 1
                realized_cost = 0
                status = "cache_hit"
            else:
                cache_misses += 1
                realized_cost = min(request_cost, share)
                status = "served" if request_cost <= share else "degraded"
                cache[key] = "snapshot.{}".format(key[:16])
            inspection_realized_cost += realized_cost
            player_reports.append(
                {
                    "player_id": player_id,
                    "target_id": target_id,
                    "budget_share_units": int(share),
                    "request_cost_units": int(request_cost),
                    "realized_cost_units": int(realized_cost),
                    "status": status,
                }
            )

        # Inspection cache lookups should avoid recomputation while keeping deterministic bounded cost.
        if inspection_realized_cost > int(envelope.get("max_inspection_cost_units_per_tick", 0)):
            bounded = False
            inspection_realized_cost = int(envelope.get("max_inspection_cost_units_per_tick", 0))

        solver_cost = max(0, _as_int(cost_usage.get("solver_cost_units", 0), 0))
        max_solver = int(envelope.get("max_solver_cost_units_per_tick", 0))
        if solver_cost > max_solver:
            bounded = False
        tick_hash = canonical_sha256(
            {
                "scenario_id": str(scenario.get("scenario_id", "")),
                "tick": int(tick),
                "workload": dict(workload),
                "solver_cost_units": int(min(solver_cost, max_solver)),
                "inspection_cost_units": int(inspection_realized_cost),
                "degradation_events": degradation_events,
                "player_reports": player_reports,
                "prior_hash_anchor": str(prior_tick_hash_anchor),
                "truth_hash_anchor": str(tick_truth_anchor),
                "arbitration_policy_id": arbitration_id,
                "multiplayer_policy_id": multiplayer_id,
            }
        )
        hash_anchor_stream.append(tick_hash)
        tick_reports.append(
            {
                "tick": int(tick),
                "result": "complete",
                "budget_outcome": str(degraded.get("budget_outcome", "nominal")),
                "workload": dict(workload),
                "cost_usage": {
                    "solver_cost_units": int(min(solver_cost, max_solver)),
                    "inspection_cost_units": int(inspection_realized_cost),
                    "subsystem_cost_units": dict(cost_usage.get("subsystem_cost_units") or {}),
                },
                "degradation_events": degradation_events,
                "player_inspection_reports": player_reports,
                "tick_hash_anchor": tick_hash,
                "truth_hash_anchor": tick_truth_anchor,
            }
        )
        prior_tick_hash_anchor = tick_hash
        prior_truth_hash_anchor = tick_truth_anchor
        prior_workload_state = dict(workload)

    total_requests = int(cache_hits + cache_misses)
    hit_rate_permille = int((1000 * cache_hits) // total_requests) if total_requests > 0 else 0
    out = {
        "schema_version": "1.0.0",
        "scenario_id": str(scenario.get("scenario_id", "")),
        "tick_count": int(ticks),
        "budget_envelope_id": str(envelope.get("envelope_id", "")),
        "arbitration_policy_id": arbitration_id,
        "multiplayer_policy_id": multiplayer_id,
        "cost_model_id": str(model.get("model_id", "")),
        "result": "complete" if bounded else "degraded",
        "bounded": bool(bounded),
        "per_tick_reports": tick_reports,
        "degradation_events": all_degradation_events,
        "hash_anchor_stream": hash_anchor_stream,
        "inspection_cache_summary": {
            "hits": int(cache_hits),
            "misses": int(cache_misses),
            "hit_rate_permille": int(hit_rate_permille),
            "max_cache_entries": int(len(cache)),
        },
        "run_meta_notes": run_meta_notes,
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out

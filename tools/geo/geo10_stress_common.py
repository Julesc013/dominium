"""Shared deterministic GEO-10 stress scenario helpers."""

from __future__ import annotations

import copy
import json
import os
from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_GEO10_SEED = 91017
DEFAULT_OUTPUT_REL = "build/geo/geo10_stress_scenario.json"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", ".."))


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _read_json(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), rel_path.replace("/", os.sep))
    try:
        return dict(json.load(open(abs_path, "r", encoding="utf-8")) or {})
    except (OSError, ValueError, TypeError):
        return {}


def write_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _with_fingerprint(payload: Mapping[str, object]) -> dict:
    row = dict(payload or {})
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def _pick(seed: int, stream: str, index: int, modulo: int, *, offset: int = 0) -> int:
    mod = int(max(1, _as_int(modulo, 1)))
    digest = canonical_sha256(
        {
            "seed": int(seed),
            "stream": str(stream),
            "index": int(index),
            "modulo": int(mod),
        }
    )
    return int(int(offset) + (int(digest[:12], 16) % int(mod)))


def _cell_key(
    *,
    topology_profile_id: str,
    partition_profile_id: str,
    chart_id: str,
    index_tuple: Sequence[int],
    refinement_level: int = 0,
) -> dict:
    row = {
        "partition_profile_id": str(partition_profile_id).strip(),
        "topology_profile_id": str(topology_profile_id).strip(),
        "chart_id": str(chart_id).strip(),
        "index_tuple": [int(_as_int(value, 0)) for value in list(index_tuple or [])],
        "refinement_level": int(max(0, _as_int(refinement_level, 0))),
        "extensions": {
            "legacy_cell_alias": "",
        },
    }
    row["extensions"]["legacy_cell_alias"] = _cell_alias(row)
    return row


def _cell_alias(cell_key: Mapping[str, object]) -> str:
    row = _as_map(cell_key)
    chart_id = str(row.get("chart_id", "")).strip().replace(".", "_")
    index_tuple = [int(_as_int(value, 0)) for value in list(row.get("index_tuple") or [])]
    return "{}.{}".format(chart_id or "cell", "_".join(str(value) for value in index_tuple))


def _frame_node(
    *,
    frame_id: str,
    parent_frame_id: str | None,
    topology_profile_id: str,
    metric_profile_id: str,
    chart_id: str,
    anchor_cell_key: Mapping[str, object],
    scale_class_id: str,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "frame_id": str(frame_id).strip(),
        "parent_frame_id": None if parent_frame_id in {None, ""} else str(parent_frame_id).strip(),
        "topology_profile_id": str(topology_profile_id).strip(),
        "metric_profile_id": str(metric_profile_id).strip(),
        "chart_id": str(chart_id).strip(),
        "anchor_cell_key": dict(anchor_cell_key or {}),
        "scale_class_id": str(scale_class_id).strip(),
        "extensions": {},
    }
    return _with_fingerprint(payload)


def _frame_transform(
    *,
    from_frame_id: str,
    to_frame_id: str,
    translation: Sequence[int],
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "from_frame_id": str(from_frame_id).strip(),
        "to_frame_id": str(to_frame_id).strip(),
        "transform_kind": "translate",
        "parameters": {
            "translation": [int(_as_int(value, 0)) for value in list(translation or [])],
        },
        "extensions": {},
    }
    return _with_fingerprint(payload)


def _position_ref_row(
    *,
    object_id: str,
    frame_id: str,
    local_position: Sequence[int],
) -> dict:
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "object_id": str(object_id).strip(),
            "frame_id": str(frame_id).strip(),
            "local_position": [int(_as_int(value, 0)) for value in list(local_position or [])],
            "extensions": {"source": "GEO10-1"},
        }
    )


def _field_layer_row(
    *,
    field_id: str,
    spatial_scope_id: str,
    topology_profile_id: str,
    metric_profile_id: str,
    partition_profile_id: str,
    chart_id: str,
    interpolation_policy_id: str,
) -> dict:
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "field_id": str(field_id).strip(),
            "field_type_id": str(field_id).strip(),
            "spatial_scope_id": str(spatial_scope_id).strip(),
            "resolution_level": "macro",
            "update_policy_id": "field.static_default",
            "extensions": {
                "topology_profile_id": str(topology_profile_id).strip(),
                "metric_profile_id": str(metric_profile_id).strip(),
                "partition_profile_id": str(partition_profile_id).strip(),
                "chart_id": str(chart_id).strip(),
                "interpolation_policy_id": str(interpolation_policy_id).strip(),
                "source": "GEO10-1",
            },
        }
    )


def _field_cell_row(
    *,
    field_id: str,
    geo_cell_key: Mapping[str, object],
    value: object,
    last_updated_tick: int = 0,
) -> dict:
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "field_id": str(field_id).strip(),
            "cell_id": _cell_alias(geo_cell_key),
            "value": copy.deepcopy(value),
            "last_updated_tick": int(max(0, _as_int(last_updated_tick, 0))),
            "extensions": {
                "geo_cell_key": dict(geo_cell_key or {}),
                "source": "GEO10-1",
            },
        }
    )


def _geometry_cell_state_row(
    *,
    geo_cell_key: Mapping[str, object],
    material_id: str,
    occupancy_fraction: int,
) -> dict:
    occupancy_value = int(max(0, min(1000, _as_int(occupancy_fraction, 0))))
    permeability_proxy = 1000 - int((occupancy_value * 3) // 4)
    conductance_proxy = int((occupancy_value * 11) // 20)
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "geo_cell_key": dict(geo_cell_key or {}),
            "material_id": str(material_id).strip(),
            "occupancy_fraction": occupancy_value,
            "permeability_proxy": int(max(0, min(1000, permeability_proxy))),
            "conductance_proxy": int(max(0, min(1000, conductance_proxy))),
            "extensions": {"source": "GEO10-1"},
        }
    )


def _worldgen_request_row(
    *,
    geo_cell_key: Mapping[str, object],
    refinement_level: int,
    reason: str,
    suite_id: str,
) -> dict:
    semantic = {
        "geo_cell_key": dict(geo_cell_key or {}),
        "refinement_level": int(max(0, _as_int(refinement_level, 0))),
        "reason": str(reason).strip().lower(),
        "suite_id": str(suite_id).strip(),
    }
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "request_id": "geo10.worldgen.{}".format(canonical_sha256(semantic)[:16]),
            "geo_cell_key": dict(geo_cell_key or {}),
            "refinement_level": int(max(0, _as_int(refinement_level, 0))),
            "reason": str(reason).strip().lower(),
            "extensions": {
                "suite_id": str(suite_id).strip(),
                "source": "GEO10-1",
            },
        }
    )


def _pollution_field_id() -> str:
    return "field.pollution.co2_stub_concentration"


def _field_binding_payload() -> dict:
    return _read_json("data/registries/field_binding_registry.json")


def _interpolation_policy_payload() -> dict:
    return _read_json("data/registries/interpolation_policy_registry.json")


def _universe_identity(seed: int) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "universe_id": "universe.geo10.stress",
        "global_seed": "seed.geo10.{}".format(int(seed)),
        "domain_binding_ids": ["domain.navigation", "domain.astronomy", "domain.field"],
        "physics_profile_id": "physics.null",
        "topology_profile_id": "geo.topology.r3_infinite",
        "metric_profile_id": "geo.metric.euclidean",
        "partition_profile_id": "geo.partition.grid_zd",
        "projection_profile_id": "geo.projection.perspective_3d",
        "generator_version_id": "gen.v0_stub",
        "realism_profile_id": "realism.realistic_default_milkyway_stub",
        "base_scenario_id": "scenario.geo10.stress",
        "initial_pack_set_hash_expectation": "e" * 64,
        "compatibility_schema_refs": [
            "generator_version@1.0.0",
            "realism_profile@1.0.0",
            "overlay_manifest@1.0.0",
            "space_topology_profile@1.0.0",
            "metric_profile@1.0.0",
            "partition_profile@1.0.0",
            "projection_profile@1.0.0",
            "universe_identity@1.0.0",
        ],
        "immutable_after_create": True,
        "extensions": {"source": "GEO10-1"},
    }
    payload["identity_hash"] = canonical_sha256(dict(payload, identity_hash=""))
    return payload


def _field_rows_for_suite(
    *,
    topology_profile_id: str,
    metric_profile_id: str,
    partition_profile_id: str,
    chart_id: str,
    center_cell_key: Mapping[str, object],
    neighbor_cell_keys: Sequence[Mapping[str, object]],
    suite_id: str,
    seed: int,
    suite_index: int,
) -> dict:
    field_binding_registry = _field_binding_payload()
    interpolation_policy_registry = _interpolation_policy_payload()
    field_layers = [
        _field_layer_row(
            field_id="field.temperature",
            spatial_scope_id="spatial.geo10.{}".format(str(suite_id).strip()),
            topology_profile_id=topology_profile_id,
            metric_profile_id=metric_profile_id,
            partition_profile_id=partition_profile_id,
            chart_id=chart_id,
            interpolation_policy_id="interp.atlas_nearest"
            if partition_profile_id == "geo.partition.atlas_tiles"
            else "interp.nearest",
        ),
        _field_layer_row(
            field_id="field.wind",
            spatial_scope_id="spatial.geo10.{}".format(str(suite_id).strip()),
            topology_profile_id=topology_profile_id,
            metric_profile_id=metric_profile_id,
            partition_profile_id=partition_profile_id,
            chart_id=chart_id,
            interpolation_policy_id="interp.atlas_nearest"
            if partition_profile_id == "geo.partition.atlas_tiles"
            else "interp.nearest",
        ),
        _field_layer_row(
            field_id=_pollution_field_id(),
            spatial_scope_id="spatial.geo10.{}".format(str(suite_id).strip()),
            topology_profile_id=topology_profile_id,
            metric_profile_id=metric_profile_id,
            partition_profile_id=partition_profile_id,
            chart_id=chart_id,
            interpolation_policy_id="interp.atlas_nearest"
            if partition_profile_id == "geo.partition.atlas_tiles"
            else "interp.nearest",
        ),
    ]
    field_cells = []
    candidate_keys = [dict(center_cell_key)] + [dict(row) for row in list(neighbor_cell_keys or [])[:4]]
    for offset, cell_key in enumerate(candidate_keys):
        temperature_value = 255 + _pick(seed, "geo10.field.temperature", (suite_index * 10) + offset, 90)
        pollution_value = 10 + _pick(seed, "geo10.field.pollution", (suite_index * 10) + offset, 60)
        wind_vector = {
            "x": _pick(seed, "geo10.field.wind.x", (suite_index * 10) + offset, 9, offset=-4),
            "y": _pick(seed, "geo10.field.wind.y", (suite_index * 10) + offset, 9, offset=-4),
            "z": _pick(seed, "geo10.field.wind.z", (suite_index * 10) + offset, 5, offset=-2),
        }
        field_cells.append(_field_cell_row(field_id="field.temperature", geo_cell_key=cell_key, value=int(temperature_value)))
        field_cells.append(_field_cell_row(field_id="field.wind", geo_cell_key=cell_key, value=wind_vector))
        field_cells.append(_field_cell_row(field_id=_pollution_field_id(), geo_cell_key=cell_key, value=int(pollution_value)))
    return {
        "field_layers": [dict(row) for row in field_layers],
        "field_cells": [dict(row) for row in field_cells],
        "field_binding_registry": field_binding_registry,
        "interpolation_policy_registry": interpolation_policy_registry,
    }


def _pollution_fixture(
    *,
    topology_profile_id: str,
    metric_profile_id: str,
    partition_profile_id: str,
) -> dict:
    return {
        "pollutant_types_by_id": {
            "pollutant.co2_stub": {
                "pollutant_id": "pollutant.co2_stub",
                "default_dispersion_policy_id": "poll.policy.geo10",
                "default_decay_model_id": "model.poll_decay_half_life_stub",
                "extensions": {
                    "diffusion_coeff_permille": 160,
                    "wind_bias_permille": 100,
                },
            }
        },
        "pollution_policies_by_id": {
            "poll.policy.geo10": {
                "policy_id": "poll.policy.geo10",
                "tier": "P1",
                "wind_modifier_enabled": True,
                "extensions": {
                    "topology_profile_id": str(topology_profile_id).strip(),
                    "metric_profile_id": str(metric_profile_id).strip(),
                    "partition_profile_id": str(partition_profile_id).strip(),
                    "neighbor_radius": 1,
                },
            }
        },
        "decay_models_by_id": {
            "model.poll_decay_half_life_stub": {
                "model_id": "model.poll_decay_half_life_stub",
                "kind": "half_life",
                "half_life_ticks": 16,
                "deposition_permille": 0,
                "extensions": {"source": "GEO10-1"},
            }
        },
        "pollution_source_event_rows": [
            {
                "source_event_id": "poll.source.geo10",
                "tick": 0,
                "pollutant_id": "pollutant.co2_stub",
                "spatial_scope_id": "",
                "emitted_mass": 60,
            }
        ],
    }


def _suite_specs() -> List[dict]:
    return [
        {
            "suite_id": "geo10.suite.r3_grid",
            "topology_profile_id": "geo.topology.r3_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
            "projection_profile_id": "geo.projection.perspective_3d",
            "view_type_id": "view.map_ortho",
            "chart_id": "chart.global.r3",
            "dimension": 3,
            "center_index": [0, 0, 0],
            "goal_index": [2, 1, 0],
            "camera_local_position": [24000, -7000, 3000],
            "target_local_position": [4000, 2000, 1000],
            "slice_axes": [],
        },
        {
            "suite_id": "geo10.suite.r2_factorio",
            "topology_profile_id": "geo.topology.r2_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
            "projection_profile_id": "geo.projection.ortho_2d",
            "view_type_id": "view.minimap",
            "chart_id": "chart.global.r2",
            "dimension": 2,
            "center_index": [4, -3],
            "goal_index": [9, -1],
            "camera_local_position": [12000, -4000],
            "target_local_position": [1000, 2000],
            "slice_axes": [],
        },
        {
            "suite_id": "geo10.suite.torus_r2",
            "topology_profile_id": "geo.topology.torus_r2",
            "metric_profile_id": "geo.metric.torus_wrap",
            "partition_profile_id": "geo.partition.grid_zd",
            "projection_profile_id": "geo.projection.ortho_2d",
            "view_type_id": "view.map_ortho",
            "chart_id": "chart.global.r2",
            "dimension": 2,
            "center_index": [99, 0],
            "goal_index": [0, 0],
            "camera_local_position": [998000, 1000],
            "target_local_position": [2000, 1000],
            "slice_axes": [],
        },
        {
            "suite_id": "geo10.suite.sphere_atlas",
            "topology_profile_id": "geo.topology.sphere_surface_s2",
            "metric_profile_id": "geo.metric.spherical_geodesic_stub",
            "partition_profile_id": "geo.partition.atlas_tiles",
            "projection_profile_id": "geo.projection.atlas_unwrap_stub",
            "view_type_id": "view.atlas_unwrap",
            "chart_id": "chart.atlas.north",
            "dimension": 2,
            "center_index": [0, 0],
            "goal_index": [1, 1],
            "camera_local_position": [1000, 1000],
            "target_local_position": [500, 500],
            "slice_axes": [],
        },
        {
            "suite_id": "geo10.suite.cube_portal",
            "topology_profile_id": "geo.topology.cube_identified_stub",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
            "projection_profile_id": "geo.projection.perspective_3d",
            "view_type_id": "view.cctv_stub",
            "chart_id": "chart.cube.volume",
            "dimension": 3,
            "center_index": [0, 0, 0],
            "goal_index": [1, 0, 0],
            "camera_local_position": [6000, 3000, 2000],
            "target_local_position": [1000, 0, 0],
            "slice_axes": [],
        },
        {
            "suite_id": "geo10.suite.r4_slice",
            "topology_profile_id": "geo.topology.r4_stub",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
            "projection_profile_id": "geo.projection.slice_nd_stub",
            "view_type_id": "view.slice_nd_stub",
            "chart_id": "chart.global.r4",
            "dimension": 4,
            "center_index": [0, 0, 0, 0],
            "goal_index": [1, 0, 0, 1],
            "camera_local_position": [12000, 0, 0, 2000],
            "target_local_position": [1000, 0, 0, 1000],
            "slice_axes": ["w"],
        },
    ]


def _suite_row(spec: Mapping[str, object], *, seed: int, suite_index: int) -> dict:
    suite_id = str(spec.get("suite_id", "")).strip()
    topology_profile_id = str(spec.get("topology_profile_id", "")).strip()
    metric_profile_id = str(spec.get("metric_profile_id", "")).strip()
    partition_profile_id = str(spec.get("partition_profile_id", "")).strip()
    chart_id = str(spec.get("chart_id", "")).strip()
    center_cell_key = _cell_key(
        topology_profile_id=topology_profile_id,
        partition_profile_id=partition_profile_id,
        chart_id=chart_id,
        index_tuple=list(spec.get("center_index") or []),
    )
    goal_cell_key = _cell_key(
        topology_profile_id=topology_profile_id,
        partition_profile_id=partition_profile_id,
        chart_id=chart_id,
        index_tuple=list(spec.get("goal_index") or []),
    )
    neighbor_cell_keys = [
        _cell_key(
            topology_profile_id=topology_profile_id,
            partition_profile_id=partition_profile_id,
            chart_id=chart_id,
            index_tuple=[int(value) + (1 if idx == axis else 0) for idx, value in enumerate(list(spec.get("center_index") or []))],
        )
        for axis in range(int(max(1, _as_int(spec.get("dimension", 1), 1))))
    ]
    frame_ids = {
        "galaxy_root": "frame.galaxy_root.{}".format(suite_id.replace(".", "_")),
        "system_root": "frame.system_root.{}".format(suite_id.replace(".", "_")),
        "planet_root": "frame.planet_root.{}".format(suite_id.replace(".", "_")),
        "surface_local": "frame.surface_local.{}".format(suite_id.replace(".", "_")),
    }
    frame_nodes = [
        _frame_node(
            frame_id=frame_ids["galaxy_root"],
            parent_frame_id=None,
            topology_profile_id=topology_profile_id,
            metric_profile_id=metric_profile_id,
            chart_id=chart_id,
            anchor_cell_key=center_cell_key,
            scale_class_id="galaxy",
        ),
        _frame_node(
            frame_id=frame_ids["system_root"],
            parent_frame_id=frame_ids["galaxy_root"],
            topology_profile_id=topology_profile_id,
            metric_profile_id=metric_profile_id,
            chart_id=chart_id,
            anchor_cell_key=center_cell_key,
            scale_class_id="system",
        ),
        _frame_node(
            frame_id=frame_ids["planet_root"],
            parent_frame_id=frame_ids["system_root"],
            topology_profile_id=topology_profile_id,
            metric_profile_id=metric_profile_id,
            chart_id=chart_id,
            anchor_cell_key=center_cell_key,
            scale_class_id="planet",
        ),
        _frame_node(
            frame_id=frame_ids["surface_local"],
            parent_frame_id=frame_ids["planet_root"],
            topology_profile_id=topology_profile_id,
            metric_profile_id=metric_profile_id,
            chart_id=chart_id,
            anchor_cell_key=center_cell_key,
            scale_class_id="local",
        ),
    ]
    frame_transform_rows = [
        _frame_transform(
            from_frame_id=frame_ids["system_root"],
            to_frame_id=frame_ids["galaxy_root"],
            translation=[_pick(seed, suite_id + ".frame.system", idx, 5, offset=1) * 1000000 for idx in range(int(spec.get("dimension", 1)))],
        ),
        _frame_transform(
            from_frame_id=frame_ids["planet_root"],
            to_frame_id=frame_ids["system_root"],
            translation=[_pick(seed, suite_id + ".frame.planet", idx, 5, offset=1) * 100000 for idx in range(int(spec.get("dimension", 1)))],
        ),
        _frame_transform(
            from_frame_id=frame_ids["surface_local"],
            to_frame_id=frame_ids["planet_root"],
            translation=[_pick(seed, suite_id + ".frame.local", idx, 5, offset=1) * 10000 for idx in range(int(spec.get("dimension", 1)))],
        ),
    ]
    target_position_ref = _position_ref_row(
        object_id="object.target.{}".format(suite_id),
        frame_id=frame_ids["surface_local"],
        local_position=[int(_as_int(value, 0)) for value in list(spec.get("target_local_position") or [])],
    )
    camera_position_ref = _position_ref_row(
        object_id="object.camera.{}".format(suite_id),
        frame_id=frame_ids["surface_local"],
        local_position=[int(_as_int(value, 0)) for value in list(spec.get("camera_local_position") or [])],
    )
    remote_camera_position_ref = _position_ref_row(
        object_id="object.remote_camera.{}".format(suite_id),
        frame_id=frame_ids["surface_local"],
        local_position=[
            int(_as_int(value, 0)) + 2000
            for value in list(spec.get("target_local_position") or [])
        ],
    )
    field_fixture = _field_rows_for_suite(
        topology_profile_id=topology_profile_id,
        metric_profile_id=metric_profile_id,
        partition_profile_id=partition_profile_id,
        chart_id=chart_id,
        center_cell_key=center_cell_key,
        neighbor_cell_keys=neighbor_cell_keys,
        suite_id=suite_id,
        seed=seed,
        suite_index=suite_index,
    )
    pollution_fixture = _pollution_fixture(
        topology_profile_id=topology_profile_id,
        metric_profile_id=metric_profile_id,
        partition_profile_id=partition_profile_id,
    )
    pollution_fixture["pollution_source_event_rows"][0]["spatial_scope_id"] = str(
        field_fixture["field_cells"][0].get("cell_id", "")
    ).strip()
    geometry_cell_states = [
        _geometry_cell_state_row(
            geo_cell_key=center_cell_key,
            material_id="material.stone_basic",
            occupancy_fraction=1000,
        ),
        _geometry_cell_state_row(
            geo_cell_key=goal_cell_key,
            material_id="material.stone_basic",
            occupancy_fraction=750,
        ),
    ]
    worldgen_request = _worldgen_request_row(
        geo_cell_key=center_cell_key,
        refinement_level=3 if suite_id in {"geo10.suite.r3_grid", "geo10.suite.sphere_atlas"} else 2,
        reason="roi",
        suite_id=suite_id,
    )
    return {
        "suite_id": suite_id,
        "topology_profile_id": topology_profile_id,
        "metric_profile_id": metric_profile_id,
        "partition_profile_id": partition_profile_id,
        "projection_profile_id": str(spec.get("projection_profile_id", "")).strip(),
        "view_type_id": str(spec.get("view_type_id", "")).strip(),
        "chart_id": chart_id,
        "dimension": int(max(1, _as_int(spec.get("dimension", 1), 1))),
        "center_cell_key": center_cell_key,
        "goal_cell_key": goal_cell_key,
        "neighbor_cell_keys": neighbor_cell_keys,
        "frame_nodes": frame_nodes,
        "frame_transform_rows": frame_transform_rows,
        "target_position_ref": target_position_ref,
        "camera_position_ref": camera_position_ref,
        "remote_camera_position_ref": remote_camera_position_ref,
        "field_fixture": field_fixture,
        "pollution_fixture": pollution_fixture,
        "geometry_cell_states": geometry_cell_states,
        "worldgen_request": worldgen_request,
        "projection_extent": {
            "radius_cells": 1,
            "slice_axes": list(spec.get("slice_axes") or []),
        },
        "resolution_spec": {
            "width": 7 if str(spec.get("view_type_id", "")).strip() == "view.cctv_stub" else 9,
            "height": 7 if str(spec.get("view_type_id", "")).strip() == "view.cctv_stub" else 9,
        },
        "deterministic_fingerprint": canonical_sha256(
            {
                "suite_id": suite_id,
                "topology_profile_id": topology_profile_id,
                "metric_profile_id": metric_profile_id,
                "partition_profile_id": partition_profile_id,
                "center_cell_key": center_cell_key,
                "goal_cell_key": goal_cell_key,
                "frame_nodes": frame_nodes,
                "frame_transform_rows": frame_transform_rows,
                "field_fixture": field_fixture,
                "worldgen_request": worldgen_request,
            }
        ),
    }


def generate_geo_stress_scenario(
    *,
    seed: int = DEFAULT_GEO10_SEED,
    include_cctv: bool = True,
) -> dict:
    seed_value = int(max(1, _as_int(seed, DEFAULT_GEO10_SEED)))
    suites = [_suite_row(spec, seed=seed_value, suite_index=index) for index, spec in enumerate(_suite_specs())]
    if not include_cctv:
        for row in suites:
            if str(row.get("view_type_id", "")).strip() == "view.cctv_stub":
                row["view_type_id"] = "view.map_ortho"
                row["projection_profile_id"] = "geo.projection.ortho_2d"

    geometry_edit_fixture = {
        "target_cell_keys": [
            copy.deepcopy(_as_map(suites[0].get("center_cell_key"))),
            copy.deepcopy(_as_map(suites[0].get("goal_cell_key"))),
        ],
        "edit_kinds": ["remove", "add", "replace", "cut"],
        "volume_amounts": [300, 100, 200, 150],
        "material_id": "material.stone_basic",
    }
    overlay_fixture = {
        "include_mods": True,
        "save_value": "Geo10 Earth",
        "pack_lock_hash": "f" * 64,
    }
    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.geo10.stress.{}".format(
            canonical_sha256({"seed": seed_value, "suite_ids": [row.get("suite_id") for row in suites]})[:12]
        ),
        "scenario_seed": int(seed_value),
        "universe_identity": _universe_identity(seed_value),
        "topology_suites": [dict(row) for row in suites],
        "geometry_edit_fixture": geometry_edit_fixture,
        "overlay_fixture": overlay_fixture,
        "budgets": {
            "max_metric_queries": 192,
            "max_neighbor_radius_noncritical": 1,
            "max_projection_cells_per_view": 81,
            "max_path_expansions": 48,
            "allow_defer_derived_views": True,
        },
        "expected_invariants_summary": {
            "must_preserve": [
                "INV-GEO-BUDGETED",
                "INV-OVERLAY-MERGE-DETERMINISTIC",
                "INV-NO-TRUTH-IN-UI",
                "INV-GEO-ID-STABLE",
            ],
            "proof_surfaces": [
                "geo_profile_registry_hashes",
                "frame_graph_hash_chain",
                "field_binding_registry_hash",
                "overlay_manifest_hash",
                "geometry_edit_event_hash_chain",
                "worldgen_result_hash_chain",
            ],
        },
        "extensions": {
            "generator": "tools/geo/tool_generate_geo_stress.py",
            "named_rng_streams": [
                "rng.worldgen.galaxy",
                "rng.worldgen.system",
                "rng.worldgen.planet",
                "rng.worldgen.surface",
            ],
        },
        "deterministic_fingerprint": "",
    }
    scenario["deterministic_fingerprint"] = canonical_sha256(dict(scenario, deterministic_fingerprint=""))
    return scenario


__all__ = [
    "DEFAULT_GEO10_SEED",
    "DEFAULT_OUTPUT_REL",
    "_as_int",
    "_as_map",
    "_read_json",
    "_sorted_tokens",
    "generate_geo_stress_scenario",
    "write_json",
]

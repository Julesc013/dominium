"""Deterministic EARTH-6 terrain collision probes for replay and TestX reuse."""

from __future__ import annotations

import copy
import os
import sys
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.embodiment import resolve_macro_heightfield_sample  # noqa: E402
from src.geo import build_geometry_cell_state, geometry_cell_state_rows_by_key  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import execute_intent, replay_intent_script  # noqa: E402
from tools.xstack.testx.tests.emb0_testlib import authority_context, law_profile, policy_context, seed_embodied_state  # noqa: E402


SURFACE_CHART_ID = "chart.atlas.north"
CENTER_INDEX = [2, 2]
COLLISION_HASH_TICK = 0


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _tile_cell_key(index_tuple: Sequence[int]) -> dict:
    u_idx = int(index_tuple[0] if len(index_tuple) > 0 else 0)
    v_idx = int(index_tuple[1] if len(index_tuple) > 1 else 0)
    return {
        "schema_version": "1.0.0",
        "partition_profile_id": "geo.partition.atlas_tiles",
        "topology_profile_id": "geo.topology.sphere_surface_s2",
        "chart_id": SURFACE_CHART_ID,
        "index_tuple": [u_idx, v_idx],
        "refinement_level": 1,
        "deterministic_fingerprint": "",
        "extensions": {
            "legacy_cell_alias": "atlas.north.{}.{}".format(u_idx, v_idx),
            "planet_object_id": "planet.sol.earth",
            "planet_tags": ["planet.earth"],
        },
    }


def _surface_tile_artifact(*, index_tuple: Sequence[int], height_proxy: int, tile_suffix: str) -> dict:
    cell_key = _tile_cell_key(index_tuple)
    return {
        "tile_object_id": "tile.earth6.{}".format(tile_suffix),
        "planet_object_id": "planet.sol.earth",
        "tile_cell_key": dict(cell_key),
        "elevation_params_ref": {
            "height_proxy": int(max(0, int(height_proxy))),
            "macro_relief_permille": 320,
            "ridge_bias_permille": 400,
            "coastal_bias_permille": 120,
            "continent_mask_permille": 1000,
        },
        "material_baseline_id": "material.stone_basic",
        "biome_stub_id": "biome.stub.temperate",
        "drainage_accumulation_proxy": 1,
        "river_flag": False,
        "deterministic_fingerprint": "",
        "extensions": {
            "surface_class_id": "surface.class.land",
            "latitude_mdeg": 12000,
            "longitude_mdeg": 33000,
            "source": "EARTH6-8",
        },
    }


def build_collision_fixture(
    *,
    center_height: int = 400,
    east_height: int = 700,
    west_height: int = 150,
    north_height: int = 450,
    south_height: int = 300,
    body_z: int = 0,
    gravity_vector: Mapping[str, object] | None = None,
) -> dict:
    state = seed_embodied_state(
        gravity_vector=dict(gravity_vector or {"x": 0, "y": 0, "z": -9}),
        mass_value=5,
        include_camera=True,
    )
    center_key = _tile_cell_key(CENTER_INDEX)
    body = dict(list(state.get("body_assemblies") or [])[0] or {})
    body["frame_id"] = "frame.surface_local"
    body["transform_mm"] = {"x": 0, "y": 0, "z": int(body_z)}
    body_extensions = dict(body.get("extensions") or {})
    body_extensions["surface_tile_cell_key"] = dict(center_key)
    body_extensions["surface_chart_id"] = SURFACE_CHART_ID
    body_extensions["topology_profile_id"] = "geo.topology.sphere_surface_s2"
    body_extensions["partition_profile_id"] = "geo.partition.atlas_tiles"
    body["extensions"] = body_extensions
    state["body_assemblies"] = [body]

    body_state = dict(list(state.get("body_states") or [])[0] or {})
    body_state["frame_id"] = "frame.surface_local"
    body_state["position_ref"] = {"x": 0, "y": 0, "z": int(body_z)}
    state_extensions = dict(body_state.get("extensions") or {})
    state_extensions["surface_tile_cell_key"] = dict(center_key)
    body_state["extensions"] = state_extensions
    state["body_states"] = [body_state]

    if state.get("camera_assemblies"):
        camera = dict(list(state.get("camera_assemblies") or [])[0] or {})
        camera["frame_id"] = "frame.surface_local"
        state["camera_assemblies"] = [camera]

    tile_rows = [
        _surface_tile_artifact(index_tuple=CENTER_INDEX, height_proxy=center_height, tile_suffix="center"),
        _surface_tile_artifact(index_tuple=[CENTER_INDEX[0] + 1, CENTER_INDEX[1]], height_proxy=east_height, tile_suffix="east"),
        _surface_tile_artifact(index_tuple=[CENTER_INDEX[0] - 1, CENTER_INDEX[1]], height_proxy=west_height, tile_suffix="west"),
        _surface_tile_artifact(index_tuple=[CENTER_INDEX[0], CENTER_INDEX[1] + 1], height_proxy=north_height, tile_suffix="north"),
        _surface_tile_artifact(index_tuple=[CENTER_INDEX[0], CENTER_INDEX[1] - 1], height_proxy=south_height, tile_suffix="south"),
    ]
    state["worldgen_surface_tile_artifacts"] = tile_rows
    state["geometry_cell_states"] = [
        build_geometry_cell_state(
            geo_cell_key=dict(center_key),
            material_id="material.stone_basic",
            occupancy_fraction=1000,
            height_proxy=int(center_height),
        )
    ]
    return state


def _execute(state: dict, *, process_id: str, inputs: Mapping[str, object]) -> dict:
    allowed_processes = ["process.body_apply_input", "process.body_tick", "process.geometry_remove"]
    entitlements = ["entitlement.control.possess", "entitlement.control.admin"]
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.earth6.{}.{}".format(process_id.replace(".", "_"), len(list(state.get("events") or []))),
            "process_id": process_id,
            "inputs": dict(inputs),
        },
        law_profile=copy.deepcopy(law_profile(allowed_processes)),
        authority_context=copy.deepcopy(authority_context(entitlements, privilege_level="operator")),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )


def ground_contact_report(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    state = build_collision_fixture(body_z=120)
    result = _execute(state, process_id="process.body_tick", inputs={"body_id": "body.emb.test", "dt_ticks": 1})
    body = dict(list(state.get("body_assemblies") or [])[0] or {})
    contact = _as_map(_as_map(body.get("extensions")).get("terrain_collision_state"))
    return {
        "result": str(result.get("result", "")).strip() or "refused",
        "grounded": bool(contact.get("grounded", False)),
        "transform_z": int(_as_map(body.get("transform_mm")).get("z", 0) or 0),
        "ground_contact_height_mm": int(contact.get("ground_contact_height_mm", 0) or 0),
        "terrain_height_mm": int(contact.get("terrain_height_mm", 0) or 0),
        "slope_angle_mdeg": int(contact.get("slope_angle_mdeg", 0) or 0),
    }


def slope_modifier_report(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    uphill_state = build_collision_fixture(body_z=1600)
    downhill_state = build_collision_fixture(body_z=1600)
    uphill = _execute(
        uphill_state,
        process_id="process.body_apply_input",
        inputs={"body_id": "body.emb.test", "move_vector_local": {"x": 1000, "y": 0, "z": 0}, "look_vector": {"x": 0, "y": 0, "z": 0}, "dt_ticks": 1},
    )
    downhill = _execute(
        downhill_state,
        process_id="process.body_apply_input",
        inputs={"body_id": "body.emb.test", "move_vector_local": {"x": -1000, "y": 0, "z": 0}, "look_vector": {"x": 0, "y": 0, "z": 0}, "dt_ticks": 1},
    )
    uphill_body = dict(list(uphill_state.get("body_assemblies") or [])[0] or {})
    downhill_body = dict(list(downhill_state.get("body_assemblies") or [])[0] or {})
    uphill_slope = _as_map(_as_map(uphill_body.get("extensions")).get("terrain_slope_response"))
    downhill_slope = _as_map(_as_map(downhill_body.get("extensions")).get("terrain_slope_response"))
    uphill_force = dict(list(uphill_state.get("force_application_rows") or [])[0] or {}).get("force_vector") or {}
    downhill_force = dict(list(downhill_state.get("force_application_rows") or [])[0] or {}).get("force_vector") or {}
    return {
        "result": "complete"
        if str(uphill.get("result", "")).strip() == "complete" and str(downhill.get("result", "")).strip() == "complete"
        else "refused",
        "uphill_force_x": int(_as_map(uphill_force).get("x", 0) or 0),
        "downhill_force_x": int(_as_map(downhill_force).get("x", 0) or 0),
        "uphill_factor_permille": int(uphill_slope.get("accel_factor_permille", 0) or 0),
        "downhill_factor_permille": int(downhill_slope.get("accel_factor_permille", 0) or 0),
        "uphill_direction_class": str(uphill_slope.get("direction_class", "")).strip(),
        "downhill_direction_class": str(downhill_slope.get("direction_class", "")).strip(),
    }


def geometry_edit_height_report(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    state = build_collision_fixture(body_z=120)
    before_tick = _execute(state, process_id="process.body_tick", inputs={"body_id": "body.emb.test", "dt_ticks": 1})
    before_body = dict(list(state.get("body_assemblies") or [])[0] or {})
    before_contact = _as_map(_as_map(before_body.get("extensions")).get("terrain_collision_state"))
    edit = _execute(
        state,
        process_id="process.geometry_remove",
        inputs={"target_cell_keys": [_tile_cell_key(CENTER_INDEX)], "volume_amount": 250},
    )
    after_tick = _execute(state, process_id="process.body_tick", inputs={"body_id": "body.emb.test", "dt_ticks": 1})
    after_body = dict(list(state.get("body_assemblies") or [])[0] or {})
    after_contact = _as_map(_as_map(after_body.get("extensions")).get("terrain_collision_state"))
    return {
        "result": "complete"
        if str(before_tick.get("result", "")).strip() == "complete"
        and str(edit.get("result", "")).strip() == "complete"
        and str(after_tick.get("result", "")).strip() == "complete"
        else "refused",
        "before_height_mm": int(before_contact.get("terrain_height_mm", 0) or 0),
        "after_height_mm": int(after_contact.get("terrain_height_mm", 0) or 0),
        "collision_cache_invalidated_entries": int(_as_map(edit.get("result_metadata")).get("collision_cache_invalidated_entries", 0) or 0),
    }


def verify_collision_window_replay(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    law = copy.deepcopy(law_profile(["process.body_apply_input", "process.body_tick"]))
    auth = copy.deepcopy(authority_context(["entitlement.control.possess"], privilege_level="operator"))
    policy = copy.deepcopy(policy_context())
    fixture = build_collision_fixture(body_z=120)
    script = [
        {
            "intent_id": "intent.earth6.body_apply_input.001",
            "process_id": "process.body_apply_input",
            "inputs": {
                "body_id": "body.emb.test",
                "move_vector_local": {"x": -1000, "y": 0, "z": 0},
                "look_vector": {"x": 0, "y": 0, "z": 0},
                "dt_ticks": 1,
            },
        },
        {
            "intent_id": "intent.earth6.body_tick.001",
            "process_id": "process.body_tick",
            "inputs": {"body_id": "body.emb.test", "dt_ticks": 1},
        },
        {
            "intent_id": "intent.earth6.body_tick.002",
            "process_id": "process.body_tick",
            "inputs": {"body_id": "body.emb.test", "dt_ticks": 1},
        },
    ]
    first = replay_intent_script(
        universe_state=copy.deepcopy(fixture),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        intents=copy.deepcopy(script),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = replay_intent_script(
        universe_state=copy.deepcopy(fixture),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        intents=copy.deepcopy(script),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    stable = (
        str(first.get("result", "")).strip() == "complete"
        and str(second.get("result", "")).strip() == "complete"
        and str(first.get("final_state_hash", "")).strip() == str(second.get("final_state_hash", "")).strip()
    )
    return {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "final_state_hash": str(first.get("final_state_hash", "")).strip(),
        "deterministic_fingerprint": canonical_sha256(
            {
                "stable_across_repeated_runs": bool(stable),
                "final_state_hash": str(first.get("final_state_hash", "")).strip(),
            }
        ),
    }


def collision_hash(repo_root: str) -> str:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    replay = verify_collision_window_replay(repo_root)
    ground = ground_contact_report(repo_root)
    slope = slope_modifier_report(repo_root)
    edit = geometry_edit_height_report(repo_root)
    return canonical_sha256(
        {
            "replay_hash": str(replay.get("final_state_hash", "")).strip(),
            "ground_contact_height_mm": int(ground.get("ground_contact_height_mm", 0) or 0),
            "grounded": bool(ground.get("grounded", False)),
            "uphill_factor_permille": int(slope.get("uphill_factor_permille", 0) or 0),
            "downhill_factor_permille": int(slope.get("downhill_factor_permille", 0) or 0),
            "after_height_mm": int(edit.get("after_height_mm", 0) or 0),
        }
    )


def direct_surface_query_report(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    fixture = build_collision_fixture(body_z=1600)
    body = dict(list(fixture.get("body_assemblies") or [])[0] or {})
    body_state = dict(list(fixture.get("body_states") or [])[0] or {})
    query = resolve_macro_heightfield_sample(
        position_mm=dict(body.get("transform_mm") or {}),
        body_row=body,
        body_state_row=body_state,
        surface_tile_rows=fixture.get("worldgen_surface_tile_artifacts"),
        geometry_rows_by_key=geometry_cell_state_rows_by_key(fixture.get("geometry_cell_states") or []),
    )
    return {
        "result": str(query.get("result", "")).strip(),
        "terrain_height_mm": int(query.get("terrain_height_mm", 0) or 0),
        "slope_angle_mdeg": int(query.get("slope_angle_mdeg", 0) or 0),
    }


__all__ = [
    "build_collision_fixture",
    "collision_hash",
    "direct_surface_query_report",
    "geometry_edit_height_report",
    "ground_contact_report",
    "slope_modifier_report",
    "verify_collision_window_replay",
]

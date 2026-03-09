"""Shared deterministic UX-0 viewer shell fixtures."""

from __future__ import annotations

import copy
import sys
from functools import lru_cache

from tools.xstack.compatx.canonical_json import canonical_sha256


UX0_FIXTURE_TICK = 128
UX0_TARGET_OBJECT_ID = "object.earth"


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _world_cell_key(index_tuple: list[int]) -> dict:
    from tools.xstack.testx.tests.geo8_testlib import worldgen_cell_key

    return worldgen_cell_key(index_tuple)


def _viewer_perceived_model(*, map_access: bool) -> dict:
    instruments = {}
    channels = []
    if map_access:
        channels = ["ch.diegetic.ground_scanner", "ch.diegetic.map_local"]
        instruments = {
            "instrument.ground_scanner": {
                "reading": {
                    "rows": [
                        {
                            "geo_cell_key": _world_cell_key([0, 0, 0]),
                            "material_id": "material.rock",
                            "occupancy_fraction": 1000,
                        }
                    ]
                }
            },
            "instrument.map_local": {
                "reading": {
                    "entries": [
                        {
                            "cell_key": "placeholder",
                            "terrain_class": "ocean",
                        }
                    ]
                }
            },
        }
    return {
        "viewpoint_id": "viewpoint.ux0.fixture",
        "camera_viewpoint": {"view_mode_id": "view.first_person.player"},
        "time_state": {"tick": UX0_FIXTURE_TICK},
        "truth_overlay": {"state_hash_anchor": "truth.ux0.fixture.001"},
        "metadata": {
            "lens_type": "diegetic",
            "epistemic_policy_id": "epistemic.diegetic_default",
        },
        "entities": {
            "entries": [
                {
                    "semantic_id": UX0_TARGET_OBJECT_ID,
                    "entity_id": UX0_TARGET_OBJECT_ID,
                    "entity_kind": "planet",
                    "type_id": "kind.planet",
                    "transform_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "representation": {"shape_type": "sphere", "material_ref": "water"},
                    "flags": {"selectable": True},
                }
            ]
        },
        "channels": list(channels),
        "diegetic_instruments": instruments,
    }


def _inspection_snapshot() -> dict:
    return {
        "target_payload": {
            "target_id": UX0_TARGET_OBJECT_ID,
            "exists": True,
            "collection": "entities.entries",
            "row": {
                "object_id": UX0_TARGET_OBJECT_ID,
                "object_kind_id": "kind.planet",
                "type": "planet",
                "hierarchy": {"parent_object_id": "object.sol"},
                "physical": {
                    "mass_kg": 5972000000000000000000000,
                    "radius_km": 6371,
                },
                "orbit": {"semi_major_axis_milli_au": 1000},
                "lod_state": "L3",
                "tile_object_id": "tile.earth.0",
                "planet_object_id": UX0_TARGET_OBJECT_ID,
                "material_baseline_id": "material.water",
                "biome_stub_id": "biome.temperate",
                "geometry_cell_state": {
                    "geometry_cell_id": "geo.cell.earth.0",
                    "occupancy_class": "solid",
                    "material_id": "material.rock",
                },
            },
        },
        "summary_sections": {
            "section.logic.network": {"status": "present"},
            "section.system.capsule": {"status": "present"},
        },
    }


def _field_values() -> dict:
    return {"temperature": 288, "daylight": 700, "pollution": 0}


def _viewer_layer_sources() -> dict:
    return {
        "layer.geometry_occupancy": {
            "rows": [
                {
                    "geo_cell_key": _world_cell_key([0, 0, 0]),
                    "material_id": "material.rock",
                    "occupancy_fraction": 1000,
                }
            ]
        },
        "layer.terrain_stub": {
            "entries": [
                {
                    "cell_key": "placeholder",
                    "terrain_class": "ocean",
                }
            ]
        },
    }


@lru_cache(maxsize=4)
def _viewer_shell_fixture_cached(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from src.client.ui.viewer_shell import build_viewer_shell_state
    from tools.xstack.testx.tests.emb0_testlib import seed_embodied_state
    from tools.xstack.testx.tests.geo9_testlib import overlay_fixture_merge_result

    body_seed = seed_embodied_state(include_camera=True)
    merge_fixture = overlay_fixture_merge_result(include_mods=True, include_save=True)
    shell_state = build_viewer_shell_state(
        repo_root=repo_root,
        seed="42",
        authority_mode="dev",
        entrypoint="client",
        ui_mode="gui",
        start_session=True,
        perceived_model=_viewer_perceived_model(map_access=True),
        requested_lens_profile_id="lens.fp",
        teleport_command="/tp sol",
        inspection_snapshot=_inspection_snapshot(),
        property_origin_request={
            "object_id": UX0_TARGET_OBJECT_ID,
            "property_path": "display_name",
            "merge_result": merge_fixture["merge_result"],
        },
        field_values=_field_values(),
        body_state=dict(body_seed["body_states"][0]),
        body_row=dict(body_seed["body_assemblies"][0]),
        previous_camera_state=dict(body_seed["camera_assemblies"][0]),
        controller_id="controller.emb.test",
        layer_source_payloads=_viewer_layer_sources(),
        map_layer_ids=["layer.terrain_stub", "layer.geometry_occupancy"],
        minimap_layer_ids=["layer.terrain_stub"],
        selection={"object_id": UX0_TARGET_OBJECT_ID},
    )
    return {
        "body_seed": copy.deepcopy(body_seed),
        "merge_fixture": copy.deepcopy(merge_fixture),
        "shell_state": dict(shell_state),
    }


def viewer_shell_fixture(repo_root: str) -> dict:
    return copy.deepcopy(_viewer_shell_fixture_cached(repo_root))


@lru_cache(maxsize=4)
def _redacted_map_fixture_cached(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from src.client.ui.map_views import build_map_view_set

    perceived_model = {
        "viewpoint_id": "viewpoint.ux0.redaction",
        "time_state": {"tick": 64},
        "truth_overlay": {"state_hash_anchor": "truth.ux0.redaction"},
        "metadata": {
            "lens_type": "diegetic",
            "epistemic_policy_id": "epistemic.diegetic_default",
        },
        "channels": [],
        "diegetic_instruments": {},
    }
    authority_context = {
        "authority_origin": "client",
        "privilege_level": "observer",
        "entitlements": [],
    }
    layer_source_payloads = {
        "layer.entity_markers_stub": {
            "required_channels": ["ch.diegetic.map_local"],
            "rows": [{"marker_id": "marker.ux0.channel_gate"}],
        },
        "layer.infrastructure_stub": {
            "required_entitlements": ["entitlement.inspect"],
            "rows": [{"marker_id": "marker.ux0.entitlement_gate"}],
        },
        "layer.terrain_stub": {
            "entries": [{"cell_key": "placeholder", "terrain_class": "ocean"}],
        },
    }
    view_set = build_map_view_set(
        perceived_model=perceived_model,
        authority_context=authority_context,
        layer_source_payloads=layer_source_payloads,
        map_layer_ids=["layer.terrain_stub", "layer.entity_markers_stub", "layer.infrastructure_stub"],
        minimap_layer_ids=["layer.terrain_stub", "layer.entity_markers_stub", "layer.infrastructure_stub"],
        lens_id="lens.diegetic.sensor",
        ui_mode="cli",
        truth_hash_anchor="truth.ux0.redaction",
    )
    return {
        "perceived_model": perceived_model,
        "authority_context": authority_context,
        "layer_source_payloads": layer_source_payloads,
        "view_set": dict(view_set),
    }


def redacted_map_fixture(repo_root: str) -> dict:
    return copy.deepcopy(_redacted_map_fixture_cached(repo_root))


@lru_cache(maxsize=4)
def _candidate_system_rows_cached(repo_root: str) -> list[dict]:
    _ensure_repo_root(repo_root)
    from src.worldgen.mw import list_systems_in_cell
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_cell_key

    worldgen_state = seed_worldgen_state()
    result = list_systems_in_cell(
        universe_identity=worldgen_state.get("universe_identity"),
        geo_cell_key=worldgen_cell_key([800, 0, 0]),
        refinement_level=1,
        cache_enabled=False,
    )
    return [dict(row) for row in list(result.get("systems") or []) if isinstance(row, dict)]


def candidate_system_rows(repo_root: str) -> list[dict]:
    return copy.deepcopy(_candidate_system_rows_cached(repo_root))


def viewer_shell_surface_hash(shell_state: dict) -> str:
    state = dict(shell_state or {})
    summary = {
        "viewer_shell_id": str(state.get("viewer_shell_id", "")).strip(),
        "state_machine": dict(state.get("state_machine") or {}),
        "lens_resolution": dict(state.get("lens_resolution") or {}),
        "control_surface": dict(state.get("control_surface") or {}),
        "teleport_plan": dict(state.get("teleport_plan") or {}),
        "inspection_surfaces": dict(state.get("inspection_surfaces") or {}),
        "map_views": dict(state.get("map_views") or {}),
        "selection_controls": dict(state.get("selection_controls") or {}),
        "ui_contract": dict(state.get("ui_contract") or {}),
        "render_model_hash": str(dict(state.get("render_contract") or {}).get("render_model_hash", "")).strip(),
    }
    return canonical_sha256(summary)

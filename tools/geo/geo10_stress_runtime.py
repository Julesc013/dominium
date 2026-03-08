"""Deterministic GEO-10 stress runtime over the existing GEO subsystem."""

from __future__ import annotations

import copy
import json
import os
from typing import List, Mapping, Sequence

from tools.geo.geo10_stress_common import (
    DEFAULT_GEO10_SEED,
    DEFAULT_OUTPUT_REL,
    _as_int,
    _as_map,
    _read_json,
    generate_geo_stress_scenario,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_REPORT_REL = "build/geo/geo10_stress_report.json"


def _load_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def load_geo_stress_scenario(path: str = "") -> dict:
    token = str(path or "").strip()
    if token:
        return _load_json(os.path.normpath(os.path.abspath(token)))
    return generate_geo_stress_scenario(seed=DEFAULT_GEO10_SEED, include_cctv=True)


def _registry_hash(rel_path: str) -> str:
    return canonical_sha256(_read_json(rel_path))


def _field_type_registry() -> dict:
    return _read_json("data/registries/field_type_registry.json")


def _field_binding_registry() -> dict:
    return _read_json("data/registries/field_binding_registry.json")


def _interpolation_policy_registry() -> dict:
    return _read_json("data/registries/interpolation_policy_registry.json")


def _metric_policy_registry() -> dict:
    return _read_json("data/registries/metric_policy_registry.json")


def _geodesic_policy_registry() -> dict:
    return _read_json("data/registries/geodesic_approx_policy_registry.json")


def _geo_profile_registry_hashes() -> dict:
    return {
        "space_topology_profile_registry_hash": _registry_hash("data/registries/space_topology_profile_registry.json"),
        "metric_profile_registry_hash": _registry_hash("data/registries/metric_profile_registry.json"),
        "partition_profile_registry_hash": _registry_hash("data/registries/partition_profile_registry.json"),
        "projection_profile_registry_hash": _registry_hash("data/registries/projection_profile_registry.json"),
        "field_binding_registry_hash": canonical_sha256(_field_binding_registry()),
        "interpolation_policy_registry_hash": canonical_sha256(_interpolation_policy_registry()),
        "metric_policy_registry_hash": canonical_sha256(_metric_policy_registry()),
        "geodesic_approx_policy_registry_hash": canonical_sha256(_geodesic_policy_registry()),
        "lens_layer_registry_hash": _registry_hash("data/registries/lens_layer_registry.json"),
        "view_type_registry_hash": _registry_hash("data/registries/view_type_registry.json"),
        "traversal_policy_registry_hash": _registry_hash("data/registries/traversal_policy_registry.json"),
        "geometry_edit_policy_registry_hash": _registry_hash("data/registries/geometry_edit_policy_registry.json"),
        "generator_version_registry_hash": _registry_hash("data/registries/generator_version_registry.json"),
        "realism_profile_registry_hash": _registry_hash("data/registries/realism_profile_registry.json"),
        "overlay_policy_registry_hash": _registry_hash("data/registries/overlay_policy_registry.json"),
    }


def _pollution_field_id() -> str:
    return "field.pollution.co2_stub_concentration"


def _cell_key_hash(cell_key: Mapping[str, object]) -> str:
    return canonical_sha256(
        {
            "partition_profile_id": str(_as_map(cell_key).get("partition_profile_id", "")).strip(),
            "topology_profile_id": str(_as_map(cell_key).get("topology_profile_id", "")).strip(),
            "chart_id": str(_as_map(cell_key).get("chart_id", "")).strip(),
            "index_tuple": [int(_as_int(value, 0)) for value in list(_as_map(cell_key).get("index_tuple") or [])],
            "refinement_level": int(max(0, _as_int(_as_map(cell_key).get("refinement_level", 0), 0))),
        }
    )


def _cell_alias(cell_key: Mapping[str, object]) -> str:
    ext = _as_map(_as_map(cell_key).get("extensions"))
    alias = str(ext.get("legacy_cell_alias", "")).strip()
    if alias:
        return alias
    chart_id = str(_as_map(cell_key).get("chart_id", "")).strip().replace(".", "_") or "cell"
    index_tuple = [int(_as_int(value, 0)) for value in list(_as_map(cell_key).get("index_tuple") or [])]
    return "{}.{}".format(chart_id, "_".join(str(value) for value in index_tuple))


def _sorted_rows(rows: object, key_fn) -> List[dict]:
    return sorted((dict(row) for row in list(rows or []) if isinstance(row, Mapping)), key=key_fn)


def _hash_chain(rows: object, key_fn) -> str:
    chain = "0" * 64
    for row in _sorted_rows(rows, key_fn):
        chain = canonical_sha256({"previous_hash": chain, "row_hash": canonical_sha256(row)})
    return chain


def _position_to_coords(position_ref: Mapping[str, object]) -> dict:
    coords = [int(_as_int(value, 0)) for value in list(_as_map(position_ref).get("local_position") or [])]
    return {"coords": coords}


def _terrain_entries(projected_cells: Sequence[Mapping[str, object]], *, suite_id: str) -> List[dict]:
    entries = []
    for row in projected_cells:
        cell_key = _as_map(_as_map(row).get("geo_cell_key"))
        entries.append(
            {
                "region_key": _cell_alias(cell_key),
                "cell_key": _cell_key_hash(cell_key),
                "terrain_class": "terrain.{}".format(str(suite_id).split(".")[-1]),
            }
        )
    return sorted((dict(row) for row in entries), key=lambda row: (str(row.get("region_key", "")), str(row.get("cell_key", ""))))


def _marker_rows(*, goal_cell_key: Mapping[str, object], marker_id: str) -> List[dict]:
    return [
        {
            "marker_id": str(marker_id),
            "geo_cell_key": dict(goal_cell_key),
            "label": "marker.{}".format(str(marker_id).split(".")[-1]),
        }
    ]


def _perceived_model(*, truth_hash_anchor: str, allow_geometry: bool, diegetic: bool = True) -> dict:
    channels = ["ch.diegetic.map_local"]
    if allow_geometry:
        channels.append("ch.diegetic.ground_scanner")
    return {
        "lens_id": "lens.diegetic.map_local" if diegetic else "lens.debug.nondiegetic",
        "metadata": {
            "lens_type": "diegetic" if diegetic else "nondiegetic",
            "epistemic_policy_id": "epistemic.geo10.diegetic" if diegetic else "epistemic.geo10.debug",
        },
        "channels": channels,
        "truth_overlay": {"state_hash_anchor": str(truth_hash_anchor).strip()},
        "diegetic_instruments": {
            "instrument.map_local": {"reading": {"entries": []}},
            "instrument.ground_scanner": {"reading": {"geometry_cell_states": []}},
        },
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.geo10.stress",
        "entitlements": ["entitlement.inspect"],
        "privilege_level": "observer",
        "subject_id": "subject.tool.geo10",
        "requester_subject_id": "subject.tool.geo10",
    }


def _resolved_overlay_packs(suite_id: str, overlay_fixture: Mapping[str, object]) -> List[dict]:
    save_pack = str(_as_map(overlay_fixture).get("pack_lock_hash", "")).strip()
    return [
        {
            "pack_id": "pack.official.{}".format(str(suite_id).split(".")[-1]),
            "canonical_hash": canonical_sha256({"suite_id": suite_id, "kind": "official"}),
            "signature_status": "official",
        },
        {
            "pack_id": "pack.mod.{}".format(str(suite_id).split(".")[-1]),
            "canonical_hash": canonical_sha256({"suite_id": suite_id, "kind": "mod"}),
            "signature_status": "unsigned",
        },
        {
            "pack_id": "pack.lock.{}".format(str(suite_id).split(".")[-1]),
            "canonical_hash": save_pack,
            "signature_status": "official",
        },
    ]


def _shard_assignment(center_cell_key: Mapping[str, object], goal_cell_key: Mapping[str, object]) -> dict:
    return {
        "default_shard_id": "shard.geo10.local",
        "cells": [
            {"geo_cell_key": dict(center_cell_key), "shard_id": "shard.geo10.alpha"},
            {"geo_cell_key": dict(goal_cell_key), "shard_id": "shard.geo10.beta"},
        ],
    }


def _path_policy_registry(max_expansions: int) -> dict:
    return {
        "record": {
            "traversal_policies": [
                {
                    "schema_version": "1.0.0",
                    "traversal_policy_id": "traverse.geo10.stress",
                    "allowed_neighbor_kinds": [],
                    "cost_weights": {
                        "base_distance": 1000,
                        "field_cost": 80,
                        "infrastructure_bias": -120,
                        "portal_cost": 25,
                    },
                    "infrastructure_preference": {
                        "overlay_kind": "road",
                        "prefer_tags": ["road"],
                    },
                    "max_expansions": int(max(1, _as_int(max_expansions, 48))),
                    "extensions": {
                        "partial_result_policy": "partial",
                        "source": "GEO10-2",
                    },
                }
            ]
        }
    }


def _field_cost_data(
    *,
    field_fixture: Mapping[str, object],
    center_cell_key: Mapping[str, object],
    goal_cell_key: Mapping[str, object],
) -> dict:
    return {
        "field_terms": [
            {"field_id": "field.temperature", "weight": 1, "sample_from": "delta"},
            {"field_id": _pollution_field_id(), "weight": 1, "sample_from": "neighbor"},
        ],
        "values_by_field_id": {
            "field.temperature": {
                _cell_key_hash(center_cell_key): 320,
                _cell_key_hash(goal_cell_key): 410,
            },
            _pollution_field_id(): {
                _cell_key_hash(center_cell_key): 18,
                _cell_key_hash(goal_cell_key): 42,
            },
        },
        "field_layer_rows": list(_as_map(field_fixture).get("field_layers") or []),
        "field_cell_rows": list(_as_map(field_fixture).get("field_cells") or []),
        "field_type_registry": _field_type_registry(),
        "field_binding_registry": _as_map(field_fixture.get("field_binding_registry")) or _field_binding_registry(),
        "interpolation_policy_registry": _as_map(field_fixture.get("interpolation_policy_registry")) or _interpolation_policy_registry(),
    }


def _infrastructure_overlay(center_cell_key: Mapping[str, object], goal_cell_key: Mapping[str, object]) -> dict:
    return {
        "overlay_kind": "road",
        "entries": [
            {
                "from_geo_cell_key": dict(center_cell_key),
                "to_geo_cell_key": dict(goal_cell_key),
                "overlay_kind": "road",
                "tags": ["road"],
                "cost_delta": -150,
            }
        ],
    }


def _metric_cache_probe(query_fn) -> dict:
    from src.geo import metric_cache_clear, metric_cache_snapshot

    metric_cache_clear()
    before = metric_cache_snapshot()
    first = query_fn()
    after_first = metric_cache_snapshot()
    second = query_fn()
    after_second = metric_cache_snapshot()
    hit = bool(
        str(_as_map(first).get("deterministic_fingerprint", "")).strip()
        and first == second
        and int(_as_int(after_first.get("cache_entry_count", 0), 0))
        == int(_as_int(after_second.get("cache_entry_count", 0), 0))
    )
    return {
        "first": dict(first) if isinstance(first, Mapping) else {},
        "second": dict(second) if isinstance(second, Mapping) else {},
        "cache_hit": bool(hit),
        "before_cache_entries": int(_as_int(before.get("cache_entry_count", 0), 0)),
        "after_cache_entries": int(_as_int(after_second.get("cache_entry_count", 0), 0)),
    }


def _suite_worldgen_and_overlay(
    *,
    suite: Mapping[str, object],
    scenario: Mapping[str, object],
) -> dict:
    from src.geo import (
        build_default_overlay_manifest,
        build_property_patch,
        explain_property_origin,
        generate_worldgen_result,
        geo_object_id,
        merge_overlay_view,
        overlay_base_objects_from_worldgen_result,
        overlay_cache_clear,
        overlay_proof_surface,
        worldgen_cache_clear,
        worldgen_result_proof_surface,
    )

    universe_identity = _as_map(scenario.get("universe_identity"))
    worldgen_request = _as_map(suite.get("worldgen_request"))
    worldgen_cache_clear()
    worldgen_first = generate_worldgen_result(
        universe_identity=universe_identity,
        worldgen_request=worldgen_request,
    )
    worldgen_second = generate_worldgen_result(
        universe_identity=universe_identity,
        worldgen_request=worldgen_request,
    )
    worldgen_result = _as_map(worldgen_first.get("worldgen_result"))
    generated_object_rows = list(worldgen_first.get("generated_object_rows") or [])
    worldgen_surface = worldgen_result_proof_surface(
        worldgen_requests=[worldgen_request],
        worldgen_results=[worldgen_result],
        worldgen_spawned_objects=generated_object_rows,
    )
    base_objects = overlay_base_objects_from_worldgen_result(
        worldgen_result=worldgen_result,
        generated_object_rows=generated_object_rows,
    )
    primary_object = dict(base_objects[0]) if base_objects else {}
    primary_object_id = str(primary_object.get("object_id", "")).strip()
    overlay_fixture = _as_map(scenario.get("overlay_fixture"))
    suite_suffix = str(suite.get("suite_id", "")).split(".")[-1]
    manifest = build_default_overlay_manifest(
        universe_id=str(universe_identity.get("universe_id", "")).strip() or "universe.geo10.stress",
        pack_lock_hash=str(overlay_fixture.get("pack_lock_hash", "")).strip() or ("f" * 64),
        save_id="save.geo10.{}".format(suite_suffix),
        generator_version_id=str(universe_identity.get("generator_version_id", "")).strip(),
        official_layer_specs=[
            {
                "layer_id": "official.reality.{}".format(suite_suffix),
                "pack_hash": canonical_sha256({"suite_id": suite.get("suite_id"), "layer_kind": "official"}),
                "pack_id": "pack.official.{}".format(suite_suffix),
                "signature_status": "official",
            }
        ],
        mod_layer_specs=[
            {
                "layer_id": "mod.{}".format(suite_suffix),
                "pack_hash": canonical_sha256({"suite_id": suite.get("suite_id"), "layer_kind": "mod"}),
                "pack_id": "pack.mod.{}".format(suite_suffix),
                "signature_status": "unsigned",
            }
        ],
        overlay_policy_id="overlay.default",
    )
    add_object = geo_object_id(
        str(universe_identity.get("identity_hash", "")).strip(),
        _as_map(suite.get("goal_cell_key")),
        "kind.structure",
        "overlay:0",
    )
    added_object_id = str(_as_map(add_object).get("object_id_hash", "")).strip()
    property_patches = []
    if primary_object_id:
        property_patches.extend(
            [
                build_property_patch(
                    target_object_id=primary_object_id,
                    property_path="display.name",
                    operation="set",
                    value="Official {}".format(suite_suffix),
                    originating_layer_id="official.reality.{}".format(suite_suffix),
                    extensions={"source": "GEO10-2"},
                ),
                build_property_patch(
                    target_object_id=primary_object_id,
                    property_path="display.name",
                    operation="set",
                    value="Modded {}".format(suite_suffix),
                    originating_layer_id="mod.{}".format(suite_suffix),
                    extensions={"source": "GEO10-2"},
                ),
                build_property_patch(
                    target_object_id=primary_object_id,
                    property_path="display.name",
                    operation="set",
                    value="{} {}".format(
                        str(overlay_fixture.get("save_value", "Geo10")),
                        suite_suffix,
                    ),
                    originating_layer_id="save.patch",
                    extensions={"source": "GEO10-2"},
                ),
            ]
        )
    if added_object_id:
        property_patches.append(
            build_property_patch(
                target_object_id=added_object_id,
                property_path="display.name",
                operation="set",
                value="Overlay Added {}".format(suite_suffix),
                originating_layer_id="mod.{}".format(suite_suffix),
                extensions={
                    "object_kind_id": "kind.structure",
                    "geo_cell_key": dict(_as_map(suite.get("goal_cell_key"))),
                    "source": "GEO10-2",
                },
            )
        )

    overlay_cache_clear()
    merge_result = merge_overlay_view(
        base_objects=base_objects,
        overlay_manifest=manifest,
        property_patches=property_patches,
        resolved_packs=_resolved_overlay_packs(str(suite.get("suite_id", "")).strip(), overlay_fixture),
        expected_pack_lock_hash=str(manifest.get("pack_lock_hash", "")).strip(),
        overlay_policy_id="overlay.default",
    )
    origin_report = (
        explain_property_origin(
            merge_result=merge_result,
            object_id=primary_object_id,
            property_path="display.name",
        )
        if primary_object_id
        else {}
    )
    overlay_surface = overlay_proof_surface(
        overlay_manifest=manifest,
        property_patches=property_patches,
        effective_object_views=merge_result.get("effective_object_views"),
    )
    merged_ids = sorted(
        str(_as_map(row).get("object_id", "")).strip()
        for row in list(merge_result.get("effective_object_views") or [])
        if str(_as_map(row).get("object_id", "")).strip()
    )
    base_ids = sorted(
        str(_as_map(row).get("object_id", "")).strip()
        for row in list(base_objects or [])
        if str(_as_map(row).get("object_id", "")).strip()
    )
    return {
        "worldgen_first": worldgen_first,
        "worldgen_second": worldgen_second,
        "worldgen_surface": worldgen_surface,
        "base_objects": base_objects,
        "overlay_manifest": manifest,
        "property_patches": property_patches,
        "merge_result": merge_result,
        "origin_report": origin_report,
        "overlay_surface": overlay_surface,
        "stable_identity_under_overlay": all(object_id in set(merged_ids) for object_id in base_ids),
    }


def _suite_geometry_and_compaction(
    *,
    suite: Mapping[str, object],
    scenario: Mapping[str, object],
) -> dict:
    from src.geo import (
        aggregate_geometry_chunk_to_cell,
        build_micro_geometry_chunk_from_cell_state,
        geometry_add_volume,
        geometry_apply_micro_chunk_edit,
        geometry_coupling_effects_for_cell_state,
        geometry_cut_volume,
        geometry_remove_volume,
        geometry_replace_material,
        geometry_state_hash_surface,
    )
    from src.meta.provenance import compact_provenance_window, verify_replay_from_compaction_anchor

    fixture = _as_map(scenario.get("geometry_edit_fixture"))
    target_cell_keys = [dict(row) for row in list(fixture.get("target_cell_keys") or [])]
    geometry_rows = [dict(row) for row in list(suite.get("geometry_cell_states") or [])]
    volume_amounts = list(fixture.get("volume_amounts") or [300, 100, 200, 150])
    remove_result = geometry_remove_volume(
        geometry_cell_states=geometry_rows,
        target_cell_keys=target_cell_keys,
        volume_amount=int(_as_int((volume_amounts + [300])[0], 300)),
        tick=0,
        operator_subject_id="subject.tool.geo10",
        geometry_edit_policy_id="geo.edit.default",
        extensions={"source": "GEO10-2"},
    )
    after_remove = list(remove_result.get("geometry_cell_states") or geometry_rows)
    add_result = geometry_add_volume(
        geometry_cell_states=after_remove,
        target_cell_keys=target_cell_keys,
        volume_amount=int(_as_int((volume_amounts + [100, 100])[1], 100)),
        material_id=str(fixture.get("material_id", "material.stone_basic")).strip(),
        tick=1,
        operator_subject_id="subject.tool.geo10",
        geometry_edit_policy_id="geo.edit.default",
        extensions={"source": "GEO10-2"},
    )
    after_add = list(add_result.get("geometry_cell_states") or after_remove)
    replace_result = geometry_replace_material(
        geometry_cell_states=after_add,
        target_cell_keys=target_cell_keys,
        material_id="material.stone_basic",
        volume_amount=int(_as_int((volume_amounts + [200, 200, 200])[2], 200)),
        tick=2,
        operator_subject_id="subject.tool.geo10",
        geometry_edit_policy_id="geo.edit.default",
        extensions={"source": "GEO10-2"},
    )
    after_replace = list(replace_result.get("geometry_cell_states") or after_add)
    cut_result = geometry_cut_volume(
        geometry_cell_states=after_replace,
        target_cell_keys=target_cell_keys,
        volume_amount=int(_as_int((volume_amounts + [150, 150, 150, 150])[3], 150)),
        tick=3,
        operator_subject_id="subject.tool.geo10",
        geometry_edit_policy_id="geo.edit.default",
        extensions={"source": "GEO10-2"},
    )
    after_cut = list(cut_result.get("geometry_cell_states") or after_replace)
    edit_events = [
        _as_map(remove_result.get("geometry_edit_event")),
        _as_map(add_result.get("geometry_edit_event")),
        _as_map(replace_result.get("geometry_edit_event")),
        _as_map(cut_result.get("geometry_edit_event")),
    ]
    edit_events = [dict(row) for row in edit_events if row]
    chunk_seed = dict(after_cut[0]) if after_cut else {}
    chunk_row = build_micro_geometry_chunk_from_cell_state(chunk_seed, subcell_count=8, extensions={"source": "GEO10-2"})
    micro_edit = geometry_apply_micro_chunk_edit(
        chunk_row,
        edit_kind="remove",
        volume_amount=50,
        extensions={"source": "GEO10-2"},
    )
    aggregated_micro = aggregate_geometry_chunk_to_cell(_as_map(micro_edit.get("chunk_state")))
    final_geometry_rows = [dict(after_cut[0])] if after_cut else []
    if final_geometry_rows:
        final_geometry_rows[0] = dict(aggregated_micro)
        final_geometry_rows.extend([dict(row) for row in list(after_cut[1:])])
    else:
        final_geometry_rows = [dict(aggregated_micro)]
    geometry_surface = geometry_state_hash_surface(
        geometry_cell_states=final_geometry_rows,
        geometry_chunk_states=[_as_map(micro_edit.get("chunk_state"))],
        geometry_edit_events=edit_events,
    )
    prior_by_hash = {_cell_key_hash(_as_map(row).get("geo_cell_key")): dict(row) for row in geometry_rows}
    coupling_rows = [
        geometry_coupling_effects_for_cell_state(row, prior_row=prior_by_hash.get(_cell_key_hash(_as_map(row).get("geo_cell_key"))))
        for row in final_geometry_rows
    ]
    compaction_state = {
        "geometry_edit_events": [dict(row) for row in edit_events],
        "derived_summary_rows": [
            {"summary_id": "derived.geo10.0", "tick": 0, "artifact_id": "artifact.geo10.0"},
            {"summary_id": "derived.geo10.1", "tick": 1, "artifact_id": "artifact.geo10.1"},
            {"summary_id": "derived.geo10.2", "tick": 2, "artifact_id": "artifact.geo10.2"},
            {"summary_id": "derived.geo10.3", "tick": 3, "artifact_id": "artifact.geo10.3"},
        ],
        "compaction_markers": [],
    }
    compaction_result = compact_provenance_window(
        state_payload=compaction_state,
        classification_rows=[],
        shard_id="shard.geo10.{}".format(str(suite.get("suite_id", "")).split(".")[-1]),
        start_tick=0,
        end_tick=3,
    )
    replay_report = {}
    if str(compaction_result.get("result", "")) == "complete":
        replay_report = verify_replay_from_compaction_anchor(
            state_payload=_as_map(compaction_result.get("state")),
            marker_id=str(_as_map(compaction_result.get("compaction_marker")).get("marker_id", "")).strip(),
        )
    return {
        "geometry_rows": final_geometry_rows,
        "geometry_chunk_rows": [_as_map(micro_edit.get("chunk_state"))],
        "geometry_edit_events": edit_events,
        "geometry_surface": geometry_surface,
        "coupling_rows": [dict(row) for row in coupling_rows],
        "compaction_result": compaction_result,
        "replay_report": replay_report,
    }


def _suite_projection_and_views(
    *,
    suite: Mapping[str, object],
    geometry_rows: object,
    scenario_truth_anchor: str,
) -> dict:
    from src.geo import (
        build_cctv_view_delivery,
        build_lens_request,
        build_projection_request,
        build_projected_view_artifact,
        project_view_cells,
        projected_view_fingerprint,
    )

    field_fixture = _as_map(suite.get("field_fixture"))
    graph_version = canonical_sha256(
        {
            "frame_nodes": list(suite.get("frame_nodes") or []),
            "frame_transform_rows": list(suite.get("frame_transform_rows") or []),
        }
    )
    projection_request = build_projection_request(
        request_id="projection_request.{}".format(str(suite.get("suite_id", "")).split(".")[-1]),
        projection_profile_id=str(suite.get("projection_profile_id", "")).strip(),
        origin_position_ref=_as_map(suite.get("camera_position_ref")),
        extent_spec=_as_map(suite.get("projection_extent")),
        resolution_spec=_as_map(suite.get("resolution_spec")),
        extensions={
            "view_type_id": str(suite.get("view_type_id", "")).strip(),
            "target_frame_id": str(_as_map(suite.get("camera_position_ref")).get("frame_id", "")).strip(),
            "chart_id": str(suite.get("chart_id", "")).strip(),
            "worldgen_refinement_level": int(max(0, _as_int(_as_map(suite.get("worldgen_request")).get("refinement_level", 0), 0))),
            "worldgen_reason": "roi",
        },
    )
    projection_result = project_view_cells(
        projection_request,
        topology_profile_id=str(suite.get("topology_profile_id", "")).strip(),
        partition_profile_id=str(suite.get("partition_profile_id", "")).strip(),
        metric_profile_id=str(suite.get("metric_profile_id", "")).strip(),
        frame_nodes=list(suite.get("frame_nodes") or []),
        frame_transform_rows=list(suite.get("frame_transform_rows") or []),
        graph_version=graph_version,
    )
    projected_cells = [dict(row) for row in list(projection_result.get("projected_cells") or [])]
    terrain_entries = _terrain_entries(projected_cells, suite_id=str(suite.get("suite_id", "")).strip())
    perceived_model = _perceived_model(
        truth_hash_anchor=scenario_truth_anchor,
        allow_geometry=True,
        diegetic=True,
    )
    perceived_model["diegetic_instruments"]["instrument.map_local"]["reading"]["entries"] = list(terrain_entries)
    perceived_model["diegetic_instruments"]["instrument.ground_scanner"]["reading"]["geometry_cell_states"] = [dict(row) for row in list(geometry_rows or [])]
    lens_request = build_lens_request(
        lens_request_id="lens_request.{}".format(str(suite.get("suite_id", "")).split(".")[-1]),
        lens_profile_id="lens.diegetic.map_local",
        included_layers=[
            "layer.terrain_stub",
            "layer.temperature",
            "layer.pollution",
            "layer.geometry_occupancy",
            "layer.infrastructure_stub",
            "layer.entity_markers_stub",
        ],
        extensions={"quantization_step": 25},
    )
    layer_sources = {
        "layer.temperature": {
            "source_kind": "field",
            "field_id": "field.temperature",
            "field_layer_rows": list(field_fixture.get("field_layers") or []),
            "field_cell_rows": list(field_fixture.get("field_cells") or []),
            "field_type_registry": _field_type_registry(),
            "field_binding_registry": _as_map(field_fixture.get("field_binding_registry")) or _field_binding_registry(),
            "interpolation_policy_registry": _as_map(field_fixture.get("interpolation_policy_registry")) or _interpolation_policy_registry(),
        },
        "layer.pollution": {
            "source_kind": "field",
            "field_id": _pollution_field_id(),
            "field_layer_rows": list(field_fixture.get("field_layers") or []),
            "field_cell_rows": list(field_fixture.get("field_cells") or []),
            "field_type_registry": _field_type_registry(),
            "field_binding_registry": _as_map(field_fixture.get("field_binding_registry")) or _field_binding_registry(),
            "interpolation_policy_registry": _as_map(field_fixture.get("interpolation_policy_registry")) or _interpolation_policy_registry(),
        },
        "layer.terrain_stub": {
            "source_kind": "terrain",
            "entries": terrain_entries,
        },
        "layer.geometry_occupancy": {
            "source_kind": "geometry_occupancy",
            "geometry_cell_states": [dict(row) for row in list(geometry_rows or [])],
        },
        "layer.infrastructure_stub": {
            "source_kind": "infrastructure",
            "rows": _marker_rows(goal_cell_key=_as_map(suite.get("goal_cell_key")), marker_id="marker.infrastructure"),
            "required_channels": ["ch.overlay.infrastructure"],
        },
        "layer.entity_markers_stub": {
            "source_kind": "entities",
            "rows": _marker_rows(goal_cell_key=_as_map(suite.get("goal_cell_key")), marker_id="marker.entity"),
            "required_entitlements": ["entitlement.debug_view"],
        },
    }
    view_artifact = build_projected_view_artifact(
        projection_request=projection_request,
        projection_result=projection_result,
        lens_request=lens_request,
        perceived_model=perceived_model,
        layer_source_payloads=layer_sources,
        authority_context=_authority_context(),
        topology_profile_id=str(suite.get("topology_profile_id", "")).strip(),
        partition_profile_id=str(suite.get("partition_profile_id", "")).strip(),
        metric_profile_id=str(suite.get("metric_profile_id", "")).strip(),
        frame_nodes=list(suite.get("frame_nodes") or []),
        frame_transform_rows=list(suite.get("frame_transform_rows") or []),
        graph_version=graph_version,
        truth_hash_anchor=scenario_truth_anchor,
    )
    cctv_delivery = {}
    if str(suite.get("view_type_id", "")).strip() == "view.cctv_stub":
        cctv_delivery = build_cctv_view_delivery(
            projected_view_artifact=view_artifact,
            created_tick=2,
            sender_subject_id="subject.camera.geo10",
            recipient_subject_id="subject.viewer.geo10",
            recipient_address={"address_kind": "subject.direct", "subject_id": "subject.viewer.geo10"},
            base_delay_ticks=2,
        )
    redaction_count = 0
    for row in list(view_artifact.get("rendered_cells") or []):
        for layer_value in _as_map(_as_map(row).get("layers")).values():
            if str(_as_map(layer_value).get("state", "")).strip() == "hidden":
                redaction_count += 1
    return {
        "projection_request": projection_request,
        "projection_result": projection_result,
        "lens_request": lens_request,
        "view_artifact": view_artifact,
        "cctv_delivery": cctv_delivery,
        "view_fingerprint": projected_view_fingerprint(view_artifact),
        "redaction_count": int(redaction_count),
    }


def _suite_metrics_and_pathing(
    *,
    suite: Mapping[str, object],
    scenario: Mapping[str, object],
) -> dict:
    from src.geo import (
        apply_floating_origin,
        build_path_request,
        choose_floating_origin_offset,
        frame_graph_hash,
        geo_geodesic,
        geo_neighbors,
        geo_path_query,
        metric_query_proof_surface,
        path_result_proof_surface,
        position_distance,
        traversal_policy_registry_hash,
    )
    from src.fields import field_sample_neighborhood, field_sample_position_ref
    from src.pollution.dispersion_engine import (
        evaluate_pollution_dispersion,
        pollution_deposition_hash_chain,
        pollution_field_hash_chain,
    )

    graph_hash = frame_graph_hash(
        frame_nodes=list(suite.get("frame_nodes") or []),
        frame_transform_rows=list(suite.get("frame_transform_rows") or []),
    )
    distance_probe = _metric_cache_probe(
        lambda: position_distance(
            _as_map(suite.get("camera_position_ref")),
            _as_map(suite.get("target_position_ref")),
            frame_nodes=list(suite.get("frame_nodes") or []),
            frame_transform_rows=list(suite.get("frame_transform_rows") or []),
            graph_version=graph_hash,
        )
    )
    geodesic_probe = _metric_cache_probe(
        lambda: geo_geodesic(
            _position_to_coords(_as_map(suite.get("camera_position_ref"))),
            _position_to_coords(_as_map(suite.get("target_position_ref"))),
            str(suite.get("topology_profile_id", "")).strip(),
            str(suite.get("metric_profile_id", "")).strip(),
        )
    )
    neighbor_probe = _metric_cache_probe(
        lambda: geo_neighbors(
            _as_map(suite.get("center_cell_key")),
            1,
            str(suite.get("topology_profile_id", "")).strip(),
            str(suite.get("metric_profile_id", "")).strip(),
            str(suite.get("partition_profile_id", "")).strip(),
        )
    )
    floating_origin_offset = choose_floating_origin_offset(
        _as_map(suite.get("camera_position_ref")),
        frame_nodes=list(suite.get("frame_nodes") or []),
        frame_transform_rows=list(suite.get("frame_transform_rows") or []),
        target_frame_id=str(_as_map(suite.get("camera_position_ref")).get("frame_id", "")).strip(),
        graph_version=graph_hash,
    )
    floating_origin_result = apply_floating_origin(
        _as_map(suite.get("target_position_ref")),
        _as_map(suite.get("camera_position_ref")),
        frame_nodes=list(suite.get("frame_nodes") or []),
        frame_transform_rows=list(suite.get("frame_transform_rows") or []),
        target_frame_id=str(_as_map(suite.get("camera_position_ref")).get("frame_id", "")).strip(),
        graph_version=graph_hash,
    )
    field_fixture = _as_map(suite.get("field_fixture"))
    field_position_sample = field_sample_position_ref(
        position_ref=_as_map(suite.get("target_position_ref")),
        target_frame_id=str(_as_map(suite.get("target_position_ref")).get("frame_id", "")).strip(),
        field_id="field.temperature",
        field_layer_rows=list(field_fixture.get("field_layers") or []),
        field_cell_rows=list(field_fixture.get("field_cells") or []),
        frame_nodes=list(suite.get("frame_nodes") or []),
        frame_transform_rows=list(suite.get("frame_transform_rows") or []),
        field_type_registry=_field_type_registry(),
        field_binding_registry=_as_map(field_fixture.get("field_binding_registry")) or _field_binding_registry(),
        interpolation_policy_registry=_as_map(field_fixture.get("interpolation_policy_registry")) or _interpolation_policy_registry(),
        graph_version=graph_hash,
    )
    field_neighborhood_sample = field_sample_neighborhood(
        field_id=_pollution_field_id(),
        center_cell_key=_as_map(suite.get("center_cell_key")),
        radius=1,
        field_layer_rows=list(field_fixture.get("field_layers") or []),
        field_cell_rows=list(field_fixture.get("field_cells") or []),
        field_type_registry=_field_type_registry(),
        field_binding_registry=_as_map(field_fixture.get("field_binding_registry")) or _field_binding_registry(),
        interpolation_policy_registry=_as_map(field_fixture.get("interpolation_policy_registry")) or _interpolation_policy_registry(),
        metric_profile_id=str(suite.get("metric_profile_id", "")).strip(),
    )
    pollution_fixture = _as_map(suite.get("pollution_fixture"))
    pollution_result = evaluate_pollution_dispersion(
        current_tick=1,
        pollutant_types_by_id=_as_map(pollution_fixture.get("pollutant_types_by_id")),
        pollution_policies_by_id=_as_map(pollution_fixture.get("pollution_policies_by_id")),
        decay_models_by_id=_as_map(pollution_fixture.get("decay_models_by_id")),
        pollution_source_event_rows=list(pollution_fixture.get("pollution_source_event_rows") or []),
        processed_source_event_ids=[],
        field_cell_rows=list(field_fixture.get("field_cells") or []),
        neighbor_map_by_cell={
            _cell_alias(_as_map(suite.get("center_cell_key"))): [_cell_alias(_as_map(row)) for row in list(suite.get("neighbor_cell_keys") or [])]
        },
        wind_field_id="field.wind",
        max_cell_updates_per_tick=32,
    )
    traversal_registry = _path_policy_registry(int(max(1, _as_int(_as_map(scenario.get("budgets")).get("max_path_expansions", 48), 48))))
    path_request = build_path_request(
        request_id="path_request.{}".format(str(suite.get("suite_id", "")).split(".")[-1]),
        start_ref={"geo_cell_key": dict(_as_map(suite.get("center_cell_key")))},
        goal_ref={"geo_cell_key": dict(_as_map(suite.get("goal_cell_key")))},
        traversal_policy_id="traverse.geo10.stress",
        tier_mode="meso",
        extensions={
            "topology_profile_id": str(suite.get("topology_profile_id", "")).strip(),
            "metric_profile_id": str(suite.get("metric_profile_id", "")).strip(),
            "partition_profile_id": str(suite.get("partition_profile_id", "")).strip(),
            "max_expansions": int(max(1, _as_int(_as_map(scenario.get("budgets")).get("max_path_expansions", 48), 48))),
        },
    )
    path_result = geo_path_query(
        path_request,
        topology_profile_id=str(suite.get("topology_profile_id", "")).strip(),
        metric_profile_id=str(suite.get("metric_profile_id", "")).strip(),
        partition_profile_id=str(suite.get("partition_profile_id", "")).strip(),
        traversal_policy_registry_payload=traversal_registry,
        field_cost_data=_field_cost_data(
            field_fixture=field_fixture,
            center_cell_key=_as_map(suite.get("center_cell_key")),
            goal_cell_key=_as_map(suite.get("goal_cell_key")),
        ),
        infrastructure_overlay=_infrastructure_overlay(
            _as_map(suite.get("center_cell_key")),
            _as_map(suite.get("goal_cell_key")),
        ),
        shard_assignment=_shard_assignment(
            _as_map(suite.get("center_cell_key")),
            _as_map(suite.get("goal_cell_key")),
        ),
        frame_nodes=list(suite.get("frame_nodes") or []),
        frame_transform_rows=list(suite.get("frame_transform_rows") or []),
        graph_version=graph_hash,
    )
    metric_surface = metric_query_proof_surface(
        [
            distance_probe.get("first"),
            geodesic_probe.get("first"),
            neighbor_probe.get("first"),
        ]
    )
    path_surface = path_result_proof_surface([_as_map(path_result.get("path_result"))] if _as_map(path_result.get("path_result")) else [])
    pollution_surface = {
        "pollution_field_hash_chain": pollution_field_hash_chain(
            field_cell_rows=list(field_fixture.get("field_cells") or []),
            pollutant_types_by_id=_as_map(pollution_fixture.get("pollutant_types_by_id")),
        ),
        "pollution_deposition_hash_chain": pollution_deposition_hash_chain(
            pollution_result.get("deposition_rows")
        ),
        "dispersion_hash_chain": _hash_chain(
            pollution_result.get("dispersion_step_rows"),
            key_fn=lambda row: (
                int(_as_int(row.get("tick", 0), 0)),
                str(row.get("pollutant_id", "")),
                str(row.get("spatial_scope_id", "")),
            ),
        ),
    }
    return {
        "graph_hash": graph_hash,
        "distance_probe": distance_probe,
        "geodesic_probe": geodesic_probe,
        "neighbor_probe": neighbor_probe,
        "floating_origin_offset": floating_origin_offset,
        "floating_origin_result": floating_origin_result,
        "field_position_sample": field_position_sample,
        "field_neighborhood_sample": field_neighborhood_sample,
        "pollution_result": pollution_result,
        "path_request": path_request,
        "path_result": path_result,
        "metric_surface": metric_surface,
        "path_surface": path_surface,
        "pollution_surface": pollution_surface,
        "traversal_policy_registry_hash": traversal_policy_registry_hash(traversal_registry),
    }


def _suite_report(
    *,
    suite: Mapping[str, object],
    scenario: Mapping[str, object],
    truth_hash_anchor: str,
) -> dict:
    suite_metrics = _suite_metrics_and_pathing(suite=suite, scenario=scenario)
    geometry_data = _suite_geometry_and_compaction(suite=suite, scenario=scenario)
    view_data = _suite_projection_and_views(
        suite=suite,
        geometry_rows=geometry_data.get("geometry_rows"),
        scenario_truth_anchor=truth_hash_anchor,
    )
    world_overlay = _suite_worldgen_and_overlay(suite=suite, scenario=scenario)
    view_artifact = _as_map(view_data.get("view_artifact"))
    path_result = _as_map(suite_metrics.get("path_result"))
    geometry_surface = _as_map(geometry_data.get("geometry_surface"))
    compaction_result = _as_map(geometry_data.get("compaction_result"))
    replay_report = _as_map(geometry_data.get("replay_report"))
    rendered_cells = list(view_artifact.get("rendered_cells") or [])
    metrics = {
        "metric_query_count": 6,
        "metric_cache_hits": int(
            bool(_as_map(suite_metrics.get("distance_probe")).get("cache_hit"))
            + bool(_as_map(suite_metrics.get("geodesic_probe")).get("cache_hit"))
            + bool(_as_map(suite_metrics.get("neighbor_probe")).get("cache_hit"))
        ),
        "neighbor_enumeration_count": 1,
        "projection_view_cell_count": int(len(rendered_cells)),
        "lens_redaction_count": int(_as_int(view_data.get("redaction_count", 0), 0)),
        "path_expansions": int(_as_int(path_result.get("expanded_count", 0), 0)),
        "geometry_edit_event_count": int(len(list(geometry_data.get("geometry_edit_events") or []))),
        "overlay_merge_count": 1,
        "compaction_marker_count": int(len(list(_as_map(compaction_result.get("state")).get("compaction_markers") or []))),
    }
    metrics["metric_cache_hit_rate_permille"] = int((metrics["metric_cache_hits"] * 1000) // max(1, metrics["metric_query_count"]))
    assertions = {
        "bounded_iterations": metrics["projection_view_cell_count"] <= int(max(1, _as_int(_as_map(scenario.get("budgets")).get("max_projection_cells_per_view", 81), 81)))
        and metrics["path_expansions"] <= int(max(1, _as_int(_as_map(scenario.get("budgets")).get("max_path_expansions", 48), 48))),
        "no_truth_leaks_in_views": "truth_overlay" not in json.dumps(view_artifact, sort_keys=True),
        "stable_ids_under_overlays": bool(world_overlay.get("stable_identity_under_overlay")),
        "replay_from_anchor_matches": str(replay_report.get("result", "")).strip() == "complete",
        "render_rebasing_preserves_truth": str(_as_map(suite_metrics.get("floating_origin_result")).get("result", "")).strip() == "complete",
    }
    proof_summary = {
        "frame_graph_hash_chain": str(suite_metrics.get("graph_hash", "")).strip(),
        "metric_query_hash_chain": str(_as_map(suite_metrics.get("metric_surface")).get("deterministic_fingerprint", "")).strip(),
        "path_result_hash_chain": str(_as_map(suite_metrics.get("path_surface")).get("path_result_hash_chain", "")).strip(),
        "pollution_field_hash_chain": str(_as_map(suite_metrics.get("pollution_surface")).get("pollution_field_hash_chain", "")).strip(),
        "projection_view_fingerprint": str(view_data.get("view_fingerprint", "")).strip(),
        "geometry_state_hash_chain": str(geometry_surface.get("deterministic_fingerprint", "")).strip(),
        "geometry_edit_event_hash_chain": str(geometry_surface.get("geometry_edit_event_hash_chain", "")).strip(),
        "compaction_marker_hash_chain": str(_as_map(compaction_result.get("compaction_marker")).get("deterministic_fingerprint", "")).strip(),
        "worldgen_result_hash_chain": str(_as_map(world_overlay.get("worldgen_surface")).get("worldgen_result_hash_chain", "")).strip(),
        "overlay_manifest_hash": str(_as_map(world_overlay.get("overlay_surface")).get("overlay_manifest_hash", "")).strip(),
        "overlay_merge_result_hash_chain": str(_as_map(world_overlay.get("overlay_surface")).get("overlay_merge_result_hash_chain", "")).strip(),
        "cctv_delivery_fingerprint": str(_as_map(view_data.get("cctv_delivery")).get("deterministic_fingerprint", "")).strip(),
    }
    report = {
        "suite_id": str(suite.get("suite_id", "")).strip(),
        "topology_profile_id": str(suite.get("topology_profile_id", "")).strip(),
        "metric_profile_id": str(suite.get("metric_profile_id", "")).strip(),
        "partition_profile_id": str(suite.get("partition_profile_id", "")).strip(),
        "projection_profile_id": str(suite.get("projection_profile_id", "")).strip(),
        "view_type_id": str(suite.get("view_type_id", "")).strip(),
        "metrics": metrics,
        "assertions": assertions,
        "proof_summary": proof_summary,
        "metric_runtime": {
            "distance_query": _as_map(suite_metrics.get("distance_probe")).get("first"),
            "geodesic_query": _as_map(suite_metrics.get("geodesic_probe")).get("first"),
            "neighbor_query": _as_map(suite_metrics.get("neighbor_probe")).get("first"),
        },
        "path_result": path_result,
        "view_artifact_fingerprint": str(view_data.get("view_fingerprint", "")).strip(),
        "property_origin_report": _as_map(world_overlay.get("origin_report")),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def run_geo_stress_scenario(
    scenario: Mapping[str, object] | None = None,
    *,
    seed: int = DEFAULT_GEO10_SEED,
) -> dict:
    payload = dict(scenario or {})
    if not payload:
        payload = generate_geo_stress_scenario(seed=int(max(1, _as_int(seed, DEFAULT_GEO10_SEED))), include_cctv=True)
    suites = [dict(row) for row in list(payload.get("topology_suites") or []) if isinstance(row, Mapping)]
    truth_hash_anchor = canonical_sha256(
        {
            "scenario_id": str(payload.get("scenario_id", "")).strip(),
            "scenario_seed": int(max(0, _as_int(payload.get("scenario_seed", 0), 0))),
            "suite_fingerprints": [str(dict(row).get("deterministic_fingerprint", "")).strip() for row in suites],
        }
    )
    suite_reports = [
        _suite_report(
            suite=row,
            scenario=payload,
            truth_hash_anchor=truth_hash_anchor,
        )
        for row in sorted(suites, key=lambda item: str(item.get("suite_id", "")))
    ]
    aggregate_metrics = {
        "metric_query_count": int(sum(int(_as_int(_as_map(row.get("metrics")).get("metric_query_count", 0), 0)) for row in suite_reports)),
        "metric_cache_hits": int(sum(int(_as_int(_as_map(row.get("metrics")).get("metric_cache_hits", 0), 0)) for row in suite_reports)),
        "neighbor_enumeration_count": int(sum(int(_as_int(_as_map(row.get("metrics")).get("neighbor_enumeration_count", 0), 0)) for row in suite_reports)),
        "projection_view_cell_count": int(sum(int(_as_int(_as_map(row.get("metrics")).get("projection_view_cell_count", 0), 0)) for row in suite_reports)),
        "lens_redaction_count": int(sum(int(_as_int(_as_map(row.get("metrics")).get("lens_redaction_count", 0), 0)) for row in suite_reports)),
        "path_expansions": int(sum(int(_as_int(_as_map(row.get("metrics")).get("path_expansions", 0), 0)) for row in suite_reports)),
        "geometry_edit_event_count": int(sum(int(_as_int(_as_map(row.get("metrics")).get("geometry_edit_event_count", 0), 0)) for row in suite_reports)),
        "overlay_merge_count": int(sum(int(_as_int(_as_map(row.get("metrics")).get("overlay_merge_count", 0), 0)) for row in suite_reports)),
        "compaction_marker_count": int(sum(int(_as_int(_as_map(row.get("metrics")).get("compaction_marker_count", 0), 0)) for row in suite_reports)),
    }
    aggregate_metrics["metric_cache_hit_rate_permille"] = int(
        (aggregate_metrics["metric_cache_hits"] * 1000) // max(1, aggregate_metrics["metric_query_count"])
    )
    assertions = {
        "deterministic_outputs": True,
        "bounded_iterations": all(bool(_as_map(row.get("assertions")).get("bounded_iterations", False)) for row in suite_reports),
        "no_truth_leaks_in_views": all(bool(_as_map(row.get("assertions")).get("no_truth_leaks_in_views", False)) for row in suite_reports),
        "stable_ids_under_overlays": all(bool(_as_map(row.get("assertions")).get("stable_ids_under_overlays", False)) for row in suite_reports),
        "replay_from_anchor_matches": all(bool(_as_map(row.get("assertions")).get("replay_from_anchor_matches", False)) for row in suite_reports),
    }
    proof_summary = {
        "geo_profile_registry_hashes": _geo_profile_registry_hashes(),
        "suite_hashes": {
            str(row.get("suite_id", "")).strip(): dict(_as_map(row.get("proof_summary")))
            for row in suite_reports
        },
    }
    proof_summary["cross_platform_determinism_hash"] = canonical_sha256(
        {
            "suite_hashes": proof_summary["suite_hashes"],
            "aggregate_metrics": aggregate_metrics,
            "assertions": assertions,
        }
    )
    report = {
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "scenario_id": str(payload.get("scenario_id", "")).strip(),
        "scenario_seed": int(max(0, _as_int(payload.get("scenario_seed", 0), 0))),
        "truth_hash_anchor": truth_hash_anchor,
        "topology_suite_reports": suite_reports,
        "aggregate_metrics": aggregate_metrics,
        "assertions": assertions,
        "proof_summary": proof_summary,
        "expected_invariants_summary": _as_map(payload.get("expected_invariants_summary")),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def verify_geo_stress_scenario(
    scenario: Mapping[str, object] | None = None,
    *,
    seed: int = DEFAULT_GEO10_SEED,
) -> dict:
    first = run_geo_stress_scenario(scenario, seed=seed)
    second = run_geo_stress_scenario(copy.deepcopy(dict(scenario or {})) if scenario else None, seed=seed)
    stable = first == second
    report = dict(first)
    report["stable_across_repeated_runs"] = bool(stable)
    report["result"] = "complete" if stable and str(report.get("result", "")).strip() == "complete" else "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report

__all__ = [
    "DEFAULT_GEO10_SEED",
    "DEFAULT_OUTPUT_REL",
    "DEFAULT_REPORT_REL",
    "load_geo_stress_scenario",
    "run_geo_stress_scenario",
    "verify_geo_stress_scenario",
]

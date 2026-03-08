"""Bounded GEO reference evaluators for META-REF."""

from __future__ import annotations

from typing import Mapping

from src.geo import (
    build_default_overlay_manifest,
    build_effective_object_view,
    build_property_patch,
    geo_distance,
    geo_neighbors,
    merge_overlay_view,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _cell(*, topology_profile_id: str, chart_id: str, index_tuple: list[int]) -> dict:
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": str(topology_profile_id),
        "chart_id": str(chart_id),
        "index_tuple": [int(_as_int(item, 0)) for item in list(index_tuple)],
        "refinement_level": 0,
        "extensions": {},
    }


def _normalize_runtime_distance(case_id: str, payload: Mapping[str, object]) -> dict:
    error_bound = _as_map(payload.get("error_bound"))
    return {
        "case_id": str(case_id),
        "distance_mm": int(_as_int(payload.get("distance_mm", payload.get("distance_value", 0)), 0)),
        "error_bound_mm": int(_as_int(error_bound.get("value", payload.get("error_bound_mm", 0)), 0)),
        "result": str(payload.get("result", "")).strip(),
    }


def evaluate_reference_metric_distance_small(*, state_payload: Mapping[str, object] | None = None) -> dict:
    del state_payload
    cases = [
        {
            "case_id": "euclidean.r2.3_4_5",
            "pos_a": {"coords": [0, 0]},
            "pos_b": {"coords": [3000, 4000]},
            "topology_profile_id": "geo.topology.r2_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "expected_distance_mm": 5000,
        },
        {
            "case_id": "torus.r2.wrap_shortcut",
            "pos_a": {"coords": [999000, 0]},
            "pos_b": {"coords": [1000, 0]},
            "topology_profile_id": "geo.topology.torus_r2",
            "metric_profile_id": "geo.metric.torus_wrap",
            "expected_distance_mm": 2000,
        },
    ]
    runtime_rows = []
    reference_rows = []
    mismatches = []
    for row in cases:
        runtime = geo_distance(
            row["pos_a"],
            row["pos_b"],
            row["topology_profile_id"],
            row["metric_profile_id"],
        )
        runtime_row = _normalize_runtime_distance(str(row["case_id"]), runtime)
        reference_row = {
            "case_id": str(row["case_id"]),
            "distance_mm": int(_as_int(row["expected_distance_mm"], 0)),
            "error_bound_mm": 0,
            "result": "complete",
        }
        runtime_rows.append(runtime_row)
        reference_rows.append(reference_row)
        if runtime_row != reference_row:
            mismatches.append("distance mismatch for {}".format(str(row["case_id"])))
    runtime_out = {
        "fixture_kind": "fixture.geo.metric_distance_small.v1",
        "cases": runtime_rows,
        "output_hash": canonical_sha256(runtime_rows),
    }
    reference_out = {
        "fixture_kind": "fixture.geo.metric_distance_small.v1",
        "cases": reference_rows,
        "output_hash": canonical_sha256(reference_rows),
    }
    return {
        "runtime": runtime_out,
        "reference": reference_out,
        "match": not mismatches and runtime_out["output_hash"] == reference_out["output_hash"],
        "discrepancy_summary": "" if not mismatches else mismatches[0],
    }


def _normalize_neighbor_rows(rows: object) -> list[dict]:
    normalized = []
    for row in list(rows or []):
        payload = _as_map(row)
        normalized.append(
            {
                "chart_id": str(payload.get("chart_id", "")).strip(),
                "index_tuple": [int(_as_int(item, 0)) for item in list(payload.get("index_tuple") or [])],
                "refinement_level": int(max(0, _as_int(payload.get("refinement_level", 0), 0))),
                "topology_profile_id": str(payload.get("topology_profile_id", "")).strip(),
            }
        )
    return sorted(
        normalized,
        key=lambda row: (
            str(row.get("chart_id", "")),
            tuple(int(item) for item in list(row.get("index_tuple") or [])),
            int(_as_int(row.get("refinement_level", 0), 0)),
            str(row.get("topology_profile_id", "")),
        ),
    )


def evaluate_reference_neighborhood_small(*, state_payload: Mapping[str, object] | None = None) -> dict:
    del state_payload
    cases = [
        {
            "case_id": "r2.cardinal",
            "center": _cell(topology_profile_id="geo.topology.r2_infinite", chart_id="chart.global.r2", index_tuple=[0, 0]),
            "topology_profile_id": "geo.topology.r2_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "expected_neighbors": [
                _cell(topology_profile_id="geo.topology.r2_infinite", chart_id="chart.global.r2", index_tuple=[-1, 0]),
                _cell(topology_profile_id="geo.topology.r2_infinite", chart_id="chart.global.r2", index_tuple=[0, -1]),
                _cell(topology_profile_id="geo.topology.r2_infinite", chart_id="chart.global.r2", index_tuple=[0, 1]),
                _cell(topology_profile_id="geo.topology.r2_infinite", chart_id="chart.global.r2", index_tuple=[1, 0]),
            ],
        },
        {
            "case_id": "torus.wrap",
            "center": _cell(topology_profile_id="geo.topology.torus_r2", chart_id="chart.global.r2", index_tuple=[99, 0]),
            "topology_profile_id": "geo.topology.torus_r2",
            "metric_profile_id": "geo.metric.torus_wrap",
            "expected_neighbors": [
                _cell(topology_profile_id="geo.topology.torus_r2", chart_id="chart.global.r2", index_tuple=[0, 0]),
                _cell(topology_profile_id="geo.topology.torus_r2", chart_id="chart.global.r2", index_tuple=[98, 0]),
                _cell(topology_profile_id="geo.topology.torus_r2", chart_id="chart.global.r2", index_tuple=[99, 1]),
                _cell(topology_profile_id="geo.topology.torus_r2", chart_id="chart.global.r2", index_tuple=[99, 99]),
            ],
        },
    ]
    runtime_rows = []
    reference_rows = []
    mismatches = []
    for row in cases:
        runtime = geo_neighbors(
            row["center"],
            1,
            row["topology_profile_id"],
            row["metric_profile_id"],
            "geo.partition.grid_zd",
        )
        runtime_row = {
            "case_id": str(row["case_id"]),
            "neighbors": _normalize_neighbor_rows(runtime.get("neighbors")),
            "result": str(runtime.get("result", "")).strip(),
        }
        reference_row = {
            "case_id": str(row["case_id"]),
            "neighbors": _normalize_neighbor_rows(row["expected_neighbors"]),
            "result": "complete",
        }
        runtime_rows.append(runtime_row)
        reference_rows.append(reference_row)
        if runtime_row != reference_row:
            mismatches.append("neighbor mismatch for {}".format(str(row["case_id"])))
    runtime_out = {
        "fixture_kind": "fixture.geo.neighborhood_small.v1",
        "cases": runtime_rows,
        "output_hash": canonical_sha256(runtime_rows),
    }
    reference_out = {
        "fixture_kind": "fixture.geo.neighborhood_small.v1",
        "cases": reference_rows,
        "output_hash": canonical_sha256(reference_rows),
    }
    return {
        "runtime": runtime_out,
        "reference": reference_out,
        "match": not mismatches and runtime_out["output_hash"] == reference_out["output_hash"],
        "discrepancy_summary": "" if not mismatches else mismatches[0],
    }


def evaluate_reference_overlay_merge_small(*, state_payload: Mapping[str, object] | None = None) -> dict:
    del state_payload
    universe_id = "universe.ref.geo.overlay"
    pack_lock_hash = "e" * 64
    base_objects = [
        build_effective_object_view(
            object_id="object.base.earth",
            object_kind_id="kind.planet",
            properties={"display_name": "Procedural Earth", "radius_km": 6300},
            extensions={"source": "META-REF0"},
        )
    ]
    manifest = build_default_overlay_manifest(
        universe_id=universe_id,
        pack_lock_hash=pack_lock_hash,
        save_id="save.ref.geo.overlay",
        generator_version_id="gen.v0_stub",
        official_layer_specs=[
            {
                "layer_id": "official.reality.earth",
                "pack_hash": "f" * 64,
                "pack_id": "pack.official.earth",
                "signature_status": "official",
            }
        ],
        mod_layer_specs=[
            {
                "layer_id": "mod.alpha",
                "pack_hash": "a" * 64,
                "pack_id": "pack.mod.alpha",
                "signature_status": "unsigned",
            }
        ],
        overlay_policy_id="overlay.default",
    )
    add_cell = _cell(topology_profile_id="geo.topology.r2_infinite", chart_id="chart.global.r2", index_tuple=[4, 2])
    property_patches = [
        build_property_patch(
            target_object_id="object.base.earth",
            property_path="display_name",
            operation="set",
            value="Earth",
            originating_layer_id="official.reality.earth",
        ),
        build_property_patch(
            target_object_id="object.base.earth",
            property_path="radius_km",
            operation="set",
            value=6371,
            originating_layer_id="official.reality.earth",
        ),
        build_property_patch(
            target_object_id="object.base.earth",
            property_path="display_name",
            operation="set",
            value="Gaia",
            originating_layer_id="mod.alpha",
        ),
        build_property_patch(
            target_object_id="object.base.earth",
            property_path="display_name",
            operation="set",
            value="Player Earth",
            originating_layer_id="save.patch",
        ),
        build_property_patch(
            target_object_id="object.overlay.relay",
            property_path="display_name",
            operation="set",
            value="Relay",
            originating_layer_id="mod.alpha",
            extensions={"object_kind_id": "kind.structure", "geo_cell_key": add_cell},
        ),
    ]
    runtime = merge_overlay_view(
        base_objects=base_objects,
        overlay_manifest=manifest,
        property_patches=property_patches,
        resolved_packs=[
            {"pack_id": "pack.official.earth", "canonical_hash": "f" * 64, "signature_status": "official"},
            {"pack_id": "pack.mod.alpha", "canonical_hash": "a" * 64, "signature_status": "unsigned"},
        ],
        expected_pack_lock_hash=pack_lock_hash,
        overlay_policy_id="overlay.default",
    )
    runtime_views = [
        {
            "object_id": str(_as_map(row).get("object_id", "")).strip(),
            "object_kind_id": str(_as_map(row).get("object_kind_id", "")).strip(),
            "properties": dict(_as_map(row).get("properties")),
        }
        for row in list(runtime.get("effective_object_views") or [])
        if str(_as_map(row).get("object_id", "")).strip()
    ]
    runtime_views = sorted(runtime_views, key=lambda row: str(row.get("object_id", "")))
    reference_views = [
        {
            "object_id": "object.base.earth",
            "object_kind_id": "kind.planet",
            "properties": {"display_name": "Player Earth", "radius_km": 6371},
        },
        {
            "object_id": "object.overlay.relay",
            "object_kind_id": "kind.structure",
            "properties": {"display_name": "Relay"},
        },
    ]
    reference_views = sorted(reference_views, key=lambda row: str(row.get("object_id", "")))
    runtime_out = {
        "fixture_kind": "fixture.geo.overlay_merge_small.v1",
        "effective_object_views": runtime_views,
        "output_hash": canonical_sha256(runtime_views),
    }
    reference_out = {
        "fixture_kind": "fixture.geo.overlay_merge_small.v1",
        "effective_object_views": reference_views,
        "output_hash": canonical_sha256(reference_views),
    }
    mismatch = runtime_views != reference_views
    return {
        "runtime": runtime_out,
        "reference": reference_out,
        "match": (not mismatch) and runtime_out["output_hash"] == reference_out["output_hash"],
        "discrepancy_summary": "" if not mismatch else "overlay merge small mismatch",
    }


__all__ = [
    "evaluate_reference_metric_distance_small",
    "evaluate_reference_neighborhood_small",
    "evaluate_reference_overlay_merge_small",
]

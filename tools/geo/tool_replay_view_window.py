#!/usr/bin/env python3
"""Verify GEO-5 projected views replay deterministically under lens gating."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.geo import (  # noqa: E402
    build_cctv_view_delivery,
    build_lens_request,
    build_projected_view_artifact,
    build_projected_view_layer_buffers,
    build_projection_request,
    build_position_ref,
    lens_layer_registry_hash,
    project_view_cells,
    projected_view_fingerprint,
    projection_profile_registry_hash,
    render_projected_view_ascii,
    view_type_registry_hash,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _projection_fixture_request() -> dict:
    origin = build_position_ref(
        object_id="object.camera.geo5",
        frame_id="frame.surface_local",
        local_position=[0, 0, 0],
        extensions={"source": "GEO5-7"},
    )
    return build_projection_request(
        request_id="projection_request.geo5.replay",
        projection_profile_id="geo.projection.ortho_2d",
        origin_position_ref=origin,
        extent_spec={"radius_cells": 1, "axis_order": ["x", "y"]},
        resolution_spec={"width": 3, "height": 3},
        extensions={
            "view_type_id": "view.map_ortho",
            "topology_profile_id": "geo.topology.r3_infinite",
            "partition_profile_id": "geo.partition.grid_zd",
            "chart_id": "chart.global.r3",
        },
    )


def _layer_source_payloads(center_cell_key: dict) -> dict:
    return {
        "layer.temperature": {
            "field_id": "field.temperature",
            "field_layer_rows": [
                {
                    "field_id": "field.temperature",
                    "field_type_id": "field.temperature",
                    "spatial_scope_id": "scope.geo5.replay",
                    "resolution_level": "macro",
                    "update_policy_id": "field.static_default",
                    "extensions": {
                        "topology_profile_id": "geo.topology.r3_infinite",
                        "partition_profile_id": "geo.partition.grid_zd",
                        "chart_id": "chart.global.r3",
                    },
                }
            ],
            "field_cell_rows": [
                {
                    "field_id": "field.temperature",
                    "cell_id": "cell.0.0.0",
                    "value": 37,
                    "last_updated_tick": 0,
                    "extensions": {"geo_cell_key": dict(center_cell_key)},
                }
            ],
        },
        "layer.terrain_stub": {
            "source_kind": "terrain",
            "entries": [
                {
                    "cell_key": canonical_sha256(center_cell_key),
                    "terrain_class": "ridge",
                }
            ],
        },
        "layer.infrastructure_stub": {
            "source_kind": "infrastructure",
            "required_channels": ["ch.diegetic.infra"],
            "rows": [{"geo_cell_key": dict(center_cell_key), "marker": "relay"}],
        },
    }


def _run_once() -> dict:
    projection_request = _projection_fixture_request()
    projection_result = project_view_cells(
        projection_request,
        topology_profile_id="geo.topology.r3_infinite",
        partition_profile_id="geo.partition.grid_zd",
        metric_profile_id="geo.metric.euclidean",
    )
    projected_cells = list(projection_result.get("projected_cells") or [])
    center_cell_key = dict(projected_cells[4].get("geo_cell_key") or {})
    lens_request = build_lens_request(
        lens_request_id="lens_request.geo5.replay",
        lens_profile_id="lens.diegetic.sensor",
        included_layers=[
            "layer.temperature",
            "layer.terrain_stub",
            "layer.infrastructure_stub",
        ],
        extensions={"quantization_step": 10},
    )
    perceived_model = {
        "lens_id": "lens.diegetic.sensor",
        "metadata": {
            "lens_type": "diegetic",
            "epistemic_policy_id": "epistemic.local_map",
        },
        "channels": ["ch.diegetic.map_local"],
        "diegetic_instruments": {
            "instrument.map_local": {
                "reading": {
                    "entries": [
                        {
                            "cell_key": canonical_sha256(center_cell_key),
                            "terrain_class": "ridge",
                        }
                    ]
                }
            }
        },
        "truth_overlay": {"state_hash_anchor": "truth.anchor.geo5.replay"},
    }
    view_artifact = build_projected_view_artifact(
        projection_result=projection_result,
        lens_request=lens_request,
        perceived_model=perceived_model,
        layer_source_payloads=_layer_source_payloads(center_cell_key),
        authority_context={"entitlements": []},
        truth_hash_anchor="truth.anchor.geo5.replay",
    )
    ascii_payload = render_projected_view_ascii(
        view_artifact,
        preferred_layer_order=["layer.infrastructure_stub", "layer.terrain_stub", "layer.temperature"],
    )
    layer_buffers = build_projected_view_layer_buffers(view_artifact)
    cctv_delivery = build_cctv_view_delivery(
        projected_view_artifact=view_artifact,
        created_tick=12,
        sender_subject_id="subject.camera.geo5",
        recipient_subject_id="subject.viewer.geo5",
        recipient_address={"address_kind": "subject.direct", "subject_id": "subject.viewer.geo5"},
        base_delay_ticks=2,
    )
    return {
        "projection_request_hash": str(projection_result.get("projection_request_hash", "")).strip(),
        "projected_cell_count": len(projected_cells),
        "view_fingerprint": projected_view_fingerprint(view_artifact),
        "ascii_grid": str(ascii_payload.get("ascii_grid", "")),
        "layer_buffer_hash": canonical_sha256(dict(layer_buffers)),
        "cctv_delivery_fingerprint": str(cctv_delivery.get("deterministic_fingerprint", "")).strip(),
        "projection_profile_registry_hash": projection_profile_registry_hash(),
        "lens_layer_registry_hash": lens_layer_registry_hash(),
        "view_type_registry_hash": view_type_registry_hash(),
    }


def verify_view_window() -> dict:
    first = _run_once()
    second = _run_once()
    stable = first == second
    report = {
        "result": "complete" if stable else "violation",
        "projection_profile_registry_hash": projection_profile_registry_hash(),
        "lens_layer_registry_hash": lens_layer_registry_hash(),
        "view_type_registry_hash": view_type_registry_hash(),
        "observed": first,
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-5 view replay determinism.")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_view_window()
    output_path = str(args.output_path or "").strip()
    if output_path:
        abs_path = os.path.normpath(os.path.abspath(output_path))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

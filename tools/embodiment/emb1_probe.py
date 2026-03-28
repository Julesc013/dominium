"""Deterministic EMB-1 toolbelt probe helpers."""

from __future__ import annotations

import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from embodiment import (  # noqa: E402
    build_cut_trench_task,
    build_fill_at_cursor_task,
    build_logic_probe_task,
    build_logic_trace_task,
    build_mine_at_cursor_task,
    build_scan_result,
    build_teleport_tool_surface,
    build_toolbelt_availability_surface,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _selection() -> dict:
    return {
        "object_id": "tile.earth.sample.001",
        "position_ref": {"x": 1200, "y": -400, "z": 300},
        "geo_cell_key": {
            "chart_id": "atlas.north",
            "refinement_level": 3,
            "index_tuple": [12, 8, 0],
            "extensions": {"legacy_cell_alias": "atlas.north.12.8"},
        },
        "tile_cell_key": {
            "chart_id": "atlas.north",
            "refinement_level": 3,
            "index_tuple": [12, 8, 0],
            "extensions": {"legacy_cell_alias": "atlas.north.12.8"},
        },
    }


def _inspection_snapshot() -> dict:
    return {
        "target_payload": {
            "target_id": "tile.earth.sample.001",
            "position_ref": {"x": 1200, "y": -400, "z": 300},
            "row": {
                "object_kind_id": "kind.surface_tile",
                "surface_tile_artifact": {
                    "tile_object_id": "tile.earth.sample.001",
                    "planet_object_id": "obj.sol.earth",
                    "tile_cell_key": _selection()["tile_cell_key"],
                    "material_baseline_id": "material.water",
                    "biome_stub_id": "biome.ocean",
                    "river_flag": True,
                    "flow_target_tile_key": {
                        "chart_id": "atlas.north",
                        "refinement_level": 3,
                        "index_tuple": [12, 9, 0],
                    },
                    "elevation_params_ref": {"height_proxy": 275},
                    "extensions": {
                        "lake_flag": False,
                        "hydrology_structure_kind": "river",
                        "biome_overlay_tags": ["river"],
                    },
                },
                "geometry_cell_state": {
                    "geometry_cell_id": "geo.cell.sample.001",
                    "occupancy_class": "occupied",
                    "material_id": "material.soil_fill",
                },
                "summary_sections": {
                    "logic.network": {"status": "idle"},
                    "system.capsule": {"capsule_id": "capsule.sample"},
                },
            },
        }
    }


def _field_values() -> dict:
    return {
        "temperature": 287,
        "daylight": 640,
        "tide_height_proxy": 14,
        "wind_vector": {"x": 30, "y": -10, "z": 0},
        "pollution": 3,
    }


def _property_origin_result() -> dict:
    return {
        "report": {
            "current_layer_id": "overlay.layer.sol_pin_minimal",
            "prior_value_chain": [{"layer_id": "base.procedural", "value": 275}],
        }
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.lab_freecam",
        "entitlements": [
            "session.boot",
            "entitlement.inspect",
            "entitlement.control.admin",
            "entitlement.teleport",
            "entitlement.tool.equip",
            "entitlement.tool.use",
            "entitlement.observer.truth",
            "ent.tool.terrain_edit",
            "ent.tool.scan",
            "ent.tool.logic_probe",
            "ent.tool.logic_trace",
            "ent.tool.teleport",
        ],
        "privilege_level": "operator",
        "epistemic_scope": {"scope_id": "epistemic.admin_full", "visibility_level": "nondiegetic"},
    }


def build_tool_session_report(repo_root: str) -> dict:
    selection = _selection()
    authority_context = _authority_context()
    inspection_snapshot = _inspection_snapshot()
    field_values = _field_values()
    property_origin_result = _property_origin_result()
    payload = {
        "availability": build_toolbelt_availability_surface(
            authority_context=authority_context,
            has_physical_access=True,
        ),
        "mine": build_mine_at_cursor_task(
            authority_context=authority_context,
            subject_id="subject.player",
            selection=selection,
            volume_amount=3,
        ),
        "fill": build_fill_at_cursor_task(
            authority_context=authority_context,
            subject_id="subject.player",
            selection=selection,
            volume_amount=2,
            material_id="material.soil_fill",
        ),
        "cut": build_cut_trench_task(
            authority_context=authority_context,
            subject_id="subject.player",
            path_stub=[selection["geo_cell_key"]],
            volume_amount=1,
            selection=selection,
        ),
        "scan": build_scan_result(
            authority_context=authority_context,
            selection=selection,
            inspection_snapshot=inspection_snapshot,
            field_values=field_values,
            property_origin_result=property_origin_result,
            has_physical_access=True,
        ),
        "probe": build_logic_probe_task(
            authority_context=authority_context,
            subject_id="net.logic.sample",
            measurement_point_id="measure.logic.signal",
            network_id="net.logic.sample",
            element_id="inst.logic.and.1",
            port_id="out.q",
        ),
        "trace": build_logic_trace_task(
            authority_context=authority_context,
            subject_id="net.logic.sample",
            measurement_point_ids=["measure.logic.signal"],
            targets=[
                {
                    "subject_id": "net.logic.sample",
                    "network_id": "net.logic.sample",
                    "element_id": "inst.logic.and.1",
                    "port_id": "out.q",
                    "measurement_point_id": "measure.logic.signal",
                }
            ],
            current_tick=7,
            duration_ticks=40,
        ),
        "teleport": build_teleport_tool_surface(
            repo_root=repo_root,
            authority_context=authority_context,
            command="/tp earth",
            universe_seed="0",
            authority_mode="dev",
            profile_bundle_path=os.path.join("profiles", "bundles", "bundle.mvp_default.json"),
            pack_lock_path=os.path.join("locks", "pack_lock.mvp_default.json"),
            teleport_counter=1,
            candidate_system_rows=[],
            surface_target_cell_key=selection["geo_cell_key"],
            current_tick=7,
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def verify_tool_session_replay(repo_root: str) -> dict:
    first = build_tool_session_report(repo_root)
    second = build_tool_session_report(repo_root)
    return {
        "result": "complete" if dict(first) == dict(second) else "refused",
        "first_fingerprint": str(first.get("deterministic_fingerprint", "")).strip(),
        "second_fingerprint": str(second.get("deterministic_fingerprint", "")).strip(),
        "match": bool(dict(first) == dict(second)),
        "deterministic_fingerprint": canonical_sha256(
            {
                "first": str(first.get("deterministic_fingerprint", "")).strip(),
                "second": str(second.get("deterministic_fingerprint", "")).strip(),
                "match": bool(dict(first) == dict(second)),
            }
        ),
    }


__all__ = [
    "build_tool_session_report",
    "verify_tool_session_replay",
]

"""Shared EMB-1 toolbelt TestX fixtures."""

from __future__ import annotations


def authority_context(*, entitlements: list[str] | None = None, privilege_level: str = "operator") -> dict:
    rows = sorted(set(["session.boot", "entitlement.inspect"] + [str(item).strip() for item in list(entitlements or []) if str(item).strip()]))
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.lab_freecam",
        "entitlements": rows,
        "privilege_level": str(privilege_level),
        "epistemic_scope": {"scope_id": "epistemic.admin_full", "visibility_level": "nondiegetic"},
    }


def selection() -> dict:
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


def inspection_snapshot() -> dict:
    return {
        "target_payload": {
            "target_id": "tile.earth.sample.001",
            "position_ref": {"x": 1200, "y": -400, "z": 300},
            "row": {
                "object_kind_id": "kind.surface_tile",
                "surface_tile_artifact": {
                    "tile_object_id": "tile.earth.sample.001",
                    "planet_object_id": "obj.sol.earth",
                    "tile_cell_key": selection()["tile_cell_key"],
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
            },
        }
    }


def field_values() -> dict:
    return {
        "temperature": 287,
        "daylight": 640,
        "tide_height_proxy": 14,
        "wind_vector": {"x": 30, "y": -10, "z": 0},
        "pollution": 3,
    }


def property_origin_result() -> dict:
    return {
        "report": {
            "current_layer_id": "overlay.layer.sol_pin_minimal",
            "prior_value_chain": [{"layer_id": "base.procedural", "value": 275}],
        }
    }


def tool_session_report(repo_root: str) -> dict:
    from tools.embodiment.emb1_probe import build_tool_session_report

    return build_tool_session_report(repo_root)

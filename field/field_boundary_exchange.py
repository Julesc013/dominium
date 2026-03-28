"""Deterministic GEO-4 shard-safe field boundary exchange helpers."""

from __future__ import annotations

from typing import Dict, Mapping, Sequence

from fields import get_field_value, normalize_field_sample_rows
from interior.compartment_flow_builder import normalize_portal_flow_params
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _vector3_int(value: object) -> dict:
    payload = _as_map(value)
    return {
        "x": int(_as_int(payload.get("x", 0), 0)),
        "y": int(_as_int(payload.get("y", 0), 0)),
        "z": int(_as_int(payload.get("z", 0), 0)),
    }


def exchange_field_boundary_values(
    *,
    current_tick: int,
    process_id: str,
    selected_graph: Mapping[str, object] | None,
    portal_rows: Sequence[Mapping[str, object]] | object,
    portal_flow_params: Sequence[Mapping[str, object]] | object,
    field_layers: object,
    field_cells: object,
    field_type_registry: Mapping[str, object] | None = None,
    field_binding_registry: Mapping[str, object] | None = None,
    interpolation_policy_registry: Mapping[str, object] | None = None,
    owner_vehicle_id: str = "",
    owner_vehicle_position_mm: Mapping[str, object] | None = None,
    owner_motion_tier: str = "macro",
    owner_vehicle_speed_mm_per_tick: int = 0,
    field_boundary_by_portal: Mapping[str, object] | None = None,
) -> dict:
    graph_row = dict(selected_graph or {})
    portal_rows_by_id = dict(
        (
            str(row.get("portal_id", "")).strip(),
            dict(row),
        )
        for row in list(portal_rows or [])
        if isinstance(row, Mapping) and str(row.get("portal_id", "")).strip()
    )
    portal_params_by_id = dict(
        (
            str(row.get("portal_id", "")).strip(),
            dict(row),
        )
        for row in list(portal_flow_params or [])
        if isinstance(row, Mapping) and str(row.get("portal_id", "")).strip()
    )
    owner_position = _vector3_int(owner_vehicle_position_mm)
    boundary_inputs = _as_map(field_boundary_by_portal)
    sample_cache: Dict[str, dict] = {}

    for portal_id in sorted(set(str(item).strip() for item in list(graph_row.get("portals") or []) if str(item).strip())):
        portal_row = dict(portal_rows_by_id.get(portal_id) or {})
        portal_ext = _as_map(portal_row.get("extensions"))
        explicit_boundary = _as_map(boundary_inputs.get(portal_id))

        sample_position = {}
        field_cell_id = str(portal_ext.get("field_cell_id", "") or explicit_boundary.get("field_cell_id", "")).strip()
        field_geo_cell_key = _as_map(portal_ext.get("field_geo_cell_key")) or _as_map(explicit_boundary.get("field_geo_cell_key"))
        if field_cell_id:
            sample_position["cell_id"] = field_cell_id
        if field_geo_cell_key:
            sample_position["geo_cell_key"] = dict(field_geo_cell_key)

        position_mm = _vector3_int(portal_ext.get("position_mm"))
        if position_mm:
            sample_position["position_mm"] = {
                "x": int(owner_position.get("x", 0)) + int(position_mm.get("x", 0)),
                "y": int(owner_position.get("y", 0)) + int(position_mm.get("y", 0)),
                "z": int(owner_position.get("z", 0)) + int(position_mm.get("z", 0)),
            }
        elif owner_position:
            sample_position["position_mm"] = dict(owner_position)

        sampled_by_field = {}
        for field_id in ("field.temperature", "field.moisture", "field.wind", "field.visibility"):
            sampled_by_field[field_id] = get_field_value(
                spatial_position=sample_position,
                field_id=field_id,
                field_layer_rows=field_layers,
                field_cell_rows=field_cells,
                field_type_registry=field_type_registry,
                field_binding_registry=field_binding_registry,
                interpolation_policy_registry=interpolation_policy_registry,
                tick=int(current_tick),
                spatial_node_id=portal_id,
                sample_cache=sample_cache,
            )

        temperature_sample = dict(sampled_by_field.get("field.temperature") or {})
        moisture_sample = dict(sampled_by_field.get("field.moisture") or {})
        wind_sample = dict(sampled_by_field.get("field.wind") or {})
        visibility_sample = dict(sampled_by_field.get("field.visibility") or {})

        boundary_temperature = int(_as_int(temperature_sample.get("value", 20), 20))
        boundary_moisture = int(max(0, _as_int(moisture_sample.get("value", 0), 0)))
        boundary_visibility = int(max(0, _as_int(visibility_sample.get("value", 1000), 1000)))
        wind_vector = _vector3_int(wind_sample.get("value"))
        wind_magnitude = int(
            abs(int(_as_int(wind_vector.get("x", 0), 0)))
            + abs(int(_as_int(wind_vector.get("y", 0), 0)))
            + abs(int(_as_int(wind_vector.get("z", 0), 0)))
        )
        ram_air_boost = 0
        if str(owner_vehicle_id or "").strip() and str(owner_motion_tier or "").strip() == "micro":
            ram_air_boost = int(min(2000, max(0, int(_as_int(owner_vehicle_speed_mm_per_tick, 0)) // 4)))
        wind_boost = int(min(2000, max(0, (wind_magnitude // 2) + int(ram_air_boost))))

        base_row = dict(
            portal_params_by_id.get(portal_id)
            or {
                "schema_version": "1.0.0",
                "portal_id": portal_id,
                "conductance_air": 0,
                "conductance_water": 0,
                "conductance_smoke": 0,
                "sealing_coefficient": 0,
                "open_state_multiplier": 1000,
                "extensions": {},
            }
        )
        base_ext = _as_map(base_row.get("extensions"))
        existing_boundary = _as_map(base_ext.get("field_boundary"))
        base_conductance_air = int(
            max(
                0,
                _as_int(
                    existing_boundary.get("base_conductance_air", base_row.get("conductance_air", 0)),
                    _as_int(base_row.get("conductance_air", 0), 0),
                ),
            )
        )
        base_row["conductance_air"] = int(base_conductance_air + wind_boost)
        base_ext["field_boundary"] = {
            "temperature": int(boundary_temperature),
            "moisture": int(boundary_moisture),
            "visibility": int(boundary_visibility),
            "wind_vector": dict(wind_vector),
            "wind_magnitude": int(wind_magnitude),
            "wind_boost_air_conductance": int(wind_boost),
            "ram_air_boost_air_conductance": int(ram_air_boost),
            "vehicle_id": str(owner_vehicle_id or "").strip() or None,
            "vehicle_motion_tier": str(owner_motion_tier or "").strip() or None,
            "vehicle_speed_mm_per_tick": int(_as_int(owner_vehicle_speed_mm_per_tick, 0))
            if str(owner_vehicle_id or "").strip()
            else None,
            "sample_position_mm": dict(sample_position.get("position_mm") or {}) if isinstance(sample_position.get("position_mm"), Mapping) else None,
            "base_conductance_air": int(base_conductance_air),
            "field_sampled_cell_ids": dict(
                (field_id, str(dict(sampled_by_field.get(field_id) or {}).get("sampled_cell_id", "")).strip())
                for field_id in sorted(sampled_by_field.keys())
            ),
            "field_sampled_geo_cell_keys": dict(
                (
                    field_id,
                    _as_map(dict(sampled_by_field.get(field_id) or {}).get("sampled_geo_cell_key")),
                )
                for field_id in sorted(sampled_by_field.keys())
            ),
            "source_process_id": str(process_id or "").strip(),
            "source_tick": int(max(0, _as_int(current_tick, 0))),
        }
        base_row["extensions"] = base_ext
        portal_params_by_id[portal_id] = normalize_portal_flow_params(base_row)

    updated_portal_flow_params = [dict(portal_params_by_id[key]) for key in sorted(portal_params_by_id.keys())]
    boundary_sample_rows = normalize_field_sample_rows(
        [dict(row) for row in list(sample_cache.values()) if isinstance(row, Mapping)]
    )
    updated_field_ids = sorted(
        set(
            str(row.get("field_id", "")).strip()
            for row in list(boundary_sample_rows or [])
            if isinstance(row, Mapping) and str(row.get("field_id", "")).strip()
        )
    )
    out = {
        "portal_flow_params": updated_portal_flow_params,
        "field_sample_rows": boundary_sample_rows,
        "updated_field_ids": updated_field_ids,
        "boundary_portal_count": int(
            len([token for token in list(graph_row.get("portals") or []) if str(token).strip()])
        ),
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


__all__ = ["exchange_field_boundary_values"]

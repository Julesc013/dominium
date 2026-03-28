"""Deterministic EMB-1 scanner summaries over derived surfaces only."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from .toolbelt_engine import evaluate_tool_access


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _quantize(value: object, quantum: int) -> int | None:
    if value is None:
        return None
    quantum = int(max(1, _as_int(quantum, 1)))
    raw = int(_as_int(value, 0))
    return int((raw // quantum) * quantum)


def _vector_quantize(value: object, quantum: int) -> dict:
    payload = _as_map(value)
    return {
        "x": _quantize(payload.get("x"), quantum),
        "y": _quantize(payload.get("y"), quantum),
        "z": _quantize(payload.get("z"), quantum),
    }


def _scan_target_row(inspection_snapshot: Mapping[str, object] | None) -> tuple[dict, dict]:
    snapshot = _as_map(inspection_snapshot)
    target_payload = _as_map(snapshot.get("target_payload"))
    return target_payload, _as_map(target_payload.get("row"))


def _surface_tile_row(inspection_snapshot: Mapping[str, object] | None) -> dict:
    _target_payload, row = _scan_target_row(inspection_snapshot)
    artifact = _as_map(row.get("surface_tile_artifact"))
    return artifact if artifact else row


def _precision_mode(authority_context: Mapping[str, object] | None) -> tuple[str, dict]:
    entitlements = set(str(item).strip() for item in list(_as_map(authority_context).get("entitlements") or []) if str(item).strip())
    if "entitlement.observer.truth" in entitlements:
        return "admin_exact", {"height": 1, "temperature": 1, "daylight": 1, "tide": 1, "vector": 1, "pollution": 1}
    return "diegetic_coarse", {"height": 50, "temperature": 5, "daylight": 5, "tide": 5, "vector": 10, "pollution": 5}


def build_scan_result(
    *,
    authority_context: Mapping[str, object] | None,
    selection: Mapping[str, object] | None,
    inspection_snapshot: Mapping[str, object] | None,
    field_values: Mapping[str, object] | None = None,
    property_origin_result: Mapping[str, object] | None = None,
    has_physical_access: bool = True,
) -> dict:
    access_result = evaluate_tool_access(
        tool_id="tool.scanner_basic",
        authority_context=authority_context,
        has_physical_access=has_physical_access,
    )
    if str(access_result.get("result", "")).strip() != "complete":
        return dict(access_result)
    surface_tile = _surface_tile_row(inspection_snapshot)
    field_map = _as_map(field_values)
    target_payload, row = _scan_target_row(inspection_snapshot)
    precision_mode, quanta = _precision_mode(authority_context)
    surface_ext = _as_map(surface_tile.get("extensions"))
    elevation = _as_map(surface_tile.get("elevation_params_ref"))
    provenance_report = _as_map(_as_map(property_origin_result).get("report"))
    payload = {
        "result": "complete",
        "scan_id": "scan.{}".format(
            canonical_sha256(
                {
                    "selection": _as_map(selection),
                    "target_id": str(target_payload.get("target_id", "")).strip(),
                    "tile_object_id": str(surface_tile.get("tile_object_id", "")).strip(),
                }
            )[:16]
        ),
        "source_kind": "derived.scan_result",
        "tool_id": "tool.scanner_basic",
        "precision_mode": precision_mode,
        "position_ref": _as_map(_as_map(selection).get("position_ref")) or _as_map(target_payload.get("position_ref")),
        "tile_cell_key": _as_map(surface_tile.get("tile_cell_key")) or _as_map(_as_map(selection).get("tile_cell_key")),
        "surface_flags": {
            "ocean": str(surface_tile.get("material_baseline_id", "")).strip() == "material.water",
            "river": bool(surface_tile.get("river_flag", False)),
            "lake": bool(surface_ext.get("lake_flag", False)),
        },
        "material_baseline_id": str(surface_tile.get("material_baseline_id", "")).strip(),
        "biome_stub_id": str(surface_tile.get("biome_stub_id", "")).strip(),
        "elevation_proxy_mm": _quantize(elevation.get("height_proxy"), quanta["height"]),
        "flow_target_tile_key": _as_map(surface_tile.get("flow_target_tile_key")),
        "temperature": _quantize(field_map.get("temperature"), quanta["temperature"]),
        "daylight": _quantize(field_map.get("daylight"), quanta["daylight"]),
        "wind_vector": _vector_quantize(field_map.get("wind_vector"), quanta["vector"]),
        "tide_height_proxy": _quantize(field_map.get("tide_height_proxy"), quanta["tide"]),
        "pollution": _quantize(field_map.get("pollution"), quanta["pollution"]),
        "overlay_provenance_summary": {
            "current_layer_id": str(provenance_report.get("current_layer_id", "")).strip(),
            "prior_value_count": len(list(provenance_report.get("prior_value_chain") or [])),
        },
        "used_tool_ids": ["tool.geo.explain_property_origin"] if provenance_report else [],
        "selection_target_kind": str(row.get("object_kind_id", "")).strip() or str(row.get("type", "")).strip(),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = ["build_scan_result"]

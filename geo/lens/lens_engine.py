"""Deterministic GEO-5 lens engine for projected view artifacts."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from fields import field_get_value
from geo.edit import geometry_get_cell_state
from geo.kernel.geo_kernel import _as_int, _as_map
from geo.projection.projection_engine import normalize_projection_request, project_view_cells, projection_request_hash


REFUSAL_GEO_LENS_REQUEST_INVALID = "refusal.geo.lens_request_invalid"
_LENS_LAYER_REGISTRY_REL = "data/registries/lens_layer_registry.json"
_VIEW_TYPE_REGISTRY_REL = "data/registries/view_type_registry.json"
_PROJECTION_PROFILE_REGISTRY_REL = "data/registries/projection_profile_registry.json"
_VIEW_CACHE: Dict[str, dict] = {}


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    current = here
    markers = (
        os.path.join("docs", "canon", "constitution_v1.md"),
        os.path.join("data", "registries"),
        os.path.join("tools", "xstack"),
    )
    while True:
        if all(os.path.exists(os.path.join(current, marker)) for marker in markers):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.normpath(os.path.join(here, "..", "..", ".."))
        current = parent


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _rows_by_id(payload: Mapping[str, object] | None, *, row_key: str, id_key: str) -> Dict[str, dict]:
    body = _as_map(payload)
    rows = body.get(row_key)
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get(row_key)
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get(id_key, ""))):
        token = str(row.get(id_key, "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _sorted_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def projection_profile_registry_hash() -> str:
    return canonical_sha256(_registry_payload(_PROJECTION_PROFILE_REGISTRY_REL))


def lens_layer_registry_hash() -> str:
    return canonical_sha256(_registry_payload(_LENS_LAYER_REGISTRY_REL))


def view_type_registry_hash() -> str:
    return canonical_sha256(_registry_payload(_VIEW_TYPE_REGISTRY_REL))


def _lens_layer_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(_LENS_LAYER_REGISTRY_REL),
        row_key="lens_layers",
        id_key="layer_id",
    )


def _layer_source_rows(layer_source_payloads: Mapping[str, object] | None, layer_id: str) -> dict:
    return _as_map(_as_map(layer_source_payloads).get(str(layer_id).strip()))


def _refusal(message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": REFUSAL_GEO_LENS_REQUEST_INVALID,
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_lens_request(
    *,
    lens_request_id: str,
    lens_profile_id: str,
    included_layers: Sequence[object],
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "lens_request_id": str(lens_request_id or "").strip(),
        "lens_profile_id": str(lens_profile_id or "").strip(),
        "included_layers": _sorted_strings(included_layers),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_lens_request(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    return build_lens_request(
        lens_request_id=str(payload.get("lens_request_id", "")).strip()
        or "lens_request.{}".format(canonical_sha256({"seed": payload})[:16]),
        lens_profile_id=str(payload.get("lens_profile_id", "")).strip() or "lens.diegetic.sensor",
        included_layers=_sorted_strings(payload.get("included_layers")),
        extensions=_as_map(payload.get("extensions")),
    )


def _is_diegetic(perceived_model: Mapping[str, object], lens_request: Mapping[str, object]) -> bool:
    lens_id = str(_as_map(perceived_model).get("lens_id", "")).strip() or str(_as_map(lens_request).get("lens_profile_id", "")).strip()
    lens_type = str(_as_map(_as_map(perceived_model).get("metadata")).get("lens_type", "")).strip().lower()
    return lens_type == "diegetic" or lens_id.startswith("lens.diegetic.")


def _channels(perceived_model: Mapping[str, object]) -> List[str]:
    return _sorted_strings(_as_map(perceived_model).get("channels"))


def _map_instrument_available(perceived_model: Mapping[str, object]) -> bool:
    channels = set(_channels(perceived_model))
    instruments = _as_map(_as_map(perceived_model).get("diegetic_instruments"))
    return ("ch.diegetic.map_local" in channels) or bool(_as_map(instruments.get("instrument.map_local")))


def _ground_scanner_available(perceived_model: Mapping[str, object]) -> bool:
    channels = set(_channels(perceived_model))
    instruments = _as_map(_as_map(perceived_model).get("diegetic_instruments"))
    return (
        "ch.diegetic.ground_scanner" in channels
        or bool(_as_map(instruments.get("instrument.ground_scanner")))
        or bool(_as_map(instruments.get("instrument.survey_level")))
    )


def _orbit_instrument_available(perceived_model: Mapping[str, object]) -> bool:
    channels = set(_channels(perceived_model))
    instruments = _as_map(_as_map(perceived_model).get("diegetic_instruments"))
    return (
        "ch.diegetic.telescope" in channels
        or "ch.diegetic.orrery" in channels
        or bool(_as_map(instruments.get("instrument.telescope")))
        or bool(_as_map(instruments.get("instrument.orrery")))
    )


def _omniscient_allowed(
    *,
    lens_request: Mapping[str, object],
    perceived_model: Mapping[str, object],
    authority_context: Mapping[str, object] | None,
) -> bool:
    if not bool(_as_map(lens_request.get("extensions")).get("allow_omniscient_debug", False)):
        return False
    lens_id = str(lens_request.get("lens_profile_id", "")).strip() or str(_as_map(perceived_model).get("lens_id", "")).strip()
    if not any(token in lens_id for token in ("observer", "debug", "nondiegetic")):
        return False
    entitlements = set(_sorted_strings(_as_map(authority_context).get("entitlements")))
    return (not entitlements) or ("entitlement.debug_view" in entitlements) or ("entitlement.inspect" in entitlements)


def _quantize_scalar(value: int, step: int) -> int:
    quantum = int(max(1, _as_int(step, 1)))
    token = int(_as_int(value, 0))
    return int((token // quantum) * quantum) if token >= 0 else int(-((abs(token) // quantum) * quantum))


def _layer_state(*, visible: bool, value: object, hidden_reason: str = "", quantized: bool = False) -> dict:
    return {
        "state": "visible" if visible else "hidden",
        "value": value if visible else None,
        "hidden_reason": "" if visible else str(hidden_reason),
        "quantized": bool(quantized if visible else False),
    }


def _field_layer_value(
    *,
    cell_key: Mapping[str, object],
    source: Mapping[str, object],
    diegetic: bool,
    quantization_step: int,
) -> dict:
    field_id = str(_as_map(source).get("field_id", "")).strip()
    if not field_id:
        return _layer_state(visible=False, value=None, hidden_reason="field_id_missing")
    sampled = field_get_value(
        field_id=field_id,
        geo_cell_key=cell_key,
        field_layer_rows=list(_as_map(source).get("field_layer_rows") or []),
        field_cell_rows=list(_as_map(source).get("field_cell_rows") or []),
        field_type_registry=_as_map(source.get("field_type_registry")),
        field_binding_registry=_as_map(source.get("field_binding_registry")),
        interpolation_policy_registry=_as_map(source.get("interpolation_policy_registry")),
    )
    if str(_as_map(sampled).get("field_id", "")).strip() != field_id:
        return _layer_state(visible=False, value=None, hidden_reason="field_sample_missing")
    value = sampled.get("value")
    quantized = False
    if diegetic and isinstance(value, int):
        value = _quantize_scalar(int(value), int(max(1, quantization_step)))
        quantized = True
    return _layer_state(visible=True, value=value, quantized=quantized)


def _terrain_layer_value(
    *,
    cell_key: Mapping[str, object],
    source: Mapping[str, object],
    perceived_model: Mapping[str, object],
    omniscient_allowed: bool,
) -> dict:
    rows = [dict(item) for item in list(_as_map(source).get("entries") or []) if isinstance(item, Mapping)]
    if not rows:
        instrument = _as_map(_as_map(_as_map(perceived_model).get("diegetic_instruments")).get("instrument.map_local"))
        reading = _as_map(instrument.get("reading"))
        rows = [dict(item) for item in list(reading.get("entries") or []) if isinstance(item, Mapping)]
    if not rows:
        return _layer_state(visible=False, value=None, hidden_reason="terrain_unavailable")
    if not omniscient_allowed and not _map_instrument_available(perceived_model):
        return _layer_state(visible=False, value=None, hidden_reason="map_instrument_required")
    cell_hash = canonical_sha256(cell_key)
    alias = str(_as_map(_as_map(cell_key).get("extensions")).get("legacy_cell_alias", "")).strip()
    for row in sorted(rows, key=lambda item: canonical_sha256(item)):
        row_key = str(row.get("region_key", "")).strip() or str(row.get("tile_key", "")).strip() or str(row.get("cell_key", "")).strip()
        if row_key and row_key != alias and row_key != cell_hash:
            continue
        return _layer_state(visible=True, value={"terrain_class": str(row.get("terrain_class", "")).strip() or "unknown"})
    return _layer_state(visible=False, value=None, hidden_reason="terrain_unknown")


def _marker_layer_value(
    *,
    cell_key: Mapping[str, object],
    source: Mapping[str, object],
    perceived_model: Mapping[str, object],
    authority_context: Mapping[str, object] | None,
) -> dict:
    required_channels = set(_sorted_strings(_as_map(source).get("required_channels")))
    required_entitlements = set(_sorted_strings(_as_map(source).get("required_entitlements")))
    channels = set(_channels(perceived_model))
    entitlements = set(_sorted_strings(_as_map(authority_context).get("entitlements")))
    if required_channels and not required_channels.issubset(channels):
        return _layer_state(visible=False, value=None, hidden_reason="channel_required")
    if required_entitlements and not required_entitlements.issubset(entitlements):
        return _layer_state(visible=False, value=None, hidden_reason="entitlement_required")
    rows = [dict(item) for item in list(_as_map(source).get("rows") or []) if isinstance(item, Mapping)]
    target_hash = canonical_sha256(cell_key)
    matched = []
    for row in sorted(rows, key=lambda item: canonical_sha256(item)):
        row_key = _as_map(row.get("geo_cell_key"))
        if row_key and canonical_sha256(row_key) != target_hash:
            continue
        matched.append(dict(row))
    if not matched:
        return _layer_state(visible=False, value=None, hidden_reason="no_marker")
    return _layer_state(visible=True, value=matched)


def _water_layer_value(
    *,
    cell_key: Mapping[str, object],
    source: Mapping[str, object],
    authority_context: Mapping[str, object] | None,
    layer_id: str,
    diegetic: bool,
    quantization_step: int,
) -> dict:
    required_entitlements = set(_sorted_strings(_as_map(source).get("required_entitlements")))
    entitlements = set(_sorted_strings(_as_map(authority_context).get("entitlements")))
    if required_entitlements and not required_entitlements.issubset(entitlements):
        return _layer_state(visible=False, value=None, hidden_reason="entitlement_required")
    rows = [dict(item) for item in list(_as_map(source).get("rows") or []) if isinstance(item, Mapping)]
    if not rows:
        return _layer_state(visible=False, value=None, hidden_reason="water_unavailable")
    target_hash = canonical_sha256(_as_map(cell_key))
    matched = {}
    for row in sorted(rows, key=lambda item: canonical_sha256(item)):
        row_key = _as_map(row.get("geo_cell_key") or row.get("tile_cell_key"))
        if row_key and canonical_sha256(row_key) != target_hash:
            continue
        matched = dict(row)
        break
    if not matched:
        return _layer_state(visible=False, value=None, hidden_reason="water_absent")
    if str(layer_id or "").strip() == "layer.tide_offset":
        value = int(_as_int(matched.get("tide_offset_value", 0), 0))
        quantized = False
        if diegetic:
            value = _quantize_scalar(value, int(max(1, quantization_step)))
            quantized = True
        return _layer_state(visible=True, value=value, quantized=quantized)
    return _layer_state(
        visible=True,
        value={
            "water_kind": str(matched.get("water_kind", "")).strip() or str(_as_map(source).get("water_kind", "")).strip(),
            "tile_object_id": str(matched.get("tile_object_id", "")).strip(),
            "flow_target_tile_key": _as_map(matched.get("flow_target_tile_key")),
            "river_width_permille": matched.get("river_width_permille"),
            "lake_fill_permille": matched.get("lake_fill_permille"),
            "tide_offset_value": int(_as_int(matched.get("tide_offset_value", 0), 0)),
        },
    )


def _orbit_layer_value(
    *,
    cell_key: Mapping[str, object],
    source: Mapping[str, object],
    perceived_model: Mapping[str, object],
    omniscient_allowed: bool,
) -> dict:
    rows = [dict(item) for item in list(_as_map(source).get("rows") or []) if isinstance(item, Mapping)]
    if not rows:
        return _layer_state(visible=False, value=None, hidden_reason="orbit_unavailable")
    if not omniscient_allowed and not _orbit_instrument_available(perceived_model):
        return _layer_state(visible=False, value=None, hidden_reason="telescope_or_orrery_required")
    target_hash = canonical_sha256(_as_map(cell_key))
    matched = {}
    for row in sorted(rows, key=lambda item: canonical_sha256(item)):
        row_key = _as_map(row.get("geo_cell_key"))
        if row_key and canonical_sha256(row_key) != target_hash:
            continue
        matched = dict(row)
        break
    if not matched:
        return _layer_state(visible=False, value=None, hidden_reason="orbit_absent")
    return _layer_state(
        visible=True,
        value={
            "marker_kind": str(matched.get("marker_kind", "")).strip() or "path",
            "object_ids": _sorted_strings(matched.get("object_ids")),
            "focus_object_id": str(matched.get("focus_object_id", "")).strip(),
            "chart_mode": str(matched.get("chart_mode", "")).strip(),
        },
    )


def _galaxy_object_layer_value(
    *,
    cell_key: Mapping[str, object],
    source: Mapping[str, object],
    perceived_model: Mapping[str, object],
    omniscient_allowed: bool,
) -> dict:
    rows = [dict(item) for item in list(_as_map(source).get("rows") or []) if isinstance(item, Mapping)]
    if not rows:
        return _layer_state(visible=False, value=None, hidden_reason="galaxy_object_unavailable")
    if not omniscient_allowed and not _orbit_instrument_available(perceived_model):
        return _layer_state(visible=False, value=None, hidden_reason="telescope_or_orrery_required")
    target_hash = canonical_sha256(_as_map(cell_key))
    matched = {}
    for row in sorted(rows, key=lambda item: canonical_sha256(item)):
        row_key = _as_map(row.get("geo_cell_key"))
        if row_key and canonical_sha256(row_key) != target_hash:
            continue
        matched = dict(row)
        break
    if not matched:
        return _layer_state(visible=False, value=None, hidden_reason="galaxy_object_absent")
    return _layer_state(
        visible=True,
        value={
            "marker_kind": str(matched.get("marker_kind", "")).strip() or "mixed",
            "object_ids": _sorted_strings(matched.get("object_ids")),
            "kind_ids": _sorted_strings(matched.get("kind_ids")),
            "radiation_bump_permille": int(_as_int(matched.get("radiation_bump_permille", 0), 0)),
            "gravity_well_bump_permille": int(_as_int(matched.get("gravity_well_bump_permille", 0), 0)),
        },
    )


def _geometry_layer_value(
    *,
    cell_key: Mapping[str, object],
    source: Mapping[str, object],
    perceived_model: Mapping[str, object],
    diegetic: bool,
    omniscient_allowed: bool,
    quantization_step: int,
) -> dict:
    if not omniscient_allowed and not (_map_instrument_available(perceived_model) or _ground_scanner_available(perceived_model)):
        return _layer_state(visible=False, value=None, hidden_reason="ground_scanner_required")
    rows = [dict(item) for item in list(_as_map(source).get("geometry_cell_states") or _as_map(source).get("rows") or []) if isinstance(item, Mapping)]
    if not rows:
        instrument = _as_map(_as_map(_as_map(perceived_model).get("diegetic_instruments")).get("instrument.ground_scanner"))
        reading = _as_map(instrument.get("reading"))
        rows = [dict(item) for item in list(reading.get("geometry_cell_states") or reading.get("rows") or []) if isinstance(item, Mapping)]
    if not rows and not omniscient_allowed:
        return _layer_state(visible=False, value=None, hidden_reason="geometry_unavailable")
    state_row = geometry_get_cell_state(cell_key, rows or [{"geo_cell_key": cell_key, "material_id": "material.air", "occupancy_fraction": 0}])
    occupancy_fraction = int(max(0, _as_int(state_row.get("occupancy_fraction", 0), 0)))
    quantized = False
    if diegetic:
        occupancy_fraction = _quantize_scalar(occupancy_fraction, int(max(1, quantization_step)))
        quantized = True
    material_id = str(state_row.get("material_id", "")).strip() or "material.air"
    scanner_available = omniscient_allowed or _ground_scanner_available(perceived_model)
    return _layer_state(
        visible=True,
        value={
            "occupancy_fraction": occupancy_fraction,
            "material_id": material_id if scanner_available else None,
            "excavated": bool(occupancy_fraction < 1000),
            "tunnel_stub": bool(occupancy_fraction <= 250),
        },
        quantized=quantized,
    )


def normalize_projected_view_artifact(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    rendered_cells = [
        {
            "geo_cell_key": _as_map(_as_map(item).get("geo_cell_key")),
            "projected_coord": _as_map(_as_map(item).get("projected_coord")),
            "layers": dict((str(layer_id), _as_map(layer_value)) for layer_id, layer_value in sorted(_as_map(_as_map(item).get("layers")).items(), key=lambda entry: str(entry[0]))),
        }
        for item in list(payload.get("rendered_cells") or [])
        if isinstance(item, Mapping)
    ]
    out = {
        "schema_version": "1.0.0",
        "view_id": str(payload.get("view_id", "")).strip(),
        "projection_request_id": str(payload.get("projection_request_id", "")).strip(),
        "lens_request_id": str(payload.get("lens_request_id", "")).strip(),
        "rendered_cells": rendered_cells,
        "deterministic_fingerprint": "",
        "extensions": _as_map(payload.get("extensions")),
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def projected_view_fingerprint(projected_view_artifact: Mapping[str, object] | None) -> str:
    artifact = normalize_projected_view_artifact(projected_view_artifact)
    semantic = dict(artifact)
    semantic.pop("deterministic_fingerprint", None)
    return canonical_sha256(semantic)


def _cached_view(cache_key: str) -> dict | None:
    cached = _VIEW_CACHE.get(str(cache_key))
    if not isinstance(cached, dict):
        return None
    return dict(cached)


def _store_view(cache_key: str, payload: Mapping[str, object]) -> dict:
    _VIEW_CACHE[str(cache_key)] = dict(payload)
    return dict(payload)


def build_projected_view_artifact(
    *,
    projection_request: Mapping[str, object] | None = None,
    projection_result: Mapping[str, object] | None = None,
    lens_request: Mapping[str, object] | None,
    perceived_model: Mapping[str, object] | None,
    layer_source_payloads: Mapping[str, object] | None = None,
    authority_context: Mapping[str, object] | None = None,
    topology_profile_id: str = "",
    partition_profile_id: str = "",
    metric_profile_id: str = "",
    frame_nodes: object = None,
    frame_transform_rows: object = None,
    graph_version: str = "",
    truth_hash_anchor: str = "",
) -> dict:
    normalized_lens = normalize_lens_request(lens_request)
    if not list(normalized_lens.get("included_layers") or []):
        return _refusal("lens_request must include at least one layer")
    perceived = _as_map(perceived_model)
    projection_payload = _as_map(projection_result)
    if not projection_payload:
        projection_payload = project_view_cells(
            projection_request,
            topology_profile_id=topology_profile_id,
            partition_profile_id=partition_profile_id,
            metric_profile_id=metric_profile_id,
            frame_nodes=frame_nodes,
            frame_transform_rows=frame_transform_rows,
            graph_version=graph_version,
        )
    if str(projection_payload.get("result", "")) != "complete":
        return dict(projection_payload)
    normalized_request = normalize_projection_request(projection_payload.get("projection_request") or projection_request)
    truth_anchor = str(truth_hash_anchor or _as_map(_as_map(perceived).get("truth_overlay")).get("state_hash_anchor", "")).strip()
    epistemic_policy = str(_as_map(_as_map(perceived).get("metadata")).get("epistemic_policy_id", "")).strip()
    cache_key = canonical_sha256(
        {
            "projection_request_hash": projection_request_hash(normalized_request),
            "lens_request": dict(normalized_lens),
            "truth_hash_anchor": truth_anchor,
            "epistemic_policy": epistemic_policy,
            "registry_hashes": {
                "projection_profile_registry_hash": projection_profile_registry_hash(),
                "lens_layer_registry_hash": lens_layer_registry_hash(),
                "view_type_registry_hash": view_type_registry_hash(),
            },
        }
    )
    cached = _cached_view(cache_key)
    if cached is not None:
        return cached
    diegetic = _is_diegetic(perceived, normalized_lens)
    omniscient = _omniscient_allowed(lens_request=normalized_lens, perceived_model=perceived, authority_context=authority_context)
    quantization_step = int(max(1, _as_int(_as_map(normalized_lens.get("extensions")).get("quantization_step", 10), 10)))
    layer_registry = _lens_layer_rows()
    rendered_cells = []
    for projected_row in list(projection_payload.get("projected_cells") or []):
        projected = dict(projected_row)
        cell_key = _as_map(projected.get("geo_cell_key"))
        layers = {}
        for layer_id in list(normalized_lens.get("included_layers") or []):
            layer_token = str(layer_id).strip()
            layer_row = dict(layer_registry.get(layer_token) or {})
            source = _layer_source_rows(layer_source_payloads, layer_token)
            source_kind = str(_as_map(layer_row.get("extensions")).get("source_kind", source.get("source_kind", ""))).strip()
            if layer_token in {"layer.temperature", "layer.pollution"} or source_kind == "field":
                layers[layer_token] = _field_layer_value(cell_key=cell_key, source=source, diegetic=diegetic, quantization_step=quantization_step)
            elif layer_token in {"layer.water_ocean", "layer.water_river", "layer.water_lake", "layer.tide_offset"} or source_kind == "water_view":
                layers[layer_token] = _water_layer_value(
                    cell_key=cell_key,
                    source=source,
                    authority_context=authority_context,
                    layer_id=layer_token,
                    diegetic=diegetic,
                    quantization_step=quantization_step,
                )
            elif layer_token == "layer.orbits" or source_kind == "orbit_view":
                layers[layer_token] = _orbit_layer_value(
                    cell_key=cell_key,
                    source=source,
                    perceived_model=perceived,
                    omniscient_allowed=omniscient,
                )
            elif layer_token == "layer.galaxy_objects" or source_kind == "galaxy_object_view":
                layers[layer_token] = _galaxy_object_layer_value(
                    cell_key=cell_key,
                    source=source,
                    perceived_model=perceived,
                    omniscient_allowed=omniscient,
                )
            elif layer_token == "layer.terrain_stub" or source_kind == "terrain":
                layers[layer_token] = _terrain_layer_value(cell_key=cell_key, source=source, perceived_model=perceived, omniscient_allowed=omniscient)
            elif layer_token == "layer.geometry_occupancy" or source_kind == "geometry_occupancy":
                layers[layer_token] = _geometry_layer_value(
                    cell_key=cell_key,
                    source=source,
                    perceived_model=perceived,
                    diegetic=diegetic,
                    omniscient_allowed=omniscient,
                    quantization_step=quantization_step,
                )
            elif layer_token in {"layer.infrastructure_stub", "layer.entity_markers_stub"} or source_kind in {"infrastructure", "entities"}:
                layers[layer_token] = _marker_layer_value(cell_key=cell_key, source=source, perceived_model=perceived, authority_context=authority_context)
            else:
                layers[layer_token] = _layer_state(visible=False, value=None, hidden_reason="layer_unavailable")
        rendered_cells.append(
            {
                "geo_cell_key": cell_key,
                "projected_coord": _as_map(projected.get("projected_coord")),
                "layers": dict((key, layers[key]) for key in sorted(layers.keys())),
            }
        )
    payload = normalize_projected_view_artifact(
        {
            "view_id": "view_artifact.{}".format(cache_key[:16]),
            "projection_request_id": str(normalized_request.get("request_id", "")).strip(),
            "lens_request_id": str(normalized_lens.get("lens_request_id", "")).strip(),
            "rendered_cells": rendered_cells,
            "extensions": {
                "projection_request_hash": projection_request_hash(normalized_request),
                "lens_profile_id": str(normalized_lens.get("lens_profile_id", "")).strip(),
                "truth_hash_anchor": truth_anchor,
                "epistemic_policy_id": epistemic_policy,
                "diegetic": bool(diegetic),
                "omniscient_debug_logged": bool(omniscient),
                "projection_profile_registry_hash": projection_profile_registry_hash(),
                "lens_layer_registry_hash": lens_layer_registry_hash(),
                "view_type_registry_hash": view_type_registry_hash(),
                "worldgen_request_ids": sorted(
                    str(dict(row).get("request_id", "")).strip()
                    for row in list(projection_payload.get("worldgen_requests") or [])
                    if isinstance(row, Mapping) and str(dict(row).get("request_id", "")).strip()
                ),
            },
        }
    )
    return _store_view(cache_key, payload)

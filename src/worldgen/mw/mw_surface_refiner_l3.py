"""Deterministic MW-3 planet-surface macro refiner."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.fields import build_field_cell, build_field_layer
from src.geo.edit import build_geometry_cell_state
from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from src.geo.index.object_id_engine import geo_object_id

from .insolation_proxy import daylight_proxy_permille, insolation_proxy_permille, orbital_period_proxy_ticks


DEFAULT_SURFACE_PRIORS_ID = "priors.surface_default_stub"
SURFACE_PRIORS_REGISTRY_REL = os.path.join("data", "registries", "surface_priors_registry.json")
SURFACE_GENERATOR_REGISTRY_REL = os.path.join("data", "registries", "surface_generator_registry.json")
SURFACE_GENERATOR_ROUTING_REGISTRY_REL = os.path.join("data", "registries", "surface_generator_routing_registry.json")
MW_SURFACE_REFINER_L3_VERSION = "MW3-3"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return dict(json.load(handle) or {})
    except (OSError, ValueError, TypeError):
        return {}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


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


def _normalized_extensions_map(value: object) -> dict:
    return dict((str(key), item) for key, item in sorted(_as_map(value).items(), key=lambda pair: str(pair[0])))


def _hash_int(seed: str, salt: str) -> int:
    return int(canonical_sha256({"seed": str(seed), "salt": str(salt)})[:16], 16)


def _named_substream_seed(seed: str, stream_name: str) -> str:
    return canonical_sha256({"seed": str(seed), "stream_name": str(stream_name)})


def _sorted_unique_strings(values: Sequence[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _spawn_object_identity(*, universe_identity_hash: str, cell_key: Mapping[str, object], object_kind_id: str, local_subkey: str) -> Tuple[str, dict]:
    object_id_payload = geo_object_id(
        universe_identity_hash=universe_identity_hash,
        cell_key=cell_key,
        object_kind_id=object_kind_id,
        local_subkey=local_subkey,
    )
    if str(object_id_payload.get("result", "")) != "complete":
        return ("", {})
    identity = _as_map(object_id_payload.get("object_identity"))
    return (
        str(object_id_payload.get("object_id_hash", "")).strip(),
        {
            "object_id_hash": str(object_id_payload.get("object_id_hash", "")).strip(),
            "object_kind_id": str(identity.get("object_kind_id", "")).strip(),
            "local_subkey": str(identity.get("local_subkey", "")).strip(),
            "geo_cell_key": _as_map(identity.get("geo_cell_key")),
        },
    )


def surface_priors_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(SURFACE_PRIORS_REGISTRY_REL), row_key="surface_priors", id_key="priors_id")


def surface_generator_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(SURFACE_GENERATOR_REGISTRY_REL),
        row_key="surface_generators",
        id_key="generator_id",
    )


def surface_generator_routing_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(SURFACE_GENERATOR_ROUTING_REGISTRY_REL),
        row_key="surface_generator_routes",
        id_key="routing_id",
    )


def _base_chart_id(value: object) -> str:
    token = str(value or "").strip().lower()
    if "south" in token:
        return "chart.atlas.south"
    return "chart.atlas.north"


def _planet_chart_id(*, planet_object_id: str, chart_id: str) -> str:
    hemisphere = "south" if "south" in str(chart_id or "").lower() else "north"
    return "chart.surface.{}.{}".format(str(planet_object_id or "")[:12] or "unknown", hemisphere)


def build_planet_surface_cell_key(
    *,
    planet_object_id: str,
    ancestor_world_cell_key: Mapping[str, object],
    chart_id: str,
    index_tuple: Sequence[int],
    refinement_level: int = 0,
    topology_profile_id: str = "geo.topology.sphere_surface_s2",
    partition_profile_id: str = "geo.partition.atlas_tiles",
    planet_tags: object = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    ancestor_key = _coerce_cell_key(ancestor_world_cell_key)
    if not ancestor_key:
        raise ValueError("ancestor_world_cell_key is required")
    planet_object_token = str(planet_object_id or "").strip()
    if not planet_object_token:
        raise ValueError("planet_object_id is required")
    surface_key = _coerce_cell_key(
        {
            "schema_version": "1.0.0",
            "partition_profile_id": str(partition_profile_id or "").strip() or "geo.partition.atlas_tiles",
            "topology_profile_id": str(topology_profile_id or "").strip() or "geo.topology.sphere_surface_s2",
            "chart_id": _planet_chart_id(planet_object_id=planet_object_token, chart_id=chart_id),
            "index_tuple": [int(item) for item in list(index_tuple or [])],
            "refinement_level": int(max(0, _as_int(refinement_level, 0))),
            "extensions": {
                "planet_object_id": planet_object_token,
                "ancestor_world_cell_key": dict(ancestor_key),
                "base_chart_id": _base_chart_id(chart_id),
                "planet_tags": _sorted_unique_strings(list(planet_tags or [])),
                **_as_map(extensions),
            },
        }
    )
    if not surface_key:
        raise ValueError("surface tile cell key is invalid")
    return surface_key


def normalize_surface_tile_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        tile_object_id = str(row.get("tile_object_id", "")).strip()
        if not tile_object_id:
            continue
        normalized = {
            "tile_object_id": tile_object_id,
            "planet_object_id": str(row.get("planet_object_id", "")).strip(),
            "tile_cell_key": _as_map(row.get("tile_cell_key")),
            "elevation_params_ref": _as_map(row.get("elevation_params_ref")),
            "material_baseline_id": str(row.get("material_baseline_id", "")).strip(),
            "biome_stub_id": str(row.get("biome_stub_id", "")).strip(),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _normalized_extensions_map(row.get("extensions")),
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[tile_object_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def surface_tile_artifact_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_surface_tile_artifact_rows(rows))


def _normalize_planet_basic_rows(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            out[object_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _normalize_planet_orbit_rows(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        object_id = str(row.get("planet_object_id", "")).strip()
        if object_id:
            out[object_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _normalize_star_rows(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            out[object_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _surface_route_tags(*, surface_cell_key: Mapping[str, object], planet_basic_row: Mapping[str, object]) -> List[str]:
    cell_ext = _as_map(_as_map(surface_cell_key).get("extensions"))
    base_tags = _sorted_unique_strings(list(_as_map(planet_basic_row).get("extensions", {}).get("tags") or []))
    request_tags = _sorted_unique_strings(list(cell_ext.get("planet_tags") or cell_ext.get("route_tags") or []))
    return _sorted_unique_strings(base_tags + request_tags)


def _select_surface_route(
    *,
    realism_profile_id: str,
    surface_priors_id: str,
    planet_object_id: str,
    planet_tags: Sequence[str],
    routing_rows: Mapping[str, object],
) -> dict:
    selector_rank = {"by_object_id": 0, "by_tag": 1, "by_profile": 2}
    ordered_rows = sorted(
        (_as_map(row) for row in dict(routing_rows or {}).values()),
        key=lambda row: (
            selector_rank.get(str(row.get("selector_kind", "")).strip(), 99),
            str(row.get("routing_id", "")).strip(),
        ),
    )
    tag_set = set(_sorted_unique_strings(list(planet_tags or [])))
    for row in ordered_rows:
        selector_kind = str(row.get("selector_kind", "")).strip()
        match_rule = _as_map(row.get("match_rule"))
        if selector_kind == "by_object_id":
            object_ids = _sorted_unique_strings(list(match_rule.get("object_ids") or []))
            single_object_id = str(match_rule.get("object_id", "")).strip()
            if str(planet_object_id).strip() and (str(planet_object_id).strip() == single_object_id or str(planet_object_id).strip() in object_ids):
                return dict(row)
        elif selector_kind == "by_tag":
            route_tags = set(_sorted_unique_strings(list(match_rule.get("planet_tags") or match_rule.get("tags") or [])))
            if tag_set.intersection(route_tags):
                return dict(row)
        elif selector_kind == "by_profile":
            realism_ids = _sorted_unique_strings(list(match_rule.get("realism_profile_ids") or []))
            surface_ids = _sorted_unique_strings(list(match_rule.get("surface_priors_ids") or []))
            if str(realism_profile_id).strip() in realism_ids or str(surface_priors_id).strip() in surface_ids:
                return dict(row)
    return {}


def _resolve_generator(*, generator_id: str, generator_rows: Mapping[str, object]) -> Tuple[dict, dict]:
    rows = dict(generator_rows or {})
    selected = _as_map(rows.get(str(generator_id).strip()))
    if not selected:
        return ({}, {})
    handler_row = dict(selected)
    visited = set()
    while True:
        if not handler_row:
            break
        current_id = str(handler_row.get("generator_id", "")).strip()
        delegate_id = str(_as_map(handler_row.get("extensions")).get("delegate_generator_id", "")).strip()
        if (not delegate_id) or delegate_id in visited:
            break
        visited.add(current_id)
        delegate_row = _as_map(rows.get(delegate_id))
        if not delegate_row:
            break
        handler_row = dict(delegate_row)
    return (dict(selected), dict(handler_row))


def _quantity_value(value: object, *, default_value: int = 0) -> int:
    row = _as_map(value)
    return _as_int(row.get("value", default_value), default_value)


def _surface_seed(*, surface_stream_seed: str, planet_object_id: str, tile_cell_key: Mapping[str, object]) -> str:
    return canonical_sha256(
        {
            "surface_stream_seed": str(surface_stream_seed),
            "planet_object_id": str(planet_object_id),
            "tile_cell_key": _semantic_cell_key(_coerce_cell_key(tile_cell_key) or {}),
            "stream_name": "rng.worldgen.surface.tile",
        }
    )


def _latitude_mdeg(tile_cell_key: Mapping[str, object], surface_priors_row: Mapping[str, object]) -> int:
    cell_key = _coerce_cell_key(tile_cell_key) or {}
    ext = _as_map(cell_key.get("extensions"))
    base_chart = _base_chart_id(ext.get("base_chart_id") or cell_key.get("chart_id"))
    atlas_resolution = max(1, _as_int(_as_map(_as_map(surface_priors_row).get("extensions")).get("atlas_resolution", 8), 8))
    refinement_level = max(0, _as_int(cell_key.get("refinement_level", 0), 0))
    band_count = max(1, atlas_resolution * max(1, 1 << refinement_level))
    index_tuple = list(cell_key.get("index_tuple") or [0, 0])
    v_idx = _clamp(_as_int(index_tuple[1] if len(index_tuple) > 1 else 0, 0), 0, band_count - 1)
    midpoint = (v_idx * 2) + 1
    if "south" in base_chart:
        return -((midpoint * 90_000) // (band_count * 2))
    return 90_000 - ((midpoint * 90_000) // (band_count * 2))


def _pressure_proxy_value(*, atmosphere_class_id: str, surface_priors_row: Mapping[str, object]) -> int:
    pressure_params = _as_map(_as_map(surface_priors_row).get("pressure_params"))
    return max(0, _as_int(pressure_params.get(str(atmosphere_class_id).strip(), 0), 0))


def _atmosphere_temperature_bias(atmosphere_class_id: str) -> int:
    return {
        "atmo.none": -35,
        "atmo.thin": -10,
        "atmo.temperate": 0,
        "atmo.dense": 12,
        "atmo.volatile": 18,
    }.get(str(atmosphere_class_id).strip(), 0)


def _material_baseline_id(*, material_key: str, surface_priors_row: Mapping[str, object]) -> str:
    baselines = _as_map(_as_map(_as_map(surface_priors_row).get("extensions")).get("material_baselines"))
    return str(baselines.get(material_key, "material.stone_basic")).strip() or "material.stone_basic"


def _height_proxy(*, tile_seed: str, material_key: str, surface_priors_row: Mapping[str, object]) -> int:
    elevation = _as_map(_as_map(surface_priors_row).get("elevation_params"))
    if material_key == "ocean":
        minimum = max(0, _as_int(elevation.get("ocean_height_min", 200), 200))
        maximum = max(minimum, _as_int(elevation.get("ocean_height_max", minimum), minimum))
    elif material_key == "ice":
        minimum = max(0, _as_int(elevation.get("ice_height_min", 900), 900))
        maximum = max(minimum, _as_int(elevation.get("ice_height_max", minimum), minimum))
    else:
        minimum = max(0, _as_int(elevation.get("land_height_min", 1200), 1200))
        maximum = max(minimum, _as_int(elevation.get("land_height_max", minimum), minimum))
    if minimum == maximum:
        return minimum
    return minimum + (_hash_int(tile_seed, "height_proxy") % (maximum - minimum + 1))


def _biome_stub_id(*, material_key: str, temperature_kelvin: int, ocean_fraction_permille: int) -> str:
    if material_key == "ocean":
        return "biome.stub.ocean"
    if material_key == "ice":
        return "biome.stub.ice_cap"
    if temperature_kelvin < 245:
        return "biome.stub.tundra"
    if temperature_kelvin > 315 and int(ocean_fraction_permille) < 250:
        return "biome.stub.desert"
    if int(ocean_fraction_permille) >= 600:
        return "biome.stub.wet_temperate"
    return "biome.stub.temperate"


def _surface_material_key(*, tile_seed: str, latitude_mdeg: int, temperature_kelvin: int, ocean_fraction_permille: int) -> str:
    ocean_roll = _hash_int(tile_seed, "ocean_roll") % 1000
    if int(temperature_kelvin) < 240 or abs(int(latitude_mdeg)) >= 78_000:
        if ocean_roll < min(1000, int(ocean_fraction_permille) + 180):
            return "ice"
    if ocean_roll < int(ocean_fraction_permille):
        return "ocean"
    return "land"


def generate_mw_surface_l3_payload(
    *,
    universe_identity_hash: str,
    surface_geo_cell_key: Mapping[str, object],
    ancestor_world_cell_key: Mapping[str, object],
    realism_profile_row: Mapping[str, object] | None,
    planet_object_id: str,
    planet_basic_artifact_rows: object,
    planet_orbit_artifact_rows: object,
    star_artifact_rows: object,
    surface_stream_seed: str,
    current_tick: int = 0,
    surface_priors_registry_payload: Mapping[str, object] | None = None,
    surface_generator_registry_payload: Mapping[str, object] | None = None,
    surface_generator_routing_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    surface_cell_key = _coerce_cell_key(surface_geo_cell_key)
    ancestor_key = _coerce_cell_key(ancestor_world_cell_key)
    planet_object_token = str(planet_object_id or "").strip()
    if not surface_cell_key:
        payload = {"result": "refused", "message": "surface_geo_cell_key is invalid for MW-3 refinement", "details": {"surface_geo_cell_key": _as_map(surface_geo_cell_key)}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    if not ancestor_key:
        payload = {"result": "refused", "message": "ancestor_world_cell_key is invalid for MW-3 refinement", "details": {"ancestor_world_cell_key": _as_map(ancestor_world_cell_key)}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    if not planet_object_token:
        payload = {"result": "refused", "message": "planet_object_id is required for MW-3 refinement", "details": {}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    realism = _as_map(realism_profile_row)
    surface_priors_id = str(realism.get("surface_priors_ref", "")).strip() or DEFAULT_SURFACE_PRIORS_ID
    surface_rows = surface_priors_rows(surface_priors_registry_payload)
    generator_rows = surface_generator_rows(surface_generator_registry_payload)
    routing_rows = surface_generator_routing_rows(surface_generator_routing_registry_payload)
    surface_priors_row = _as_map(surface_rows.get(surface_priors_id))
    if not surface_priors_row:
        payload = {"result": "refused", "message": "surface_priors_ref is not declared", "details": {"surface_priors_id": surface_priors_id}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    expected_topology_id = str(surface_priors_row.get("topology_profile_id", "")).strip()
    expected_partition_id = str(surface_priors_row.get("partition_profile_id", "")).strip()
    if expected_topology_id and str(surface_cell_key.get("topology_profile_id", "")).strip() != expected_topology_id:
        payload = {"result": "refused", "message": "surface tile topology does not match surface priors", "details": {"expected_topology_profile_id": expected_topology_id, "observed_topology_profile_id": str(surface_cell_key.get("topology_profile_id", "")).strip()}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    if expected_partition_id and str(surface_cell_key.get("partition_profile_id", "")).strip() != expected_partition_id:
        payload = {"result": "refused", "message": "surface tile partition does not match surface priors", "details": {"expected_partition_profile_id": expected_partition_id, "observed_partition_profile_id": str(surface_cell_key.get("partition_profile_id", "")).strip()}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    planet_basic_rows = _normalize_planet_basic_rows(planet_basic_artifact_rows)
    planet_orbit_rows = _normalize_planet_orbit_rows(planet_orbit_artifact_rows)
    star_rows = _normalize_star_rows(star_artifact_rows)
    planet_basic_row = _as_map(planet_basic_rows.get(planet_object_token))
    planet_orbit_row = _as_map(planet_orbit_rows.get(planet_object_token))
    star_object_id = str(planet_orbit_row.get("star_object_id", "")).strip()
    star_row = _as_map(star_rows.get(star_object_id))
    if not planet_basic_row or not planet_orbit_row or not star_row:
        payload = {"result": "refused", "message": "planet lineage artifacts are incomplete for MW-3 refinement", "details": {"planet_object_id": planet_object_token, "has_planet_basic": bool(planet_basic_row), "has_planet_orbit": bool(planet_orbit_row), "has_star_artifact": bool(star_row)}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    planet_tags = _surface_route_tags(surface_cell_key=surface_cell_key, planet_basic_row=planet_basic_row)
    route_row = _select_surface_route(
        realism_profile_id=str(realism.get("realism_profile_id", "")).strip() or str(realism.get("profile_id", "")).strip(),
        surface_priors_id=surface_priors_id,
        planet_object_id=planet_object_token,
        planet_tags=planet_tags,
        routing_rows=routing_rows,
    )
    if not route_row:
        payload = {"result": "refused", "message": "no surface generator route matched the tile context", "details": {"surface_priors_id": surface_priors_id, "planet_tags": list(planet_tags)}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    selected_generator_row, handler_row = _resolve_generator(
        generator_id=str(route_row.get("generator_id", "")).strip(),
        generator_rows=generator_rows,
    )
    if not selected_generator_row or not handler_row:
        payload = {"result": "refused", "message": "surface generator route points to an undeclared generator", "details": {"routing_id": str(route_row.get("routing_id", "")).strip(), "generator_id": str(route_row.get("generator_id", "")).strip()}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    tile_object_id, object_row = _spawn_object_identity(
        universe_identity_hash=universe_identity_hash,
        cell_key=surface_cell_key,
        object_kind_id="kind.surface_tile",
        local_subkey="planet:{}:surface_tile".format(planet_object_token),
    )
    if not tile_object_id:
        payload = {"result": "refused", "message": "failed to derive surface tile object identity", "details": {"planet_object_id": planet_object_token}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    tile_seed = _surface_seed(surface_stream_seed=surface_stream_seed, planet_object_id=planet_object_token, tile_cell_key=surface_cell_key)
    generator_seed = _named_substream_seed(tile_seed, "rng.worldgen.surface.generator")
    latitude_mdeg = _latitude_mdeg(surface_cell_key, surface_priors_row)
    star_mass_milli_solar = _quantity_value(star_row.get("star_mass"), default_value=1000)
    luminosity_permille = _quantity_value(star_row.get("luminosity_proxy"), default_value=1000)
    semi_major_axis_milli_au = _quantity_value(planet_orbit_row.get("semi_major_axis"), default_value=1000)
    axial_tilt_mdeg = _quantity_value(planet_basic_row.get("axial_tilt"), default_value=0)
    ocean_fraction_permille = _quantity_value(planet_basic_row.get("ocean_fraction"), default_value=0)
    atmosphere_class_id = str(planet_basic_row.get("atmosphere_class_id", "")).strip()
    orbital_period_ticks = orbital_period_proxy_ticks(
        semi_major_axis_milli_au=semi_major_axis_milli_au,
        star_mass_milli_solar=star_mass_milli_solar,
    )
    daylight_params = _as_map(surface_priors_row.get("daylight_params"))
    daylight_value = daylight_proxy_permille(
        latitude_mdeg=latitude_mdeg,
        axial_tilt_mdeg=axial_tilt_mdeg,
        current_tick=current_tick,
        orbital_period_ticks=orbital_period_ticks,
        daylight_params=daylight_params,
    )
    insolation_value = insolation_proxy_permille(
        daylight_permille=daylight_value,
        luminosity_permille=luminosity_permille,
        semi_major_axis_milli_au=semi_major_axis_milli_au,
    )
    temperature_params = _as_map(surface_priors_row.get("temperature_params"))
    temperature_value = _clamp(
        _as_int(temperature_params.get("baseline_kelvin", 210), 210)
        + ((insolation_value * _as_int(temperature_params.get("insolation_weight_kelvin", 120), 120)) // 1000)
        - ((abs(latitude_mdeg) * _as_int(temperature_params.get("latitude_cooling_max_kelvin", 80), 80)) // 90_000)
        + ((daylight_value * _as_int(temperature_params.get("daylight_bonus_max_kelvin", 35), 35)) // 1000)
        + ((ocean_fraction_permille * _as_int(temperature_params.get("ocean_moderation_kelvin", 10), 10)) // 1000)
        + _atmosphere_temperature_bias(atmosphere_class_id),
        120,
        480,
    )
    material_key = _surface_material_key(
        tile_seed=generator_seed,
        latitude_mdeg=latitude_mdeg,
        temperature_kelvin=temperature_value,
        ocean_fraction_permille=ocean_fraction_permille,
    )
    material_baseline_id = _material_baseline_id(material_key=material_key, surface_priors_row=surface_priors_row)
    biome_stub_id = _biome_stub_id(
        material_key=material_key,
        temperature_kelvin=temperature_value,
        ocean_fraction_permille=ocean_fraction_permille,
    )
    height_proxy = _height_proxy(tile_seed=generator_seed, material_key=material_key, surface_priors_row=surface_priors_row)
    pressure_value = _pressure_proxy_value(atmosphere_class_id=atmosphere_class_id, surface_priors_row=surface_priors_row)
    occupancy_fraction = 700 if material_key == "ocean" else 1000

    tile_artifact_row = {
        "tile_object_id": tile_object_id,
        "planet_object_id": planet_object_token,
        "tile_cell_key": dict(surface_cell_key),
        "elevation_params_ref": {
            "noise_seed": _named_substream_seed(generator_seed, "rng.worldgen.surface.elevation"),
            "height_proxy": int(height_proxy),
            "macro_relief_permille": int(200 + (_hash_int(generator_seed, "macro_relief") % 801)),
            "ridge_bias_permille": int(_hash_int(generator_seed, "ridge_bias") % 1000),
            "coastal_bias_permille": int(ocean_fraction_permille),
        },
        "material_baseline_id": material_baseline_id,
        "biome_stub_id": biome_stub_id,
        "deterministic_fingerprint": "",
        "extensions": {
            "ancestor_world_cell_key": dict(ancestor_key),
            "parent_system_object_id": str(_as_map(planet_basic_row.get("extensions")).get("parent_system_object_id", "")).strip(),
            "parent_star_object_id": str(_as_map(planet_basic_row.get("extensions")).get("parent_star_object_id", "")).strip(),
            "latitude_mdeg": int(latitude_mdeg),
            "route_tags": list(planet_tags),
            "routing_id": str(route_row.get("routing_id", "")).strip(),
            "selected_generator_id": str(selected_generator_row.get("generator_id", "")).strip(),
            "handler_id": str(handler_row.get("handler_id", "")).strip(),
            "source": MW_SURFACE_REFINER_L3_VERSION,
        },
    }
    tile_artifact_row["deterministic_fingerprint"] = canonical_sha256(dict(tile_artifact_row, deterministic_fingerprint=""))

    field_layers = [
        build_field_layer(
            field_id="field.temperature.surface.{}".format(planet_object_token),
            field_type_id="field.temperature",
            spatial_scope_id="spatial.surface.{}".format(planet_object_token),
            resolution_level="macro",
            update_policy_id="field.profile_defined",
            extensions={
                "topology_profile_id": str(surface_cell_key.get("topology_profile_id", "")).strip(),
                "partition_profile_id": str(surface_cell_key.get("partition_profile_id", "")).strip(),
                "chart_id": str(surface_cell_key.get("chart_id", "")).strip(),
                "storage_kind": "tile",
                "interpolation_policy_id": "interp.atlas_nearest",
                "planet_object_id": planet_object_token,
                "field_domain": "surface_macro",
                "source": MW_SURFACE_REFINER_L3_VERSION,
            },
        ),
        build_field_layer(
            field_id="field.daylight.surface.{}".format(planet_object_token),
            field_type_id="field.daylight",
            spatial_scope_id="spatial.surface.{}".format(planet_object_token),
            resolution_level="macro",
            update_policy_id="field.profile_defined",
            extensions={
                "topology_profile_id": str(surface_cell_key.get("topology_profile_id", "")).strip(),
                "partition_profile_id": str(surface_cell_key.get("partition_profile_id", "")).strip(),
                "chart_id": str(surface_cell_key.get("chart_id", "")).strip(),
                "storage_kind": "tile",
                "interpolation_policy_id": "interp.atlas_nearest",
                "planet_object_id": planet_object_token,
                "field_domain": "surface_macro",
                "source": MW_SURFACE_REFINER_L3_VERSION,
            },
        ),
    ]
    field_initializations = [
        build_field_cell(
            field_id="field.temperature.surface.{}".format(planet_object_token),
            value=int(temperature_value),
            last_updated_tick=max(0, _as_int(current_tick, 0)),
            geo_cell_key=surface_cell_key,
            extensions={
                "field_type_id": "field.temperature",
                "planet_object_id": planet_object_token,
                "initialization_kind": "mw3_surface_temperature",
                "source": MW_SURFACE_REFINER_L3_VERSION,
            },
        ),
        build_field_cell(
            field_id="field.daylight.surface.{}".format(planet_object_token),
            value=int(daylight_value),
            last_updated_tick=max(0, _as_int(current_tick, 0)),
            geo_cell_key=surface_cell_key,
            extensions={
                "field_type_id": "field.daylight",
                "planet_object_id": planet_object_token,
                "initialization_kind": "mw3_surface_daylight",
                "source": MW_SURFACE_REFINER_L3_VERSION,
            },
        ),
    ]
    if atmosphere_class_id and atmosphere_class_id != "atmo.none":
        field_layers.append(
            build_field_layer(
                field_id="field.pressure_stub.surface.{}".format(planet_object_token),
                field_type_id="field.pressure_stub",
                spatial_scope_id="spatial.surface.{}".format(planet_object_token),
                resolution_level="macro",
                update_policy_id="field.profile_defined",
                extensions={
                    "topology_profile_id": str(surface_cell_key.get("topology_profile_id", "")).strip(),
                    "partition_profile_id": str(surface_cell_key.get("partition_profile_id", "")).strip(),
                    "chart_id": str(surface_cell_key.get("chart_id", "")).strip(),
                    "storage_kind": "tile",
                    "interpolation_policy_id": "interp.atlas_nearest",
                    "planet_object_id": planet_object_token,
                    "field_domain": "surface_macro",
                    "source": MW_SURFACE_REFINER_L3_VERSION,
                },
            )
        )
        field_initializations.append(
            build_field_cell(
                field_id="field.pressure_stub.surface.{}".format(planet_object_token),
                value=int(pressure_value),
                last_updated_tick=max(0, _as_int(current_tick, 0)),
                geo_cell_key=surface_cell_key,
                extensions={
                    "field_type_id": "field.pressure_stub",
                    "planet_object_id": planet_object_token,
                    "initialization_kind": "mw3_surface_pressure",
                    "source": MW_SURFACE_REFINER_L3_VERSION,
                },
            )
        )

    geometry_row = build_geometry_cell_state(
        geo_cell_key=surface_cell_key,
        material_id=material_baseline_id,
        occupancy_fraction=occupancy_fraction,
        height_proxy=int(height_proxy),
        extensions={
            "tile_object_id": tile_object_id,
            "planet_object_id": planet_object_token,
            "initialization_kind": "mw3_surface_macro",
            "source": MW_SURFACE_REFINER_L3_VERSION,
        },
    )
    payload = {
        "result": "complete",
        "surface_priors_id": surface_priors_id,
        "routing_id": str(route_row.get("routing_id", "")).strip(),
        "selected_generator_id": str(selected_generator_row.get("generator_id", "")).strip(),
        "handler_id": str(handler_row.get("handler_id", "")).strip(),
        "generated_object_rows": [dict(object_row)],
        "generated_surface_tile_artifact_rows": normalize_surface_tile_artifact_rows([tile_artifact_row]),
        "field_layers": [dict(row) for row in list(field_layers or [])],
        "field_initializations": [dict(row) for row in list(field_initializations or [])],
        "geometry_initializations": [dict(geometry_row)],
        "surface_summary": {
            "planet_object_id": planet_object_token,
            "tile_object_id": tile_object_id,
            "temperature_value": int(temperature_value),
            "daylight_value": int(daylight_value),
            "pressure_value": int(pressure_value),
            "material_baseline_id": material_baseline_id,
            "biome_stub_id": biome_stub_id,
            "latitude_mdeg": int(latitude_mdeg),
            "current_tick": int(max(0, _as_int(current_tick, 0))),
            "deterministic_fingerprint": "",
        },
        "deterministic_fingerprint": "",
    }
    payload["surface_summary"]["deterministic_fingerprint"] = canonical_sha256(dict(payload["surface_summary"], deterministic_fingerprint=""))
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_SURFACE_PRIORS_ID",
    "MW_SURFACE_REFINER_L3_VERSION",
    "SURFACE_GENERATOR_REGISTRY_REL",
    "SURFACE_GENERATOR_ROUTING_REGISTRY_REL",
    "SURFACE_PRIORS_REGISTRY_REL",
    "build_planet_surface_cell_key",
    "generate_mw_surface_l3_payload",
    "normalize_surface_tile_artifact_rows",
    "surface_generator_rows",
    "surface_generator_routing_rows",
    "surface_priors_rows",
    "surface_tile_artifact_hash_chain",
]

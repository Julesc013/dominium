"""Deterministic GEO-8 cell-scoped world generation helpers."""

from __future__ import annotations

import copy
import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from src.meta_extensions_engine import normalize_extensions_tree

from src.fields import build_field_cell, build_field_layer
from src.geo.edit import build_geometry_cell_state
from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from src.geo.index.object_id_engine import geo_object_id
from src.worldgen.refinement.refinement_cache import build_refinement_cache_key
from src.worldgen.mw.mw_cell_generator import (
    galaxy_priors_rows,
    generate_mw_cell_payload,
    normalize_star_system_artifact_rows,
    normalize_star_system_seed_rows,
)
from src.worldgen.mw.mw_system_refiner_l2 import (
    generate_mw_system_l2_payload,
    normalize_planet_basic_artifact_rows,
    normalize_planet_orbit_artifact_rows,
    normalize_star_artifact_rows,
    normalize_system_l2_summary_rows,
)
from src.worldgen.mw.mw_surface_refiner_l3 import (
    generate_mw_surface_l3_payload,
    normalize_surface_tile_artifact_rows,
)
from src.worldgen.galaxy import generate_galaxy_object_stub_payload, normalize_galaxy_object_stub_rows


REFUSAL_GEO_WORLDGEN_INVALID = "refusal.geo.worldgen_invalid"
DEFAULT_REALISM_PROFILE_ID = "realism.realistic_default_milkyway_stub"
DEFAULT_GENERATOR_VERSION_ID = "gen.v0_stub"

RNG_WORLDGEN_GALAXY = "rng.worldgen.galaxy"
RNG_WORLDGEN_SYSTEM = "rng.worldgen.system"
RNG_WORLDGEN_PLANET = "rng.worldgen.planet"
RNG_WORLDGEN_SURFACE = "rng.worldgen.surface"

_REALISM_PROFILE_REGISTRY_REL = os.path.join("data", "registries", "realism_profile_registry.json")
_GENERATOR_VERSION_REGISTRY_REL = os.path.join("data", "registries", "generator_version_registry.json")
_WORLDGEN_CACHE: Dict[str, dict] = {}
_WORLDGEN_CACHE_MAX = 256
_WORLDGEN_VERSION = "GEO8-7"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return dict(normalize_extensions_tree(json.load(handle)) or {})
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


def _sorted_unique_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


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


def _geo_cell_key_sort_tuple(value: object) -> Tuple[str, Tuple[int, ...], int, str, str]:
    row = _coerce_cell_key(value)
    if not row:
        return ("", tuple(), 0, "", "")
    return (
        str(row.get("chart_id", "")).strip(),
        tuple(int(item) for item in list(row.get("index_tuple") or [])),
        int(max(0, _as_int(row.get("refinement_level", 0), 0))),
        str(row.get("partition_profile_id", "")).strip(),
        str(row.get("topology_profile_id", "")).strip(),
    )


def _cache_lookup(cache_key: str) -> dict | None:
    cached = _WORLDGEN_CACHE.get(str(cache_key))
    if not isinstance(cached, dict):
        return None
    return copy.deepcopy(cached)


def _cache_store(cache_key: str, payload: Mapping[str, object]) -> dict:
    _WORLDGEN_CACHE[str(cache_key)] = copy.deepcopy(dict(payload))
    if len(_WORLDGEN_CACHE) > _WORLDGEN_CACHE_MAX:
        for stale_key in sorted(_WORLDGEN_CACHE.keys())[:-_WORLDGEN_CACHE_MAX]:
            _WORLDGEN_CACHE.pop(stale_key, None)
    return copy.deepcopy(dict(payload))


def worldgen_cache_clear() -> None:
    _WORLDGEN_CACHE.clear()


def worldgen_cache_snapshot() -> dict:
    return dict((key, copy.deepcopy(_WORLDGEN_CACHE[key])) for key in sorted(_WORLDGEN_CACHE.keys()))


def _refusal(message: str, details: Mapping[str, object] | None = None, *, refusal_code: str = REFUSAL_GEO_WORLDGEN_INVALID) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": str(refusal_code),
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _realism_profile_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(_REALISM_PROFILE_REGISTRY_REL), row_key="realism_profiles", id_key="realism_profile_id")


def _generator_version_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(_GENERATOR_VERSION_REGISTRY_REL),
        row_key="generator_versions",
        id_key="generator_version_id",
    )


def realism_profile_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(_REALISM_PROFILE_REGISTRY_REL))


def generator_version_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(_GENERATOR_VERSION_REGISTRY_REL))


def build_worldgen_request(
    *,
    request_id: str,
    geo_cell_key: Mapping[str, object],
    refinement_level: int,
    reason: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        raise ValueError("geo_cell_key is required")
    token = str(reason or "").strip().lower()
    if token not in {"roi", "query", "pathing", "system_spawn"}:
        raise ValueError("reason is invalid")
    payload = {
        "schema_version": "1.0.0",
        "request_id": str(request_id or "").strip(),
        "geo_cell_key": dict(cell_key),
        "refinement_level": int(max(0, _as_int(refinement_level, 0))),
        "reason": token,
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_worldgen_request(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    request_id = str(payload.get("request_id", "")).strip()
    if not request_id:
        request_id = "worldgen_request.{}".format(canonical_sha256(_as_map(payload))[:16])
    return build_worldgen_request(
        request_id=request_id,
        geo_cell_key=_as_map(payload.get("geo_cell_key")),
        refinement_level=_as_int(payload.get("refinement_level", 0), 0),
        reason=str(payload.get("reason", "")).strip() or "query",
        extensions=_as_map(payload.get("extensions")),
    )


def worldgen_request_hash(row: Mapping[str, object] | None) -> str:
    payload = normalize_worldgen_request(row)
    semantic = dict(payload)
    semantic.pop("request_id", None)
    semantic.pop("deterministic_fingerprint", None)
    return canonical_sha256(semantic)


def normalize_worldgen_request_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("request_id", ""))):
        try:
            normalized = normalize_worldgen_request(row)
        except ValueError:
            continue
        out[str(normalized.get("request_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def worldgen_request_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_worldgen_request_rows(rows))


def _normalize_field_initializations(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=canonical_sha256):
        field_id = str(row.get("field_id", "")).strip()
        cell_id = str(row.get("cell_id", "")).strip()
        if not field_id:
            continue
        key = "{}::{}".format(field_id, cell_id or canonical_sha256(_as_map(_as_map(row.get("extensions")).get("geo_cell_key"))))
        out[key] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys())]


def _normalize_geometry_initializations(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        try:
            normalized = build_geometry_cell_state(
                geo_cell_key=_as_map(row.get("geo_cell_key")),
                material_id=str(row.get("material_id", "")).strip(),
                occupancy_fraction=_as_int(row.get("occupancy_fraction", 0), 0),
                height_proxy=(None if row.get("height_proxy") is None else _as_int(row.get("height_proxy", 0), 0)),
                permeability_proxy=(None if row.get("permeability_proxy") is None else _as_int(row.get("permeability_proxy", 0), 0)),
                conductance_proxy=(None if row.get("conductance_proxy") is None else _as_int(row.get("conductance_proxy", 0), 0)),
                extensions=_as_map(row.get("extensions")),
            )
        except ValueError:
            continue
        out[canonical_sha256(_semantic_cell_key(normalized.get("geo_cell_key") or {}))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_worldgen_result(
    *,
    geo_cell_key: Mapping[str, object],
    generator_version_id: str,
    realism_profile_id: str,
    spawned_object_ids: Sequence[object],
    field_initializations: object,
    geometry_initializations: object,
    result_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        raise ValueError("geo_cell_key is required")
    object_ids = _sorted_unique_strings(spawned_object_ids)
    fields = _normalize_field_initializations(field_initializations)
    geometry = _normalize_geometry_initializations(geometry_initializations)
    out = {
        "schema_version": "1.0.0",
        "result_id": str(result_id or "").strip(),
        "geo_cell_key": dict(cell_key),
        "generator_version_id": str(generator_version_id or "").strip() or DEFAULT_GENERATOR_VERSION_ID,
        "realism_profile_id": str(realism_profile_id or "").strip() or DEFAULT_REALISM_PROFILE_ID,
        "spawned_object_ids": object_ids,
        "field_initializations": fields,
        "geometry_initializations": geometry,
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    if not out["result_id"]:
        semantic = dict(out)
        semantic["result_id"] = ""
        semantic["deterministic_fingerprint"] = ""
        out["result_id"] = "worldgen_result.{}".format(canonical_sha256(semantic)[:16])
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def normalize_worldgen_result(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    return build_worldgen_result(
        result_id=str(payload.get("result_id", "")).strip(),
        geo_cell_key=_as_map(payload.get("geo_cell_key")),
        generator_version_id=str(payload.get("generator_version_id", "")).strip() or DEFAULT_GENERATOR_VERSION_ID,
        realism_profile_id=str(payload.get("realism_profile_id", "")).strip() or DEFAULT_REALISM_PROFILE_ID,
        spawned_object_ids=_as_list(payload.get("spawned_object_ids")),
        field_initializations=payload.get("field_initializations"),
        geometry_initializations=payload.get("geometry_initializations"),
        extensions=_as_map(payload.get("extensions")),
    )


def normalize_worldgen_result_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("result_id", ""))):
        try:
            normalized = normalize_worldgen_result(row)
        except ValueError:
            continue
        out[str(normalized.get("result_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def worldgen_result_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_worldgen_result_rows(rows))


def worldgen_spawned_object_hash_chain(rows: object) -> str:
    object_rows = [dict(item) for item in list(rows or []) if isinstance(item, Mapping)]
    normalized = []
    for row in sorted(object_rows, key=lambda item: (str(item.get("object_id_hash", "")), str(item.get("object_kind_id", "")), str(item.get("local_subkey", "")))):
        normalized.append(
            {
                "object_id_hash": str(row.get("object_id_hash", "")).strip(),
                "object_kind_id": str(row.get("object_kind_id", "")).strip(),
                "local_subkey": str(row.get("local_subkey", "")).strip(),
                "geo_cell_key": _as_map(row.get("geo_cell_key")),
            }
        )
    return canonical_sha256(normalized)


def worldgen_result_proof_surface(
    *,
    worldgen_requests: object,
    worldgen_results: object,
    worldgen_spawned_objects: object = None,
) -> dict:
    request_rows = normalize_worldgen_request_rows(worldgen_requests)
    result_rows = normalize_worldgen_result_rows(worldgen_results)
    object_rows = [dict(item) for item in list(worldgen_spawned_objects or []) if isinstance(item, Mapping)]
    payload = {
        "worldgen_request_hash_chain": worldgen_request_hash_chain(request_rows),
        "worldgen_result_hash_chain": worldgen_result_hash_chain(result_rows),
        "worldgen_spawned_object_hash_chain": worldgen_spawned_object_hash_chain(object_rows),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _locked_generator_version_id(universe_identity: Mapping[str, object] | None) -> str:
    payload = _as_map(universe_identity)
    return str(payload.get("generator_version_id", "")).strip() or DEFAULT_GENERATOR_VERSION_ID


def _locked_realism_profile_id(universe_identity: Mapping[str, object] | None) -> str:
    payload = _as_map(universe_identity)
    return str(payload.get("realism_profile_id", "")).strip() or DEFAULT_REALISM_PROFILE_ID


def worldgen_stream_seed(
    *,
    universe_seed: object,
    generator_version_id: str,
    realism_profile_id: str,
    geo_cell_key: Mapping[str, object],
    stream_name: str,
) -> str:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        return ""
    return canonical_sha256(
        {
            "universe_seed": str(universe_seed),
            "generator_version_id": str(generator_version_id or "").strip() or DEFAULT_GENERATOR_VERSION_ID,
            "realism_profile_id": str(realism_profile_id or "").strip() or DEFAULT_REALISM_PROFILE_ID,
            "geo_cell_key": _semantic_cell_key(cell_key),
            "stream_name": str(stream_name or "").strip(),
        }
    )


def worldgen_rng_stream_policy(
    *,
    universe_identity: Mapping[str, object] | None,
    geo_cell_key: Mapping[str, object],
    generator_version_id: str = "",
    realism_profile_id: str = "",
) -> dict:
    payload = _as_map(universe_identity)
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        return _refusal("geo_cell_key is invalid for worldgen RNG policy")
    resolved_generator_version_id = str(generator_version_id or _locked_generator_version_id(payload)).strip() or DEFAULT_GENERATOR_VERSION_ID
    resolved_realism_profile_id = str(realism_profile_id or _locked_realism_profile_id(payload)).strip() or DEFAULT_REALISM_PROFILE_ID
    streams = []
    for stream_name in (
        RNG_WORLDGEN_GALAXY,
        RNG_WORLDGEN_SYSTEM,
        RNG_WORLDGEN_PLANET,
        RNG_WORLDGEN_SURFACE,
    ):
        streams.append(
            {
                "stream_name": stream_name,
                "stream_seed": worldgen_stream_seed(
                    universe_seed=payload.get("global_seed", ""),
                    generator_version_id=resolved_generator_version_id,
                    realism_profile_id=resolved_realism_profile_id,
                    geo_cell_key=cell_key,
                    stream_name=stream_name,
                ),
            }
        )
    out = {
        "result": "complete",
        "generator_version_id": resolved_generator_version_id,
        "realism_profile_id": resolved_realism_profile_id,
        "streams": streams,
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def _hash_int(seed: str, salt: str) -> int:
    return int(canonical_sha256({"seed": str(seed), "salt": str(salt)})[:16], 16)


def _count_from_seed(seed: str, *, minimum: int, maximum: int, salt: str) -> int:
    floor = int(max(0, minimum))
    ceiling = int(max(floor, maximum))
    if floor == ceiling:
        return floor
    return floor + (_hash_int(seed, salt) % (ceiling - floor + 1))


def _material_id_from_surface_seed(surface_seed: str, realism_profile_id: str) -> str:
    realism = str(realism_profile_id or "").strip().lower()
    if "flat_world" in realism:
        return "material.soil_basic"
    if "fantasy" in realism:
        return "material.wood_basic"
    choices = ("material.stone_basic", "material.soil_basic", "material.sand_basic")
    return str(choices[_hash_int(surface_seed, "material_id") % len(choices)])


def _build_field_layers_for_result(cell_key: Mapping[str, object]) -> List[dict]:
    coerced = _coerce_cell_key(cell_key)
    chart_id = str(coerced.get("chart_id", "")).strip() if coerced else "chart.global"
    return [
        build_field_layer(
            field_id="field.temperature",
            field_type_id="field.temperature",
            spatial_scope_id="spatial.worldgen.base",
            resolution_level="macro",
            update_policy_id="field.static_default",
            extensions={"chart_id": chart_id, "source": "GEO8-4"},
        )
    ]


def _build_field_initializations(cell_key: Mapping[str, object], planet_seed: str) -> List[dict]:
    temperature = 240 + (_hash_int(planet_seed, "temperature") % 120)
    return [
        build_field_cell(
            field_id="field.temperature",
            value=int(temperature),
            last_updated_tick=0,
            geo_cell_key=cell_key,
            extensions={"source": "GEO8-4", "initialization_kind": "worldgen_base"},
        )
    ]


def _build_geometry_initializations(cell_key: Mapping[str, object], surface_seed: str, realism_profile_id: str, refinement_level: int) -> List[dict]:
    if int(max(0, refinement_level)) < 3:
        return []
    occupancy = 1000 if (_hash_int(surface_seed, "solid") % 5) else 700
    height_proxy = _hash_int(surface_seed, "height_proxy") % 4000
    return [
        build_geometry_cell_state(
            geo_cell_key=cell_key,
            material_id=_material_id_from_surface_seed(surface_seed, realism_profile_id),
            occupancy_fraction=int(occupancy),
            height_proxy=int(height_proxy),
            extensions={"source": "GEO8-4", "initialization_kind": "worldgen_macro_surface"},
        )
    ]


def _spawn_object_row(
    *,
    universe_identity_hash: str,
    cell_key: Mapping[str, object],
    object_kind_id: str,
    local_subkey: str,
) -> dict:
    object_id_payload = geo_object_id(
        universe_identity_hash=universe_identity_hash,
        cell_key=cell_key,
        object_kind_id=object_kind_id,
        local_subkey=local_subkey,
    )
    if str(object_id_payload.get("result", "")) != "complete":
        return {}
    identity = _as_map(object_id_payload.get("object_identity"))
    return {
        "object_id_hash": str(object_id_payload.get("object_id_hash", "")).strip(),
        "object_kind_id": str(identity.get("object_kind_id", "")).strip(),
        "local_subkey": str(identity.get("local_subkey", "")).strip(),
        "geo_cell_key": _as_map(identity.get("geo_cell_key")),
    }


def _system_seed_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in normalize_star_system_seed_rows(rows):
        local_index = int(max(0, _as_int(row.get("local_index", 0), 0)))
        extensions = _as_map(row.get("extensions"))
        normalized = {
            "cell_key": _as_map(row.get("cell_key")),
            "local_index": local_index,
            "local_subkey": str(extensions.get("local_subkey", "star_system:{}".format(local_index))).strip() or "star_system:{}".format(local_index),
            "seed_subkey": str(extensions.get("seed_subkey", "")).strip(),
            "system_seed": str(row.get("system_seed_value", "")).strip(),
            "system_seed_value": str(row.get("system_seed_value", "")).strip(),
            "object_id": str(row.get("object_id", "")).strip(),
            "object_id_hash": str(row.get("object_id", "")).strip(),
            "metallicity_permille": int(max(0, _as_int(extensions.get("metallicity_permille", 0), 0))),
            "age_bucket": str(extensions.get("age_bucket", "")).strip(),
            "imf_bucket": str(extensions.get("imf_bucket", "")).strip(),
            "habitable_filter_bias_permille": int(max(0, _as_int(extensions.get("habitable_filter_bias_permille", 0), 0))),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": extensions,
        }
        out["{:08d}".format(local_index)] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _star_system_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in normalize_star_system_artifact_rows(rows):
        object_id = str(row.get("object_id", "")).strip()
        if not object_id:
            continue
        extensions = _as_map(row.get("extensions"))
        normalized = {
            "object_id": object_id,
            "object_id_hash": object_id,
            "system_seed_value": str(row.get("system_seed_value", "")).strip(),
            "metallicity_proxy": _as_map(row.get("metallicity_proxy")),
            "galaxy_position_ref": _as_map(row.get("galaxy_position_ref")),
            "local_index": int(max(0, _as_int(extensions.get("local_index", 0), 0))),
            "local_subkey": str(extensions.get("local_subkey", "")).strip(),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": extensions,
        }
        out[object_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _star_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in normalize_star_artifact_rows(rows):
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            out[object_id] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys())]


def _planet_orbit_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in normalize_planet_orbit_artifact_rows(rows):
        planet_object_id = str(row.get("planet_object_id", "")).strip()
        if planet_object_id:
            out[planet_object_id] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys())]


def _planet_basic_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in normalize_planet_basic_artifact_rows(rows):
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            out[object_id] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys())]


def _surface_tile_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in normalize_surface_tile_artifact_rows(rows):
        tile_object_id = str(row.get("tile_object_id", "")).strip()
        if tile_object_id:
            out[tile_object_id] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys())]


def _galaxy_object_stub_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in normalize_galaxy_object_stub_rows(rows):
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            out[object_id] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys())]


def _system_l2_summary_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in normalize_system_l2_summary_rows(rows):
        system_object_id = str(row.get("system_object_id", "")).strip()
        if system_object_id:
            out[system_object_id] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys())]


def _generated_object_rows(
    *,
    universe_identity_hash: str,
    cell_key: Mapping[str, object],
    refinement_level: int,
    system_seed_rows: object,
    l2_object_rows: object = None,
    l3_object_rows: object = None,
) -> List[dict]:
    seeded_systems = _system_seed_rows(system_seed_rows)
    out = [
        _spawn_object_row(
            universe_identity_hash=universe_identity_hash,
            cell_key=cell_key,
            object_kind_id="kind.galaxy_cell",
            local_subkey="galaxy_cell:0",
        )
    ]
    if int(max(0, refinement_level)) >= 1:
        for system_row in seeded_systems:
            out.append(
                _spawn_object_row(
                    universe_identity_hash=universe_identity_hash,
                    cell_key=cell_key,
                    object_kind_id="kind.star_system",
                    local_subkey=str(system_row.get("local_subkey", "")).strip(),
                )
            )
    if int(max(0, refinement_level)) >= 2:
        for row in list(l2_object_rows or []):
            if not isinstance(row, Mapping):
                continue
            if str(dict(row).get("object_id_hash", "")).strip():
                out.append(dict(row))
    if int(max(0, refinement_level)) >= 3:
        for row in list(l3_object_rows or []):
            if not isinstance(row, Mapping):
                continue
            if str(dict(row).get("object_id_hash", "")).strip():
                out.append(dict(row))
    return [dict(row) for row in sorted((row for row in out if row), key=lambda item: (str(item.get("object_kind_id", "")), str(item.get("local_subkey", "")), str(item.get("object_id_hash", ""))))]


def _cache_key(
    *,
    universe_identity: Mapping[str, object],
    worldgen_request: Mapping[str, object],
    generator_version_id: str,
    realism_profile_id: str,
    universe_contract_bundle_hash: str = "",
    overlay_manifest_hash: str = "",
    mod_policy_id: str = "",
    current_tick: int = 0,
) -> str:
    request = normalize_worldgen_request(worldgen_request)
    del current_tick
    identity_payload = _as_map(universe_identity)
    return build_refinement_cache_key(
        universe_identity_hash=_resolved_universe_identity_hash(identity_payload),
        universe_contract_bundle_hash=(
            str(universe_contract_bundle_hash or "").strip()
            or str(identity_payload.get("universe_contract_bundle_hash", "")).strip()
        ),
        generator_version_id=str(generator_version_id),
        realism_profile_id=str(realism_profile_id),
        overlay_manifest_hash=(
            str(overlay_manifest_hash or "").strip()
            or str(_as_map(request.get("extensions")).get("overlay_manifest_hash", "")).strip()
        ),
        mod_policy_id=(
            str(mod_policy_id or "").strip()
            or str(_as_map(request.get("extensions")).get("mod_policy_id", "")).strip()
        ),
        geo_cell_key=_as_map(request.get("geo_cell_key")),
        refinement_level=int(max(0, _as_int(request.get("refinement_level", 0), 0))),
    )


def _resolved_universe_identity_hash(universe_identity: Mapping[str, object] | None) -> str:
    payload = _as_map(universe_identity)
    token = str(payload.get("identity_hash", "")).strip()
    if token:
        return token
    semantic = {
        "universe_id": str(payload.get("universe_id", "")).strip(),
        "global_seed": str(payload.get("global_seed", "")).strip(),
        "topology_profile_id": str(payload.get("topology_profile_id", "")).strip(),
        "partition_profile_id": str(payload.get("partition_profile_id", "")).strip(),
        "generator_version_id": _locked_generator_version_id(payload),
        "realism_profile_id": _locked_realism_profile_id(payload),
    }
    return canonical_sha256(semantic)


def _surface_request_context(cell_key: Mapping[str, object] | None) -> dict:
    row = _coerce_cell_key(cell_key)
    if not row:
        return {}
    ext = _as_map(row.get("extensions"))
    planet_object_id = str(ext.get("planet_object_id", "")).strip()
    ancestor_world_cell_key = _coerce_cell_key(ext.get("ancestor_world_cell_key"))
    if not planet_object_id or not ancestor_world_cell_key:
        return {}
    return {
        "planet_object_id": planet_object_id,
        "ancestor_world_cell_key": ancestor_world_cell_key,
        "planet_tags": sorted(str(item).strip() for item in list(ext.get("planet_tags") or []) if str(item).strip()),
        "base_chart_id": str(ext.get("base_chart_id", "")).strip(),
    }


def generate_worldgen_result(
    *,
    universe_identity: Mapping[str, object] | None,
    worldgen_request: Mapping[str, object] | None,
    generator_version_id: str = "",
    realism_profile_id: str = "",
    universe_contract_bundle_hash: str = "",
    overlay_manifest_hash: str = "",
    mod_policy_id: str = "",
    realism_profile_registry_payload: Mapping[str, object] | None = None,
    generator_version_registry_payload: Mapping[str, object] | None = None,
    current_tick: int = 0,
    cache_enabled: bool = True,
) -> dict:
    identity = _as_map(universe_identity)
    try:
        request = normalize_worldgen_request(worldgen_request)
    except ValueError:
        return _refusal("worldgen_request is invalid")
    cell_key = _coerce_cell_key(request.get("geo_cell_key"))
    if not cell_key:
        return _refusal("worldgen_request.geo_cell_key is invalid")

    locked_generator_version_id = _locked_generator_version_id(identity)
    locked_realism_profile_id = _locked_realism_profile_id(identity)
    requested_generator_version_id = str(generator_version_id or _as_map(request.get("extensions")).get("generator_version_id", "")).strip()
    requested_realism_profile_id = str(realism_profile_id or _as_map(request.get("extensions")).get("realism_profile_id", "")).strip()
    resolved_generator_version_id = requested_generator_version_id or locked_generator_version_id
    resolved_realism_profile_id = requested_realism_profile_id or locked_realism_profile_id
    if resolved_generator_version_id != locked_generator_version_id:
        return _refusal(
            "generator_version_id override breaks immutable universe lineage",
            {
                "locked_generator_version_id": locked_generator_version_id,
                "requested_generator_version_id": resolved_generator_version_id,
            },
            refusal_code="refusal.geo.generator_version_locked",
        )
    if resolved_realism_profile_id != locked_realism_profile_id:
        return _refusal(
            "realism_profile_id override breaks immutable universe lineage",
            {
                "locked_realism_profile_id": locked_realism_profile_id,
                "requested_realism_profile_id": resolved_realism_profile_id,
            },
            refusal_code="refusal.geo.realism_profile_locked",
        )

    realism_rows = _realism_profile_rows(realism_profile_registry_payload)
    generator_rows = _generator_version_rows(generator_version_registry_payload)
    if resolved_realism_profile_id not in realism_rows:
        return _refusal("realism_profile_id is not declared", {"realism_profile_id": resolved_realism_profile_id})
    if resolved_generator_version_id not in generator_rows:
        return _refusal("generator_version_id is not declared", {"generator_version_id": resolved_generator_version_id})

    refinement_level = int(max(0, _as_int(request.get("refinement_level", 0), 0)))
    current_tick_value = int(max(0, _as_int(current_tick, 0)))
    surface_request = _surface_request_context(cell_key) if refinement_level >= 3 else {}
    cache_key = _cache_key(
        universe_identity=identity,
        worldgen_request=request,
        generator_version_id=resolved_generator_version_id,
        realism_profile_id=resolved_realism_profile_id,
        universe_contract_bundle_hash=str(universe_contract_bundle_hash or "").strip(),
        overlay_manifest_hash=str(overlay_manifest_hash or "").strip(),
        mod_policy_id=str(mod_policy_id or "").strip(),
        current_tick=current_tick_value,
    )
    cached = _cache_lookup(cache_key) if cache_enabled else None
    if cached is not None:
        payload = dict(cached)
        payload["cache_hit"] = True
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    universe_identity_hash = _resolved_universe_identity_hash(identity)
    realism_row = realism_rows.get(resolved_realism_profile_id)
    galaxy_priors_by_id = galaxy_priors_rows()

    mw_cell_payload: dict = {}
    system_seed_rows: List[dict] = []
    star_system_artifact_rows: List[dict] = []
    l2_payload = {}
    star_artifact_rows: List[dict] = []
    planet_orbit_artifact_rows: List[dict] = []
    planet_basic_artifact_rows: List[dict] = []
    system_l2_summary_rows: List[dict] = []
    l2_object_rows: List[dict] = []
    galaxy_object_stub_artifact_rows: List[dict] = []
    generated_object_rows: List[dict] = []
    field_layers: List[dict] = []
    field_initializations: List[dict] = []
    geometry_initializations: List[dict] = []
    surface_tile_artifact_rows: List[dict] = []
    surface_payload: dict = {}
    named_rng_streams: List[dict] = []
    ancestor_named_rng_streams: List[dict] = []

    if surface_request:
        ancestor_world_cell_key = _as_map(surface_request.get("ancestor_world_cell_key"))
        surface_rng_policy = worldgen_rng_stream_policy(
            universe_identity=identity,
            geo_cell_key=cell_key,
            generator_version_id=resolved_generator_version_id,
            realism_profile_id=resolved_realism_profile_id,
        )
        if str(surface_rng_policy.get("result", "")) != "complete":
            return dict(surface_rng_policy)
        ancestor_rng_policy = worldgen_rng_stream_policy(
            universe_identity=identity,
            geo_cell_key=ancestor_world_cell_key,
            generator_version_id=resolved_generator_version_id,
            realism_profile_id=resolved_realism_profile_id,
        )
        if str(ancestor_rng_policy.get("result", "")) != "complete":
            return dict(ancestor_rng_policy)
        named_rng_streams = [dict(row) for row in list(surface_rng_policy.get("streams") or []) if isinstance(row, Mapping)]
        ancestor_named_rng_streams = [dict(row) for row in list(ancestor_rng_policy.get("streams") or []) if isinstance(row, Mapping)]
        surface_stream_seed_by_name = dict(
            (str(row.get("stream_name", "")).strip(), str(row.get("stream_seed", "")).strip())
            for row in named_rng_streams
        )
        ancestor_stream_seed_by_name = dict(
            (str(row.get("stream_name", "")).strip(), str(row.get("stream_seed", "")).strip())
            for row in ancestor_named_rng_streams
        )
        mw_cell_payload = generate_mw_cell_payload(
            universe_identity_hash=universe_identity_hash,
            geo_cell_key=ancestor_world_cell_key,
            realism_profile_row=realism_row,
            galaxy_stream_seed=str(ancestor_stream_seed_by_name.get(RNG_WORLDGEN_GALAXY, "")).strip(),
            system_stream_seed=str(ancestor_stream_seed_by_name.get(RNG_WORLDGEN_SYSTEM, "")).strip(),
        )
        if str(mw_cell_payload.get("result", "")) != "complete":
            return _refusal(
                str(mw_cell_payload.get("message", "Milky Way cell generation refused")),
                _as_map(mw_cell_payload.get("details")),
            )
        system_seed_rows = _system_seed_rows(mw_cell_payload.get("system_seed_rows"))
        star_system_artifact_rows = _star_system_artifact_rows(mw_cell_payload.get("star_system_artifact_rows"))
        l2_payload = generate_mw_system_l2_payload(
            universe_identity_hash=universe_identity_hash,
            geo_cell_key=ancestor_world_cell_key,
            realism_profile_row=realism_row,
            star_system_artifact_rows=star_system_artifact_rows,
        )
        if str(l2_payload.get("result", "")) != "complete":
            return _refusal(
                str(l2_payload.get("message", "MW-2 system refinement refused")),
                _as_map(l2_payload.get("details")),
            )
        star_artifact_rows = _star_artifact_rows(l2_payload.get("generated_star_artifact_rows"))
        planet_orbit_artifact_rows = _planet_orbit_artifact_rows(l2_payload.get("generated_planet_orbit_artifact_rows"))
        planet_basic_artifact_rows = _planet_basic_artifact_rows(l2_payload.get("generated_planet_basic_artifact_rows"))
        system_l2_summary_rows = _system_l2_summary_rows(l2_payload.get("generated_system_l2_summary_rows"))
        l2_object_rows = [dict(row) for row in list(l2_payload.get("generated_object_rows") or []) if isinstance(row, Mapping)]
        surface_payload = generate_mw_surface_l3_payload(
            universe_identity_hash=universe_identity_hash,
            surface_geo_cell_key=cell_key,
            ancestor_world_cell_key=ancestor_world_cell_key,
            realism_profile_row=realism_row,
            planet_object_id=str(surface_request.get("planet_object_id", "")).strip(),
            planet_basic_artifact_rows=planet_basic_artifact_rows,
            planet_orbit_artifact_rows=planet_orbit_artifact_rows,
            star_artifact_rows=star_artifact_rows,
            surface_stream_seed=str(surface_stream_seed_by_name.get(RNG_WORLDGEN_SURFACE, "")).strip(),
            current_tick=current_tick_value,
        )
        if str(surface_payload.get("result", "")) != "complete":
            return _refusal(
                str(surface_payload.get("message", "MW-3 surface refinement refused")),
                _as_map(surface_payload.get("details")),
            )
        generated_object_rows = [dict(row) for row in list(surface_payload.get("generated_object_rows") or []) if isinstance(row, Mapping)]
        surface_tile_artifact_rows = _surface_tile_artifact_rows(surface_payload.get("generated_surface_tile_artifact_rows"))
        field_layers = [dict(row) for row in list(surface_payload.get("field_layers") or []) if isinstance(row, Mapping)]
        field_initializations = [dict(row) for row in list(surface_payload.get("field_initializations") or []) if isinstance(row, Mapping)]
        geometry_initializations = [dict(row) for row in list(surface_payload.get("geometry_initializations") or []) if isinstance(row, Mapping)]
    else:
        rng_policy = worldgen_rng_stream_policy(
            universe_identity=identity,
            geo_cell_key=cell_key,
            generator_version_id=resolved_generator_version_id,
            realism_profile_id=resolved_realism_profile_id,
        )
        if str(rng_policy.get("result", "")) != "complete":
            return dict(rng_policy)
        named_rng_streams = [dict(row) for row in list(rng_policy.get("streams") or []) if isinstance(row, Mapping)]
        stream_seed_by_name = dict(
            (str(row.get("stream_name", "")).strip(), str(row.get("stream_seed", "")).strip())
            for row in named_rng_streams
        )
        system_seed = str(stream_seed_by_name.get(RNG_WORLDGEN_SYSTEM, "")).strip()
        planet_seed = str(stream_seed_by_name.get(RNG_WORLDGEN_PLANET, "")).strip()
        surface_seed = str(stream_seed_by_name.get(RNG_WORLDGEN_SURFACE, "")).strip()
        galaxy_object_stream_seed = worldgen_stream_seed(
            universe_seed=identity.get("global_seed", ""),
            generator_version_id=resolved_generator_version_id,
            realism_profile_id=resolved_realism_profile_id,
            geo_cell_key=cell_key,
            stream_name="rng.worldgen.galaxy_objects",
        )
        mw_cell_payload = generate_mw_cell_payload(
            universe_identity_hash=universe_identity_hash,
            geo_cell_key=cell_key,
            realism_profile_row=realism_row,
            galaxy_stream_seed=str(stream_seed_by_name.get(RNG_WORLDGEN_GALAXY, "")).strip(),
            system_stream_seed=system_seed,
        )
        if str(mw_cell_payload.get("result", "")) != "complete":
            return _refusal(
                str(mw_cell_payload.get("message", "Milky Way cell generation refused")),
                _as_map(mw_cell_payload.get("details")),
            )
        galaxy_object_payload = generate_galaxy_object_stub_payload(
            universe_identity_hash=universe_identity_hash,
            geo_cell_key=cell_key,
            galaxy_priors_row=_as_map(galaxy_priors_by_id.get(str(mw_cell_payload.get("galaxy_priors_id", "")).strip())),
            galaxy_priors_id=str(mw_cell_payload.get("galaxy_priors_id", "")).strip(),
            stream_seed=galaxy_object_stream_seed,
        )
        galaxy_object_stub_artifact_rows = _galaxy_object_stub_artifact_rows(galaxy_object_payload.get("artifact_rows"))
        system_seed_rows = _system_seed_rows(mw_cell_payload.get("system_seed_rows"))
        star_system_artifact_rows = (
            _star_system_artifact_rows(mw_cell_payload.get("star_system_artifact_rows"))
            if refinement_level >= 1
            else []
        )
        if refinement_level >= 2:
            l2_payload = generate_mw_system_l2_payload(
                universe_identity_hash=universe_identity_hash,
                geo_cell_key=cell_key,
                realism_profile_row=realism_row,
                star_system_artifact_rows=star_system_artifact_rows,
            )
            if str(l2_payload.get("result", "")) != "complete":
                return _refusal(
                    str(l2_payload.get("message", "MW-2 system refinement refused")),
                    _as_map(l2_payload.get("details")),
                )
            star_artifact_rows = _star_artifact_rows(l2_payload.get("generated_star_artifact_rows"))
            planet_orbit_artifact_rows = _planet_orbit_artifact_rows(l2_payload.get("generated_planet_orbit_artifact_rows"))
            planet_basic_artifact_rows = _planet_basic_artifact_rows(l2_payload.get("generated_planet_basic_artifact_rows"))
            system_l2_summary_rows = _system_l2_summary_rows(l2_payload.get("generated_system_l2_summary_rows"))
            l2_object_rows = [dict(row) for row in list(l2_payload.get("generated_object_rows") or []) if isinstance(row, Mapping)]
        generated_object_rows = _generated_object_rows(
            universe_identity_hash=universe_identity_hash,
            cell_key=cell_key,
            refinement_level=refinement_level,
            system_seed_rows=system_seed_rows,
            l2_object_rows=l2_object_rows,
        )
        if galaxy_object_stub_artifact_rows:
            existing_hashes = set(str(row.get("object_id_hash", "")).strip() for row in generated_object_rows)
            for row in list(galaxy_object_payload.get("generated_object_rows") or []):
                if not isinstance(row, Mapping):
                    continue
                object_id_hash = str(dict(row).get("object_id_hash", "")).strip()
                if (not object_id_hash) or object_id_hash in existing_hashes:
                    continue
                generated_object_rows.append(dict(row))
                existing_hashes.add(object_id_hash)
            generated_object_rows = sorted(
                generated_object_rows,
                key=lambda row: (
                    str(row.get("object_kind_id", "")),
                    str(row.get("local_subkey", "")),
                    str(row.get("object_id_hash", "")),
                ),
            )
        field_layers = _build_field_layers_for_result(cell_key)
        field_initializations = _build_field_initializations(cell_key, planet_seed)
        geometry_initializations = _build_geometry_initializations(cell_key, surface_seed, resolved_realism_profile_id, refinement_level)

    result_extensions = {
        "source": _WORLDGEN_VERSION,
        "refinement_level": refinement_level,
        "cache_key": cache_key,
        "field_layers": field_layers,
        "generated_object_rows": generated_object_rows,
        "mw_cell_summary": _as_map(mw_cell_payload.get("cell_summary")),
        "generated_system_seed_rows": system_seed_rows,
        "generated_star_system_artifact_rows": star_system_artifact_rows,
        "generated_star_artifact_rows": star_artifact_rows,
        "generated_planet_orbit_artifact_rows": planet_orbit_artifact_rows,
        "generated_planet_basic_artifact_rows": planet_basic_artifact_rows,
        "generated_system_l2_summary_rows": system_l2_summary_rows,
        "generated_surface_tile_artifact_rows": surface_tile_artifact_rows,
        "star_system_artifact_ids": [str(row.get("object_id", "")).strip() for row in star_system_artifact_rows],
        "star_system_artifact_seed_values": [str(row.get("system_seed_value", "")).strip() for row in star_system_artifact_rows],
        "star_artifact_ids": [str(row.get("object_id", "")).strip() for row in star_artifact_rows],
        "planet_object_ids": [str(row.get("object_id", "")).strip() for row in planet_basic_artifact_rows],
        "surface_tile_artifact_ids": [str(row.get("tile_object_id", "")).strip() for row in surface_tile_artifact_rows],
        "planet_orbit_artifact_fingerprints": [str(row.get("deterministic_fingerprint", "")).strip() for row in planet_orbit_artifact_rows],
        "planet_basic_artifact_fingerprints": [str(row.get("deterministic_fingerprint", "")).strip() for row in planet_basic_artifact_rows],
        "surface_tile_artifact_fingerprints": [str(row.get("deterministic_fingerprint", "")).strip() for row in surface_tile_artifact_rows],
        "galaxy_priors_id": str(mw_cell_payload.get("galaxy_priors_id", "")).strip(),
        "system_priors_id": str(l2_payload.get("system_priors_id", "")).strip(),
        "planet_priors_id": str(l2_payload.get("planet_priors_id", "")).strip(),
        "surface_priors_id": str(surface_payload.get("surface_priors_id", "")).strip(),
        "surface_routing_id": str(surface_payload.get("routing_id", "")).strip(),
        "surface_generator_id": str(surface_payload.get("selected_generator_id", "")).strip(),
        "surface_handler_id": str(surface_payload.get("handler_id", "")).strip(),
        "surface_summary": _as_map(surface_payload.get("surface_summary")),
        "surface_request_context": surface_request,
        "named_rng_streams": list(named_rng_streams or []),
    }
    if galaxy_object_stub_artifact_rows:
        result_extensions["generated_galaxy_object_stub_artifact_rows"] = list(galaxy_object_stub_artifact_rows)
        result_extensions["galaxy_object_stub_ids"] = [
            str(row.get("object_id", "")).strip()
            for row in galaxy_object_stub_artifact_rows
        ]
    if surface_request:
        result_extensions["ancestor_named_rng_streams"] = list(ancestor_named_rng_streams or [])

    result_row = build_worldgen_result(
        geo_cell_key=cell_key,
        generator_version_id=resolved_generator_version_id,
        realism_profile_id=resolved_realism_profile_id,
        spawned_object_ids=[row.get("object_id_hash") for row in generated_object_rows],
        field_initializations=field_initializations,
        geometry_initializations=geometry_initializations,
        extensions=result_extensions,
    )
    payload = {
        "result": "complete",
        "cache_hit": False,
        "worldgen_request": dict(request),
        "worldgen_result": result_row,
        "generated_object_rows": generated_object_rows,
        "field_layers": field_layers,
        "field_initializations": field_initializations,
        "geometry_initializations": geometry_initializations,
        "generated_system_seed_rows": system_seed_rows,
        "generated_star_system_artifact_rows": star_system_artifact_rows,
        "generated_star_artifact_rows": star_artifact_rows,
        "generated_planet_orbit_artifact_rows": planet_orbit_artifact_rows,
        "generated_planet_basic_artifact_rows": planet_basic_artifact_rows,
        "generated_system_l2_summary_rows": system_l2_summary_rows,
        "generated_surface_tile_artifact_rows": surface_tile_artifact_rows,
        "mw_cell_summary": _as_map(mw_cell_payload.get("cell_summary")),
        "galaxy_priors_id": str(mw_cell_payload.get("galaxy_priors_id", "")).strip(),
        "system_priors_id": str(l2_payload.get("system_priors_id", "")).strip(),
        "planet_priors_id": str(l2_payload.get("planet_priors_id", "")).strip(),
        "surface_priors_id": str(surface_payload.get("surface_priors_id", "")).strip(),
        "surface_routing_id": str(surface_payload.get("routing_id", "")).strip(),
        "surface_generator_id": str(surface_payload.get("selected_generator_id", "")).strip(),
        "surface_handler_id": str(surface_payload.get("handler_id", "")).strip(),
        "surface_summary": _as_map(surface_payload.get("surface_summary")),
        "generator_version_id": resolved_generator_version_id,
        "realism_profile_id": resolved_realism_profile_id,
        "universe_contract_bundle_hash": str(universe_contract_bundle_hash or "").strip(),
        "overlay_manifest_hash": str(overlay_manifest_hash or "").strip(),
        "mod_policy_id": str(mod_policy_id or "").strip(),
        "cache_key": cache_key,
        "deterministic_fingerprint": "",
    }
    if galaxy_object_stub_artifact_rows:
        payload["generated_galaxy_object_stub_artifact_rows"] = list(galaxy_object_stub_artifact_rows)
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload) if cache_enabled else payload


def build_worldgen_request_for_cell(
    *,
    geo_cell_key: Mapping[str, object],
    refinement_level: int,
    reason: str,
    request_id_prefix: str = "worldgen",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        raise ValueError("geo_cell_key is required")
    request_seed = {
        "geo_cell_key": _semantic_cell_key(cell_key),
        "refinement_level": int(max(0, _as_int(refinement_level, 0))),
        "reason": str(reason or "").strip().lower(),
        "extensions": _as_map(extensions),
    }
    return build_worldgen_request(
        request_id="{}.{}".format(str(request_id_prefix or "worldgen").strip(), canonical_sha256(request_seed)[:16]),
        geo_cell_key=cell_key,
        refinement_level=int(max(0, _as_int(refinement_level, 0))),
        reason=str(reason or "").strip().lower(),
        extensions=extensions,
    )


def build_worldgen_request_for_query(
    *,
    geo_cell_key: Mapping[str, object],
    refinement_level: int = 0,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    return build_worldgen_request_for_cell(
        geo_cell_key=geo_cell_key,
        refinement_level=refinement_level,
        reason="query",
        request_id_prefix="worldgen.query",
        extensions=extensions,
    )


def build_worldgen_requests_for_roi(
    *,
    geo_cell_keys: Sequence[object],
    refinement_level: int = 0,
    reason: str = "roi",
    extensions: Mapping[str, object] | None = None,
) -> List[dict]:
    rows = [_coerce_cell_key(item) for item in list(geo_cell_keys or [])]
    out = []
    for row in sorted((row for row in rows if row), key=_geo_cell_key_sort_tuple):
        out.append(
            build_worldgen_request_for_cell(
                geo_cell_key=row,
                refinement_level=refinement_level,
                reason=reason,
                request_id_prefix="worldgen.{}".format(str(reason or "roi").strip() or "roi"),
                extensions=extensions,
            )
        )
    return [dict(item) for item in out]


def build_worldgen_requests_for_projection(
    *,
    projected_cells: Sequence[object],
    refinement_level: int = 0,
    reason: str = "roi",
    extensions: Mapping[str, object] | None = None,
) -> List[dict]:
    geo_cell_keys = [_as_map(_as_map(row).get("geo_cell_key")) for row in list(projected_cells or []) if isinstance(row, Mapping)]
    return build_worldgen_requests_for_roi(
        geo_cell_keys=geo_cell_keys,
        refinement_level=refinement_level,
        reason=reason,
        extensions=extensions,
    )


__all__ = [
    "DEFAULT_GENERATOR_VERSION_ID",
    "DEFAULT_REALISM_PROFILE_ID",
    "REFUSAL_GEO_WORLDGEN_INVALID",
    "RNG_WORLDGEN_GALAXY",
    "RNG_WORLDGEN_PLANET",
    "RNG_WORLDGEN_SURFACE",
    "RNG_WORLDGEN_SYSTEM",
    "build_worldgen_request",
    "build_worldgen_request_for_cell",
    "build_worldgen_request_for_query",
    "build_worldgen_requests_for_projection",
    "build_worldgen_requests_for_roi",
    "build_worldgen_result",
    "generate_worldgen_result",
    "generator_version_registry_hash",
    "normalize_worldgen_request",
    "normalize_worldgen_request_rows",
    "normalize_worldgen_result",
    "normalize_worldgen_result_rows",
    "realism_profile_registry_hash",
    "worldgen_request_hash",
    "worldgen_request_hash_chain",
    "worldgen_cache_clear",
    "worldgen_cache_snapshot",
    "worldgen_result_hash_chain",
    "worldgen_result_proof_surface",
    "worldgen_rng_stream_policy",
    "worldgen_spawned_object_hash_chain",
    "worldgen_stream_seed",
]

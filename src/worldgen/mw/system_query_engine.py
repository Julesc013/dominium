"""Deterministic MW-1 star-system discovery and query helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.frame.frame_engine import position_to_frame
from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key, geo_cell_key_neighbors
from src.geo.metric.metric_engine import geo_distance
from src.geo.worldgen.worldgen_engine import (
    DEFAULT_REALISM_PROFILE_ID,
    build_worldgen_request_for_query,
    generate_worldgen_result,
)
from src.worldgen.mw.mw_cell_generator import (
    DEFAULT_GALAXY_PRIORS_ID,
    MW_CELL_GENERATOR_VERSION,
    MW_GALACTIC_FRAME_ID,
    PARSEC_MM,
    galaxy_priors_rows,
    normalize_star_system_artifact_rows,
)


DEFAULT_QUERY_MAX_CELLS = 256
REALISM_PROFILE_REGISTRY_REL = os.path.join("data", "registries", "realism_profile_registry.json")


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _refusal(message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


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


def _realism_profile_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    body = _as_map(payload) or _registry_payload(REALISM_PROFILE_REGISTRY_REL)
    rows = _as_list(body.get("realism_profiles")) or _as_list(_as_map(body.get("record")).get("realism_profiles"))
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        realism_profile_id = str(row.get("realism_profile_id", "")).strip()
        if realism_profile_id:
            out[realism_profile_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _resolved_cell_size_pc(universe_identity: Mapping[str, object] | None) -> int:
    identity = _as_map(universe_identity)
    realism_profile_id = str(identity.get("realism_profile_id", "")).strip() or DEFAULT_REALISM_PROFILE_ID
    realism_row = dict(_realism_profile_rows().get(realism_profile_id) or {})
    galaxy_priors_id = str(realism_row.get("galaxy_priors_ref", "")).strip() or DEFAULT_GALAXY_PRIORS_ID
    galaxy_priors_row = dict(galaxy_priors_rows().get(galaxy_priors_id) or {})
    return int(max(1, _as_int(galaxy_priors_row.get("cell_size_pc", 10), 10)))


def _default_frame_nodes() -> List[dict]:
    return [
        {
            "frame_id": MW_GALACTIC_FRAME_ID,
            "parent_frame_id": None,
            "topology_profile_id": "geo.topology.r3_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "chart_id": "chart.global.r3",
            "anchor_cell_key": {
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global.r3",
                "index_tuple": [0, 0, 0],
                "refinement_level": 0,
            },
            "scale_class_id": "galaxy",
            "extensions": {"source": "MW1-4"},
        }
    ]


def _default_frame_transforms() -> List[dict]:
    return []


def _frame_context(frame_nodes: object, frame_transform_rows: object) -> Tuple[List[dict], List[dict]]:
    nodes = [dict(row) for row in _as_list(frame_nodes) if isinstance(row, Mapping)]
    transforms = [dict(row) for row in _as_list(frame_transform_rows) if isinstance(row, Mapping)]
    return (
        nodes if nodes else _default_frame_nodes(),
        transforms if transforms else _default_frame_transforms(),
    )


def _resolved_position_ref(
    *,
    position_ref: Mapping[str, object] | None,
    frame_nodes: object = None,
    frame_transform_rows: object = None,
) -> dict | None:
    payload = _as_map(position_ref)
    frame_id = str(payload.get("frame_id", "")).strip()
    if not payload or not frame_id:
        return None
    if frame_id == MW_GALACTIC_FRAME_ID:
        return payload
    nodes, transforms = _frame_context(frame_nodes=frame_nodes, frame_transform_rows=frame_transform_rows)
    converted = position_to_frame(
        payload,
        MW_GALACTIC_FRAME_ID,
        frame_nodes=nodes,
        frame_transform_rows=transforms,
    )
    if str(converted.get("result", "")) != "complete":
        return None
    return _as_map(converted.get("target_position_ref"))


def _cell_sort_tuple(cell_key: Mapping[str, object] | None) -> Tuple[str, Tuple[int, ...], int, str]:
    row = _coerce_cell_key(cell_key)
    if not row:
        return ("", tuple(), 0, "")
    return (
        str(row.get("chart_id", "")).strip(),
        tuple(int(item) for item in _as_list(row.get("index_tuple"))),
        int(max(0, _as_int(row.get("refinement_level", 0), 0))),
        str(row.get("partition_profile_id", "")).strip(),
    )


def _normalized_query_row(artifact_row: Mapping[str, object]) -> dict:
    raw = _as_map(artifact_row)
    if raw.get("cell_key") and raw.get("galaxy_position_ref") and raw.get("object_id"):
        payload = {
            "object_id": str(raw.get("object_id", "")).strip(),
            "system_seed_value": str(raw.get("system_seed_value", "")).strip(),
            "metallicity_proxy": _as_map(raw.get("metallicity_proxy")),
            "galaxy_position_ref": _as_map(raw.get("galaxy_position_ref")),
            "extensions": {
                "cell_key": _as_map(raw.get("cell_key")),
                "local_index": int(max(0, _as_int(raw.get("local_index", 0), 0))),
                "local_subkey": str(raw.get("local_subkey", "")).strip(),
                "age_bucket": str(raw.get("age_bucket", "")).strip(),
                "imf_bucket": str(raw.get("imf_bucket", "")).strip(),
                "habitable_filter_bias_permille": int(max(0, _as_int(raw.get("habitable_filter_bias_permille", 0), 0))),
                "habitable_likely": bool(raw.get("habitable_likely", False)),
            },
        }
    else:
        payload = next(iter(normalize_star_system_artifact_rows([artifact_row])), {})
    extensions = _as_map(payload.get("extensions"))
    metallicity_proxy = _as_map(payload.get("metallicity_proxy"))
    row = {
        "object_id": str(payload.get("object_id", "")).strip(),
        "cell_key": _coerce_cell_key(_as_map(extensions.get("cell_key"))) or {},
        "local_index": int(max(0, _as_int(extensions.get("local_index", 0), 0))),
        "local_subkey": str(extensions.get("local_subkey", "")).strip(),
        "system_seed_value": str(payload.get("system_seed_value", "")).strip(),
        "metallicity_proxy": metallicity_proxy,
        "metallicity_permille": int(max(0, _as_int(metallicity_proxy.get("metallicity_permille", 0), 0))),
        "galaxy_position_ref": _as_map(payload.get("galaxy_position_ref")),
        "habitable_filter_bias_permille": int(max(0, _as_int(extensions.get("habitable_filter_bias_permille", 0), 0))),
        "habitable_likely": bool(extensions.get("habitable_likely", False)),
        "age_bucket": str(extensions.get("age_bucket", "")).strip(),
        "imf_bucket": str(extensions.get("imf_bucket", "")).strip(),
        "deterministic_fingerprint": "",
        "extensions": {"source": "MW1-4"},
    }
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def _normalized_query_rows(rows: Iterable[object]) -> List[dict]:
    out: Dict[str, dict] = {}
    for item in rows:
        if not isinstance(item, Mapping):
            continue
        row = _normalized_query_row(item)
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            out[object_id] = row
    return [dict(out[key]) for key in sorted(out.keys())]


def _cell_query_result(
    *,
    universe_identity: Mapping[str, object] | None,
    geo_cell_key: Mapping[str, object],
    cache_enabled: bool,
) -> dict:
    request = build_worldgen_request_for_query(
        geo_cell_key=geo_cell_key,
        refinement_level=1,
        extensions={"query_surface_id": "mw.system_query.cell", "source": MW_CELL_GENERATOR_VERSION},
    )
    return generate_worldgen_result(
        universe_identity=universe_identity,
        worldgen_request=request,
        realism_profile_id=str(_as_map(universe_identity).get("realism_profile_id", "")).strip() or DEFAULT_REALISM_PROFILE_ID,
        cache_enabled=bool(cache_enabled),
    )


def _galactic_cell_key_from_position(
    *,
    universe_identity: Mapping[str, object] | None,
    galactic_position_ref: Mapping[str, object],
) -> dict | None:
    identity = _as_map(universe_identity)
    local_position = _as_list(_as_map(galactic_position_ref).get("local_position"))
    if not local_position:
        return None
    cell_size_pc = _resolved_cell_size_pc(identity)
    cell_span_mm = cell_size_pc * PARSEC_MM
    index_tuple = [
        int(int(_as_int(value, 0)) // cell_span_mm)
        for value in (local_position[:3] + [0, 0, 0])[:3]
    ]
    return _coerce_cell_key(
        {
            "partition_profile_id": str(identity.get("partition_profile_id", "")).strip() or "geo.partition.grid_zd",
            "topology_profile_id": str(identity.get("topology_profile_id", "")).strip() or "geo.topology.r3_infinite",
            "chart_id": "chart.global.r3",
            "index_tuple": index_tuple,
            "refinement_level": 0,
            "extensions": {"source": "MW1-4"},
        }
    )


def list_systems_in_cell(
    *,
    universe_identity: Mapping[str, object] | None,
    geo_cell_key: Mapping[str, object],
    cache_enabled: bool = True,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        return _refusal("geo_cell_key is invalid", {"geo_cell_key": _as_map(geo_cell_key)})
    generated = _cell_query_result(
        universe_identity=universe_identity,
        geo_cell_key=cell_key,
        cache_enabled=cache_enabled,
    )
    if str(generated.get("result", "")) != "complete":
        return _refusal("cell query failed", {"generated": dict(generated)})
    systems = _normalized_query_rows(generated.get("generated_star_system_artifact_rows"))
    payload = {
        "result": "complete",
        "geo_cell_key": cell_key,
        "systems": systems,
        "count": int(len(systems)),
        "mw_cell_summary": _as_map(generated.get("mw_cell_summary")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _distance_mm(
    *,
    origin_position_ref: Mapping[str, object],
    target_position_ref: Mapping[str, object],
    topology_profile_id: str,
    metric_profile_id: str,
) -> int:
    result = geo_distance(
        {"coords": list(_as_list(_as_map(origin_position_ref).get("local_position")))},
        {"coords": list(_as_list(_as_map(target_position_ref).get("local_position")))},
        str(topology_profile_id or "").strip() or "geo.topology.r3_infinite",
        str(metric_profile_id or "").strip() or "geo.metric.euclidean",
    )
    if str(result.get("result", "")) != "complete":
        raise ValueError(str(result.get("message", "distance query failed")))
    return int(max(0, _as_int(result.get("distance_mm", 0), 0)))


def query_nearest_system(
    *,
    universe_identity: Mapping[str, object] | None,
    position_ref: Mapping[str, object] | None,
    radius: int,
    frame_nodes: object = None,
    frame_transform_rows: object = None,
    max_cells: int = DEFAULT_QUERY_MAX_CELLS,
    cache_enabled: bool = True,
) -> dict:
    galactic_position = _resolved_position_ref(
        position_ref=position_ref,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
    )
    if galactic_position is None:
        return _refusal("position_ref is invalid or cannot be converted into the Milky Way frame", {"position_ref": _as_map(position_ref)})
    identity = _as_map(universe_identity)
    topology_profile_id = str(identity.get("topology_profile_id", "")).strip() or "geo.topology.r3_infinite"
    metric_profile_id = str(identity.get("metric_profile_id", "")).strip() or "geo.metric.euclidean"
    center_cell = _galactic_cell_key_from_position(universe_identity=identity, galactic_position_ref=galactic_position)
    if not center_cell:
        return _refusal("center GEO cell is invalid", {"position_ref": galactic_position})
    center_listing = list_systems_in_cell(
        universe_identity=identity,
        geo_cell_key=center_cell,
        cache_enabled=cache_enabled,
    )
    if str(center_listing.get("result", "")) != "complete":
        return dict(center_listing)
    cell_size_pc = int(max(1, _as_int(_as_map(center_listing.get("mw_cell_summary")).get("cell_size_pc", 10), 10)))
    cell_span_mm = cell_size_pc * PARSEC_MM
    radius_mm = int(max(0, _as_int(radius, 0)))
    cell_radius = int((radius_mm + cell_span_mm - 1) // cell_span_mm) if radius_mm > 0 else 0
    neighbors_payload = geo_cell_key_neighbors(center_cell, cell_radius, metric_profile_id=metric_profile_id)
    if str(neighbors_payload.get("result", "")) != "complete":
        return _refusal("unable to enumerate neighboring GEO cells", {"geo_cell_key": center_cell})
    discovered_cells: Dict[str, dict] = {
        canonical_sha256(_semantic_cell_key(center_cell)): center_cell,
    }
    for row in _as_list(neighbors_payload.get("neighbors")):
        coerced = _coerce_cell_key(row)
        if coerced:
            discovered_cells[canonical_sha256(_semantic_cell_key(coerced))] = coerced
    ordered_cells = [
        dict(discovered_cells[key])
        for key in sorted(discovered_cells.keys(), key=lambda item: _cell_sort_tuple(discovered_cells[item]))
    ][: max(1, int(max_cells))]

    candidate_rows = []
    for cell_key in ordered_cells:
        cell_listing = (
            center_listing
            if canonical_sha256(_semantic_cell_key(cell_key)) == canonical_sha256(_semantic_cell_key(center_cell))
            else list_systems_in_cell(
                universe_identity=identity,
                geo_cell_key=cell_key,
                cache_enabled=cache_enabled,
            )
        )
        if str(cell_listing.get("result", "")) != "complete":
            continue
        for system_row in _as_list(cell_listing.get("systems")):
            if not isinstance(system_row, Mapping):
                continue
            system_position = _as_map(_as_map(system_row).get("galaxy_position_ref"))
            if not system_position:
                continue
            try:
                distance_mm = _distance_mm(
                    origin_position_ref=galactic_position,
                    target_position_ref=system_position,
                    topology_profile_id=topology_profile_id,
                    metric_profile_id=metric_profile_id,
                )
            except ValueError:
                continue
            if radius_mm and distance_mm > radius_mm:
                continue
            candidate_rows.append(
                {
                    **dict(system_row),
                    "distance_mm": int(distance_mm),
                }
            )
    candidate_rows = sorted(
        (dict(row) for row in candidate_rows),
        key=lambda row: (
            int(_as_int(row.get("distance_mm", 0), 0)),
            int(_as_int(row.get("local_index", 0), 0)),
            str(row.get("object_id", "")),
        ),
    )
    payload = {
        "result": "complete",
        "query_position_ref": galactic_position,
        "radius_mm": int(radius_mm),
        "searched_cell_count": int(len(ordered_cells)),
        "candidate_count": int(len(candidate_rows)),
        "nearest_system": dict(candidate_rows[0]) if candidate_rows else {},
        "found": bool(candidate_rows),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def filter_habitable_candidates(*, system_rows: object, criteria_stub: Mapping[str, object] | None = None) -> dict:
    criteria = _as_map(criteria_stub)
    min_habitable_bias = int(max(0, min(1000, _as_int(criteria.get("min_habitable_bias_permille", 650), 650))))
    metallicity_floor = int(max(0, _as_int(criteria.get("metallicity_floor_permille", 700), 700)))
    metallicity_ceiling = int(max(metallicity_floor, _as_int(criteria.get("metallicity_ceiling_permille", 1300), 1300)))
    limit = int(max(1, _as_int(criteria.get("limit", 32), 32)))
    candidates = []
    for row in _normalized_query_rows(system_rows):
        metallicity_permille = int(max(0, _as_int(row.get("metallicity_permille", 0), 0)))
        habitable_bias = int(max(0, _as_int(row.get("habitable_filter_bias_permille", 0), 0)))
        if habitable_bias < min_habitable_bias:
            continue
        if metallicity_permille < metallicity_floor or metallicity_permille > metallicity_ceiling:
            continue
        candidates.append(dict(row))
    candidates = sorted(
        candidates,
        key=lambda row: (
            -int(_as_int(row.get("habitable_filter_bias_permille", 0), 0)),
            -int(_as_int(row.get("metallicity_permille", 0), 0)),
            str(row.get("object_id", "")),
        ),
    )[:limit]
    payload = {
        "result": "complete",
        "criteria_stub": {
            "surface_id": "mw.habitable_likely.stub",
            "min_habitable_bias_permille": min_habitable_bias,
            "metallicity_floor_permille": metallicity_floor,
            "metallicity_ceiling_permille": metallicity_ceiling,
            "limit": limit,
        },
        "candidates": candidates,
        "count": int(len(candidates)),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_system_teleport_plan(system_row: Mapping[str, object] | None) -> dict:
    row = _normalized_query_row(_as_map(system_row))
    object_id = str(row.get("object_id", "")).strip()
    cell_key = _coerce_cell_key(row.get("cell_key"))
    if not object_id or not cell_key:
        return _refusal("system_row is missing object_id or cell_key", {"system_row": _as_map(system_row)})
    request = build_worldgen_request_for_query(
        geo_cell_key=cell_key,
        refinement_level=1,
        extensions={
            "source": "mw.system_query.teleport",
            "target_object_id": object_id,
        },
    )
    payload = {
        "result": "complete",
        "target_object_id": object_id,
        "worldgen_request": request,
        "camera_teleport_inputs": {
            "target_object_id": object_id,
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_procedural_astronomy_index(system_rows: object) -> dict:
    entries = []
    search_index: Dict[str, List[str]] = {}
    for row in _normalized_query_rows(system_rows):
        object_id = str(row.get("object_id", "")).strip()
        position_ref = _as_map(row.get("galaxy_position_ref"))
        entry = {
            "object_id": object_id,
            "kind": "star_system",
            "parent_id": "object.milky_way",
            "frame_id": str(position_ref.get("frame_id", "")).strip() or MW_GALACTIC_FRAME_ID,
            "bounds": {
                "kind": "sphere",
                "sphere_radius_mm": 61_713_551_629_827_344_000,
            },
            "physical_params": {
                "metallicity_permille": int(_as_int(row.get("metallicity_permille", 0), 0)),
                "habitable_filter_bias_permille": int(_as_int(row.get("habitable_filter_bias_permille", 0), 0)),
            },
            "search_keys": [
                object_id,
                str(row.get("local_subkey", "")).strip(),
            ],
            "position_ref": position_ref,
            "position_mm": {
                "x": int(_as_int(_as_list(position_ref.get("local_position"))[0] if len(_as_list(position_ref.get("local_position"))) > 0 else 0, 0)),
                "y": int(_as_int(_as_list(position_ref.get("local_position"))[1] if len(_as_list(position_ref.get("local_position"))) > 1 else 0, 0)),
                "z": int(_as_int(_as_list(position_ref.get("local_position"))[2] if len(_as_list(position_ref.get("local_position"))) > 2 else 0, 0)),
            },
        }
        entries.append(entry)
        for key in sorted(set(str(token).strip().lower() for token in entry["search_keys"] if str(token).strip())):
            search_index.setdefault(key, []).append(object_id)
    payload = {
        "schema_version": "1.0.0",
        "entries": sorted((dict(row) for row in entries), key=lambda row: str(row.get("object_id", ""))),
        "reference_frames": [MW_GALACTIC_FRAME_ID],
        "search_index": dict((key, sorted(set(values))) for key, values in sorted(search_index.items(), key=lambda item: str(item[0]))),
        "registry_hash": "",
        "deterministic_fingerprint": "",
    }
    payload["registry_hash"] = canonical_sha256(dict(payload, registry_hash="", deterministic_fingerprint=""))
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_QUERY_MAX_CELLS",
    "build_procedural_astronomy_index",
    "build_system_teleport_plan",
    "filter_habitable_candidates",
    "list_systems_in_cell",
    "query_nearest_system",
]

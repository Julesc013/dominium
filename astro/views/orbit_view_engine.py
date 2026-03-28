"""Deterministic SOL-2 orbit view artifact engine."""

from __future__ import annotations

import copy
from typing import Dict, List, Mapping, Sequence

from astro.ephemeris.kepler_proxy_engine import (
    DEFAULT_EPHEMERIS_PROVIDER_ID,
    DEFAULT_ORBIT_CHART_ID,
    DEFAULT_ORBIT_FRAME_ID,
    DEFAULT_ORBIT_PATH_POLICY_ID,
    build_orbit_body_descriptors,
    build_orbit_position_ref,
    ephemeris_provider_registry_hash,
    orbit_path_policy_registry_hash,
    orbit_path_policy_rows,
    orbit_vector_units_at_tick,
    period_estimate_ticks_for_body,
    resolve_ephemeris_provider,
    sample_orbit_path_points,
)
from geo.index.geo_index_engine import _coerce_cell_key, geo_cell_key_from_position
from tools.xstack.compatx.canonical_json import canonical_sha256


ORBIT_VIEW_ENGINE_VERSION = "SOL2-4"
DEFAULT_ORBIT_RADIUS_LOCAL_UNITS = 40_000
_ORBIT_VIEW_CACHE: Dict[str, dict] = {}
_ORBIT_VIEW_CACHE_MAX = 128


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _ordered_strings(values: object) -> list[str]:
    out: list[str] = []
    for item in list(values or []):
        token = str(item).strip()
        if token and token not in out:
            out.append(token)
    return out


def _sorted_strings(values: object) -> list[str]:
    return sorted(set(_ordered_strings(values)))


def _cache_lookup(cache_key: str) -> dict | None:
    row = _ORBIT_VIEW_CACHE.get(str(cache_key))
    if not isinstance(row, dict):
        return None
    return copy.deepcopy(dict(row))


def _cache_store(cache_key: str, payload: Mapping[str, object]) -> dict:
    _ORBIT_VIEW_CACHE[str(cache_key)] = copy.deepcopy(dict(payload))
    if len(_ORBIT_VIEW_CACHE) > _ORBIT_VIEW_CACHE_MAX:
        for stale_key in sorted(_ORBIT_VIEW_CACHE.keys())[:-_ORBIT_VIEW_CACHE_MAX]:
            _ORBIT_VIEW_CACHE.pop(stale_key, None)
    return copy.deepcopy(dict(payload))


def _rows_by_object_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in list(rows or []):
        if not isinstance(row, Mapping):
            continue
        token = str(dict(row).get("object_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _target_row(
    *,
    focus_object_id: str,
    inspection_snapshot: Mapping[str, object] | None,
    selection: Mapping[str, object] | None,
) -> tuple[str, dict]:
    if str(focus_object_id or "").strip():
        return str(focus_object_id).strip(), {}
    selected = _as_map(selection)
    selected_id = str(selected.get("object_id", "")).strip() or str(selected.get("target_id", "")).strip()
    if selected_id:
        return selected_id, dict(selected)
    snapshot = _as_map(inspection_snapshot)
    target_payload = _as_map(snapshot.get("target_payload"))
    row = _as_map(target_payload.get("row"))
    target_id = str(target_payload.get("target_id", "")).strip() or str(row.get("object_id", "")).strip()
    return target_id, row


def _focus_descriptor(
    *,
    focus_object_id: str,
    focus_row: Mapping[str, object],
    body_rows_by_id: Mapping[str, dict],
) -> dict:
    row = _as_map(body_rows_by_id.get(str(focus_object_id or "").strip()))
    if row:
        return row
    object_kind_id = str(_as_map(focus_row).get("object_kind_id", "")).strip()
    if object_kind_id in {"kind.star", "kind.star_system", "kind.planet", "kind.moon"}:
        return {
            "object_id": str(focus_object_id or "").strip(),
            "kind": object_kind_id,
            "relative_parent_object_id": str(_as_map(_as_map(focus_row).get("hierarchy")).get("parent_object_id", "")).strip()
            or str(_as_map(_as_map(focus_row).get("orbit")).get("parent_object_id", "")).strip(),
            "body_slot_id": str(_as_map(_as_map(focus_row).get("hierarchy")).get("body_slot_id", "")).strip(),
        }
    return {}


def _children_by_parent(body_rows_by_id: Mapping[str, dict]) -> Dict[str, list[str]]:
    out: Dict[str, list[str]] = {}
    for object_id, row in sorted(body_rows_by_id.items()):
        parent_id = str(_as_map(row).get("relative_parent_object_id", "")).strip()
        if not parent_id or parent_id == object_id:
            continue
        out.setdefault(parent_id, []).append(object_id)
    return dict((key, sorted(out[key])) for key in sorted(out.keys()))


def _primary_star_id(body_rows_by_id: Mapping[str, dict]) -> str:
    stars = [object_id for object_id, row in sorted(body_rows_by_id.items()) if str(_as_map(row).get("kind", "")).strip() == "kind.star"]
    return stars[0] if stars else ""


def _orbit_focus_context(
    *,
    focus_row: Mapping[str, object],
    body_rows_by_id: Mapping[str, dict],
    children_by_parent: Mapping[str, list[str]],
) -> dict:
    focus = _as_map(focus_row)
    focus_object_id = str(focus.get("object_id", "")).strip()
    kind = str(focus.get("kind", "")).strip()
    direct_children = list(children_by_parent.get(focus_object_id, []))
    direct_moons = [object_id for object_id in direct_children if str(_as_map(body_rows_by_id.get(object_id)).get("kind", "")).strip() == "kind.moon"]
    if kind == "kind.moon":
        parent_object_id = str(focus.get("relative_parent_object_id", "")).strip()
        return {
            "chart_mode": "planet_local",
            "center_object_id": parent_object_id or focus_object_id,
            "path_body_ids": [focus_object_id] if focus_object_id else [],
            "body_ids": _ordered_strings([parent_object_id, focus_object_id]),
        }
    if kind == "kind.planet" and direct_moons:
        return {
            "chart_mode": "planet_local",
            "center_object_id": focus_object_id,
            "path_body_ids": list(direct_moons),
            "body_ids": _ordered_strings([focus_object_id] + list(direct_moons)),
        }
    center_object_id = _primary_star_id(body_rows_by_id) or focus_object_id
    path_body_ids = [
        object_id
        for object_id, row in sorted(body_rows_by_id.items())
        if str(_as_map(row).get("kind", "")).strip() == "kind.planet"
        and str(_as_map(row).get("relative_parent_object_id", "")).strip() == center_object_id
    ]
    return {
        "chart_mode": "system",
        "center_object_id": center_object_id,
        "path_body_ids": list(path_body_ids),
        "body_ids": _ordered_strings([center_object_id] + list(path_body_ids)),
    }


def _scale_vector(vector_units: Sequence[int], max_radius_units: int) -> list[int]:
    scale_denominator = max(1, int(max_radius_units))
    return [
        int((int(_as_int(vector_units[idx], 0)) * DEFAULT_ORBIT_RADIUS_LOCAL_UNITS) // scale_denominator)
        for idx in range(3)
    ]


def _vector_subtract(left: Sequence[int], right: Sequence[int]) -> list[int]:
    return [int(_as_int(left[idx], 0) - _as_int(right[idx], 0)) for idx in range(3)]


def _geo_cell_key_from_local_position(local_position: Sequence[int], chart_id: str) -> dict:
    result = geo_cell_key_from_position(
        {
            "coords": [int(_as_int(value, 0)) for value in list(local_position or [])[:3]],
            "chart_id": str(chart_id or DEFAULT_ORBIT_CHART_ID).strip() or DEFAULT_ORBIT_CHART_ID,
            "refinement_level": 0,
        },
        "geo.topology.r3_infinite",
        "geo.partition.grid_zd",
        str(chart_id or DEFAULT_ORBIT_CHART_ID).strip() or DEFAULT_ORBIT_CHART_ID,
    )
    if str(_as_map(result).get("result", "")).strip() == "complete":
        return _as_map(result.get("cell_key"))
    return {}


def orbit_view_artifact_hash(artifact_row: Mapping[str, object] | None) -> str:
    artifact = _as_map(artifact_row)
    if not artifact:
        return ""
    semantic = dict(artifact)
    semantic.pop("deterministic_fingerprint", None)
    return canonical_sha256(semantic)


def build_orbit_layer_source_payloads(orbit_view_surface: Mapping[str, object] | None) -> dict:
    surface = _as_map(orbit_view_surface)
    artifact = _as_map(surface.get("orbit_view_artifact"))
    artifact_hash = orbit_view_artifact_hash(artifact)
    rows = [dict(row) for row in list(_as_map(artifact.get("extensions")).get("layer_marker_rows") or []) if isinstance(row, Mapping)]
    return {
        "layer.orbits": {
            "source_kind": "orbit_view",
            "rows": rows,
            "orbit_view_artifact_hash": artifact_hash,
            "chart_mode": str(_as_map(artifact.get("extensions")).get("chart_mode", "")).strip(),
        }
    }


def build_orbit_view_surface(
    *,
    current_tick: int,
    viewer_ref: Mapping[str, object] | None,
    selection: Mapping[str, object] | None = None,
    inspection_snapshot: Mapping[str, object] | None = None,
    authority_context: Mapping[str, object] | None = None,
    focus_object_id: str = "",
    effective_object_views: object = None,
    star_artifact_rows: object = None,
    planet_orbit_artifact_rows: object = None,
    planet_basic_artifact_rows: object = None,
    provider_declarations: Sequence[Mapping[str, object]] | None = None,
    explicit_provider_resolutions: Sequence[Mapping[str, object]] | None = None,
    orbit_path_policy_id: str = DEFAULT_ORBIT_PATH_POLICY_ID,
    ui_mode: str = "gui",
) -> dict:
    del authority_context
    viewer = _as_map(viewer_ref)
    body_rows = build_orbit_body_descriptors(
        effective_object_views=effective_object_views,
        star_artifact_rows=star_artifact_rows,
        planet_orbit_artifact_rows=planet_orbit_artifact_rows,
        planet_basic_artifact_rows=planet_basic_artifact_rows,
    )
    body_rows_by_id = _rows_by_object_id(body_rows)
    target_object_id, target_row = _target_row(
        focus_object_id=str(focus_object_id or "").strip(),
        inspection_snapshot=inspection_snapshot,
        selection=selection,
    )
    focus_row = _focus_descriptor(
        focus_object_id=str(target_object_id or "").strip(),
        focus_row=target_row,
        body_rows_by_id=body_rows_by_id,
    )
    if not body_rows_by_id or not focus_row:
        payload = {
            "result": "complete",
            "available": False,
            "source_kind": "derived.orbit_view_artifact",
            "orbit_view_artifact": {},
            "layer_source_payloads": {},
            "presentation": {
                "preferred_presentation": "summary" if str(ui_mode or "").strip().lower() in {"cli", "tui"} else "buffer",
                "summary": {"body_count": 0, "path_count": 0},
                "summary_text": "orbit view unavailable",
            },
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    provider_resolution = resolve_ephemeris_provider(
        instance_id="orbit_view.{}".format(str(target_object_id or "focus")),
        provider_declarations=provider_declarations,
        explicit_resolutions=explicit_provider_resolutions,
    )
    if str(provider_resolution.get("result", "")).strip() != "complete":
        payload = {
            "result": "refused",
            "available": False,
            "source_kind": "derived.orbit_view_artifact",
            "provider_resolution": dict(provider_resolution),
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    children_by_parent = _children_by_parent(body_rows_by_id)
    focus_context = _orbit_focus_context(
        focus_row=focus_row,
        body_rows_by_id=body_rows_by_id,
        children_by_parent=children_by_parent,
    )
    policy_row = dict(
        orbit_path_policy_rows().get(str(orbit_path_policy_id or "").strip() or DEFAULT_ORBIT_PATH_POLICY_ID)
        or orbit_path_policy_rows().get(DEFAULT_ORBIT_PATH_POLICY_ID)
        or {}
    )
    sample_count = int(max(8, min(512, _as_int(policy_row.get("samples_per_orbit", 128), 128))))
    max_paths = int(max(1, min(64, _as_int(policy_row.get("max_paths_per_view", 16), 16))))
    selected_path_body_ids = list(focus_context.get("path_body_ids") or [])[:max_paths]
    chart_mode = str(focus_context.get("chart_mode", "")).strip() or "system"
    center_object_id = str(focus_context.get("center_object_id", "")).strip() or str(focus_row.get("object_id", "")).strip()
    chart_frame_id = "{}.{}".format(DEFAULT_ORBIT_FRAME_ID, center_object_id or "focus")
    chart_id = DEFAULT_ORBIT_CHART_ID
    cache_key = canonical_sha256(
        {
            "tick": int(max(0, _as_int(current_tick, 0))),
            "viewer_ref": {
                "object_id": str(viewer.get("object_id", "")).strip(),
                "frame_id": str(viewer.get("frame_id", "")).strip(),
                "local_position": list(viewer.get("local_position") or []),
            },
            "focus_object_id": str(focus_row.get("object_id", "")).strip(),
            "chart_mode": chart_mode,
            "center_object_id": center_object_id,
            "body_rows_hash": canonical_sha256(body_rows),
            "sample_count": sample_count,
            "max_paths": max_paths,
            "provider_id": str(provider_resolution.get("provider_id", "")).strip(),
            "policy_id": str(policy_row.get("policy_id", "")).strip(),
        }
    )
    cached = _cache_lookup(cache_key)
    if cached is not None:
        out = dict(cached)
        out["cache_hit"] = True
        return out

    current_vectors: Dict[str, list[int]] = {}
    sampled_path_rows: Dict[str, list[dict]] = {}
    max_radius_units = 1
    for object_id in _ordered_strings(focus_context.get("body_ids")):
        current_vector = orbit_vector_units_at_tick(body_object_id=object_id, tick=int(current_tick), body_rows_by_id=body_rows_by_id)
        current_vectors[object_id] = list(current_vector)
    center_current_vector = list(current_vectors.get(center_object_id) or [0, 0, 0])
    for object_id in _ordered_strings(focus_context.get("body_ids")):
        relative_current = _vector_subtract(current_vectors.get(object_id, [0, 0, 0]), center_current_vector)
        max_radius_units = max(max_radius_units, max(abs(value) for value in relative_current))
    for object_id in selected_path_body_ids:
        row = _as_map(body_rows_by_id.get(object_id))
        samples = sample_orbit_path_points(
            body_row=row,
            body_rows_by_id=body_rows_by_id,
            sample_count=sample_count,
            frame_id=chart_frame_id,
            chart_id=chart_id,
        )
        sampled_path_rows[object_id] = [dict(sample) for sample in samples]
        for sample in samples:
            absolute_vector = list(_as_map(sample.get("position_ref")).get("local_position") or [])
            center_sample_vector = orbit_vector_units_at_tick(
                body_object_id=center_object_id,
                tick=int(_as_int(_as_map(sample).get("sample_tick", 0), 0)),
                body_rows_by_id=body_rows_by_id,
            )
            relative_vector = _vector_subtract(absolute_vector, center_sample_vector)
            if relative_vector:
                max_radius_units = max(max_radius_units, max(abs(int(_as_int(value, 0))) for value in relative_vector))

    body_entries = []
    sampled_paths = []
    marker_rows_by_hash: Dict[str, dict] = {}
    focus_object_id = str(focus_row.get("object_id", "")).strip()
    for object_id in _ordered_strings(focus_context.get("body_ids")):
        row = _as_map(body_rows_by_id.get(object_id))
        relative_current = _vector_subtract(current_vectors.get(object_id, [0, 0, 0]), center_current_vector)
        scaled_current = _scale_vector(relative_current, max_radius_units)
        current_position_ref = build_orbit_position_ref(
            object_id=object_id,
            local_position=scaled_current,
            frame_id=chart_frame_id,
            chart_id=chart_id,
            extensions={
                "chart_mode": chart_mode,
                "center_object_id": center_object_id,
            },
        )
        body_entries.append(
            {
                "object_id": object_id,
                "display_name": str(row.get("display_name", "")).strip() or object_id,
                "kind": str(row.get("kind", "")).strip(),
                "body_slot_id": str(row.get("body_slot_id", "")).strip(),
                "parent_object_id": str(row.get("relative_parent_object_id", "")).strip(),
                "semi_major_axis_proxy_units": int(_as_int(row.get("semi_major_axis_units", 0), 0)),
                "eccentricity_permille": int(_as_int(row.get("eccentricity_permille", 0), 0)),
                "inclination_mdeg": int(_as_int(row.get("inclination_mdeg", 0), 0)),
                "period_estimate_ticks": int(
                    period_estimate_ticks_for_body(body_row=row, body_rows_by_id=body_rows_by_id)
                ),
                "provider_id": str(provider_resolution.get("provider_id", DEFAULT_EPHEMERIS_PROVIDER_ID)).strip() or DEFAULT_EPHEMERIS_PROVIDER_ID,
                "current_position_ref": current_position_ref,
            }
        )
        current_cell_key = _coerce_cell_key(_geo_cell_key_from_local_position(scaled_current, chart_id))
        if current_cell_key:
            cell_hash = canonical_sha256(current_cell_key)
            marker_rows_by_hash.setdefault(
                cell_hash,
                {
                    "geo_cell_key": dict(current_cell_key),
                    "object_ids": [],
                    "marker_kinds": [],
                },
            )
            marker_rows_by_hash[cell_hash]["object_ids"].append(object_id)
            marker_rows_by_hash[cell_hash]["marker_kinds"].append("focus" if object_id == focus_object_id else "body")

    for object_id in selected_path_body_ids:
        samples = [dict(row) for row in list(sampled_path_rows.get(object_id) or [])]
        sampled_points = []
        for sample in samples:
            sample_index = int(_as_int(_as_map(sample).get("sample_index", 0), 0))
            absolute_vector = list(_as_map(sample.get("position_ref")).get("local_position") or [])
            center_sample_vector = orbit_vector_units_at_tick(
                body_object_id=center_object_id,
                tick=int(_as_int(_as_map(sample).get("sample_tick", 0), 0)),
                body_rows_by_id=body_rows_by_id,
            )
            relative_vector = _vector_subtract(absolute_vector, center_sample_vector)
            scaled = _scale_vector(relative_vector, max_radius_units)
            position_ref = build_orbit_position_ref(
                object_id=object_id,
                local_position=scaled,
                frame_id=chart_frame_id,
                chart_id=chart_id,
                extensions={
                    "sample_index": int(sample_index),
                    "chart_mode": chart_mode,
                },
            )
            cell_key = _coerce_cell_key(_geo_cell_key_from_local_position(scaled, chart_id))
            sampled_points.append(
                {
                    "sample_index": int(sample_index),
                    "sample_tick": int(_as_int(_as_map(sample).get("sample_tick", 0), 0)),
                    "position_ref": position_ref,
                    "geo_cell_key": dict(cell_key or {}),
                }
            )
            if cell_key:
                cell_hash = canonical_sha256(cell_key)
                marker_rows_by_hash.setdefault(
                    cell_hash,
                    {
                        "geo_cell_key": dict(cell_key),
                        "object_ids": [],
                        "marker_kinds": [],
                    },
                )
                marker_rows_by_hash[cell_hash]["object_ids"].append(object_id)
                marker_rows_by_hash[cell_hash]["marker_kinds"].append("path")
        sampled_paths.append(
            {
                "object_id": object_id,
                "sampled_points": sampled_points,
            }
        )

    layer_marker_rows = []
    for cell_hash in sorted(marker_rows_by_hash.keys()):
        row = dict(marker_rows_by_hash[cell_hash])
        object_ids = _sorted_strings(row.get("object_ids"))
        marker_kinds = _sorted_strings(row.get("marker_kinds"))
        marker_kind = "path"
        if "focus" in marker_kinds:
            marker_kind = "focus"
        elif "body" in marker_kinds:
            marker_kind = "body"
        layer_marker_rows.append(
            {
                "geo_cell_key": dict(_as_map(row.get("geo_cell_key"))),
                "object_ids": object_ids,
                "marker_kind": marker_kind,
                "marker_kinds": marker_kinds,
                "chart_mode": chart_mode,
                "focus_object_id": focus_object_id,
            }
        )

    artifact = {
        "schema_version": "1.0.0",
        "view_id": "orbit_view.{}.tick.{}".format((center_object_id or "focus")[:24], int(max(0, _as_int(current_tick, 0)))),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "viewer_ref": dict(viewer),
        "bodies": list(body_entries),
        "sampled_paths": list(sampled_paths),
        "deterministic_fingerprint": "",
        "extensions": {
            "source": ORBIT_VIEW_ENGINE_VERSION,
            "derived_only": True,
            "compactable": True,
            "artifact_class": "DERIVED_VIEW",
            "chart_mode": chart_mode,
            "center_object_id": center_object_id,
            "focus_object_id": focus_object_id,
            "chart_id": chart_id,
            "frame_id": chart_frame_id,
            "map_origin_position_ref": build_orbit_position_ref(
                object_id=center_object_id or "camera.orbit",
                local_position=[0, 0, 0],
                frame_id=chart_frame_id,
                chart_id=chart_id,
                extensions={
                    "role": "orbit_map_origin",
                    "chart_mode": chart_mode,
                },
            ),
            "provider_id": str(provider_resolution.get("provider_id", DEFAULT_EPHEMERIS_PROVIDER_ID)).strip() or DEFAULT_EPHEMERIS_PROVIDER_ID,
            "provider_resolution": dict(provider_resolution),
            "orbit_path_policy_id": str(policy_row.get("policy_id", "")).strip() or DEFAULT_ORBIT_PATH_POLICY_ID,
            "layer_marker_rows": list(layer_marker_rows),
            "registry_hashes": {
                "ephemeris_provider_registry_hash": ephemeris_provider_registry_hash(),
                "orbit_path_policy_registry_hash": orbit_path_policy_registry_hash(),
            },
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    payload = {
        "result": "complete",
        "available": True,
        "source_kind": "derived.orbit_view_artifact",
        "cache_hit": False,
        "cache_key": cache_key,
        "lens_layer_ids": ["layer.orbits"],
        "orbit_view_artifact": artifact,
        "layer_source_payloads": build_orbit_layer_source_payloads({"orbit_view_artifact": artifact}),
        "presentation": {
            "preferred_presentation": "summary" if str(ui_mode or "").strip().lower() in {"cli", "tui"} else "buffer",
            "summary": {
                "chart_mode": chart_mode,
                "body_count": len(body_entries),
                "path_count": len(sampled_paths),
                "focus_object_id": focus_object_id,
            },
            "summary_text": "orbit chart={} bodies={} paths={}".format(
                chart_mode,
                len(body_entries),
                len(sampled_paths),
            ),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


__all__ = [
    "ORBIT_VIEW_ENGINE_VERSION",
    "build_orbit_layer_source_payloads",
    "build_orbit_view_surface",
    "orbit_view_artifact_hash",
]

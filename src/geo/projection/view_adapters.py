"""Deterministic GEO-5 projected-view adapters for ASCII and GUI buffers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _cell_sort_key(row: Mapping[str, object]) -> Tuple[int, int, str]:
    projected = _as_map(row.get("projected_coord"))
    geo_cell_key = _as_map(row.get("geo_cell_key"))
    return (
        int(_as_int(projected.get("y_index", projected.get("v_index", 0)), 0)),
        int(_as_int(projected.get("x_index", projected.get("u_index", 0)), 0)),
        canonical_sha256(geo_cell_key),
    )


def _visible_layer_ids(row: Mapping[str, object]) -> List[str]:
    layers = _as_map(row.get("layers"))
    visible = []
    for layer_id in sorted(layers.keys()):
        if str(_as_map(layers.get(layer_id)).get("state", "")).strip().lower() == "visible":
            visible.append(layer_id)
    return visible


def _glyph_for_cell(row: Mapping[str, object], preferred_layer_order: List[str]) -> str:
    layers = _as_map(row.get("layers"))
    ordered_layer_ids = preferred_layer_order + [layer_id for layer_id in sorted(layers.keys()) if layer_id not in set(preferred_layer_order)]
    for layer_id in ordered_layer_ids:
        layer = _as_map(layers.get(layer_id))
        if str(layer.get("state", "")).strip().lower() != "visible":
            continue
        value = layer.get("value")
        if layer_id == "layer.entity_markers_stub":
            return "E"
        if layer_id == "layer.infrastructure_stub":
            return "#"
        if layer_id == "layer.terrain_stub":
            token = str(_as_map(value).get("terrain_class", value)).strip()
            return token[:1].upper() if token else "T"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, int):
            band = max(-9, min(9, int(value) // 10))
            return str(abs(band)) if band != 0 else "."
        if isinstance(value, str) and value:
            return value[:1].upper()
        return "*"
    return "?"


def render_projected_view_ascii(
    projected_view_artifact: Mapping[str, object] | None,
    *,
    preferred_layer_order: Iterable[object] | None = None,
) -> dict:
    artifact = _as_map(projected_view_artifact)
    rows = sorted(
        (dict(item) for item in list(artifact.get("rendered_cells") or []) if isinstance(item, Mapping)),
        key=_cell_sort_key,
    )
    if not rows:
        payload = {"result": "complete", "ascii_lines": [], "ascii_grid": "", "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    preferred = _sorted_strings(preferred_layer_order)
    xs = [int(_as_int(_as_map(row.get("projected_coord")).get("x_index", _as_map(row.get("projected_coord")).get("u_index", 0)), 0)) for row in rows]
    ys = [int(_as_int(_as_map(row.get("projected_coord")).get("y_index", _as_map(row.get("projected_coord")).get("v_index", 0)), 0)) for row in rows]
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    width = int(max_x - min_x + 1)
    height = int(max_y - min_y + 1)
    grid = [[" " for _ in range(width)] for _ in range(height)]
    for row in rows:
        projected = _as_map(row.get("projected_coord"))
        x_idx = int(_as_int(projected.get("x_index", projected.get("u_index", 0)), 0)) - min_x
        y_idx = int(_as_int(projected.get("y_index", projected.get("v_index", 0)), 0)) - min_y
        grid[y_idx][x_idx] = _glyph_for_cell(row, preferred)
    lines = ["".join(line) for line in grid]
    payload = {
        "result": "complete",
        "ascii_lines": lines,
        "ascii_grid": "\n".join(lines),
        "visible_layer_ids": _sorted_strings(layer_id for row in rows for layer_id in _visible_layer_ids(row)),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_projected_view_layer_buffers(projected_view_artifact: Mapping[str, object] | None) -> dict:
    artifact = _as_map(projected_view_artifact)
    rendered_cells = sorted(
        (dict(item) for item in list(artifact.get("rendered_cells") or []) if isinstance(item, Mapping)),
        key=_cell_sort_key,
    )
    layer_buffers: Dict[str, List[dict]] = {}
    for row in rendered_cells:
        projected = _as_map(row.get("projected_coord"))
        for layer_id in sorted(_as_map(row.get("layers")).keys()):
            layer = _as_map(_as_map(row.get("layers")).get(layer_id))
            layer_buffers.setdefault(layer_id, []).append(
                {
                    "projected_coord": dict(projected),
                    "geo_cell_key": _as_map(row.get("geo_cell_key")),
                    "state": str(layer.get("state", "")).strip() or "hidden",
                    "value": layer.get("value"),
                }
            )
    payload = {
        "result": "complete",
        "layer_buffers": dict((key, list(layer_buffers[key])) for key in sorted(layer_buffers.keys())),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload

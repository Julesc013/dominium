"""Deterministic core SpatialNode helpers."""

from __future__ import annotations

from typing import Dict, Mapping


REFUSAL_CORE_SPATIAL_INVALID = "refusal.core.spatial.invalid"


class SpatialError(ValueError):
    """Deterministic spatial refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _round_div_away_from_zero(numerator: int, denominator: int) -> int:
    if int(denominator) == 0:
        raise SpatialError(
            REFUSAL_CORE_SPATIAL_INVALID,
            "division by zero in SpatialNode fixed-point calculation",
            {"denominator": str(denominator)},
        )
    n = int(numerator)
    d = int(denominator)
    sign = -1 if (n < 0) ^ (d < 0) else 1
    abs_n = abs(n)
    abs_d = abs(d)
    quotient = abs_n // abs_d
    remainder = abs_n % abs_d
    if remainder * 2 >= abs_d:
        quotient += 1
    return int(sign * quotient)


def _normalize_transform(row: object) -> dict:
    payload = dict(row or {}) if isinstance(row, dict) else {}
    translation = dict(payload.get("translation_mm") or {})
    rotation = dict(payload.get("rotation_mdeg") or {})
    scale_permille = int(_as_int(payload.get("scale_permille", 1000), 1000))
    if scale_permille <= 0:
        scale_permille = 1000
    return {
        "translation_mm": {
            "x": int(_as_int(translation.get("x", 0), 0)),
            "y": int(_as_int(translation.get("y", 0), 0)),
            "z": int(_as_int(translation.get("z", 0), 0)),
        },
        "rotation_mdeg": {
            "yaw": int(_as_int(rotation.get("yaw", 0), 0)),
            "pitch": int(_as_int(rotation.get("pitch", 0), 0)),
            "roll": int(_as_int(rotation.get("roll", 0), 0)),
        },
        "scale_permille": int(scale_permille),
    }


def normalize_spatial_node(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    spatial_id = str(payload.get("spatial_id", "")).strip()
    frame_id = str(payload.get("frame_id", "")).strip()
    if not spatial_id or not frame_id:
        raise SpatialError(
            REFUSAL_CORE_SPATIAL_INVALID,
            "spatial node missing required spatial_id/frame_id",
            {"spatial_id": spatial_id, "frame_id": frame_id},
        )
    parent_spatial_id_raw = payload.get("parent_spatial_id")
    parent_spatial_id = None
    if parent_spatial_id_raw is not None:
        token = str(parent_spatial_id_raw).strip()
        parent_spatial_id = token if token else None
    bounds = payload.get("bounds")
    if bounds is None:
        bounds = {}
    if not isinstance(bounds, dict):
        raise SpatialError(
            REFUSAL_CORE_SPATIAL_INVALID,
            "spatial node bounds must be object",
            {"spatial_id": spatial_id},
        )
    return {
        "schema_version": "1.0.0",
        "spatial_id": spatial_id,
        "parent_spatial_id": parent_spatial_id,
        "frame_id": frame_id,
        "transform": _normalize_transform(payload.get("transform")),
        "bounds": dict(bounds),
        "extensions": dict(payload.get("extensions") or {}),
    }


def compose_transforms(parent_transform: Mapping[str, object], child_transform: Mapping[str, object]) -> dict:
    parent = _normalize_transform(parent_transform)
    child = _normalize_transform(child_transform)
    return {
        "translation_mm": {
            "x": int(parent["translation_mm"]["x"] + child["translation_mm"]["x"]),
            "y": int(parent["translation_mm"]["y"] + child["translation_mm"]["y"]),
            "z": int(parent["translation_mm"]["z"] + child["translation_mm"]["z"]),
        },
        "rotation_mdeg": {
            "yaw": int(parent["rotation_mdeg"]["yaw"] + child["rotation_mdeg"]["yaw"]),
            "pitch": int(parent["rotation_mdeg"]["pitch"] + child["rotation_mdeg"]["pitch"]),
            "roll": int(parent["rotation_mdeg"]["roll"] + child["rotation_mdeg"]["roll"]),
        },
        "scale_permille": int(
            _round_div_away_from_zero(
                int(parent["scale_permille"]) * int(child["scale_permille"]),
                1000,
            )
        ),
    }


def resolve_world_transform(spatial_nodes: object, *, target_spatial_id: str) -> dict:
    rows: Dict[str, dict] = {}
    for row in list(spatial_nodes or []):
        if not isinstance(row, dict):
            continue
        normalized = normalize_spatial_node(row)
        rows[str(normalized.get("spatial_id", ""))] = normalized
    target_id = str(target_spatial_id).strip()
    if target_id not in rows:
        raise SpatialError(
            REFUSAL_CORE_SPATIAL_INVALID,
            "target spatial node is missing",
            {"target_spatial_id": target_id},
        )
    visited = set()
    chain = []
    cursor = target_id
    while cursor:
        if cursor in visited:
            raise SpatialError(
                REFUSAL_CORE_SPATIAL_INVALID,
                "spatial hierarchy cycle detected",
                {"spatial_id": cursor},
            )
        visited.add(cursor)
        row = dict(rows.get(cursor) or {})
        chain.append(row)
        parent = row.get("parent_spatial_id")
        cursor = str(parent).strip() if isinstance(parent, str) and str(parent).strip() else ""
    world = _normalize_transform({})
    for row in reversed(chain):
        world = compose_transforms(world, dict(row.get("transform") or {}))
    return {
        "target_spatial_id": target_id,
        "world_transform": world,
        "depth": len(chain),
    }


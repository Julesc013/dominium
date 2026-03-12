"""Deterministic GAL-0 galaxy metadata proxy helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from math import isqrt
from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from src.worldgen.mw import (
    DEFAULT_GALAXY_PRIORS_ID,
    galaxy_priors_rows,
    mw_cell_position_pc,
    mw_density_permille,
    mw_metallicity_permille,
)


GALACTIC_REGION_REGISTRY_REL = os.path.join("data", "registries", "galactic_region_registry.json")
GALAXY_PROXY_ENGINE_VERSION = "GAL0-3"
GALAXY_PROXY_SPATIAL_SCOPE_ID = "spatial.galaxy.default"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return dict(json.load(handle) or {})
    except (OSError, TypeError, ValueError):
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


def galactic_region_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(GALACTIC_REGION_REGISTRY_REL),
        row_key="galactic_regions",
        id_key="region_id",
    )


def galactic_region_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(GALACTIC_REGION_REGISTRY_REL))


def _galactic_region_by_id() -> Dict[str, dict]:
    return galactic_region_rows()


def galactic_region_value_from_id(region_id: str) -> int:
    row = _as_map(_galactic_region_by_id().get(str(region_id).strip()))
    return int(max(0, _as_int(row.get("field_scalar_code", 0), 0)))


def galactic_region_id_from_value(region_value: int) -> str:
    value = int(max(0, _as_int(region_value, 0)))
    for region_id, row in sorted(_galactic_region_by_id().items()):
        if int(max(0, _as_int(_as_map(row).get("field_scalar_code", 0), 0))) == value:
            return str(region_id)
    return ""


def _quantity_value(payload: Mapping[str, object], default_value: int) -> int:
    row = _as_map(payload)
    return max(0, _as_int(row.get("value"), default_value))


def _geo_hash(geo_cell_key: Mapping[str, object]) -> str:
    key_row = _coerce_cell_key(geo_cell_key) or {}
    return canonical_sha256(_semantic_cell_key(key_row)) if key_row else ""


def _geo_sort_tuple(geo_cell_key: Mapping[str, object]) -> tuple:
    key_row = _coerce_cell_key(geo_cell_key) or {}
    index_tuple = [int(item) for item in list(key_row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return (
        str(key_row.get("chart_id", "")).strip(),
        int(_as_int(key_row.get("refinement_level", 0), 0)),
        int(index_tuple[0]),
        int(index_tuple[1]),
        int(index_tuple[2]),
    )


def _legacy_cell_alias_from_key(geo_cell_key: Mapping[str, object]) -> str:
    key_row = _coerce_cell_key(geo_cell_key) or {}
    extensions = _as_map(key_row.get("extensions"))
    alias = str(extensions.get("legacy_cell_alias", "")).strip()
    if alias:
        return alias
    index_tuple = [int(item) for item in list(key_row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return "cell.{}.{}.{}".format(index_tuple[0], index_tuple[1], index_tuple[2])


def classify_galactic_region(
    *,
    priors_row: Mapping[str, object],
    radius_pc: int,
    z_pc: int,
) -> str:
    row = _as_map(priors_row)
    disk_radius_pc = max(1, _quantity_value(_as_map(row.get("disk_radius")), 60000))
    bulge_radius_pc = max(1, _quantity_value(_as_map(row.get("bulge_radius")), 6000))
    disk_half_thickness_pc = max(1, _quantity_value(_as_map(row.get("disk_thickness")), 1200) // 2)
    bulge_distance_pc = isqrt((max(0, int(radius_pc)) ** 2) + (abs(int(z_pc)) ** 2))
    if bulge_distance_pc <= bulge_radius_pc:
        return "region.bulge"
    if abs(int(z_pc)) > disk_half_thickness_pc * 2 or int(radius_pc) > disk_radius_pc:
        return "region.halo"
    if int(radius_pc) <= max(bulge_radius_pc + 1, disk_radius_pc // 2):
        return "region.inner_disk"
    return "region.outer_disk"


def radiation_background_proxy_permille(
    *,
    priors_row: Mapping[str, object],
    radius_pc: int,
    z_pc: int,
    stellar_density_proxy_value: int,
    galactic_region_id: str,
) -> int:
    row = _as_map(priors_row)
    disk_radius_pc = max(1, _quantity_value(_as_map(row.get("disk_radius")), 60000))
    disk_half_thickness_pc = max(1, _quantity_value(_as_map(row.get("disk_thickness")), 1200) // 2)
    center_term = max(0, 1000 - min(1000, (max(0, int(radius_pc)) * 1000) // max(1, disk_radius_pc)))
    vertical_term = max(0, 1000 - min(1000, (abs(int(z_pc)) * 1000) // max(1, disk_half_thickness_pc * 4)))
    value = ((center_term * 600) + (vertical_term * 150) + (int(stellar_density_proxy_value) * 250)) // 1000
    if str(galactic_region_id).strip() == "region.bulge":
        value = max(value, 760)
    elif str(galactic_region_id).strip() == "region.halo":
        value = min(value, 240)
    return int(_clamp(value, 0, 1000))


def evaluate_galaxy_cell_proxy(
    *,
    geo_cell_key: Mapping[str, object],
    galaxy_priors_row: Mapping[str, object],
    galaxy_priors_id: str = DEFAULT_GALAXY_PRIORS_ID,
    current_tick: int = 0,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key) or {}
    if not cell_key:
        return {}
    priors_row = _as_map(galaxy_priors_row)
    cell_size_pc = max(1, _as_int(priors_row.get("cell_size_pc", 10), 10))
    x_pc, y_pc, z_pc = mw_cell_position_pc(cell_key, cell_size_pc)
    radius_pc = isqrt((abs(int(x_pc)) ** 2) + (abs(int(y_pc)) ** 2))
    stellar_density_proxy_value = mw_density_permille(
        priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
        x_pc=x_pc,
        y_pc=y_pc,
        cell_size_pc=cell_size_pc,
    )
    metallicity_proxy_value = mw_metallicity_permille(priors_row, radius_pc)
    galactic_region_id = classify_galactic_region(
        priors_row=priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
    )
    galactic_region_value = galactic_region_value_from_id(galactic_region_id)
    radiation_proxy_value = radiation_background_proxy_permille(
        priors_row=priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
        stellar_density_proxy_value=stellar_density_proxy_value,
        galactic_region_id=galactic_region_id,
    )
    payload = {
        "cell_id": _legacy_cell_alias_from_key(cell_key),
        "geo_cell_key": dict(cell_key),
        "current_tick": int(max(0, _as_int(current_tick, 0))),
        "galaxy_priors_id": str(galaxy_priors_id).strip() or DEFAULT_GALAXY_PRIORS_ID,
        "stellar_density_proxy_value": int(_clamp(stellar_density_proxy_value, 0, 1000)),
        "metallicity_proxy_value": int(_clamp(metallicity_proxy_value, 0, 1000)),
        "radiation_background_proxy_value": int(_clamp(radiation_proxy_value, 0, 1000)),
        "galactic_region_id": str(galactic_region_id),
        "galactic_region_value": int(galactic_region_value),
        "deterministic_fingerprint": "",
        "extensions": {
            "galactocentric_position_pc": [int(x_pc), int(y_pc), int(z_pc)],
            "galactocentric_radius_pc": int(radius_pc),
            "registry_hashes": {
                "galaxy_priors_registry_hash": canonical_sha256({"rows": galaxy_priors_rows()}),
                "galactic_region_registry_hash": galactic_region_registry_hash(),
            },
            "source": GALAXY_PROXY_ENGINE_VERSION,
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _candidate_row(raw: Mapping[str, object]) -> dict:
    row = _as_map(raw)
    worldgen_result = _as_map(row.get("worldgen_result"))
    worldgen_ext = _as_map(worldgen_result.get("extensions"))
    geo_cell_key = _coerce_cell_key(row.get("geo_cell_key")) or _coerce_cell_key(worldgen_result.get("geo_cell_key")) or {}
    galaxy_priors_id = str(row.get("galaxy_priors_id", "")).strip() or str(worldgen_ext.get("galaxy_priors_id", "")).strip()
    return {
        "geo_cell_key": dict(geo_cell_key),
        "galaxy_priors_id": galaxy_priors_id or DEFAULT_GALAXY_PRIORS_ID,
    }


def build_galaxy_proxy_field_updates(
    *,
    proxy_evaluations: Sequence[Mapping[str, object]],
    spatial_scope_id: str = GALAXY_PROXY_SPATIAL_SCOPE_ID,
) -> List[dict]:
    evaluations = [dict(row) for row in list(proxy_evaluations or []) if isinstance(row, Mapping)]
    field_updates: List[dict] = []
    for row in evaluations:
        cell_id = str(row.get("cell_id", "")).strip()
        geo_cell_key = _coerce_cell_key(row.get("geo_cell_key")) or {}
        if not cell_id:
            continue
        field_updates.extend(
            [
                {
                    "field_id": "field.stellar_density_proxy.galaxy",
                    "field_type_id": "field.stellar_density_proxy",
                    "spatial_scope_id": str(spatial_scope_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("stellar_density_proxy_value", 0), 0)),
                    "extensions": {
                        "source": GALAXY_PROXY_ENGINE_VERSION,
                    },
                },
                {
                    "field_id": "field.metallicity_proxy.galaxy",
                    "field_type_id": "field.metallicity_proxy",
                    "spatial_scope_id": str(spatial_scope_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("metallicity_proxy_value", 0), 0)),
                    "extensions": {
                        "source": GALAXY_PROXY_ENGINE_VERSION,
                    },
                },
                {
                    "field_id": "field.radiation_background_proxy.galaxy",
                    "field_type_id": "field.radiation_background_proxy",
                    "spatial_scope_id": str(spatial_scope_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("radiation_background_proxy_value", 0), 0)),
                    "extensions": {
                        "source": GALAXY_PROXY_ENGINE_VERSION,
                    },
                },
                {
                    "field_id": "field.galactic_region_id.galaxy",
                    "field_type_id": "field.galactic_region_id",
                    "spatial_scope_id": str(spatial_scope_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("galactic_region_value", 0), 0)),
                    "extensions": {
                        "galactic_region_id": str(row.get("galactic_region_id", "")).strip(),
                        "source": GALAXY_PROXY_ENGINE_VERSION,
                    },
                },
            ]
        )
    return sorted(
        field_updates,
        key=lambda row: (
            str(row.get("field_id", "")),
            _geo_sort_tuple(row.get("geo_cell_key") or {}),
            str(row.get("cell_id", "")),
        ),
    )


def build_galaxy_proxy_update_plan(
    *,
    worldgen_results: object,
    current_tick: int,
    galaxy_priors_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    priors_by_id = galaxy_priors_rows(galaxy_priors_registry_payload)
    candidates = []
    for raw in list(worldgen_results or []):
        if not isinstance(raw, Mapping):
            continue
        candidate = _candidate_row(raw)
        if not candidate.get("geo_cell_key"):
            continue
        priors_id = str(candidate.get("galaxy_priors_id", "")).strip() or DEFAULT_GALAXY_PRIORS_ID
        priors_row = _as_map(priors_by_id.get(priors_id))
        if not priors_row:
            continue
        candidates.append(
            {
                "geo_cell_key": dict(candidate.get("geo_cell_key") or {}),
                "galaxy_priors_id": priors_id,
                "galaxy_priors_row": priors_row,
            }
        )
    candidates = sorted(
        candidates,
        key=lambda row: (
            _geo_sort_tuple(row.get("geo_cell_key") or {}),
            str(row.get("galaxy_priors_id", "")),
        ),
    )
    evaluations = [
        evaluate_galaxy_cell_proxy(
            geo_cell_key=dict(row.get("geo_cell_key") or {}),
            galaxy_priors_row=dict(row.get("galaxy_priors_row") or {}),
            galaxy_priors_id=str(row.get("galaxy_priors_id", "")).strip(),
            current_tick=int(current_tick),
        )
        for row in candidates
    ]
    field_updates = build_galaxy_proxy_field_updates(proxy_evaluations=evaluations)
    payload = {
        "result": "complete",
        "current_tick": int(max(0, _as_int(current_tick, 0))),
        "cell_ids": [str(row.get("cell_id", "")).strip() for row in evaluations if str(row.get("cell_id", "")).strip()],
        "evaluations": [dict(row) for row in evaluations],
        "field_updates": [dict(row) for row in field_updates],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def galaxy_proxy_window_hash(rows: object) -> str:
    normalized = []
    for raw in list(rows or []):
        row = _as_map(raw)
        normalized.append(
            {
                "cell_id": str(row.get("cell_id", "")).strip(),
                "stellar_density_proxy_value": int(_as_int(row.get("stellar_density_proxy_value", 0), 0)),
                "metallicity_proxy_value": int(_as_int(row.get("metallicity_proxy_value", 0), 0)),
                "radiation_background_proxy_value": int(_as_int(row.get("radiation_background_proxy_value", 0), 0)),
                "galactic_region_id": str(row.get("galactic_region_id", "")).strip(),
            }
        )
    normalized.sort(key=lambda item: item["cell_id"])
    return canonical_sha256(normalized)


__all__ = [
    "GALACTIC_REGION_REGISTRY_REL",
    "GALAXY_PROXY_ENGINE_VERSION",
    "GALAXY_PROXY_SPATIAL_SCOPE_ID",
    "build_galaxy_proxy_field_updates",
    "build_galaxy_proxy_update_plan",
    "classify_galactic_region",
    "evaluate_galaxy_cell_proxy",
    "galactic_region_id_from_value",
    "galactic_region_registry_hash",
    "galactic_region_rows",
    "galactic_region_value_from_id",
    "galaxy_proxy_window_hash",
    "radiation_background_proxy_permille",
]

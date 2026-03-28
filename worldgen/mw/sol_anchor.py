"""Deterministic Sol anchor helpers for the official minimal pin pack."""

from __future__ import annotations

import copy
from typing import Dict, List, Mapping

from geo.index.geo_index_engine import _coerce_cell_key
from geo.index.object_id_engine import geo_object_id


SOL_ANCHOR_ID = "anchor.sol.default"
SOL_ANCHOR_CELL_INDEX_TUPLE = [801, 0, 0]
SOL_ANCHOR_BODY_SLOTS = (
    {"slot_id": "sol.system", "display_name": "Sol", "object_kind_id": "kind.star_system", "local_subkey": "star_system:0"},
    {"slot_id": "sol.star", "display_name": "Sol", "object_kind_id": "kind.star", "parent_slot_id": "sol.system", "star_index": 0},
    {"slot_id": "sol.planet.mercury", "display_name": "Mercury", "object_kind_id": "kind.planet", "parent_slot_id": "sol.system", "planet_index": 0},
    {"slot_id": "sol.planet.venus", "display_name": "Venus", "object_kind_id": "kind.planet", "parent_slot_id": "sol.system", "planet_index": 1},
    {"slot_id": "sol.planet.earth", "display_name": "Earth", "object_kind_id": "kind.planet", "parent_slot_id": "sol.system", "planet_index": 2},
    {"slot_id": "sol.moon.luna", "display_name": "Luna", "object_kind_id": "kind.moon", "parent_slot_id": "sol.planet.earth", "planet_index": 2, "moon_index": 0},
    {"slot_id": "sol.planet.mars", "display_name": "Mars", "object_kind_id": "kind.planet", "parent_slot_id": "sol.system", "planet_index": 3},
    {"slot_id": "sol.planet.jupiter", "display_name": "Jupiter", "object_kind_id": "kind.planet", "parent_slot_id": "sol.system", "planet_index": 4},
    {"slot_id": "sol.planet.saturn", "display_name": "Saturn", "object_kind_id": "kind.planet", "parent_slot_id": "sol.system", "planet_index": 5},
    {"slot_id": "sol.planet.uranus", "display_name": "Uranus", "object_kind_id": "kind.planet", "parent_slot_id": "sol.system", "planet_index": 6},
    {"slot_id": "sol.planet.neptune", "display_name": "Neptune", "object_kind_id": "kind.planet", "parent_slot_id": "sol.system", "planet_index": 7},
)


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _default_anchor_cell_key() -> dict:
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.r3_infinite",
        "chart_id": "chart.global.r3",
        "index_tuple": [int(item) for item in list(SOL_ANCHOR_CELL_INDEX_TUPLE)],
        "refinement_level": 0,
        "extensions": {
            "anchor_id": SOL_ANCHOR_ID,
            "source": "SOL0-3",
        },
    }


def resolve_sol_anchor_cell_key(realism_profile_row: Mapping[str, object] | None = None) -> dict:
    realism_row = _as_map(realism_profile_row)
    extensions = _as_map(realism_row.get("extensions"))
    candidate = _coerce_cell_key(_as_map(extensions.get("sol_anchor_cell_key")))
    return candidate or _default_anchor_cell_key()


def sol_anchor_matches_cell(
    geo_cell_key: Mapping[str, object] | None,
    realism_profile_row: Mapping[str, object] | None = None,
) -> bool:
    candidate = _coerce_cell_key(geo_cell_key)
    anchor = resolve_sol_anchor_cell_key(realism_profile_row)
    if not candidate or not anchor:
        return False
    return bool(
        str(candidate.get("partition_profile_id", "")).strip() == str(anchor.get("partition_profile_id", "")).strip()
        and str(candidate.get("topology_profile_id", "")).strip() == str(anchor.get("topology_profile_id", "")).strip()
        and str(candidate.get("chart_id", "")).strip() == str(anchor.get("chart_id", "")).strip()
        and int(_as_int(candidate.get("refinement_level", 0), 0)) == int(_as_int(anchor.get("refinement_level", 0), 0))
        and [int(_as_int(item, 0)) for item in list(candidate.get("index_tuple") or [])]
        == [int(_as_int(item, 0)) for item in list(anchor.get("index_tuple") or [])]
    )


def sol_anchor_body_slots() -> List[dict]:
    return [copy.deepcopy(dict(row)) for row in SOL_ANCHOR_BODY_SLOTS]


def sol_anchor_body_slots_by_id() -> Dict[str, dict]:
    rows = {}
    for row in sol_anchor_body_slots():
        slot_id = str(row.get("slot_id", "")).strip()
        if slot_id:
            rows[slot_id] = row
    return dict((key, dict(rows[key])) for key in sorted(rows.keys()))


def _slot_local_subkey(slot_row: Mapping[str, object], object_ids_by_slot: Mapping[str, str]) -> str:
    slot_id = str(_as_map(slot_row).get("slot_id", "")).strip()
    if slot_id == "sol.system":
        return "star_system:0"
    parent_system_id = str(object_ids_by_slot.get("sol.system", "")).strip()
    planet_index = _as_int(_as_map(slot_row).get("planet_index"), 0)
    moon_index = _as_int(_as_map(slot_row).get("moon_index"), 0)
    star_index = _as_int(_as_map(slot_row).get("star_index"), 0)
    if slot_id == "sol.star":
        return "system:{}:star:{}".format(parent_system_id, star_index)
    if str(_as_map(slot_row).get("object_kind_id", "")).strip() == "kind.moon":
        return "system:{}:moon:{}:{}".format(parent_system_id, planet_index, moon_index)
    return "system:{}:planet:{}".format(parent_system_id, planet_index)


def sol_anchor_object_rows(
    *,
    universe_identity_hash: str,
    geo_cell_key: Mapping[str, object] | None = None,
    realism_profile_row: Mapping[str, object] | None = None,
) -> List[dict]:
    anchor_cell_key = _coerce_cell_key(geo_cell_key) or resolve_sol_anchor_cell_key(realism_profile_row)
    rows: List[dict] = []
    object_ids_by_slot: Dict[str, str] = {}
    for slot_row in sol_anchor_body_slots():
        slot_id = str(slot_row.get("slot_id", "")).strip()
        object_kind_id = str(slot_row.get("object_kind_id", "")).strip()
        if not slot_id or not object_kind_id:
            continue
        local_subkey = _slot_local_subkey(slot_row, object_ids_by_slot)
        object_payload = geo_object_id(
            universe_identity_hash=str(universe_identity_hash or "").strip(),
            cell_key=anchor_cell_key,
            object_kind_id=object_kind_id,
            local_subkey=local_subkey,
        )
        if str(object_payload.get("result", "")) != "complete":
            continue
        object_id = str(object_payload.get("object_id_hash", "")).strip()
        object_ids_by_slot[slot_id] = object_id
        rows.append(
            {
                "slot_id": slot_id,
                "display_name": str(slot_row.get("display_name", "")).strip(),
                "object_kind_id": object_kind_id,
                "local_subkey": local_subkey,
                "object_id": object_id,
                "geo_cell_key": copy.deepcopy(anchor_cell_key),
                "planet_index": _as_map(slot_row).get("planet_index"),
                "moon_index": _as_map(slot_row).get("moon_index"),
                "parent_slot_id": str(slot_row.get("parent_slot_id", "")).strip(),
                "extensions": {
                    "anchor_id": SOL_ANCHOR_ID,
                    "source": "SOL0-3",
                },
            }
        )
    return [dict(row) for row in rows]


def sol_anchor_object_ids(
    *,
    universe_identity_hash: str,
    geo_cell_key: Mapping[str, object] | None = None,
    realism_profile_row: Mapping[str, object] | None = None,
) -> Dict[str, str]:
    rows = sol_anchor_object_rows(
        universe_identity_hash=universe_identity_hash,
        geo_cell_key=geo_cell_key,
        realism_profile_row=realism_profile_row,
    )
    return dict(
        (str(row.get("slot_id", "")).strip(), str(row.get("object_id", "")).strip())
        for row in rows
        if str(row.get("slot_id", "")).strip() and str(row.get("object_id", "")).strip()
    )


__all__ = [
    "SOL_ANCHOR_BODY_SLOTS",
    "SOL_ANCHOR_CELL_INDEX_TUPLE",
    "SOL_ANCHOR_ID",
    "resolve_sol_anchor_cell_key",
    "sol_anchor_body_slots",
    "sol_anchor_body_slots_by_id",
    "sol_anchor_matches_cell",
    "sol_anchor_object_ids",
    "sol_anchor_object_rows",
]

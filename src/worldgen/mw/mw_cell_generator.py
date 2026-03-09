"""Deterministic MW-0 cell-scoped Milky Way generator."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from math import isqrt
from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from src.geo.index.object_id_engine import geo_object_id


DEFAULT_GALAXY_PRIORS_ID = "priors.milkyway_stub_default"
GALAXY_PRIORS_REGISTRY_REL = os.path.join("data", "registries", "galaxy_priors_registry.json")
MW_CELL_GENERATOR_VERSION = "MW0-3"

_TAN_22_5_PERMILLE = 414
_TAN_67_5_PERMILLE = 2414


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


def _refusal(message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def galaxy_priors_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(GALAXY_PRIORS_REGISTRY_REL), row_key="galaxy_priors", id_key="priors_id")


def galaxy_priors_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(GALAXY_PRIORS_REGISTRY_REL))


def _hash_int(seed: str, salt: str) -> int:
    return int(canonical_sha256({"seed": str(seed), "salt": str(salt)})[:16], 16)


def _pick_weighted(seed: str, salt: str, weights: Mapping[str, object], default_value: str) -> str:
    rows = []
    total = 0
    for key, value in sorted(_as_map(weights).items(), key=lambda item: str(item[0])):
        weight = max(0, _as_int(value, 0))
        if weight <= 0:
            continue
        token = str(key).strip()
        if not token:
            continue
        rows.append((token, weight))
        total += weight
    if total <= 0:
        return str(default_value)
    draw = _hash_int(seed, salt) % total
    cursor = 0
    for token, weight in rows:
        cursor += weight
        if draw < cursor:
            return token
    return rows[-1][0]


def _quantity_value(payload: Mapping[str, object], default_value: int) -> int:
    row = _as_map(payload)
    return max(0, _as_int(row.get("value"), default_value))


def _pitch_angle_mdeg(payload: Mapping[str, object], default_value: int = 12000) -> int:
    row = _as_map(payload)
    return max(1000, _as_int(row.get("value_milli"), default_value))


def _position_pc(cell_key: Mapping[str, object], cell_size_pc: int) -> Tuple[int, int, int]:
    index_tuple = list(_as_map(cell_key).get("index_tuple") or [])
    x_idx = _as_int(index_tuple[0] if len(index_tuple) > 0 else 0, 0)
    y_idx = _as_int(index_tuple[1] if len(index_tuple) > 1 else 0, 0)
    z_idx = _as_int(index_tuple[2] if len(index_tuple) > 2 else 0, 0)
    scale = max(1, int(cell_size_pc))
    return (x_idx * scale, y_idx * scale, z_idx * scale)


def _angle_sector_8(x_pc: int, y_pc: int) -> int:
    if x_pc == 0 and y_pc == 0:
        return 0
    ax = abs(int(x_pc))
    ay = abs(int(y_pc))
    if ay * 1000 <= ax * _TAN_22_5_PERMILLE:
        return 0 if x_pc >= 0 else 4
    if ay * 1000 >= ax * _TAN_67_5_PERMILLE:
        return 2 if y_pc >= 0 else 6
    if x_pc >= 0 and y_pc >= 0:
        return 1
    if x_pc < 0 <= y_pc:
        return 3
    if x_pc < 0 and y_pc < 0:
        return 5
    return 7


def _spiral_arm_bonus_permille(priors_row: Mapping[str, object], *, radius_pc: int, x_pc: int, y_pc: int, cell_size_pc: int) -> int:
    arm_count = max(1, min(8, _as_int(priors_row.get("arm_count"), 4)))
    density_params = _as_map(_as_map(priors_row).get("density_params"))
    arm_contrast_permille = max(0, _as_int(density_params.get("arm_contrast_permille"), 240))
    arm_width_sectors = max(0, _as_int(density_params.get("arm_width_sectors"), 1))
    pitch_deg = max(1, _pitch_angle_mdeg(_as_map(priors_row.get("pitch_angle")), 12000) // 1000)
    arm_twist_pc = max(max(1, int(cell_size_pc)), 180000 // pitch_deg)
    arm_stride = max(1, 8 // arm_count)
    sector = (_angle_sector_8(x_pc, y_pc) - ((max(0, int(radius_pc)) // arm_twist_pc) % 8)) % 8
    anchors = [((idx * arm_stride) % 8) for idx in range(arm_count)]
    distance = min(min((sector - anchor) % 8, (anchor - sector) % 8) for anchor in anchors)
    if distance > arm_width_sectors:
        return 0
    width = arm_width_sectors + 1
    return max(0, arm_contrast_permille * (width - distance) // width)


def _density_permille(priors_row: Mapping[str, object], *, radius_pc: int, z_pc: int, x_pc: int, y_pc: int, cell_size_pc: int) -> int:
    row = _as_map(priors_row)
    density_params = _as_map(row.get("density_params"))
    disk_radius_pc = max(1, _quantity_value(_as_map(row.get("disk_radius")), 60000))
    bulge_radius_pc = max(1, _quantity_value(_as_map(row.get("bulge_radius")), 6000))
    disk_half_thickness_pc = max(1, _quantity_value(_as_map(row.get("disk_thickness")), 1200) // 2)
    bulge_distance_pc = isqrt((max(0, int(radius_pc)) ** 2) + (abs(int(z_pc)) ** 2))
    if int(radius_pc) > disk_radius_pc and bulge_distance_pc > bulge_radius_pc:
        return 0

    radial_scale_length_pc = max(1, _as_int(density_params.get("radial_scale_length_pc"), 18000))
    vertical_scale_height_pc = max(1, _as_int(density_params.get("vertical_scale_height_pc"), 400))
    bulge_core_boost_permille = max(0, _as_int(density_params.get("bulge_core_boost_permille"), 1800))
    halo_floor_permille = max(0, _as_int(density_params.get("halo_floor_permille"), 20))

    radial_permille = max(0, 1000 - min(1000, (max(0, int(radius_pc)) * 1000) // radial_scale_length_pc))
    vertical_permille = max(0, 1000 - min(1000, (abs(int(z_pc)) * 1000) // vertical_scale_height_pc))
    disk_permille = (radial_permille * vertical_permille) // 1000
    if abs(int(z_pc)) > disk_half_thickness_pc * 3:
        disk_permille = 0
    arm_bonus_permille = _spiral_arm_bonus_permille(
        row,
        radius_pc=int(radius_pc),
        x_pc=int(x_pc),
        y_pc=int(y_pc),
        cell_size_pc=int(cell_size_pc),
    )
    bulge_permille = 0
    if bulge_distance_pc <= bulge_radius_pc:
        bulge_permille = bulge_core_boost_permille * (bulge_radius_pc - bulge_distance_pc) // bulge_radius_pc
    return max(0, halo_floor_permille + disk_permille + arm_bonus_permille + bulge_permille)


def _expected_system_count_milli(priors_row: Mapping[str, object], *, density_permille: int) -> int:
    row = _as_map(priors_row)
    density_params = _as_map(row.get("density_params"))
    cell_size_pc = max(1, _as_int(row.get("cell_size_pc"), 10))
    volume_pc3 = cell_size_pc * cell_size_pc * cell_size_pc
    base_density = max(0, _as_int(density_params.get("midplane_systems_per_million_cubic_pc"), 9000))
    return max(0, (base_density * volume_pc3 * max(0, int(density_permille))) // 1000000)


def _deterministic_system_count(expected_system_count_milli: int, max_systems_per_cell: int, galaxy_stream_seed: str) -> int:
    base_count = max(0, int(expected_system_count_milli)) // 1000
    remainder = max(0, int(expected_system_count_milli)) % 1000
    extra = 1 if (_hash_int(galaxy_stream_seed, "mw0.system_count.remainder") % 1000) < remainder else 0
    return min(max(0, int(max_systems_per_cell)), base_count + extra)


def _metallicity_permille(priors_row: Mapping[str, object], radius_pc: int) -> int:
    metallicity_params = _as_map(_as_map(priors_row).get("metallicity_params"))
    solar_radius_pc = max(0, _as_int(metallicity_params.get("solar_radius_pc"), 8000))
    solar_metallicity_permille = max(0, _as_int(metallicity_params.get("solar_metallicity_permille"), 1000))
    drop_permille_per_kpc = max(0, _as_int(metallicity_params.get("radial_gradient_drop_permille_per_kpc"), 40))
    floor_permille = max(0, _as_int(metallicity_params.get("floor_permille"), 300))
    ceiling_permille = max(floor_permille, _as_int(metallicity_params.get("ceiling_permille"), 1400))
    delta_kpc = (max(0, int(radius_pc)) - solar_radius_pc) // 1000
    value = solar_metallicity_permille - (delta_kpc * drop_permille_per_kpc)
    return max(floor_permille, min(ceiling_permille, value))


def _habitability_bias_permille(priors_row: Mapping[str, object], *, radius_pc: int, z_pc: int, metallicity_permille: int) -> int:
    star_priors = _as_map(_as_map(_as_map(priors_row).get("extensions")).get("star_formation_priors"))
    center_pc = max(0, _as_int(star_priors.get("habitable_band_center_pc"), 8000))
    half_width_pc = max(1, _as_int(star_priors.get("habitable_band_half_width_pc"), 4000))
    vertical_half_thickness_pc = max(1, _as_int(star_priors.get("vertical_habitable_half_thickness_pc"), 600))
    radial_gap = abs(int(radius_pc) - center_pc)
    radial_bias = max(0, 1000 - min(1000, (radial_gap * 1000) // half_width_pc))
    vertical_bias = max(0, 1000 - min(1000, (abs(int(z_pc)) * 1000) // vertical_half_thickness_pc))
    metallicity_bias = max(0, 1000 - min(1000, abs(int(metallicity_permille) - 1000)))
    return max(0, (radial_bias * vertical_bias * metallicity_bias) // 1000000)


def _system_seed_rows(
    *,
    universe_identity_hash: str,
    cell_key: Mapping[str, object],
    priors_row: Mapping[str, object],
    system_count: int,
    system_stream_seed: str,
    metallicity_permille: int,
    habitability_bias_permille: int,
) -> List[dict]:
    star_priors = _as_map(_as_map(_as_map(priors_row).get("extensions")).get("star_formation_priors"))
    out = []
    for local_index in range(max(0, int(system_count))):
        local_subkey = "star_system:{}".format(int(local_index))
        system_seed = canonical_sha256(
            {
                "system_stream_seed": str(system_stream_seed),
                "geo_cell_key": _semantic_cell_key(_as_map(cell_key)),
                "local_index": int(local_index),
            }
        )
        object_row = geo_object_id(
            universe_identity_hash=str(universe_identity_hash),
            cell_key=_as_map(cell_key),
            object_kind_id="kind.star_system",
            local_subkey=local_subkey,
        )
        metallicity_jitter = (_hash_int(system_seed, "mw0.metallicity_jitter") % 81) - 40
        system_metallicity = max(0, int(metallicity_permille) + metallicity_jitter)
        habitable_bias = max(
            0,
            min(
                1000,
                int(habitability_bias_permille) + ((_hash_int(system_seed, "mw0.habitable_bias_jitter") % 121) - 60),
            ),
        )
        out.append(
            {
                "local_index": int(local_index),
                "local_subkey": local_subkey,
                "seed_subkey": canonical_sha256({"system_seed": system_seed, "kind": "star_system.subkey"}),
                "system_seed": system_seed,
                "object_id_hash": str(object_row.get("object_id_hash", "")).strip(),
                "metallicity_permille": int(system_metallicity),
                "age_bucket": _pick_weighted(system_seed, "mw0.age_bucket", _as_map(star_priors.get("age_weights")), "mature"),
                "imf_bucket": _pick_weighted(system_seed, "mw0.imf_bucket", _as_map(star_priors.get("imf_weights")), "m"),
                "habitable_filter_bias_permille": int(habitable_bias),
            }
        )
    return [
        dict(row)
        for row in sorted(
            out,
            key=lambda item: (
                int(item.get("local_index", 0)),
                str(item.get("local_subkey", "")),
                str(item.get("object_id_hash", "")),
            ),
        )
    ]


def generate_mw_cell_payload(
    *,
    universe_identity_hash: str,
    geo_cell_key: Mapping[str, object],
    realism_profile_row: Mapping[str, object] | None,
    galaxy_stream_seed: str,
    system_stream_seed: str,
    galaxy_priors_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        return _refusal("geo_cell_key is invalid", {"geo_cell_key": _as_map(geo_cell_key)})

    realism_row = _as_map(realism_profile_row)
    priors_id = str(realism_row.get("galaxy_priors_ref", "")).strip() or DEFAULT_GALAXY_PRIORS_ID
    priors_rows = galaxy_priors_rows(galaxy_priors_registry_payload)
    priors_row = priors_rows.get(priors_id)
    if not isinstance(priors_row, dict):
        return _refusal("galaxy_priors_ref is not declared", {"galaxy_priors_id": priors_id})

    cell_size_pc = max(1, _as_int(priors_row.get("cell_size_pc"), 10))
    max_systems_per_cell = max(0, _as_int(priors_row.get("max_systems_per_cell"), 24))
    x_pc, y_pc, z_pc = _position_pc(cell_key, cell_size_pc)
    radius_pc = isqrt((abs(int(x_pc)) ** 2) + (abs(int(y_pc)) ** 2))
    density_permille = _density_permille(
        priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
        x_pc=x_pc,
        y_pc=y_pc,
        cell_size_pc=cell_size_pc,
    )
    expected_system_count_milli = _expected_system_count_milli(priors_row, density_permille=density_permille)
    system_count = _deterministic_system_count(
        expected_system_count_milli=expected_system_count_milli,
        max_systems_per_cell=max_systems_per_cell,
        galaxy_stream_seed=str(galaxy_stream_seed),
    )
    metallicity_permille = _metallicity_permille(priors_row, radius_pc)
    habitability_bias_permille = _habitability_bias_permille(
        priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
        metallicity_permille=metallicity_permille,
    )
    system_seed_rows = _system_seed_rows(
        universe_identity_hash=str(universe_identity_hash),
        cell_key=cell_key,
        priors_row=priors_row,
        system_count=system_count,
        system_stream_seed=str(system_stream_seed),
        metallicity_permille=metallicity_permille,
        habitability_bias_permille=habitability_bias_permille,
    )
    summary = {
        "generator_surface_id": "worldgen.mw.cell",
        "generator_surface_version": MW_CELL_GENERATOR_VERSION,
        "galaxy_priors_id": priors_id,
        "cell_size_pc": int(cell_size_pc),
        "max_systems_per_cell": int(max_systems_per_cell),
        "galactocentric_position_pc": [int(x_pc), int(y_pc), int(z_pc)],
        "galactocentric_radius_pc": int(radius_pc),
        "density_permille": int(density_permille),
        "expected_system_count_milli": int(expected_system_count_milli),
        "system_count": int(system_count),
        "metallicity_permille": int(metallicity_permille),
        "habitable_filter_bias_permille": int(habitability_bias_permille),
        "deterministic_fingerprint": "",
    }
    summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
    payload = {
        "result": "complete",
        "galaxy_priors_id": priors_id,
        "cell_summary": summary,
        "system_seed_rows": system_seed_rows,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload

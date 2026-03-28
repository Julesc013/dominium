"""Deterministic MW-0 cell-scoped Milky Way generator."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from math import isqrt
from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from geo.frame.frame_engine import build_position_ref
from geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from geo.index.object_id_engine import geo_object_id
from worldgen.mw.sol_anchor import SOL_ANCHOR_ID, resolve_sol_anchor_cell_key, sol_anchor_matches_cell


DEFAULT_GALAXY_PRIORS_ID = "priors.milkyway_stub_default"
GALAXY_PRIORS_REGISTRY_REL = os.path.join("data", "registries", "galaxy_priors_registry.json")
MW_CELL_GENERATOR_VERSION = "MW1-3"
MW_GALACTIC_FRAME_ID = "frame.milky_way.galactic"
PARSEC_MM = 30_856_775_814_913_672_000

_TAN_22_5_PERMILLE = 414
_TAN_67_5_PERMILLE = 2414


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


def mw_cell_position_pc(cell_key: Mapping[str, object], cell_size_pc: int) -> Tuple[int, int, int]:
    return _position_pc(cell_key, cell_size_pc)


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


def mw_density_permille(
    priors_row: Mapping[str, object],
    *,
    radius_pc: int,
    z_pc: int,
    x_pc: int,
    y_pc: int,
    cell_size_pc: int,
) -> int:
    return _density_permille(
        priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
        x_pc=x_pc,
        y_pc=y_pc,
        cell_size_pc=cell_size_pc,
    )


def _expected_system_count_milli(priors_row: Mapping[str, object], *, density_permille: int) -> int:
    row = _as_map(priors_row)
    density_params = _as_map(row.get("density_params"))
    cell_size_pc = max(1, _as_int(row.get("cell_size_pc"), 10))
    volume_pc3 = cell_size_pc * cell_size_pc * cell_size_pc
    base_density = max(0, _as_int(density_params.get("midplane_systems_per_million_cubic_pc"), 9000))
    return max(0, (base_density * volume_pc3 * max(0, int(density_permille))) // 1000000)


def _deterministic_system_count(expected_system_count_milli: int, max_systems_per_cell: int, galaxy_stream_seed: str) -> Tuple[int, int, str]:
    base_count = max(0, int(expected_system_count_milli)) // 1000
    remainder = max(0, int(expected_system_count_milli)) % 1000
    extra = 1 if (_hash_int(galaxy_stream_seed, "mw0.system_count.remainder") % 1000) < remainder else 0
    uncapped_count = max(0, base_count + extra)
    bounded_count = min(max(0, int(max_systems_per_cell)), uncapped_count)
    if bounded_count < uncapped_count:
        return (uncapped_count, bounded_count, "capped")
    if extra:
        return (uncapped_count, bounded_count, "rounded_up")
    return (uncapped_count, bounded_count, "floor")


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


def mw_metallicity_permille(priors_row: Mapping[str, object], radius_pc: int) -> int:
    return _metallicity_permille(priors_row, radius_pc)


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


def mw_habitability_bias_permille(
    priors_row: Mapping[str, object],
    *,
    radius_pc: int,
    z_pc: int,
    metallicity_permille: int,
) -> int:
    return _habitability_bias_permille(
        priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
        metallicity_permille=metallicity_permille,
    )


def _pc_to_mm(value_pc: int) -> int:
    return int(value_pc) * PARSEC_MM


def _cell_origin_mm(*, x_pc: int, y_pc: int, z_pc: int) -> Tuple[int, int, int]:
    return (_pc_to_mm(x_pc), _pc_to_mm(y_pc), _pc_to_mm(z_pc))


def _axis_offset_mm(system_seed: str, axis: str, cell_size_pc: int) -> int:
    extent_mm = max(1, int(cell_size_pc)) * PARSEC_MM
    return (_hash_int(system_seed, "mw1.axis.{}".format(str(axis))) % extent_mm)


def _system_position_ref(
    *,
    object_id: str,
    system_seed: str,
    x_pc: int,
    y_pc: int,
    z_pc: int,
    cell_size_pc: int,
) -> dict:
    origin_x, origin_y, origin_z = _cell_origin_mm(x_pc=x_pc, y_pc=y_pc, z_pc=z_pc)
    return build_position_ref(
        object_id=str(object_id),
        frame_id=MW_GALACTIC_FRAME_ID,
        local_position=[
            origin_x + _axis_offset_mm(system_seed, "x", cell_size_pc),
            origin_y + _axis_offset_mm(system_seed, "y", cell_size_pc),
            origin_z + _axis_offset_mm(system_seed, "z", cell_size_pc),
        ],
        extensions={
            "source": MW_CELL_GENERATOR_VERSION,
            "position_space": "galactic_mm",
        },
    )


def _build_star_system_seed_row(
    *,
    cell_key: Mapping[str, object],
    local_index: int,
    local_subkey: str,
    seed_subkey: str,
    system_seed: str,
    object_id: str,
    metallicity_permille: int,
    age_bucket: str,
    imf_bucket: str,
    habitable_filter_bias_permille: int,
) -> dict:
    row = {
        "schema_version": "1.0.0",
        "cell_key": _as_map(cell_key),
        "local_index": int(local_index),
        "system_seed_value": str(system_seed).strip(),
        "object_id": str(object_id).strip(),
        "deterministic_fingerprint": "",
        "extensions": {
            "local_subkey": str(local_subkey).strip(),
            "seed_subkey": str(seed_subkey).strip(),
            "object_id_hash": str(object_id).strip(),
            "metallicity_permille": int(metallicity_permille),
            "age_bucket": str(age_bucket).strip(),
            "imf_bucket": str(imf_bucket).strip(),
            "habitable_filter_bias_permille": int(habitable_filter_bias_permille),
            "source": MW_CELL_GENERATOR_VERSION,
        },
    }
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def normalize_star_system_seed_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[Tuple[int, str], dict] = {}
    for item in rows:
        if not isinstance(item, Mapping):
            continue
        cell_key = _coerce_cell_key(_as_map(item.get("cell_key")))
        if not cell_key:
            continue
        local_index = max(0, _as_int(item.get("local_index", 0), 0))
        extensions = _as_map(item.get("extensions"))
        local_subkey = str(item.get("local_subkey", "")).strip() or str(extensions.get("local_subkey", "")).strip() or "star_system:{}".format(local_index)
        system_seed_value = str(item.get("system_seed_value", "")).strip() or str(item.get("system_seed", "")).strip()
        object_id = str(item.get("object_id", "")).strip() or str(item.get("object_id_hash", "")).strip() or str(extensions.get("object_id_hash", "")).strip()
        seed_subkey = str(item.get("seed_subkey", "")).strip() or str(extensions.get("seed_subkey", "")).strip()
        row = _build_star_system_seed_row(
            cell_key=cell_key,
            local_index=local_index,
            local_subkey=local_subkey,
            seed_subkey=seed_subkey,
            system_seed=system_seed_value,
            object_id=object_id,
            metallicity_permille=max(0, _as_int(item.get("metallicity_permille", extensions.get("metallicity_permille", 0)), 0)),
            age_bucket=str(item.get("age_bucket", "")).strip() or str(extensions.get("age_bucket", "")).strip(),
            imf_bucket=str(item.get("imf_bucket", "")).strip() or str(extensions.get("imf_bucket", "")).strip(),
            habitable_filter_bias_permille=max(
                0,
                min(
                    1000,
                    _as_int(
                        item.get(
                            "habitable_filter_bias_permille",
                            extensions.get("habitable_filter_bias_permille", 0),
                        ),
                        0,
                    ),
                ),
            ),
        )
        out[(local_index, local_subkey)] = row
    return [
        dict(out[key])
        for key in sorted(out.keys(), key=lambda item: (int(item[0]), str(item[1])))
    ]


def _build_star_system_artifact_row(
    *,
    object_id: str,
    system_seed: str,
    metallicity_permille: int,
    galaxy_position_ref: Mapping[str, object],
    cell_key: Mapping[str, object],
    local_index: int,
    local_subkey: str,
    age_bucket: str,
    imf_bucket: str,
    habitable_filter_bias_permille: int,
) -> dict:
    row = {
        "schema_version": "1.0.0",
        "object_id": str(object_id).strip(),
        "system_seed_value": str(system_seed).strip(),
        "metallicity_proxy": {
            "metallicity_permille": int(max(0, metallicity_permille)),
            "solar_relative_permille": int(max(0, metallicity_permille)),
        },
        "galaxy_position_ref": _as_map(galaxy_position_ref),
        "deterministic_fingerprint": "",
        "extensions": {
            "cell_key": _as_map(cell_key),
            "local_index": int(local_index),
            "local_subkey": str(local_subkey).strip(),
            "object_kind_id": "kind.star_system",
            "age_bucket": str(age_bucket).strip(),
            "imf_bucket": str(imf_bucket).strip(),
            "habitable_filter_bias_permille": int(max(0, min(1000, habitable_filter_bias_permille))),
            "habitable_likely": bool(int(max(0, min(1000, habitable_filter_bias_permille))) >= 650),
            "source": MW_CELL_GENERATOR_VERSION,
        },
    }
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def normalize_star_system_artifact_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for item in rows:
        if not isinstance(item, Mapping):
            continue
        object_id = str(item.get("object_id", "")).strip() or str(item.get("object_id_hash", "")).strip()
        if not object_id:
            continue
        extensions = _as_map(item.get("extensions"))
        row = _build_star_system_artifact_row(
            object_id=object_id,
            system_seed=str(item.get("system_seed_value", "")).strip() or str(item.get("system_seed", "")).strip(),
            metallicity_permille=max(
                0,
                _as_int(
                    _as_map(item.get("metallicity_proxy")).get("metallicity_permille", extensions.get("metallicity_permille", 0)),
                    0,
                ),
            ),
            galaxy_position_ref=_as_map(item.get("galaxy_position_ref")),
            cell_key=_coerce_cell_key(_as_map(extensions.get("cell_key"))) or {},
            local_index=max(0, _as_int(item.get("local_index", extensions.get("local_index", 0)), 0)),
            local_subkey=str(item.get("local_subkey", "")).strip() or str(extensions.get("local_subkey", "")).strip(),
            age_bucket=str(item.get("age_bucket", "")).strip() or str(extensions.get("age_bucket", "")).strip(),
            imf_bucket=str(item.get("imf_bucket", "")).strip() or str(extensions.get("imf_bucket", "")).strip(),
            habitable_filter_bias_permille=max(
                0,
                min(
                    1000,
                    _as_int(
                        item.get(
                            "habitable_filter_bias_permille",
                            extensions.get("habitable_filter_bias_permille", 0),
                        ),
                        0,
                    ),
                ),
            ),
        )
        out[object_id] = row
    return [dict(out[key]) for key in sorted(out.keys())]


def star_system_artifact_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_star_system_artifact_rows(rows))


def _system_seed_rows(
    *,
    universe_identity_hash: str,
    cell_key: Mapping[str, object],
    priors_row: Mapping[str, object],
    system_count: int,
    system_stream_seed: str,
    x_pc: int,
    y_pc: int,
    z_pc: int,
    cell_size_pc: int,
    metallicity_permille: int,
    habitability_bias_permille: int,
) -> Tuple[List[dict], List[dict]]:
    star_priors = _as_map(_as_map(_as_map(priors_row).get("extensions")).get("star_formation_priors"))
    seed_rows = []
    artifact_rows = []
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
        age_bucket = _pick_weighted(system_seed, "mw0.age_bucket", _as_map(star_priors.get("age_weights")), "mature")
        imf_bucket = _pick_weighted(system_seed, "mw0.imf_bucket", _as_map(star_priors.get("imf_weights")), "m")
        seed_subkey = canonical_sha256({"system_seed": system_seed, "kind": "star_system.subkey"})
        object_id = str(object_row.get("object_id_hash", "")).strip()
        galaxy_position_ref = _system_position_ref(
            object_id=object_id,
            system_seed=system_seed,
            x_pc=x_pc,
            y_pc=y_pc,
            z_pc=z_pc,
            cell_size_pc=cell_size_pc,
        )
        seed_rows.append(
            _build_star_system_seed_row(
                cell_key=cell_key,
                local_index=local_index,
                local_subkey=local_subkey,
                seed_subkey=seed_subkey,
                system_seed=system_seed,
                object_id=object_id,
                metallicity_permille=system_metallicity,
                age_bucket=age_bucket,
                imf_bucket=imf_bucket,
                habitable_filter_bias_permille=habitable_bias,
            )
        )
        artifact_rows.append(
            _build_star_system_artifact_row(
                object_id=object_id,
                system_seed=system_seed,
                metallicity_permille=system_metallicity,
                galaxy_position_ref=galaxy_position_ref,
                cell_key=cell_key,
                local_index=local_index,
                local_subkey=local_subkey,
                age_bucket=age_bucket,
                imf_bucket=imf_bucket,
                habitable_filter_bias_permille=habitable_bias,
            )
        )
    return (
        normalize_star_system_seed_rows(seed_rows),
        normalize_star_system_artifact_rows(artifact_rows),
    )


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
    x_pc, y_pc, z_pc = mw_cell_position_pc(cell_key, cell_size_pc)
    radius_pc = isqrt((abs(int(x_pc)) ** 2) + (abs(int(y_pc)) ** 2))
    density_permille = mw_density_permille(
        priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
        x_pc=x_pc,
        y_pc=y_pc,
        cell_size_pc=cell_size_pc,
    )
    expected_system_count_milli = _expected_system_count_milli(priors_row, density_permille=density_permille)
    sol_anchor_active = sol_anchor_matches_cell(cell_key, realism_row)
    uncapped_system_count, system_count, count_resolution = _deterministic_system_count(
        expected_system_count_milli=expected_system_count_milli,
        max_systems_per_cell=max_systems_per_cell,
        galaxy_stream_seed=str(galaxy_stream_seed),
    )
    sol_anchor_forced_minimum = False
    if sol_anchor_active and int(system_count) < 1:
        uncapped_system_count = max(1, int(uncapped_system_count))
        system_count = 1
        count_resolution = "anchor_minimum"
        sol_anchor_forced_minimum = True
    metallicity_permille = mw_metallicity_permille(priors_row, radius_pc)
    habitability_bias_permille = mw_habitability_bias_permille(
        priors_row,
        radius_pc=radius_pc,
        z_pc=z_pc,
        metallicity_permille=metallicity_permille,
    )
    system_seed_rows, star_system_artifact_rows = _system_seed_rows(
        universe_identity_hash=str(universe_identity_hash),
        cell_key=cell_key,
        priors_row=priors_row,
        system_count=system_count,
        system_stream_seed=str(system_stream_seed),
        x_pc=x_pc,
        y_pc=y_pc,
        z_pc=z_pc,
        cell_size_pc=cell_size_pc,
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
        "uncapped_system_count": int(uncapped_system_count),
        "system_count": int(system_count),
        "count_resolution": str(count_resolution),
        "metallicity_permille": int(metallicity_permille),
        "habitable_filter_bias_permille": int(habitability_bias_permille),
        "deterministic_fingerprint": "",
    }
    if sol_anchor_active:
        summary["extensions"] = {
            "sol_anchor_active": True,
            "sol_anchor_cell_key": resolve_sol_anchor_cell_key(realism_row),
            "sol_anchor_forced_minimum": bool(sol_anchor_forced_minimum),
            "sol_anchor_id": SOL_ANCHOR_ID,
            "source": "SOL0-3",
        }
    summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
    payload = {
        "result": "complete",
        "galaxy_priors_id": priors_id,
        "cell_summary": summary,
        "star_system_seed_rows": system_seed_rows,
        "star_system_artifact_rows": star_system_artifact_rows,
        "system_seed_rows": system_seed_rows,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload

"""Deterministic MW-2 system-level star and orbital prior refiner."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from math import isqrt
from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import _coerce_cell_key
from src.geo.index.object_id_engine import geo_object_id


DEFAULT_SYSTEM_PRIORS_ID = "priors.system_default_stub"
DEFAULT_PLANET_PRIORS_ID = "priors.planet_default_stub"
SYSTEM_PRIORS_REGISTRY_REL = os.path.join("data", "registries", "system_priors_registry.json")
PLANET_PRIORS_REGISTRY_REL = os.path.join("data", "registries", "planet_priors_registry.json")
MW_SYSTEM_REFINER_L2_VERSION = "MW2-3"


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


def _hash_int(seed: str, salt: str) -> int:
    return int(canonical_sha256({"seed": str(seed), "salt": str(salt)})[:16], 16)


def _named_substream_seed(seed: str, stream_name: str) -> str:
    return canonical_sha256({"seed": str(seed), "stream_name": str(stream_name)})


def _pick_from_list(seed: str, salt: str, values: object, default_value: str) -> str:
    rows = [str(item).strip() for item in list(values or []) if str(item).strip()]
    if not rows:
        return str(default_value)
    return rows[_hash_int(seed, salt) % len(rows)]


def _range_value(seed: str, salt: str, minimum: int, maximum: int) -> int:
    floor = int(min(minimum, maximum))
    ceiling = int(max(minimum, maximum))
    if floor == ceiling:
        return floor
    return floor + (_hash_int(seed, salt) % (ceiling - floor + 1))


def _ratio_mul(value: int, ratio_permille: int) -> int:
    return (max(0, int(value)) * max(0, int(ratio_permille)) + 999) // 1000


def _quantity(unit: str, value: int) -> dict:
    return {"unit": str(unit), "value": int(value)}


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


def system_priors_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(SYSTEM_PRIORS_REGISTRY_REL), row_key="system_priors", id_key="priors_id")


def planet_priors_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(PLANET_PRIORS_REGISTRY_REL), row_key="planet_priors", id_key="priors_id")


def system_priors_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(SYSTEM_PRIORS_REGISTRY_REL))


def planet_priors_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(PLANET_PRIORS_REGISTRY_REL))


def _normalized_extensions_map(value: object) -> dict:
    return dict((str(key), item) for key, item in sorted(_as_map(value).items(), key=lambda pair: str(pair[0])))


def normalize_star_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        object_id = str(row.get("object_id", "")).strip()
        if not object_id:
            continue
        normalized = {
            "object_id": object_id,
            "star_mass": _as_map(row.get("star_mass")),
            "luminosity_proxy": _as_map(row.get("luminosity_proxy")),
            "age_proxy": _as_map(row.get("age_proxy")),
            "metallicity_proxy": _as_map(row.get("metallicity_proxy")),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _normalized_extensions_map(row.get("extensions")),
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[object_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_planet_orbit_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        planet_object_id = str(row.get("planet_object_id", "")).strip()
        if not planet_object_id:
            continue
        normalized = {
            "planet_object_id": planet_object_id,
            "star_object_id": str(row.get("star_object_id", "")).strip(),
            "semi_major_axis": _as_map(row.get("semi_major_axis")),
            "eccentricity": _as_map(row.get("eccentricity")),
            "inclination": _as_map(row.get("inclination")),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _normalized_extensions_map(row.get("extensions")),
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[planet_object_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_planet_basic_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        object_id = str(row.get("object_id", "")).strip()
        if not object_id:
            continue
        normalized = {
            "object_id": object_id,
            "radius": _as_map(row.get("radius")),
            "density_class_id": str(row.get("density_class_id", "")).strip(),
            "atmosphere_class_id": str(row.get("atmosphere_class_id", "")).strip(),
            "ocean_fraction": _as_map(row.get("ocean_fraction")),
            "rotation_period": _as_map(row.get("rotation_period")),
            "axial_tilt": _as_map(row.get("axial_tilt")),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _normalized_extensions_map(row.get("extensions")),
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[object_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_system_l2_summary_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        system_object_id = str(row.get("system_object_id", "")).strip()
        if not system_object_id:
            continue
        normalized = {
            "system_object_id": system_object_id,
            "star_object_id": str(row.get("star_object_id", "")).strip(),
            "star_mass_milli_solar": int(max(0, _as_int(row.get("star_mass_milli_solar", 0), 0))),
            "planet_count": int(max(0, _as_int(row.get("planet_count", 0), 0))),
            "candidate_habitable_planet_count": int(max(0, _as_int(row.get("candidate_habitable_planet_count", 0), 0))),
            "planet_object_ids": sorted(str(item).strip() for item in _as_list(row.get("planet_object_ids")) if str(item).strip()),
            "moon_object_ids": sorted(str(item).strip() for item in _as_list(row.get("moon_object_ids")) if str(item).strip()),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _normalized_extensions_map(row.get("extensions")),
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[system_object_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _normalize_star_system_artifact_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        object_id = str(row.get("object_id", "")).strip() or str(row.get("object_id_hash", "")).strip()
        if not object_id:
            continue
        extensions = _normalized_extensions_map(row.get("extensions"))
        normalized = {
            "object_id": object_id,
            "system_seed_value": str(row.get("system_seed_value", "")).strip() or str(row.get("system_seed", "")).strip(),
            "metallicity_proxy": _as_map(row.get("metallicity_proxy")),
            "galaxy_position_ref": _as_map(row.get("galaxy_position_ref")),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": extensions,
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[object_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def star_artifact_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_star_artifact_rows(rows))


def planet_orbit_artifact_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_planet_orbit_artifact_rows(rows))


def planet_basic_artifact_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_planet_basic_artifact_rows(rows))


def system_l2_summary_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_system_l2_summary_rows(rows))


def _star_band(system_row: Mapping[str, object], system_priors_row: Mapping[str, object]) -> str:
    bands = _as_map(_as_map(system_priors_row).get("extensions")).get("star_mass_band_ranges_milli_solar")
    choices = _as_map(bands)
    requested = str(_as_map(system_row).get("extensions", {}).get("imf_bucket", "")).strip().lower()
    if requested in choices:
        return requested
    return "g" if "g" in choices else next(iter(sorted(choices.keys())), "g")


def _star_mass_milli_solar(system_seed_value: str, system_row: Mapping[str, object], system_priors_row: Mapping[str, object]) -> Tuple[str, int]:
    ranges = _as_map(_as_map(_as_map(system_priors_row).get("extensions")).get("star_mass_band_ranges_milli_solar"))
    band = _star_band(system_row, system_priors_row)
    band_row = _as_map(ranges.get(band))
    minimum = max(1, _as_int(band_row.get("min", 900), 900))
    maximum = max(minimum, _as_int(band_row.get("max", minimum), minimum))
    seed = _named_substream_seed(system_seed_value, "rng.worldgen.system.primary_star")
    return (band, _range_value(seed, "star_mass", minimum, maximum))


def _luminosity_permille(star_mass_milli_solar: int) -> int:
    mass = max(1, int(star_mass_milli_solar))
    if mass <= 430:
        return max(5, (23 * mass * mass) // 100_000)
    if mass <= 2000:
        return max(10, (mass * mass * mass * mass) // 1_000_000_000)
    return max(1000, (15 * mass * mass * mass) // 1_000_000_000)


def _age_gyr_milli(system_seed_value: str, system_row: Mapping[str, object], system_priors_row: Mapping[str, object]) -> int:
    ranges = _as_map(_as_map(_as_map(system_priors_row).get("extensions")).get("age_bucket_ranges_gyr_milli"))
    bucket = str(_as_map(system_row).get("extensions", {}).get("age_bucket", "")).strip().lower()
    if bucket not in ranges:
        bucket = "mature" if "mature" in ranges else next(iter(sorted(ranges.keys())), "mature")
    bucket_row = _as_map(ranges.get(bucket))
    minimum = max(1, _as_int(bucket_row.get("min", 2500), 2500))
    maximum = max(minimum, _as_int(bucket_row.get("max", minimum), minimum))
    seed = _named_substream_seed(system_seed_value, "rng.worldgen.system.primary_star")
    return _range_value(seed, "age_proxy", minimum, maximum)


def _metallicity_permille(system_row: Mapping[str, object]) -> int:
    metallicity_proxy = _as_map(_as_map(system_row).get("metallicity_proxy"))
    return max(0, _as_int(metallicity_proxy.get("metallicity_permille", 0), 0))


def _habitability_bias_permille(system_row: Mapping[str, object]) -> int:
    return max(0, min(1000, _as_int(_as_map(system_row).get("extensions", {}).get("habitable_filter_bias_permille", 0), 0)))


def _planet_count(
    *,
    system_seed_value: str,
    system_row: Mapping[str, object],
    system_priors_row: Mapping[str, object],
    star_band: str,
    star_mass_milli_solar: int,
) -> int:
    params = _as_map(_as_map(system_priors_row).get("planet_count_params"))
    counts = _as_map(params.get("base_count_by_star_band"))
    base_count = max(0, _as_int(counts.get(star_band, 3), 3))
    jitter_span = max(0, _as_int(params.get("count_jitter", 1), 1))
    jitter = 0
    if jitter_span > 0:
        jitter = (_hash_int(_named_substream_seed(system_seed_value, "rng.worldgen.system.planet_count"), "count_jitter") % (jitter_span * 2 + 1)) - jitter_span
    metallicity_bonus = 0
    if _metallicity_permille(system_row) >= max(0, _as_int(params.get("metallicity_bonus_threshold_permille", 950), 950)):
        metallicity_bonus = max(0, _as_int(params.get("metallicity_bonus_planets", 1), 1))
    habitability_bonus = 0
    if _habitability_bias_permille(system_row) >= max(0, _as_int(params.get("habitability_bonus_threshold_permille", 780), 780)):
        habitability_bonus = max(0, _as_int(params.get("habitability_bonus_planets", 1), 1))
    hot_star_penalty = 0
    if int(star_mass_milli_solar) >= max(1, _as_int(params.get("hot_star_penalty_threshold_milli_solar", 1500), 1500)):
        hot_star_penalty = max(0, _as_int(params.get("hot_star_penalty_planets", 1), 1))
    max_planets = max(0, _as_int(params.get("max_planets", 8), 8))
    return max(0, min(max_planets, base_count + jitter + metallicity_bonus + habitability_bonus - hot_star_penalty))


def _habitable_center_milli_au(luminosity_permille: int) -> int:
    return max(150, isqrt(max(1, int(luminosity_permille)) * 1000))


def _planet_class_id(
    *,
    orbit_seed: str,
    planet_index: int,
    planet_count: int,
    semi_major_axis_milli_au: int,
    habitable_center_milli_au: int,
    habitability_bias_permille: int,
    planet_priors_row: Mapping[str, object],
) -> str:
    thresholds = _as_map(_as_map(planet_priors_row).get("extensions")).get("class_selection_thresholds")
    threshold_row = _as_map(thresholds)
    hot_zone = _ratio_mul(habitable_center_milli_au, max(100, _as_int(threshold_row.get("hot_zone_ratio_permille", 700), 700)))
    temperate_zone = _ratio_mul(habitable_center_milli_au, max(100, _as_int(threshold_row.get("temperate_zone_ratio_permille", 1600), 1600)))
    gas_outer_threshold = max(temperate_zone + 400, _as_int(threshold_row.get("gas_dwarf_outer_threshold_milli_au", 1800), 1800))
    if semi_major_axis_milli_au >= gas_outer_threshold and (planet_index >= max(0, planet_count - 2) or (_hash_int(orbit_seed, "gas_dwarf_hint") % 5) == 0):
        return "gas_dwarf"
    if semi_major_axis_milli_au < hot_zone:
        return "rocky"
    if semi_major_axis_milli_au <= temperate_zone:
        if habitability_bias_permille >= 780 and (_hash_int(orbit_seed, "oceanic_hint") % 1000) < min(900, habitability_bias_permille):
            return "oceanic"
        return "terrestrial"
    return "icy"


def _density_class_id(orbit_seed: str, planet_class_id: str, semi_major_axis_milli_au: int, habitable_center_milli_au: int, planet_priors_row: Mapping[str, object]) -> str:
    params = _as_map(_as_map(planet_priors_row).get("density_class_params"))
    if planet_class_id == "gas_dwarf":
        return _pick_from_list(orbit_seed, "density_class", params.get("gas_classes"), "density.gas_dwarf")
    if semi_major_axis_milli_au < _ratio_mul(habitable_center_milli_au, 700):
        return _pick_from_list(orbit_seed, "density_class", params.get("hot_inner_classes"), "density.rocky_dense")
    if semi_major_axis_milli_au <= _ratio_mul(habitable_center_milli_au, 1600):
        return _pick_from_list(orbit_seed, "density_class", params.get("temperate_classes"), "density.rocky_temperate")
    return _pick_from_list(orbit_seed, "density_class", params.get("cold_outer_classes"), "density.icy")


def _atmosphere_class_id(orbit_seed: str, planet_class_id: str, semi_major_axis_milli_au: int, habitable_center_milli_au: int, planet_priors_row: Mapping[str, object]) -> str:
    params = _as_map(_as_map(planet_priors_row).get("atmosphere_class_params"))
    if planet_class_id == "gas_dwarf":
        return _pick_from_list(orbit_seed, "atmosphere_class", params.get("gas_classes"), "atmo.volatile")
    if semi_major_axis_milli_au < _ratio_mul(habitable_center_milli_au, 700):
        return _pick_from_list(orbit_seed, "atmosphere_class", params.get("hot_inner_classes"), "atmo.none")
    if semi_major_axis_milli_au <= _ratio_mul(habitable_center_milli_au, 1600):
        return _pick_from_list(orbit_seed, "atmosphere_class", params.get("temperate_classes"), "atmo.temperate")
    return _pick_from_list(orbit_seed, "atmosphere_class", params.get("cold_outer_classes"), "atmo.thin")


def _ocean_fraction_permille(orbit_seed: str, planet_class_id: str, planet_priors_row: Mapping[str, object]) -> int:
    params = _as_map(_as_map(planet_priors_row).get("ocean_fraction_params"))
    if planet_class_id == "gas_dwarf":
        return max(0, _as_int(params.get("gas_dwarf_permille", 0), 0))
    if planet_class_id == "icy":
        return _range_value(orbit_seed, "ocean_fraction", 0, max(0, _as_int(params.get("icy_max_permille", 80), 80)))
    if planet_class_id == "rocky":
        return _range_value(orbit_seed, "ocean_fraction", 0, max(0, _as_int(params.get("dry_max_permille", 120), 120)))
    return _range_value(
        orbit_seed,
        "ocean_fraction",
        max(0, _as_int(params.get("temperate_min_permille", 150), 150)),
        max(0, _as_int(params.get("temperate_max_permille", 900), 900)),
    )


def _rotation_period_hours_milli(orbit_seed: str, planet_class_id: str, semi_major_axis_milli_au: int, habitable_center_milli_au: int, planet_priors_row: Mapping[str, object]) -> int:
    params = _as_map(_as_map(planet_priors_row).get("rotation_params"))
    if planet_class_id == "gas_dwarf":
        return _range_value(orbit_seed, "rotation_period", _as_int(params.get("gas_hours_milli_min", 8000), 8000), _as_int(params.get("gas_hours_milli_max", 20000), 20000))
    if semi_major_axis_milli_au < _ratio_mul(habitable_center_milli_au, 700):
        return _range_value(orbit_seed, "rotation_period", _as_int(params.get("inner_hours_milli_min", 6000), 6000), _as_int(params.get("inner_hours_milli_max", 24000), 24000))
    if semi_major_axis_milli_au <= _ratio_mul(habitable_center_milli_au, 1600):
        return _range_value(orbit_seed, "rotation_period", _as_int(params.get("temperate_hours_milli_min", 10000), 10000), _as_int(params.get("temperate_hours_milli_max", 42000), 42000))
    return _range_value(orbit_seed, "rotation_period", _as_int(params.get("outer_hours_milli_min", 12000), 12000), _as_int(params.get("outer_hours_milli_max", 72000), 72000))


def _axial_tilt_mdeg(orbit_seed: str, planet_class_id: str, semi_major_axis_milli_au: int, habitable_center_milli_au: int, planet_priors_row: Mapping[str, object]) -> int:
    params = _as_map(_as_map(planet_priors_row).get("axial_tilt_params"))
    minimum = max(0, _as_int(params.get("min_mdeg", 0), 0))
    if planet_class_id == "gas_dwarf":
        return _range_value(orbit_seed, "axial_tilt", minimum, max(minimum, _as_int(params.get("gas_max_mdeg", 30000), 30000)))
    if semi_major_axis_milli_au < _ratio_mul(habitable_center_milli_au, 700):
        return _range_value(orbit_seed, "axial_tilt", minimum, max(minimum, _as_int(params.get("inner_max_mdeg", 18000), 18000)))
    if semi_major_axis_milli_au <= _ratio_mul(habitable_center_milli_au, 1600):
        return _range_value(orbit_seed, "axial_tilt", minimum, max(minimum, _as_int(params.get("temperate_max_mdeg", 35000), 35000)))
    return _range_value(orbit_seed, "axial_tilt", minimum, max(minimum, _as_int(params.get("outer_max_mdeg", 50000), 50000)))


def _radius_km(orbit_seed: str, planet_class_id: str, planet_priors_row: Mapping[str, object]) -> int:
    params = _as_map(_as_map(planet_priors_row).get("radius_params"))
    class_row = _as_map(params.get(planet_class_id))
    minimum = max(100, _as_int(class_row.get("min_km", 3000), 3000))
    maximum = max(minimum, _as_int(class_row.get("max_km", minimum), minimum))
    return _range_value(orbit_seed, "radius_km", minimum, maximum)


def _moon_stub_count(orbit_seed: str, planet_class_id: str, system_priors_row: Mapping[str, object]) -> int:
    orbital_spacing = _as_map(_as_map(system_priors_row).get("orbital_spacing_params"))
    max_moons = max(0, _as_int(orbital_spacing.get("max_moons_per_planet", 1), 1))
    chances = _as_map(_as_map(_as_map(system_priors_row).get("extensions")).get("moon_stub_chance_permille_by_planet_class"))
    chance = max(0, min(1000, _as_int(chances.get(planet_class_id, 0), 0)))
    return min(max_moons, 1 if (_hash_int(orbit_seed, "moon_stub_count") % 1000) < chance else 0)


def _planet_habitable_likely(
    *,
    planet_class_id: str,
    atmosphere_class_id: str,
    ocean_fraction_permille: int,
    semi_major_axis_milli_au: int,
    habitable_center_milli_au: int,
) -> bool:
    if planet_class_id not in {"terrestrial", "oceanic"}:
        return False
    if atmosphere_class_id not in {"atmo.temperate", "atmo.dense"}:
        return False
    if not (150 <= int(ocean_fraction_permille) <= 900):
        return False
    inner = _ratio_mul(habitable_center_milli_au, 700)
    outer = _ratio_mul(habitable_center_milli_au, 1600)
    return int(inner) <= int(semi_major_axis_milli_au) <= int(outer)


def generate_mw_system_l2_payload(
    *,
    universe_identity_hash: str,
    geo_cell_key: Mapping[str, object],
    realism_profile_row: Mapping[str, object] | None,
    star_system_artifact_rows: object,
    system_priors_registry_payload: Mapping[str, object] | None = None,
    planet_priors_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        payload = {"result": "refused", "message": "geo_cell_key is invalid for MW-2 refinement", "details": {"geo_cell_key": _as_map(geo_cell_key)}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    realism_row = _as_map(realism_profile_row)
    system_priors_id = str(realism_row.get("system_priors_ref", "")).strip() or DEFAULT_SYSTEM_PRIORS_ID
    planet_priors_id = str(realism_row.get("planet_priors_ref", "")).strip() or DEFAULT_PLANET_PRIORS_ID
    system_rows = system_priors_rows(system_priors_registry_payload)
    planet_rows = planet_priors_rows(planet_priors_registry_payload)
    system_priors_row = _as_map(system_rows.get(system_priors_id))
    planet_priors_row = _as_map(planet_rows.get(planet_priors_id))
    if not system_priors_row:
        payload = {"result": "refused", "message": "system_priors_ref is not declared", "details": {"system_priors_id": system_priors_id}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    if not planet_priors_row:
        payload = {"result": "refused", "message": "planet_priors_ref is not declared", "details": {"planet_priors_id": planet_priors_id}, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    star_rows: List[dict] = []
    orbit_rows: List[dict] = []
    basic_rows: List[dict] = []
    object_rows: List[dict] = []
    summary_rows: List[dict] = []

    for system_row in _normalize_star_system_artifact_rows(star_system_artifact_rows):
        system_object_id = str(system_row.get("object_id", "")).strip()
        system_seed_value = str(system_row.get("system_seed_value", "")).strip()
        if not system_object_id or not system_seed_value:
            continue
        star_band, star_mass_milli_solar = _star_mass_milli_solar(system_seed_value, system_row, system_priors_row)
        luminosity_permille = _luminosity_permille(star_mass_milli_solar)
        age_gyr_milli = _age_gyr_milli(system_seed_value, system_row, system_priors_row)
        habitability_bias_permille = _habitability_bias_permille(system_row)
        habitable_center_milli_au = _habitable_center_milli_au(luminosity_permille)
        star_object_id, star_object_row = _spawn_object_identity(
            universe_identity_hash=universe_identity_hash,
            cell_key=cell_key,
            object_kind_id="kind.star",
            local_subkey="system:{}:star:0".format(system_object_id),
        )
        if not star_object_id:
            continue
        object_rows.append(star_object_row)
        star_row = {
            "object_id": star_object_id,
            "star_mass": _quantity("milli_solar_mass", star_mass_milli_solar),
            "luminosity_proxy": _quantity("milli_solar_luminosity", luminosity_permille),
            "age_proxy": _quantity("gyr_milli", age_gyr_milli),
            "metallicity_proxy": _as_map(system_row.get("metallicity_proxy")),
            "deterministic_fingerprint": "",
            "extensions": {"parent_system_object_id": system_object_id, "star_index": 0, "star_band_id": star_band, "named_rng_stream": "rng.worldgen.system.primary_star", "source": MW_SYSTEM_REFINER_L2_VERSION},
        }
        star_row["deterministic_fingerprint"] = canonical_sha256(dict(star_row, deterministic_fingerprint=""))
        star_rows.append(star_row)

        planet_count = _planet_count(system_seed_value=system_seed_value, system_row=system_row, system_priors_row=system_priors_row, star_band=star_band, star_mass_milli_solar=star_mass_milli_solar)
        orbital_spacing = _as_map(system_priors_row.get("orbital_spacing_params"))
        inner_edge_milli_au = max(50, _as_int(orbital_spacing.get("inner_edge_milli_au", 220), 220))
        outer_edge_milli_au = max(inner_edge_milli_au, _as_int(orbital_spacing.get("outer_edge_milli_au", 24000), 24000))
        nominal_ratio_permille = max(1050, _as_int(orbital_spacing.get("nominal_spacing_ratio_permille", 1680), 1680))
        band_jitter_permille = max(0, _as_int(orbital_spacing.get("band_jitter_permille", 140), 140))
        eccentricity_params = _as_map(system_priors_row.get("eccentricity_params"))
        inclination_params = _as_map(system_priors_row.get("inclination_params"))
        min_spacing_ratio_permille = max(1000, _as_int(orbital_spacing.get("min_spacing_ratio_permille", 1350), 1350))
        push_out_ratio_permille = max(min_spacing_ratio_permille, _as_int(orbital_spacing.get("push_out_ratio_permille", 1450), 1450))
        periapsis_gap_ratio_permille = max(1000, _as_int(eccentricity_params.get("periapsis_gap_ratio_permille", 1050), 1050))
        last_axis_milli_au = inner_edge_milli_au
        last_apoapsis_milli_au = 0
        planet_object_ids: List[str] = []
        moon_object_ids: List[str] = []
        habitable_planet_count = 0

        # Deterministic forward pass: bounded push-out for spacing, then a periapsis-order clamp for eccentricity.
        for planet_index in range(planet_count):
            orbit_seed = _named_substream_seed(system_seed_value, "rng.worldgen.system.planet.{}".format(planet_index))
            nominal_axis = inner_edge_milli_au if planet_index == 0 else min(outer_edge_milli_au, _ratio_mul(last_axis_milli_au, nominal_ratio_permille))
            jitter_span = (nominal_axis * band_jitter_permille) // 1000
            candidate_axis = nominal_axis + ((_hash_int(orbit_seed, "semi_major_jitter") % (jitter_span * 2 + 1)) - jitter_span) if jitter_span > 0 else nominal_axis
            semi_major_axis_milli_au = max(inner_edge_milli_au, min(outer_edge_milli_au, candidate_axis))
            spacing_adjusted = False
            if planet_index > 0:
                min_allowed_axis = _ratio_mul(last_axis_milli_au, min_spacing_ratio_permille)
                if semi_major_axis_milli_au < min_allowed_axis:
                    semi_major_axis_milli_au = min(outer_edge_milli_au, _ratio_mul(last_axis_milli_au, push_out_ratio_permille))
                    spacing_adjusted = True
            base_e_max = max(0, min(900, _as_int(eccentricity_params.get("base_max_permille", 260), 260)))
            if semi_major_axis_milli_au < _ratio_mul(habitable_center_milli_au, 700):
                base_e_max = min(900, base_e_max + max(0, _as_int(eccentricity_params.get("inner_zone_bonus_permille", 30), 30)))
            raw_eccentricity_permille = _hash_int(orbit_seed, "eccentricity") % (base_e_max + 1 if base_e_max > 0 else 1)
            max_eccentricity_permille = base_e_max
            if planet_index > 0 and semi_major_axis_milli_au > 0:
                max_from_periapsis = 1000 - ((last_apoapsis_milli_au * periapsis_gap_ratio_permille + semi_major_axis_milli_au - 1) // semi_major_axis_milli_au)
                max_eccentricity_permille = min(base_e_max, max(0, max_from_periapsis))
            eccentricity_permille = max(0, min(raw_eccentricity_permille, max_eccentricity_permille))
            base_inclination_mdeg = max(0, _as_int(inclination_params.get("base_max_mdeg", 3500), 3500))
            if semi_major_axis_milli_au > _ratio_mul(habitable_center_milli_au, 1600):
                base_inclination_mdeg += max(0, _as_int(inclination_params.get("outer_zone_bonus_mdeg", 2500), 2500))
            inclination_mdeg = _hash_int(orbit_seed, "inclination") % (base_inclination_mdeg + 1 if base_inclination_mdeg > 0 else 1)
            planet_object_id, planet_object_row = _spawn_object_identity(
                universe_identity_hash=universe_identity_hash,
                cell_key=cell_key,
                object_kind_id="kind.planet",
                local_subkey="system:{}:planet:{}".format(system_object_id, planet_index),
            )
            if not planet_object_id:
                continue
            object_rows.append(planet_object_row)
            planet_object_ids.append(planet_object_id)
            planet_class_id = _planet_class_id(orbit_seed=orbit_seed, planet_index=planet_index, planet_count=planet_count, semi_major_axis_milli_au=semi_major_axis_milli_au, habitable_center_milli_au=habitable_center_milli_au, habitability_bias_permille=habitability_bias_permille, planet_priors_row=planet_priors_row)
            density_class_id = _density_class_id(orbit_seed, planet_class_id, semi_major_axis_milli_au, habitable_center_milli_au, planet_priors_row)
            atmosphere_class_id = _atmosphere_class_id(orbit_seed, planet_class_id, semi_major_axis_milli_au, habitable_center_milli_au, planet_priors_row)
            ocean_fraction_permille = _ocean_fraction_permille(orbit_seed, planet_class_id, planet_priors_row)
            rotation_period_hours_milli = _rotation_period_hours_milli(orbit_seed, planet_class_id, semi_major_axis_milli_au, habitable_center_milli_au, planet_priors_row)
            axial_tilt_mdeg = _axial_tilt_mdeg(orbit_seed, planet_class_id, semi_major_axis_milli_au, habitable_center_milli_au, planet_priors_row)
            radius_km = _radius_km(orbit_seed, planet_class_id, planet_priors_row)
            current_moon_ids: List[str] = []
            for moon_index in range(_moon_stub_count(orbit_seed, planet_class_id, system_priors_row)):
                moon_object_id, moon_object_row = _spawn_object_identity(
                    universe_identity_hash=universe_identity_hash,
                    cell_key=cell_key,
                    object_kind_id="kind.moon",
                    local_subkey="system:{}:moon:{}:{}".format(system_object_id, planet_index, moon_index),
                )
                if not moon_object_id:
                    continue
                object_rows.append(moon_object_row)
                current_moon_ids.append(moon_object_id)
                moon_object_ids.append(moon_object_id)
            habitable_likely = _planet_habitable_likely(planet_class_id=planet_class_id, atmosphere_class_id=atmosphere_class_id, ocean_fraction_permille=ocean_fraction_permille, semi_major_axis_milli_au=semi_major_axis_milli_au, habitable_center_milli_au=habitable_center_milli_au)
            if habitable_likely:
                habitable_planet_count += 1
            orbit_row = {
                "planet_object_id": planet_object_id,
                "star_object_id": star_object_id,
                "semi_major_axis": _quantity("milli_au", semi_major_axis_milli_au),
                "eccentricity": _quantity("permille", eccentricity_permille),
                "inclination": _quantity("mdeg", inclination_mdeg),
                "deterministic_fingerprint": "",
                "extensions": {
                    "parent_system_object_id": system_object_id,
                    "planet_index": planet_index,
                    "planet_class_id": planet_class_id,
                    "named_rng_stream": "rng.worldgen.system.planet.{}".format(planet_index),
                    "habitable_center_milli_au": habitable_center_milli_au,
                    "spacing_adjusted": bool(spacing_adjusted),
                    "raw_eccentricity_permille": int(raw_eccentricity_permille),
                    "max_eccentricity_permille": int(max_eccentricity_permille),
                    "source": MW_SYSTEM_REFINER_L2_VERSION,
                },
            }
            orbit_row["deterministic_fingerprint"] = canonical_sha256(dict(orbit_row, deterministic_fingerprint=""))
            orbit_rows.append(orbit_row)
            basic_row = {
                "object_id": planet_object_id,
                "radius": _quantity("km", radius_km),
                "density_class_id": density_class_id,
                "atmosphere_class_id": atmosphere_class_id,
                "ocean_fraction": _quantity("permille", ocean_fraction_permille),
                "rotation_period": _quantity("hours_milli", rotation_period_hours_milli),
                "axial_tilt": _quantity("mdeg", axial_tilt_mdeg),
                "deterministic_fingerprint": "",
                "extensions": {"parent_system_object_id": system_object_id, "parent_star_object_id": star_object_id, "planet_index": planet_index, "planet_class_id": planet_class_id, "moon_stub_count": len(current_moon_ids), "moon_object_ids": list(current_moon_ids), "habitable_likely": bool(habitable_likely), "source": MW_SYSTEM_REFINER_L2_VERSION},
            }
            basic_row["deterministic_fingerprint"] = canonical_sha256(dict(basic_row, deterministic_fingerprint=""))
            basic_rows.append(basic_row)
            last_axis_milli_au = semi_major_axis_milli_au
            last_apoapsis_milli_au = (semi_major_axis_milli_au * (1000 + eccentricity_permille) + 999) // 1000

        summary_row = {
            "system_object_id": system_object_id,
            "star_object_id": star_object_id,
            "star_mass_milli_solar": star_mass_milli_solar,
            "planet_count": len(planet_object_ids),
            "candidate_habitable_planet_count": habitable_planet_count,
            "planet_object_ids": list(planet_object_ids),
            "moon_object_ids": list(moon_object_ids),
            "deterministic_fingerprint": "",
            "extensions": {"star_band_id": star_band, "system_seed_value": system_seed_value, "habitable_center_milli_au": habitable_center_milli_au, "source": MW_SYSTEM_REFINER_L2_VERSION},
        }
        summary_row["deterministic_fingerprint"] = canonical_sha256(dict(summary_row, deterministic_fingerprint=""))
        summary_rows.append(summary_row)

    payload = {
        "result": "complete",
        "system_priors_id": system_priors_id,
        "planet_priors_id": planet_priors_id,
        "generated_star_artifact_rows": normalize_star_artifact_rows(star_rows),
        "generated_planet_orbit_artifact_rows": normalize_planet_orbit_artifact_rows(orbit_rows),
        "generated_planet_basic_artifact_rows": normalize_planet_basic_artifact_rows(basic_rows),
        "generated_object_rows": [dict(row) for row in sorted(object_rows, key=lambda item: (str(item.get("object_kind_id", "")), str(item.get("local_subkey", "")), str(item.get("object_id_hash", ""))))],
        "generated_system_l2_summary_rows": normalize_system_l2_summary_rows(summary_rows),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_PLANET_PRIORS_ID",
    "DEFAULT_SYSTEM_PRIORS_ID",
    "MW_SYSTEM_REFINER_L2_VERSION",
    "PLANET_PRIORS_REGISTRY_REL",
    "SYSTEM_PRIORS_REGISTRY_REL",
    "generate_mw_system_l2_payload",
    "normalize_planet_basic_artifact_rows",
    "normalize_planet_orbit_artifact_rows",
    "normalize_star_artifact_rows",
    "normalize_system_l2_summary_rows",
    "planet_basic_artifact_hash_chain",
    "planet_orbit_artifact_hash_chain",
    "planet_priors_registry_hash",
    "planet_priors_rows",
    "star_artifact_hash_chain",
    "system_l2_summary_hash_chain",
    "system_priors_registry_hash",
    "system_priors_rows",
]

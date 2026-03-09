"""Deterministic EARTH-0 macro surface generator."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


EARTH_SURFACE_GENERATOR_VERSION = "EARTH0-3"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def _hash_permille(seed: str, *, salt: str, coords: Mapping[str, object]) -> int:
    return int(canonical_sha256({"seed": str(seed), "salt": str(salt), "coords": dict(coords)})[:8], 16) % 1000


def _named_substream_seed(seed: str, stream_name: str) -> str:
    return canonical_sha256({"seed": str(seed), "stream_name": str(stream_name)})


def _wrap_longitude_mdeg(longitude_mdeg: int) -> int:
    wrapped = ((int(longitude_mdeg) + 180_000) % 360_000) - 180_000
    return -180_000 if wrapped == 180_000 else int(wrapped)


def _triangle_wave_permille(*, position_mdeg: int, period_mdeg: int, phase_mdeg: int = 0) -> int:
    period = max(1, int(period_mdeg))
    phase = (int(position_mdeg) + int(phase_mdeg)) % period
    half = max(1, period // 2)
    if phase <= half:
        return _clamp((phase * 1000) // half, 0, 1000)
    return _clamp(((period - phase) * 1000) // max(1, period - half), 0, 1000)


def _interpolated_noise_permille(
    *,
    seed: str,
    latitude_mdeg: int,
    longitude_mdeg: int,
    lat_step_mdeg: int,
    lon_step_mdeg: int,
    salt: str,
) -> int:
    lat_step = max(1, int(lat_step_mdeg))
    lon_step = max(1, int(lon_step_mdeg))
    lat_value = _clamp(int(latitude_mdeg) + 90_000, 0, 180_000)
    lon_value = (_wrap_longitude_mdeg(int(longitude_mdeg)) + 180_000) % 360_000
    lat_bucket = lat_value // lat_step
    lon_bucket = lon_value // lon_step
    lat_remainder = lat_value % lat_step
    lon_remainder = lon_value % lon_step
    lon_bucket_count = max(1, (360_000 + lon_step - 1) // lon_step)

    def sample(lat_idx: int, lon_idx: int) -> int:
        return _hash_permille(
            seed,
            salt=salt,
            coords={
                "lat_bucket": int(lat_idx),
                "lon_bucket": int(lon_idx % lon_bucket_count),
            },
        )

    v00 = sample(lat_bucket, lon_bucket)
    v01 = sample(lat_bucket, lon_bucket + 1)
    v10 = sample(lat_bucket + 1, lon_bucket)
    v11 = sample(lat_bucket + 1, lon_bucket + 1)
    top = ((v00 * (lon_step - lon_remainder)) + (v01 * lon_remainder)) // lon_step
    bottom = ((v10 * (lon_step - lon_remainder)) + (v11 * lon_remainder)) // lon_step
    return _clamp(((top * (lat_step - lat_remainder)) + (bottom * lat_remainder)) // lat_step, 0, 1000)


def _material_baseline_id(*, material_key: str, surface_priors_row: Mapping[str, object]) -> str:
    baselines = _as_map(_as_map(_as_map(surface_priors_row).get("extensions")).get("material_baselines"))
    return str(baselines.get(material_key, "material.stone_basic")).strip() or "material.stone_basic"


def _range_height(
    *,
    params: Mapping[str, object],
    minimum_key: str,
    maximum_key: str,
    bias_permille: int,
) -> int:
    minimum = max(0, _as_int(_as_map(params).get(minimum_key, 0), 0))
    maximum = max(minimum, _as_int(_as_map(params).get(maximum_key, minimum), minimum))
    return minimum if minimum == maximum else minimum + ((_clamp(bias_permille, 0, 1000) * (maximum - minimum)) // 1000)


def generate_earth_surface_tile_plan(
    *,
    tile_seed: str,
    planet_object_id: str,
    tile_cell_key: Mapping[str, object],
    surface_priors_row: Mapping[str, object],
    earth_surface_params_row: Mapping[str, object],
    latitude_mdeg: int,
    longitude_mdeg: int,
    base_temperature_kelvin: int,
    daylight_permille: int,
    insolation_permille: int,
) -> dict:
    del planet_object_id
    del tile_cell_key

    params_row = _as_map(earth_surface_params_row)
    params_ext = _as_map(params_row.get("extensions"))
    biome_thresholds = _as_map(params_row.get("biome_thresholds"))
    elevation_params = _as_map(_as_map(surface_priors_row).get("elevation_params"))

    continent_count_target = _clamp(_as_int(params_row.get("continent_count_target", 6), 6), 4, 8)
    ocean_fraction_target = _clamp(_as_int(params_row.get("ocean_fraction_target", 700), 700), 550, 850)
    mountain_intensity = _clamp(_as_int(params_row.get("mountain_intensity", 620), 620), 0, 1000)
    plate_region_count = max(4, _as_int(params_ext.get("plate_region_count", 12), 12))
    continent_wave_count = max(2, _as_int(params_ext.get("continent_wave_count", continent_count_target), continent_count_target))
    continentality_weight = _clamp(_as_int(params_ext.get("continentality_weight_permille", 720), 720), 250, 1000)
    ridge_frequency = max(2, _as_int(params_ext.get("ridge_frequency", 7), 7))
    ridge_weight = _clamp(_as_int(params_ext.get("ridge_weight_permille", 580), 580), 0, 1000)
    polar_ice_bonus = _clamp(_as_int(params_ext.get("polar_ice_bonus_permille", 180), 180), 0, 400)

    wrapped_longitude = _wrap_longitude_mdeg(longitude_mdeg)
    continent_noise = _interpolated_noise_permille(
        seed=tile_seed,
        latitude_mdeg=latitude_mdeg,
        longitude_mdeg=wrapped_longitude,
        lat_step_mdeg=max(18_000, 180_000 // continent_count_target),
        lon_step_mdeg=max(24_000, 360_000 // max(4, continent_wave_count * 2)),
        salt="earth.continent.base",
    )
    plate_noise = _interpolated_noise_permille(
        seed=tile_seed,
        latitude_mdeg=latitude_mdeg,
        longitude_mdeg=wrapped_longitude,
        lat_step_mdeg=30_000,
        lon_step_mdeg=45_000,
        salt="earth.plate.proxy",
    )
    phase_primary = _hash_permille(tile_seed, salt="earth.continent.phase_primary", coords={"band": continent_wave_count}) * 360
    phase_secondary = _hash_permille(tile_seed, salt="earth.continent.phase_secondary", coords={"band": continent_wave_count + 2}) * 360
    continent_wave_primary = _triangle_wave_permille(
        position_mdeg=wrapped_longitude,
        period_mdeg=max(18_000, 360_000 // continent_wave_count),
        phase_mdeg=phase_primary,
    )
    continent_wave_secondary = _triangle_wave_permille(
        position_mdeg=wrapped_longitude + (latitude_mdeg // 3),
        period_mdeg=max(16_000, 360_000 // (continent_wave_count + 2)),
        phase_mdeg=phase_secondary,
    )
    latitude_softener = (abs(int(latitude_mdeg)) * 120) // 90_000
    continent_score = _clamp(
        (
            (continent_noise * continentality_weight)
            + (continent_wave_primary * 180)
            + (continent_wave_secondary * 100)
            + (plate_noise * 220)
        )
        // max(1, continentality_weight + 500)
        + 40
        - (latitude_softener // 3),
        0,
        1000,
    )
    land_threshold = _clamp(int(ocean_fraction_target) - 120, 350, 850)
    is_land = continent_score >= land_threshold
    coastal_proximity_permille = _clamp(1000 - (abs(continent_score - land_threshold) * 4), 0, 1000)

    ridge_noise = _interpolated_noise_permille(
        seed=tile_seed,
        latitude_mdeg=latitude_mdeg,
        longitude_mdeg=wrapped_longitude,
        lat_step_mdeg=12_000,
        lon_step_mdeg=14_000,
        salt="earth.ridge.base",
    )
    ridge_band = _triangle_wave_permille(
        position_mdeg=(wrapped_longitude * 2) + (latitude_mdeg // 5),
        period_mdeg=max(10_000, 360_000 // max(4, ridge_frequency * 4)),
        phase_mdeg=_hash_permille(tile_seed, salt="earth.ridge.phase", coords={"ridge_frequency": ridge_frequency}) * 360,
    )
    ridge_emphasis = abs(ridge_noise - 500) * 2
    mountain_ridge_permille = _clamp(((ridge_emphasis * ridge_weight) + (ridge_band * (1000 - ridge_weight))) // 1000, 0, 1000)
    mountain_permille = _clamp(((mountain_ridge_permille * mountain_intensity) // 1000) + (plate_noise // 4), 0, 1000)

    temperature_value = _clamp(
        int(base_temperature_kelvin)
        + (4 if is_land else -2)
        - ((mountain_permille * 18) // 1000 if is_land else 0),
        120,
        480,
    )

    polar_latitude_mdeg = _clamp(_as_int(biome_thresholds.get("polar_latitude_mdeg", 70_000), 70_000), 50_000, 85_000)
    ice_temperature_kelvin = _clamp(_as_int(biome_thresholds.get("ice_temperature_kelvin", 255), 255), 180, 300)
    tropical_latitude_mdeg = _clamp(_as_int(biome_thresholds.get("tropical_latitude_mdeg", 23_500), 23_500), 10_000, 35_000)
    arid_band_min_mdeg = _clamp(_as_int(biome_thresholds.get("arid_band_min_mdeg", 18_000), 18_000), 5_000, 45_000)
    arid_band_max_mdeg = _clamp(_as_int(biome_thresholds.get("arid_band_max_mdeg", 36_000), 36_000), arid_band_min_mdeg, 55_000)
    temperate_min_kelvin = _clamp(_as_int(biome_thresholds.get("temperate_min_kelvin", 265), 265), 220, 320)
    tropical_min_kelvin = _clamp(_as_int(biome_thresholds.get("tropical_min_kelvin", 295), 295), temperate_min_kelvin, 340)
    is_ice = bool(
        (
            abs(int(latitude_mdeg)) >= polar_latitude_mdeg
            and int(temperature_value) <= (ice_temperature_kelvin + 24)
        )
        or (
            abs(int(latitude_mdeg)) >= (polar_latitude_mdeg - 2_000)
            and not is_land
            and int(temperature_value) <= ice_temperature_kelvin
            and coastal_proximity_permille >= (860 - polar_ice_bonus)
        )
    )

    if is_ice:
        surface_class_id = "surface.class.ice"
        material_key = "ice"
        climate_band_id = "climate.band.polar"
        biome_stub_id = "biome.stub.polar"
        far_lod_visual_class = "visual.class.white_polar"
        height_proxy = _range_height(
            params=elevation_params,
            minimum_key="ice_height_min",
            maximum_key="ice_height_max",
            bias_permille=max(coastal_proximity_permille, mountain_permille),
        )
        macro_relief_permille = _clamp(220 + (mountain_permille // 2), 0, 1000)
    elif not is_land:
        surface_class_id = "surface.class.ocean"
        material_key = "ocean"
        climate_band_id = "climate.band.oceanic"
        biome_stub_id = "biome.stub.ocean"
        far_lod_visual_class = "visual.class.blue_ocean"
        height_proxy = _range_height(
            params=elevation_params,
            minimum_key="ocean_height_min",
            maximum_key="ocean_height_max",
            bias_permille=coastal_proximity_permille,
        )
        macro_relief_permille = _clamp(160 + (coastal_proximity_permille // 8), 0, 1000)
    else:
        surface_class_id = "surface.class.land"
        if abs(int(latitude_mdeg)) <= tropical_latitude_mdeg and int(temperature_value) >= tropical_min_kelvin:
            climate_band_id = "climate.band.tropical"
            biome_stub_id = "biome.stub.tropical"
        elif (
            abs(int(latitude_mdeg)) >= arid_band_min_mdeg
            and abs(int(latitude_mdeg)) <= arid_band_max_mdeg
            and int(temperature_value) >= temperate_min_kelvin
            and int(daylight_permille) >= 520
            and coastal_proximity_permille <= 420
        ):
            climate_band_id = "climate.band.arid"
            biome_stub_id = "biome.stub.arid"
        else:
            climate_band_id = "climate.band.temperate"
            biome_stub_id = "biome.stub.temperate"
        material_key = "land"
        far_lod_visual_class = "visual.class.green_brown_land"
        land_bias_permille = _clamp((coastal_proximity_permille // 3) + mountain_permille, 0, 1000)
        height_proxy = _range_height(
            params=elevation_params,
            minimum_key="land_height_min",
            maximum_key="land_height_max",
            bias_permille=land_bias_permille,
        )
        macro_relief_permille = _clamp(260 + ((mountain_permille * 3) // 4), 0, 1000)

    plate_region_id = _as_int(
        (_hash_permille(tile_seed, salt="earth.plate.region", coords={"latitude_mdeg": latitude_mdeg, "longitude_mdeg": wrapped_longitude}) * plate_region_count) // 1000,
        0,
    )
    elevation_params_ref = {
        "noise_seed": _named_substream_seed(tile_seed, "rng.worldgen.surface.earth.elevation"),
        "height_proxy": int(height_proxy),
        "macro_relief_permille": int(macro_relief_permille),
        "ridge_bias_permille": int(mountain_ridge_permille),
        "coastal_bias_permille": int(coastal_proximity_permille),
        "continent_mask_permille": int(continent_score),
        "plate_region_id": int(_clamp(plate_region_id, 0, max(0, plate_region_count - 1))),
    }

    return {
        "temperature_value": int(temperature_value),
        "material_baseline_id": _material_baseline_id(material_key=material_key, surface_priors_row=surface_priors_row),
        "biome_stub_id": biome_stub_id,
        "height_proxy": int(height_proxy),
        "elevation_params_ref": elevation_params_ref,
        "extensions": {
            "latitude_mdeg": int(latitude_mdeg),
            "longitude_mdeg": int(wrapped_longitude),
            "continent_score_permille": int(continent_score),
            "coastal_proximity_permille": int(coastal_proximity_permille),
            "mountain_ridge_permille": int(mountain_ridge_permille),
            "surface_class_id": surface_class_id,
            "climate_band_id": climate_band_id,
            "far_lod_visual_class": far_lod_visual_class,
            "insolation_permille": int(insolation_permille),
            "source": EARTH_SURFACE_GENERATOR_VERSION,
        },
    }

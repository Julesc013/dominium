"""Deterministic SOL-2 Kepler proxy ephemeris helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from math import isqrt
from typing import Dict, List, Mapping, Sequence

from src.astro.illumination.illumination_geometry_engine import (
    cos_permille_from_angle_mdeg,
    sin_permille_from_angle_mdeg,
)
from src.geo import build_position_ref
from src.lib.provides.provider_resolution import resolve_providers
from src.worldgen.mw import (
    normalize_planet_basic_artifact_rows,
    normalize_planet_orbit_artifact_rows,
    normalize_star_artifact_rows,
)
from src.worldgen.mw.insolation_proxy import orbital_period_proxy_ticks
from tools.xstack.compatx.canonical_json import canonical_sha256


EPHEMERIS_PROVIDER_REGISTRY_REL = os.path.join("data", "registries", "ephemeris_provider_registry.json")
ORBIT_PATH_POLICY_REGISTRY_REL = os.path.join("data", "registries", "orbit_path_policy_registry.json")
DEFAULT_EPHEMERIS_PROVIDER_ID = "ephemeris.kepler_proxy"
DEFAULT_ORBIT_PATH_POLICY_ID = "orbitpath.mvp_default"
DEFAULT_EPHEMERIS_PROVIDES_ID = "provides.ephemeris.system.v1"
DEFAULT_ORBIT_FRAME_ID = "frame.orbit.proxy"
DEFAULT_ORBIT_CHART_ID = "chart.global.r3"
KEPLER_PROXY_ENGINE_VERSION = "SOL2-3"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


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


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def _round_div_away_from_zero(numerator: int, denominator: int) -> int:
    if int(denominator) == 0:
        raise ValueError("denominator must be non-zero")
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


def _quantity_value(value: object, default_value: int = 0) -> int:
    row = _as_map(value)
    return int(_as_int(row.get("value", default_value), default_value))


def _hash_int(seed: Mapping[str, object]) -> int:
    return int(canonical_sha256(dict(seed or {}))[:16], 16)


def ephemeris_provider_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(EPHEMERIS_PROVIDER_REGISTRY_REL), row_key="ephemeris_providers", id_key="provider_id")


def orbit_path_policy_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(ORBIT_PATH_POLICY_REGISTRY_REL), row_key="orbit_path_policies", id_key="policy_id")


def ephemeris_provider_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(EPHEMERIS_PROVIDER_REGISTRY_REL))


def orbit_path_policy_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(ORBIT_PATH_POLICY_REGISTRY_REL))


def _provider_id_from_resolution(
    *,
    resolution: Mapping[str, object],
    provider_declarations: Sequence[Mapping[str, object]],
) -> str:
    provides_resolutions = [dict(row) for row in _as_list(_as_map(resolution).get("provides_resolutions")) if isinstance(row, Mapping)]
    chosen_pack_id = str(_as_map(provides_resolutions[0]).get("chosen_pack_id", "")).strip() if provides_resolutions else ""
    for row in list(provider_declarations or []):
        declaration = _as_map(row)
        if str(declaration.get("pack_id", "")).strip() != chosen_pack_id:
            continue
        provider_id = str(_as_map(declaration.get("extensions")).get("provider_id", "")).strip()
        if provider_id:
            return provider_id
    return DEFAULT_EPHEMERIS_PROVIDER_ID


def resolve_ephemeris_provider(
    *,
    instance_id: str,
    provider_declarations: Sequence[Mapping[str, object]] | None = None,
    explicit_resolutions: Sequence[Mapping[str, object]] | None = None,
    required_provides_ids: Sequence[str] | None = None,
) -> dict:
    declarations = [dict(row) for row in list(provider_declarations or []) if isinstance(row, Mapping)]
    required_ids = list(required_provides_ids or [DEFAULT_EPHEMERIS_PROVIDES_ID])
    if not declarations:
        payload = {
            "result": "complete",
            "provider_id": DEFAULT_EPHEMERIS_PROVIDER_ID,
            "resolution_policy_id": "resolve.mvp_default",
            "provides_id": DEFAULT_EPHEMERIS_PROVIDES_ID,
            "selection_logged": False,
            "provides_resolution": {},
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    resolution = resolve_providers(
        instance_id=str(instance_id or "orbit_view"),
        required_provides_ids=required_ids,
        provider_declarations=declarations,
        explicit_resolutions=explicit_resolutions or [],
        resolution_policy_id="resolve.deterministic_highest_priority",
    )
    if str(resolution.get("result", "")).strip() != "complete":
        payload = {
            "result": "refused",
            "provider_id": "",
            "provides_id": DEFAULT_EPHEMERIS_PROVIDES_ID,
            "resolution_policy_id": str(resolution.get("resolution_policy_id", "")).strip(),
            "refusal_code": str(resolution.get("refusal_code", "")).strip() or "refusal.provides.missing_provider",
            "errors": [dict(row) for row in list(resolution.get("errors") or []) if isinstance(row, Mapping)],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    provider_id = _provider_id_from_resolution(resolution=resolution, provider_declarations=declarations)
    if provider_id not in ephemeris_provider_rows():
        payload = {
            "result": "refused",
            "provider_id": provider_id,
            "provides_id": DEFAULT_EPHEMERIS_PROVIDES_ID,
            "resolution_policy_id": str(resolution.get("resolution_policy_id", "")).strip(),
            "refusal_code": "refusal.ephemeris.provider_unregistered",
            "errors": [{"code": "refusal.ephemeris.provider_unregistered", "message": "resolved provider is not declared in the ephemeris provider registry"}],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    provides_resolutions = [dict(row) for row in list(resolution.get("provides_resolutions") or []) if isinstance(row, Mapping)]
    payload = {
        "result": "complete",
        "provider_id": provider_id,
        "provides_id": DEFAULT_EPHEMERIS_PROVIDES_ID,
        "resolution_policy_id": str(resolution.get("resolution_policy_id", "")).strip(),
        "selection_logged": bool(resolution.get("selection_logged", False)),
        "provides_resolution": provides_resolutions[0] if provides_resolutions else {},
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _phase_offset_mdeg(object_id: str, parent_object_id: str) -> int:
    return int(_hash_int({"object_id": str(object_id), "parent_object_id": str(parent_object_id), "source": KEPLER_PROXY_ENGINE_VERSION}) % 360_000)


def _descriptor_from_effective_object(row: Mapping[str, object]) -> dict:
    properties = _as_map(_as_map(row).get("properties"))
    hierarchy = _as_map(properties.get("hierarchy"))
    orbit = _as_map(properties.get("orbit"))
    surface = _as_map(properties.get("surface"))
    physical = _as_map(properties.get("physical"))
    object_id = str(_as_map(row).get("object_id", "")).strip()
    kind = str(_as_map(row).get("object_kind_id", "")).strip()
    hierarchy_parent_id = str(hierarchy.get("parent_object_id", "")).strip()
    orbit_parent_id = str(orbit.get("parent_object_id", "")).strip()
    relative_parent_object_id = hierarchy_parent_id if kind == "kind.moon" and hierarchy_parent_id else orbit_parent_id or hierarchy_parent_id
    if kind == "kind.star":
        relative_parent_object_id = ""
    return {
        "object_id": object_id,
        "display_name": str(properties.get("display_name", "")).strip() or object_id,
        "kind": kind,
        "body_slot_id": str(hierarchy.get("body_slot_id", "")).strip(),
        "hierarchy_parent_object_id": hierarchy_parent_id,
        "relative_parent_object_id": relative_parent_object_id,
        "orbit_parent_object_id": orbit_parent_id,
        "semi_major_axis_units": int(max(0, _as_int(orbit.get("semi_major_axis_milli_au", 0), 0))),
        "eccentricity_permille": int(_clamp(_as_int(orbit.get("eccentricity_permille", 0), 0), 0, 900)),
        "inclination_mdeg": int(_clamp(_as_int(orbit.get("inclination_mdeg", 0), 0), -180_000, 180_000)),
        "radius_km": int(max(0, _as_int(physical.get("radius_km", 0), 0))),
        "body_albedo_proxy_permille": int(_clamp(_as_int(surface.get("body_albedo_proxy_permille", 0), 0), 0, 1000)),
        "luminosity_proxy_value": int(max(0, _quantity_value(properties.get("luminosity_proxy"), _as_int(properties.get("luminosity_proxy", 0), 0)))),
        "mass_proxy_milli": int(max(0, _as_int(physical.get("mass_milli_solar", 0), 0))),
        "phase_offset_mdeg": int(_phase_offset_mdeg(object_id, relative_parent_object_id)),
        "source_kind": "effective_object_view",
        "deterministic_fingerprint": "",
        "extensions": {
            "source": KEPLER_PROXY_ENGINE_VERSION,
        },
    }


def _descriptor_from_worldgen(
    *,
    orbit_row: Mapping[str, object],
    basic_row: Mapping[str, object],
) -> dict:
    planet_object_id = str(_as_map(orbit_row).get("planet_object_id", "")).strip()
    star_object_id = str(_as_map(orbit_row).get("star_object_id", "")).strip()
    basic_ext = _as_map(_as_map(basic_row).get("extensions"))
    return {
        "object_id": planet_object_id,
        "display_name": str(basic_ext.get("planet_class_id", "")).strip() or planet_object_id,
        "kind": "kind.planet",
        "body_slot_id": "",
        "hierarchy_parent_object_id": str(basic_ext.get("parent_system_object_id", "")).strip(),
        "relative_parent_object_id": star_object_id,
        "orbit_parent_object_id": star_object_id,
        "semi_major_axis_units": int(max(0, _quantity_value(_as_map(orbit_row).get("semi_major_axis"), 0))),
        "eccentricity_permille": int(_clamp(_quantity_value(_as_map(orbit_row).get("eccentricity"), 0), 0, 900)),
        "inclination_mdeg": int(_clamp(_quantity_value(_as_map(orbit_row).get("inclination"), 0), -180_000, 180_000)),
        "radius_km": int(max(0, _quantity_value(_as_map(basic_row).get("radius"), 0))),
        "body_albedo_proxy_permille": int(_clamp(_quantity_value(_as_map(basic_row).get("body_albedo_proxy"), 0), 0, 1000)),
        "luminosity_proxy_value": 0,
        "mass_proxy_milli": 0,
        "phase_offset_mdeg": int(_phase_offset_mdeg(planet_object_id, star_object_id)),
        "source_kind": "worldgen_artifact",
        "deterministic_fingerprint": "",
        "extensions": {
            "planet_class_id": str(basic_ext.get("planet_class_id", "")).strip(),
            "source": KEPLER_PROXY_ENGINE_VERSION,
        },
    }


def _moon_descriptors_from_worldgen(
    *,
    basic_row: Mapping[str, object],
) -> List[dict]:
    basic = _as_map(basic_row)
    parent_object_id = str(basic.get("object_id", "")).strip()
    basic_ext = _as_map(basic.get("extensions"))
    moon_rows = sorted(
        [dict(row) for row in _as_list(basic_ext.get("moon_stub_descriptors")) if isinstance(row, Mapping)],
        key=lambda row: (int(_as_int(row.get("moon_index", 0), 0)), str(row.get("object_id", ""))),
    )
    out: List[dict] = []
    for row in moon_rows:
        object_id = str(row.get("object_id", "")).strip()
        if not object_id:
            continue
        moon_index = int(max(0, _as_int(row.get("moon_index", 0), 0)))
        radius_km = int(max(1, _quantity_value(_as_map(row).get("radius"), 1737)))
        semi_major_axis_units = int(max(800, radius_km * 60))
        out.append(
            {
                "object_id": object_id,
                "display_name": "moon_stub_{}".format(moon_index),
                "kind": "kind.moon",
                "body_slot_id": "",
                "hierarchy_parent_object_id": parent_object_id,
                "relative_parent_object_id": parent_object_id,
                "orbit_parent_object_id": parent_object_id,
                "semi_major_axis_units": semi_major_axis_units,
                "eccentricity_permille": 40,
                "inclination_mdeg": int((_hash_int({"moon_object_id": object_id, "moon_index": moon_index}) % 18_000) - 9_000),
                "radius_km": radius_km,
                "body_albedo_proxy_permille": int(_clamp(_quantity_value(_as_map(row).get("body_albedo_proxy"), 120), 0, 1000)),
                "luminosity_proxy_value": 0,
                "mass_proxy_milli": 80,
                "phase_offset_mdeg": int(_phase_offset_mdeg(object_id, parent_object_id)),
                "source_kind": "worldgen_stub_moon",
                "deterministic_fingerprint": "",
                "extensions": {
                    "moon_index": moon_index,
                    "derived_orbit_stub": True,
                    "source": KEPLER_PROXY_ENGINE_VERSION,
                },
            }
        )
    return out


def build_orbit_body_descriptors(
    *,
    effective_object_views: object = None,
    star_artifact_rows: object = None,
    planet_orbit_artifact_rows: object = None,
    planet_basic_artifact_rows: object = None,
) -> List[dict]:
    out: Dict[str, dict] = {}
    effective_rows = [dict(row) for row in list(effective_object_views or []) if isinstance(row, Mapping)]
    if effective_rows:
        for row in sorted(effective_rows, key=lambda item: (str(item.get("object_kind_id", "")), str(item.get("object_id", "")))):
            descriptor = _descriptor_from_effective_object(row)
            object_id = str(descriptor.get("object_id", "")).strip()
            if not object_id:
                continue
            if str(descriptor.get("kind", "")).strip() not in {"kind.star", "kind.star_system", "kind.planet", "kind.moon"}:
                continue
            descriptor["deterministic_fingerprint"] = canonical_sha256(dict(descriptor, deterministic_fingerprint=""))
            out[object_id] = descriptor
        return [dict(out[key]) for key in sorted(out.keys())]

    star_rows = normalize_star_artifact_rows(star_artifact_rows)
    orbit_rows = normalize_planet_orbit_artifact_rows(planet_orbit_artifact_rows)
    basic_rows = normalize_planet_basic_artifact_rows(planet_basic_artifact_rows)
    orbit_by_planet = dict((str(row.get("planet_object_id", "")).strip(), dict(row)) for row in orbit_rows if str(row.get("planet_object_id", "")).strip())
    basic_by_object = dict((str(row.get("object_id", "")).strip(), dict(row)) for row in basic_rows if str(row.get("object_id", "")).strip())
    for star_row in star_rows:
        object_id = str(star_row.get("object_id", "")).strip()
        if not object_id:
            continue
        descriptor = {
            "object_id": object_id,
            "display_name": object_id,
            "kind": "kind.star",
            "body_slot_id": "",
            "hierarchy_parent_object_id": str(_as_map(star_row.get("extensions")).get("parent_system_object_id", "")).strip(),
            "relative_parent_object_id": "",
            "orbit_parent_object_id": "",
            "semi_major_axis_units": 0,
            "eccentricity_permille": 0,
            "inclination_mdeg": 0,
            "radius_km": 0,
            "body_albedo_proxy_permille": 0,
            "luminosity_proxy_value": int(max(0, _quantity_value(star_row.get("luminosity_proxy"), 1000))),
            "mass_proxy_milli": int(max(0, _quantity_value(star_row.get("star_mass"), 1000))),
            "phase_offset_mdeg": 0,
            "source_kind": "worldgen_artifact",
            "deterministic_fingerprint": "",
            "extensions": {
                "source": KEPLER_PROXY_ENGINE_VERSION,
            },
        }
        descriptor["deterministic_fingerprint"] = canonical_sha256(dict(descriptor, deterministic_fingerprint=""))
        out[object_id] = descriptor
    for planet_object_id in sorted(orbit_by_planet.keys()):
        orbit_row = dict(orbit_by_planet.get(planet_object_id) or {})
        basic_row = dict(basic_by_object.get(planet_object_id) or {})
        descriptor = _descriptor_from_worldgen(orbit_row=orbit_row, basic_row=basic_row)
        descriptor["deterministic_fingerprint"] = canonical_sha256(dict(descriptor, deterministic_fingerprint=""))
        out[planet_object_id] = descriptor
        for moon_descriptor in _moon_descriptors_from_worldgen(basic_row=basic_row):
            moon_object_id = str(moon_descriptor.get("object_id", "")).strip()
            if not moon_object_id:
                continue
            moon_descriptor["deterministic_fingerprint"] = canonical_sha256(dict(moon_descriptor, deterministic_fingerprint=""))
            out[moon_object_id] = moon_descriptor
    return [dict(out[key]) for key in sorted(out.keys())]


def _parent_mass_proxy_milli(body_row: Mapping[str, object], body_rows_by_id: Mapping[str, dict]) -> int:
    parent_object_id = str(_as_map(body_row).get("relative_parent_object_id", "")).strip()
    parent_row = _as_map(body_rows_by_id.get(parent_object_id))
    if not parent_row:
        return 1000
    if str(parent_row.get("kind", "")).strip() == "kind.star":
        return int(max(80, _as_int(parent_row.get("mass_proxy_milli", 1000), 1000)))
    return int(max(80, _as_int(parent_row.get("mass_proxy_milli", 120), 120)))


def _period_estimate_ticks(body_row: Mapping[str, object], body_rows_by_id: Mapping[str, dict]) -> int:
    if str(_as_map(body_row).get("kind", "")).strip() not in {"kind.planet", "kind.moon"}:
        return 0
    semi_major_axis_units = int(max(80, _as_int(_as_map(body_row).get("semi_major_axis_units", 0), 0)))
    return int(
        orbital_period_proxy_ticks(
            semi_major_axis_milli_au=semi_major_axis_units,
            star_mass_milli_solar=_parent_mass_proxy_milli(body_row, body_rows_by_id),
        )
    )


def _vector_add(left: Sequence[int], right: Sequence[int]) -> list[int]:
    return [int(_as_int(left[idx], 0) + _as_int(right[idx], 0)) for idx in range(3)]


def _relative_orbit_vector_units(body_row: Mapping[str, object], tick: int, body_rows_by_id: Mapping[str, dict]) -> list[int]:
    row = _as_map(body_row)
    kind = str(row.get("kind", "")).strip()
    if kind not in {"kind.planet", "kind.moon"}:
        return [0, 0, 0]
    axis_units = int(max(1, _as_int(row.get("semi_major_axis_units", 0), 0)))
    eccentricity_permille = int(_clamp(_as_int(row.get("eccentricity_permille", 0), 0), 0, 900))
    inclination_mdeg = int(_clamp(_as_int(row.get("inclination_mdeg", 0), 0), -180_000, 180_000))
    period_ticks = int(max(1, _period_estimate_ticks(row, body_rows_by_id)))
    phase_offset_mdeg = int(_as_int(row.get("phase_offset_mdeg", 0), 0))
    anomaly_mdeg = int((((max(0, _as_int(tick, 0)) % period_ticks) * 360_000) // period_ticks + phase_offset_mdeg) % 360_000)
    cos_anomaly = int(cos_permille_from_angle_mdeg(anomaly_mdeg))
    sin_anomaly = int(sin_permille_from_angle_mdeg(anomaly_mdeg))
    minor_axis_units = int(max(1, _round_div_away_from_zero(axis_units * isqrt(max(0, 1_000_000 - (eccentricity_permille * eccentricity_permille))), 1000)))
    x_planar = int(_round_div_away_from_zero(axis_units * cos_anomaly, 1000) - _round_div_away_from_zero(axis_units * eccentricity_permille, 1000))
    y_planar = int(_round_div_away_from_zero(minor_axis_units * sin_anomaly, 1000))
    cos_inclination = int(cos_permille_from_angle_mdeg(inclination_mdeg))
    sin_inclination = int(sin_permille_from_angle_mdeg(inclination_mdeg))
    y_units = int(_round_div_away_from_zero(y_planar * cos_inclination, 1000))
    z_units = int(_round_div_away_from_zero(y_planar * sin_inclination, 1000))
    return [int(x_planar), int(y_units), int(z_units)]


def orbit_vector_units_at_tick(
    *,
    body_object_id: str,
    tick: int,
    body_rows_by_id: Mapping[str, dict],
) -> list[int]:
    object_id = str(body_object_id or "").strip()
    row = _as_map(body_rows_by_id.get(object_id))
    if not row:
        return [0, 0, 0]
    parent_object_id = str(row.get("relative_parent_object_id", "")).strip()
    relative = _relative_orbit_vector_units(row, int(tick), body_rows_by_id)
    if not parent_object_id or parent_object_id == object_id or parent_object_id not in body_rows_by_id:
        return relative
    parent_absolute = orbit_vector_units_at_tick(body_object_id=parent_object_id, tick=int(tick), body_rows_by_id=body_rows_by_id)
    return _vector_add(parent_absolute, relative)


def build_orbit_position_ref(
    *,
    object_id: str,
    local_position: Sequence[int],
    frame_id: str = DEFAULT_ORBIT_FRAME_ID,
    chart_id: str = DEFAULT_ORBIT_CHART_ID,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    return build_position_ref(
        object_id=str(object_id or "").strip(),
        frame_id=str(frame_id or DEFAULT_ORBIT_FRAME_ID).strip() or DEFAULT_ORBIT_FRAME_ID,
        local_position=[int(_as_int(value, 0)) for value in list(local_position or [])[:3]],
        extensions={
            "chart_id": str(chart_id or DEFAULT_ORBIT_CHART_ID).strip() or DEFAULT_ORBIT_CHART_ID,
            "source": KEPLER_PROXY_ENGINE_VERSION,
            "derived_only": True,
            **_as_map(extensions),
        },
    )


def sample_orbit_path_points(
    *,
    body_row: Mapping[str, object],
    body_rows_by_id: Mapping[str, dict],
    sample_count: int,
    frame_id: str,
    chart_id: str,
) -> list[dict]:
    row = _as_map(body_row)
    kind = str(row.get("kind", "")).strip()
    if kind not in {"kind.planet", "kind.moon"}:
        return []
    period_ticks = int(max(1, _period_estimate_ticks(row, body_rows_by_id)))
    count = int(max(8, min(512, _as_int(sample_count, 8))))
    out = []
    for sample_index in range(count):
        sample_tick = int((period_ticks * sample_index) // count)
        absolute_vector = orbit_vector_units_at_tick(
            body_object_id=str(row.get("object_id", "")).strip(),
            tick=sample_tick,
            body_rows_by_id=body_rows_by_id,
        )
        out.append(
            {
                "sample_index": int(sample_index),
                "sample_tick": int(sample_tick),
                "absolute_vector_units": list(absolute_vector),
                "position_ref": build_orbit_position_ref(
                    object_id=str(row.get("object_id", "")).strip(),
                    local_position=absolute_vector,
                    frame_id=frame_id,
                    chart_id=chart_id,
                    extensions={
                        "sample_index": int(sample_index),
                        "path_point": True,
                    },
                ),
            }
        )
    return out


def period_estimate_ticks_for_body(
    *,
    body_row: Mapping[str, object],
    body_rows_by_id: Mapping[str, dict],
) -> int:
    return int(_period_estimate_ticks(_as_map(body_row), body_rows_by_id))


__all__ = [
    "DEFAULT_EPHEMERIS_PROVIDER_ID",
    "DEFAULT_ORBIT_PATH_POLICY_ID",
    "EPHEMERIS_PROVIDER_REGISTRY_REL",
    "KEPLER_PROXY_ENGINE_VERSION",
    "ORBIT_PATH_POLICY_REGISTRY_REL",
    "build_orbit_body_descriptors",
    "build_orbit_position_ref",
    "ephemeris_provider_registry_hash",
    "ephemeris_provider_rows",
    "orbit_path_policy_registry_hash",
    "orbit_path_policy_rows",
    "period_estimate_ticks_for_body",
    "orbit_vector_units_at_tick",
    "resolve_ephemeris_provider",
    "sample_orbit_path_points",
]

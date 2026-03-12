"""Deterministic SOL-1 illumination geometry helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from math import isqrt
from typing import Dict, Mapping, Sequence

from src.geo import build_position_ref
from tools.xstack.compatx.canonical_json import canonical_sha256


EMITTER_KIND_REGISTRY_REL = os.path.join("data", "registries", "emitter_kind_registry.json")
RECEIVER_KIND_REGISTRY_REL = os.path.join("data", "registries", "receiver_kind_registry.json")
OCCLUSION_POLICY_REGISTRY_REL = os.path.join("data", "registries", "occlusion_policy_registry.json")

DEFAULT_OCCLUSION_POLICY_ID = "occlusion.none_stub"
DEFAULT_ILLUMINATION_FRAME_ID = "frame.illumination.proxy"
DEFAULT_EMITTER_DISTANCE_UNITS = 100_000_000
DEFAULT_RECEIVER_DISTANCE_UNITS = 1_000_000
ILLUMINATION_GEOMETRY_ENGINE_VERSION = "SOL1-3"

_PHASE_ANGLE_BY_COS_PERMILLE = [
    (1000, 0),
    (1000, 1000),
    (999, 2000),
    (999, 3000),
    (998, 4000),
    (996, 5000),
    (995, 6000),
    (993, 7000),
    (990, 8000),
    (988, 9000),
    (985, 10000),
    (982, 11000),
    (978, 12000),
    (974, 13000),
    (970, 14000),
    (966, 15000),
    (961, 16000),
    (956, 17000),
    (951, 18000),
    (946, 19000),
    (940, 20000),
    (934, 21000),
    (927, 22000),
    (921, 23000),
    (914, 24000),
    (906, 25000),
    (899, 26000),
    (891, 27000),
    (883, 28000),
    (875, 29000),
    (866, 30000),
    (857, 31000),
    (848, 32000),
    (839, 33000),
    (829, 34000),
    (819, 35000),
    (809, 36000),
    (799, 37000),
    (788, 38000),
    (777, 39000),
    (766, 40000),
    (755, 41000),
    (743, 42000),
    (731, 43000),
    (719, 44000),
    (707, 45000),
    (695, 46000),
    (682, 47000),
    (669, 48000),
    (656, 49000),
    (643, 50000),
    (629, 51000),
    (616, 52000),
    (602, 53000),
    (588, 54000),
    (574, 55000),
    (559, 56000),
    (545, 57000),
    (530, 58000),
    (515, 59000),
    (500, 60000),
    (485, 61000),
    (469, 62000),
    (454, 63000),
    (438, 64000),
    (423, 65000),
    (407, 66000),
    (391, 67000),
    (375, 68000),
    (358, 69000),
    (342, 70000),
    (326, 71000),
    (309, 72000),
    (292, 73000),
    (276, 74000),
    (259, 75000),
    (242, 76000),
    (225, 77000),
    (208, 78000),
    (191, 79000),
    (174, 80000),
    (156, 81000),
    (139, 82000),
    (122, 83000),
    (105, 84000),
    (87, 85000),
    (70, 86000),
    (52, 87000),
    (35, 88000),
    (17, 89000),
    (0, 90000),
    (-17, 91000),
    (-35, 92000),
    (-52, 93000),
    (-70, 94000),
    (-87, 95000),
    (-105, 96000),
    (-122, 97000),
    (-139, 98000),
    (-156, 99000),
    (-174, 100000),
    (-191, 101000),
    (-208, 102000),
    (-225, 103000),
    (-242, 104000),
    (-259, 105000),
    (-276, 106000),
    (-292, 107000),
    (-309, 108000),
    (-326, 109000),
    (-342, 110000),
    (-358, 111000),
    (-375, 112000),
    (-391, 113000),
    (-407, 114000),
    (-423, 115000),
    (-438, 116000),
    (-454, 117000),
    (-469, 118000),
    (-485, 119000),
    (-500, 120000),
    (-515, 121000),
    (-530, 122000),
    (-545, 123000),
    (-559, 124000),
    (-574, 125000),
    (-588, 126000),
    (-602, 127000),
    (-616, 128000),
    (-629, 129000),
    (-643, 130000),
    (-656, 131000),
    (-669, 132000),
    (-682, 133000),
    (-695, 134000),
    (-707, 135000),
    (-719, 136000),
    (-731, 137000),
    (-743, 138000),
    (-755, 139000),
    (-766, 140000),
    (-777, 141000),
    (-788, 142000),
    (-799, 143000),
    (-809, 144000),
    (-819, 145000),
    (-829, 146000),
    (-839, 147000),
    (-848, 148000),
    (-857, 149000),
    (-866, 150000),
    (-875, 151000),
    (-883, 152000),
    (-891, 153000),
    (-899, 154000),
    (-906, 155000),
    (-914, 156000),
    (-921, 157000),
    (-927, 158000),
    (-934, 159000),
    (-940, 160000),
    (-946, 161000),
    (-951, 162000),
    (-956, 163000),
    (-961, 164000),
    (-966, 165000),
    (-970, 166000),
    (-974, 167000),
    (-978, 168000),
    (-982, 169000),
    (-985, 170000),
    (-988, 171000),
    (-990, 172000),
    (-993, 173000),
    (-995, 174000),
    (-996, 175000),
    (-998, 176000),
    (-999, 177000),
    (-999, 178000),
    (-1000, 179000),
    (-1000, 180000),
]


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


def _quantity(unit: str, value: int) -> dict:
    return {"unit": str(unit), "value": int(value)}


def _vector3(value: object) -> list[int]:
    if isinstance(value, list):
        vector = [int(_as_int(item, 0)) for item in value[:3]]
    else:
        payload = _as_map(value)
        vector = [
            int(_as_int(payload.get("x", 0), 0)),
            int(_as_int(payload.get("y", 0), 0)),
            int(_as_int(payload.get("z", 0), 0)),
        ]
    while len(vector) < 3:
        vector.append(0)
    return vector[:3]


def _direction_components(direction: Mapping[str, object] | None) -> tuple[list[int], int]:
    payload = _as_map(direction)
    scale = max(1, _as_int(payload.get("scale", 1000), 1000))
    vector = _vector3(payload)
    if vector == [0, 0, 0]:
        vector = [0, 0, scale]
    return vector, scale


def _position_vector(position_ref: Mapping[str, object] | None) -> list[int]:
    return _vector3(_as_map(position_ref).get("local_position"))


def _vector_sub(left: Sequence[int], right: Sequence[int]) -> list[int]:
    return [int(_as_int(left[idx], 0) - _as_int(right[idx], 0)) for idx in range(3)]


def _dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(int(_as_int(left[idx], 0)) * int(_as_int(right[idx], 0)) for idx in range(3))


def _mag_sq(vector: Sequence[int]) -> int:
    return sum(int(_as_int(item, 0)) * int(_as_int(item, 0)) for item in vector[:3])


def _cos_permille(left: Sequence[int], right: Sequence[int]) -> int:
    left_sq = _mag_sq(left)
    right_sq = _mag_sq(right)
    if left_sq <= 0 or right_sq <= 0:
        return 1000
    denominator = isqrt(left_sq * right_sq)
    if denominator <= 0:
        return 1000
    return _clamp(_round_div_away_from_zero(_dot(left, right) * 1000, denominator), -1000, 1000)


def _phase_angle_from_cos_permille(cos_permille: int) -> int:
    clamped = _clamp(_as_int(cos_permille, 0), -1000, 1000)
    if clamped >= 1000:
        return 0
    if clamped <= -1000:
        return 180_000
    for index in range(len(_PHASE_ANGLE_BY_COS_PERMILLE) - 1):
        cos_hi, angle_lo = _PHASE_ANGLE_BY_COS_PERMILLE[index]
        cos_lo, angle_hi = _PHASE_ANGLE_BY_COS_PERMILLE[index + 1]
        if clamped > cos_hi or clamped < cos_lo:
            continue
        if cos_hi == cos_lo:
            return int(max(angle_lo, angle_hi))
        offset = cos_hi - clamped
        span = cos_hi - cos_lo
        return int(angle_lo + _round_div_away_from_zero(offset * (angle_hi - angle_lo), span))
    return 180_000


def cos_permille_from_angle_mdeg(angle_mdeg: int) -> int:
    normalized = int(_as_int(angle_mdeg, 0)) % 360_000
    if normalized < 0:
        normalized += 360_000
    if normalized <= 180_000:
        lookup_angle = normalized
        sign = 1
    else:
        lookup_angle = 360_000 - normalized
        sign = 1
    lower_index = max(0, min(len(_PHASE_ANGLE_BY_COS_PERMILLE) - 1, lookup_angle // 1000))
    upper_index = min(len(_PHASE_ANGLE_BY_COS_PERMILLE) - 1, lower_index + 1)
    cos_lo, angle_lo = _PHASE_ANGLE_BY_COS_PERMILLE[lower_index]
    cos_hi, angle_hi = _PHASE_ANGLE_BY_COS_PERMILLE[upper_index]
    if angle_hi == angle_lo:
        return int(sign * cos_lo)
    offset = lookup_angle - angle_lo
    span = angle_hi - angle_lo
    interpolated = int(cos_lo + _round_div_away_from_zero(offset * (cos_hi - cos_lo), span))
    return int(_clamp(sign * interpolated, -1000, 1000))


def sin_permille_from_angle_mdeg(angle_mdeg: int) -> int:
    return int(cos_permille_from_angle_mdeg(90_000 - int(_as_int(angle_mdeg, 0))))


def emitter_kind_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(EMITTER_KIND_REGISTRY_REL), row_key="emitter_kinds", id_key="emitter_kind_id")


def receiver_kind_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(RECEIVER_KIND_REGISTRY_REL), row_key="receiver_kinds", id_key="receiver_kind_id")


def occlusion_policy_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(payload) or _registry_payload(OCCLUSION_POLICY_REGISTRY_REL), row_key="occlusion_policies", id_key="policy_id")


def emitter_kind_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(EMITTER_KIND_REGISTRY_REL))


def receiver_kind_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(RECEIVER_KIND_REGISTRY_REL))


def occlusion_policy_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(OCCLUSION_POLICY_REGISTRY_REL))


def build_direction_position_ref(
    *,
    object_id: str,
    direction: Mapping[str, object] | None,
    distance_units: int,
    frame_id: str = DEFAULT_ILLUMINATION_FRAME_ID,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    vector, scale = _direction_components(direction)
    distance = max(1, _as_int(distance_units, DEFAULT_RECEIVER_DISTANCE_UNITS))
    local_position = [
        int(_round_div_away_from_zero(vector[0] * distance, scale)),
        int(_round_div_away_from_zero(vector[1] * distance, scale)),
        int(_round_div_away_from_zero(vector[2] * distance, scale)),
    ]
    return build_position_ref(
        object_id=str(object_id or "").strip(),
        frame_id=str(frame_id or DEFAULT_ILLUMINATION_FRAME_ID).strip() or DEFAULT_ILLUMINATION_FRAME_ID,
        local_position=local_position,
        extensions={
            "derived_only": True,
            "source": ILLUMINATION_GEOMETRY_ENGINE_VERSION,
            **_as_map(extensions),
        },
    )


def build_emitter_descriptor(
    *,
    emitter_id: str,
    object_id: str,
    luminosity_proxy_value: int,
    kind: str = "emitter.star",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "emitter_id": str(emitter_id or "").strip(),
        "kind": str(kind or "emitter.star").strip() or "emitter.star",
        "object_id": str(object_id or "").strip(),
        "luminosity_proxy": _quantity("milli_solar_luminosity", max(0, _as_int(luminosity_proxy_value, 0))),
        "deterministic_fingerprint": "",
        "extensions": {
            "source": ILLUMINATION_GEOMETRY_ENGINE_VERSION,
            **_as_map(extensions),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_receiver_descriptor(
    *,
    receiver_id: str,
    object_id: str,
    radius_km: int,
    albedo_proxy_permille: int,
    kind: str = "receiver.moon",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "receiver_id": str(receiver_id or "").strip(),
        "kind": str(kind or "receiver.moon").strip() or "receiver.moon",
        "object_id": str(object_id or "").strip(),
        "radius": _quantity("km", max(1, _as_int(radius_km, 1))),
        "albedo_proxy": _quantity("permille", _clamp(_as_int(albedo_proxy_permille, 0), 0, 1000)),
        "deterministic_fingerprint": "",
        "extensions": {
            "source": ILLUMINATION_GEOMETRY_ENGINE_VERSION,
            **_as_map(extensions),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _occlusion_fraction_permille(
    *,
    occlusion_policy_id: str,
) -> int:
    policy_id = str(occlusion_policy_id or DEFAULT_OCCLUSION_POLICY_ID).strip() or DEFAULT_OCCLUSION_POLICY_ID
    policy_row = dict(occlusion_policy_rows().get(policy_id) or {})
    extensions = _as_map(policy_row.get("extensions"))
    return _clamp(_as_int(extensions.get("visible_fraction_permille", 1000), 1000), 0, 1000)


def build_illumination_view_artifact(
    *,
    tick: int,
    viewer_ref: Mapping[str, object] | None,
    emitter_row: Mapping[str, object] | None,
    receiver_row: Mapping[str, object] | None,
    emitter_position_ref: Mapping[str, object] | None,
    receiver_position_ref: Mapping[str, object] | None,
    occlusion_policy_id: str = DEFAULT_OCCLUSION_POLICY_ID,
) -> dict:
    viewer = _as_map(viewer_ref)
    emitter = _as_map(emitter_row)
    receiver = _as_map(receiver_row)
    emitter_ref = _as_map(emitter_position_ref)
    receiver_ref = _as_map(receiver_position_ref)
    viewer_vector = _position_vector(viewer)
    emitter_vector = _position_vector(emitter_ref)
    receiver_vector = _position_vector(receiver_ref)
    receiver_to_emitter = _vector_sub(emitter_vector, receiver_vector)
    receiver_to_viewer = _vector_sub(viewer_vector, receiver_vector)
    cos_phase_permille = _cos_permille(receiver_to_emitter, receiver_to_viewer)
    phase_angle_mdeg = _phase_angle_from_cos_permille(cos_phase_permille)
    illumination_fraction = _clamp((1000 + cos_phase_permille) // 2, 0, 1000)
    occlusion_fraction = _occlusion_fraction_permille(occlusion_policy_id=str(occlusion_policy_id))
    effective_fraction = _clamp((illumination_fraction * occlusion_fraction) // 1000, 0, 1000)
    viewer_hash = canonical_sha256(
        {
            "object_id": str(viewer.get("object_id", "")).strip(),
            "frame_id": str(viewer.get("frame_id", "")).strip(),
            "local_position": _position_vector(viewer),
        }
    )
    payload = {
        "schema_version": "1.0.0",
        "view_id": "illumination.{}.{}.tick.{}".format(
            str(emitter.get("object_id", "")).strip() or "emitter",
            str(receiver.get("object_id", "")).strip() or "receiver",
            max(0, _as_int(tick, 0)),
        ),
        "tick": int(max(0, _as_int(tick, 0))),
        "viewer_ref": dict(viewer),
        "emitter_object_id": str(emitter.get("object_id", "")).strip(),
        "receiver_object_id": str(receiver.get("object_id", "")).strip(),
        "phase_angle": int(phase_angle_mdeg),
        "illumination_fraction": int(effective_fraction),
        "occlusion_fraction": int(occlusion_fraction),
        "deterministic_fingerprint": "",
        "extensions": {
            "source": ILLUMINATION_GEOMETRY_ENGINE_VERSION,
            "derived_only": True,
            "compactable": True,
            "artifact_class": "DERIVED_VIEW",
            "viewer_ref_hash": viewer_hash,
            "cos_phase_permille": int(cos_phase_permille),
            "base_illumination_fraction": int(illumination_fraction),
            "emitter_ref": dict(emitter_ref),
            "receiver_ref": dict(receiver_ref),
            "emitter_kind": str(emitter.get("kind", "")).strip(),
            "receiver_kind": str(receiver.get("kind", "")).strip(),
            "receiver_radius_km": int(_as_int(_as_map(receiver.get("radius")).get("value", 0), 0)),
            "receiver_albedo_proxy_permille": int(_as_int(_as_map(receiver.get("albedo_proxy")).get("value", 0), 0)),
            "luminosity_proxy_value": int(_as_int(_as_map(emitter.get("luminosity_proxy")).get("value", 0), 0)),
            "occlusion_policy_id": str(occlusion_policy_id or DEFAULT_OCCLUSION_POLICY_ID).strip() or DEFAULT_OCCLUSION_POLICY_ID,
            "eclipse_ready": True,
            "registry_hashes": {
                "emitter_kind_registry_hash": emitter_kind_registry_hash(),
                "receiver_kind_registry_hash": receiver_kind_registry_hash(),
                "occlusion_policy_registry_hash": occlusion_policy_registry_hash(),
            },
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_view_artifact_from_directions(
    *,
    tick: int,
    viewer_ref: Mapping[str, object] | None,
    emitter_object_id: str,
    receiver_object_id: str,
    emitter_direction: Mapping[str, object] | None,
    receiver_direction: Mapping[str, object] | None,
    luminosity_proxy_value: int,
    receiver_radius_km: int,
    receiver_albedo_proxy_permille: int,
    receiver_kind: str = "receiver.moon",
    occlusion_policy_id: str = DEFAULT_OCCLUSION_POLICY_ID,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    emitter_id = "emitter.{}".format(str(emitter_object_id or "").strip() or "star")
    receiver_id = "receiver.{}".format(str(receiver_object_id or "").strip() or "body")
    emitter_row = build_emitter_descriptor(
        emitter_id=emitter_id,
        object_id=str(emitter_object_id or "").strip() or "object.star.stub",
        luminosity_proxy_value=int(luminosity_proxy_value),
        extensions=_as_map(extensions).get("emitter_extensions"),
    )
    receiver_row = build_receiver_descriptor(
        receiver_id=receiver_id,
        object_id=str(receiver_object_id or "").strip() or "object.receiver.stub",
        radius_km=int(receiver_radius_km),
        albedo_proxy_permille=int(receiver_albedo_proxy_permille),
        kind=str(receiver_kind or "receiver.moon").strip() or "receiver.moon",
        extensions=_as_map(extensions).get("receiver_extensions"),
    )
    emitter_ref = build_direction_position_ref(
        object_id=str(emitter_row.get("object_id", "")).strip(),
        direction=emitter_direction,
        distance_units=DEFAULT_EMITTER_DISTANCE_UNITS,
        extensions={"role": "emitter", **_as_map(_as_map(extensions).get("emitter_position_extensions"))},
    )
    receiver_ref = build_direction_position_ref(
        object_id=str(receiver_row.get("object_id", "")).strip(),
        direction=receiver_direction,
        distance_units=DEFAULT_RECEIVER_DISTANCE_UNITS,
        extensions={"role": "receiver", **_as_map(_as_map(extensions).get("receiver_position_extensions"))},
    )
    return build_illumination_view_artifact(
        tick=int(tick),
        viewer_ref=viewer_ref,
        emitter_row=emitter_row,
        receiver_row=receiver_row,
        emitter_position_ref=emitter_ref,
        receiver_position_ref=receiver_ref,
        occlusion_policy_id=str(occlusion_policy_id or DEFAULT_OCCLUSION_POLICY_ID).strip() or DEFAULT_OCCLUSION_POLICY_ID,
    )


__all__ = [
    "DEFAULT_OCCLUSION_POLICY_ID",
    "EMITTER_KIND_REGISTRY_REL",
    "ILLUMINATION_GEOMETRY_ENGINE_VERSION",
    "OCCLUSION_POLICY_REGISTRY_REL",
    "RECEIVER_KIND_REGISTRY_REL",
    "build_direction_position_ref",
    "build_emitter_descriptor",
    "build_illumination_view_artifact",
    "build_receiver_descriptor",
    "build_view_artifact_from_directions",
    "cos_permille_from_angle_mdeg",
    "emitter_kind_registry_hash",
    "emitter_kind_rows",
    "occlusion_policy_registry_hash",
    "occlusion_policy_rows",
    "receiver_kind_registry_hash",
    "receiver_kind_rows",
    "sin_permille_from_angle_mdeg",
]

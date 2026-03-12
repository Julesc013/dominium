"""Deterministic GAL-1 compact-object stub generation helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.frame.frame_engine import build_position_ref
from src.geo.index.geo_index_engine import _coerce_cell_key
from src.geo.index.object_id_engine import geo_object_id
from src.worldgen.galaxy.galaxy_proxy_field_engine import evaluate_galaxy_cell_proxy
from src.worldgen.mw import DEFAULT_GALAXY_PRIORS_ID, MW_GALACTIC_FRAME_ID, PARSEC_MM


GALAXY_OBJECT_STUB_GENERATOR_VERSION = "GAL1-3"
MAX_GALAXY_OBJECT_STUBS_PER_CELL = 1
RNG_WORLDGEN_GALAXY_OBJECTS = "rng.worldgen.galaxy_objects"
BLACK_HOLE_LOCAL_SUBKEY = "galactic_center:black_hole"
SPARSE_OBJECT_POLICY_ID = "galaxy_object_stub.sparse_v1"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _is_origin_cell(geo_cell_key: Mapping[str, object]) -> bool:
    key_row = _coerce_cell_key(geo_cell_key) or {}
    index_tuple = [int(_as_int(item, 0)) for item in list(key_row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return index_tuple[:3] == [0, 0, 0]


def _hash_int(seed: str, salt: str) -> int:
    return int(canonical_sha256({"seed": str(seed), "salt": str(salt)})[:16], 16)


def _quantity(unit: str, value: int) -> dict:
    return {"unit": str(unit or "").strip(), "value": int(max(0, _as_int(value, 0)))}


def _local_position_mm(position_pc: Sequence[int]) -> List[int]:
    return [int(_as_int(value, 0)) * int(PARSEC_MM) for value in list(position_pc or [0, 0, 0])]


def _offset_vector_pc(stream_seed: str, *, max_abs_pc: int) -> List[int]:
    span = int(max(0, _as_int(max_abs_pc, 0)))
    if span <= 0:
        return [0, 0, 0]
    width = (span * 2) + 1
    return [
        int((_hash_int(stream_seed, "offset.x") % width) - span),
        int((_hash_int(stream_seed, "offset.y") % width) - span),
        int((_hash_int(stream_seed, "offset.z") % width) - span),
    ]


def build_galaxy_object_stub_row(
    *,
    object_id: str,
    kind: str,
    position_ref: Mapping[str, object],
    mass_proxy: Mapping[str, object] | None = None,
    radius_proxy: Mapping[str, object] | None = None,
    hazard_strength_proxy: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "object_id": str(object_id or "").strip(),
        "kind": str(kind or "").strip(),
        "position_ref": _as_map(position_ref),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if _as_map(mass_proxy):
        payload["mass_proxy"] = _as_map(mass_proxy)
    if _as_map(radius_proxy):
        payload["radius_proxy"] = _as_map(radius_proxy)
    if _as_map(hazard_strength_proxy):
        payload["hazard_strength_proxy"] = _as_map(hazard_strength_proxy)
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_galaxy_object_stub_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        row = _as_map(raw)
        object_id = str(row.get("object_id", "")).strip()
        if not object_id:
            continue
        out[object_id] = build_galaxy_object_stub_row(
            object_id=object_id,
            kind=str(row.get("kind", "")).strip(),
            position_ref=_as_map(row.get("position_ref")),
            mass_proxy=_as_map(row.get("mass_proxy")),
            radius_proxy=_as_map(row.get("radius_proxy")),
            hazard_strength_proxy=_as_map(row.get("hazard_strength_proxy")),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def galaxy_object_stub_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_galaxy_object_stub_rows(rows))


def _spawn_identity(
    *,
    universe_identity_hash: str,
    geo_cell_key: Mapping[str, object],
    object_kind_id: str,
    local_subkey: str,
) -> tuple[dict, dict]:
    payload = geo_object_id(
        universe_identity_hash=str(universe_identity_hash or "").strip(),
        cell_key=geo_cell_key,
        object_kind_id=str(object_kind_id or "").strip(),
        local_subkey=str(local_subkey or "").strip(),
    )
    if str(payload.get("result", "")).strip() != "complete":
        return {}, {}
    identity = _as_map(payload.get("object_identity"))
    object_id = str(payload.get("object_id_hash", "")).strip()
    return identity, {
        "object_id_hash": object_id,
        "object_kind_id": str(identity.get("object_kind_id", "")).strip(),
        "local_subkey": str(identity.get("local_subkey", "")).strip(),
        "geo_cell_key": _as_map(identity.get("geo_cell_key")),
    }


def _sparse_stub_descriptor(
    *,
    geo_cell_key: Mapping[str, object],
    galaxy_proxy: Mapping[str, object],
    stream_seed: str,
    cell_size_pc: int,
) -> dict:
    if _is_origin_cell(geo_cell_key):
        return {}
    proxy_row = _as_map(galaxy_proxy)
    proxy_ext = _as_map(proxy_row.get("extensions"))
    radius_pc = int(max(0, _as_int(proxy_ext.get("galactocentric_radius_pc", 0), 0)))
    density = int(max(0, _as_int(proxy_row.get("stellar_density_proxy_value", 0), 0)))
    metallicity = int(max(0, _as_int(proxy_row.get("metallicity_proxy_value", 0), 0)))
    radiation = int(max(0, _as_int(proxy_row.get("radiation_background_proxy_value", 0), 0)))
    region_id = str(proxy_row.get("galactic_region_id", "")).strip()
    if radius_pc <= 0 or radius_pc > 6000:
        return {}
    if region_id not in {"region.bulge", "region.inner_disk"}:
        return {}
    if density < 900 or metallicity < 900:
        return {}
    chance_permille = min(220, max(60, ((density - 850) + (metallicity - 850)) // 2))
    if (_hash_int(stream_seed, "sparse.draw") % 1000) >= chance_permille:
        return {}
    remnant_bias_permille = min(760, max(280, 280 + ((radiation - 700) // 2)))
    is_remnant = (_hash_int(stream_seed, "sparse.kind") % 1000) < remnant_bias_permille
    sparse_kind = "kind.supernova_remnant_stub" if is_remnant else "kind.nebula_stub"
    return {
        "kind": sparse_kind,
        "local_subkey": "sparse:{}".format("remnant:0" if is_remnant else "nebula:0"),
        "local_offset_pc": _offset_vector_pc(
            stream_seed,
            max_abs_pc=max(1, min(max(1, int(cell_size_pc)) // 4, 3)),
        ),
        "radius_proxy": _quantity("parsec_stub", 8 if is_remnant else 24),
        "hazard_strength_proxy": _quantity("permille", 420 if is_remnant else 260),
        "mass_proxy": (_quantity("stellar_mass_stub", 12) if is_remnant else {}),
    }


def generate_galaxy_object_stub_payload(
    *,
    universe_identity_hash: str,
    geo_cell_key: Mapping[str, object],
    galaxy_priors_row: Mapping[str, object],
    galaxy_priors_id: str = DEFAULT_GALAXY_PRIORS_ID,
    stream_seed: str = "",
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key) or {}
    priors_row = _as_map(galaxy_priors_row)
    if not cell_key or not priors_row:
        payload = {
            "result": "refused",
            "artifact_rows": [],
            "generated_object_rows": [],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    proxy_row = evaluate_galaxy_cell_proxy(
        geo_cell_key=cell_key,
        galaxy_priors_row=priors_row,
        galaxy_priors_id=str(galaxy_priors_id or "").strip() or DEFAULT_GALAXY_PRIORS_ID,
    )
    proxy_ext = _as_map(proxy_row.get("extensions"))
    center_pc = [int(_as_int(value, 0)) for value in list(proxy_ext.get("galactocentric_position_pc") or [0, 0, 0])]
    cell_size_pc = int(max(1, _as_int(priors_row.get("cell_size_pc", 10), 10)))
    stream_name = str(RNG_WORLDGEN_GALAXY_OBJECTS)
    stream_seed_hash = canonical_sha256({"stream_name": stream_name, "stream_seed": str(stream_seed or "").strip()})

    artifact_rows: List[dict] = []
    generated_object_rows: List[dict] = []

    if _is_origin_cell(cell_key):
        identity, spawned = _spawn_identity(
            universe_identity_hash=universe_identity_hash,
            geo_cell_key=cell_key,
            object_kind_id="kind.black_hole_stub",
            local_subkey=BLACK_HOLE_LOCAL_SUBKEY,
        )
        object_id = str(identity.get("object_id_hash", "")).strip() or str(spawned.get("object_id_hash", "")).strip()
        if object_id:
            artifact_rows.append(
                build_galaxy_object_stub_row(
                    object_id=object_id,
                    kind="kind.black_hole_stub",
                    position_ref=build_position_ref(
                        object_id=object_id,
                        frame_id=MW_GALACTIC_FRAME_ID,
                        local_position=[0, 0, 0],
                        extensions={"chart_id": "chart.galaxy", "source": GALAXY_OBJECT_STUB_GENERATOR_VERSION},
                    ),
                    mass_proxy=_quantity("solar_mass_stub", 4_300_000),
                    radius_proxy=_quantity("parsec_stub", 1),
                    hazard_strength_proxy=_quantity("permille", 1000),
                    extensions={
                        "source": GALAXY_OBJECT_STUB_GENERATOR_VERSION,
                        "policy_id": SPARSE_OBJECT_POLICY_ID,
                        "geo_cell_key": dict(cell_key),
                        "local_subkey": BLACK_HOLE_LOCAL_SUBKEY,
                        "galaxy_priors_id": str(galaxy_priors_id or "").strip() or DEFAULT_GALAXY_PRIORS_ID,
                        "galactic_region_id": str(proxy_row.get("galactic_region_id", "")).strip(),
                        "hazard_effects": {
                            "radiation_bump_permille": 640,
                            "gravity_well_bump_permille": 1000,
                        },
                        "stream_name": stream_name,
                        "stream_seed_hash": stream_seed_hash,
                    },
                )
            )
            generated_object_rows.append(spawned)

    sparse_descriptor = _sparse_stub_descriptor(
        geo_cell_key=cell_key,
        galaxy_proxy=proxy_row,
        stream_seed=str(stream_seed or "").strip(),
        cell_size_pc=cell_size_pc,
    )
    sparse_kind = str(sparse_descriptor.get("kind", "")).strip()
    if sparse_kind and len(artifact_rows) < MAX_GALAXY_OBJECT_STUBS_PER_CELL:
        local_subkey = str(sparse_descriptor.get("local_subkey", "")).strip()
        identity, spawned = _spawn_identity(
            universe_identity_hash=universe_identity_hash,
            geo_cell_key=cell_key,
            object_kind_id=sparse_kind,
            local_subkey=local_subkey,
        )
        object_id = str(identity.get("object_id_hash", "")).strip() or str(spawned.get("object_id_hash", "")).strip()
        if object_id:
            offset_pc = [int(_as_int(value, 0)) for value in list(sparse_descriptor.get("local_offset_pc") or [0, 0, 0])]
            artifact_rows.append(
                build_galaxy_object_stub_row(
                    object_id=object_id,
                    kind=sparse_kind,
                    position_ref=build_position_ref(
                        object_id=object_id,
                        frame_id=MW_GALACTIC_FRAME_ID,
                        local_position=_local_position_mm(
                            [
                                int(center_pc[0]) + int(offset_pc[0]),
                                int(center_pc[1]) + int(offset_pc[1]),
                                int(center_pc[2]) + int(offset_pc[2]),
                            ]
                        ),
                        extensions={"chart_id": "chart.galaxy", "source": GALAXY_OBJECT_STUB_GENERATOR_VERSION},
                    ),
                    mass_proxy=_as_map(sparse_descriptor.get("mass_proxy")),
                    radius_proxy=_as_map(sparse_descriptor.get("radius_proxy")),
                    hazard_strength_proxy=_as_map(sparse_descriptor.get("hazard_strength_proxy")),
                    extensions={
                        "source": GALAXY_OBJECT_STUB_GENERATOR_VERSION,
                        "policy_id": SPARSE_OBJECT_POLICY_ID,
                        "geo_cell_key": dict(cell_key),
                        "local_subkey": local_subkey,
                        "local_offset_pc": list(offset_pc),
                        "galaxy_priors_id": str(galaxy_priors_id or "").strip() or DEFAULT_GALAXY_PRIORS_ID,
                        "galactic_region_id": str(proxy_row.get("galactic_region_id", "")).strip(),
                        "proxy_snapshot": {
                            "stellar_density_proxy_value": int(_as_int(proxy_row.get("stellar_density_proxy_value", 0), 0)),
                            "metallicity_proxy_value": int(_as_int(proxy_row.get("metallicity_proxy_value", 0), 0)),
                            "radiation_background_proxy_value": int(_as_int(proxy_row.get("radiation_background_proxy_value", 0), 0)),
                        },
                        "hazard_effects": {
                            "radiation_bump_permille": (180 if sparse_kind == "kind.supernova_remnant_stub" else 90),
                            "gravity_well_bump_permille": (60 if sparse_kind == "kind.supernova_remnant_stub" else 20),
                        },
                        "stream_name": stream_name,
                        "stream_seed_hash": stream_seed_hash,
                    },
                )
            )
            generated_object_rows.append(spawned)

    artifact_rows = normalize_galaxy_object_stub_rows(artifact_rows)[:MAX_GALAXY_OBJECT_STUBS_PER_CELL]
    object_id_set = {str(row.get("object_id", "")).strip() for row in artifact_rows}
    generated_object_rows = [
        dict(row)
        for row in sorted(
            (dict(row) for row in generated_object_rows if str(_as_map(row).get("object_id_hash", "")).strip() in object_id_set),
            key=lambda item: (
                str(item.get("object_kind_id", "")),
                str(item.get("local_subkey", "")),
                str(item.get("object_id_hash", "")),
            ),
        )
    ]
    payload = {
        "result": "complete",
        "artifact_rows": artifact_rows,
        "generated_object_rows": generated_object_rows,
        "max_objects_per_cell": int(MAX_GALAXY_OBJECT_STUBS_PER_CELL),
        "geo_cell_key": dict(cell_key),
        "proxy_snapshot": {
            "galactic_region_id": str(proxy_row.get("galactic_region_id", "")).strip(),
            "stellar_density_proxy_value": int(_as_int(proxy_row.get("stellar_density_proxy_value", 0), 0)),
            "metallicity_proxy_value": int(_as_int(proxy_row.get("metallicity_proxy_value", 0), 0)),
            "radiation_background_proxy_value": int(_as_int(proxy_row.get("radiation_background_proxy_value", 0), 0)),
        },
        "stream_name": stream_name,
        "stream_seed_hash": stream_seed_hash,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "BLACK_HOLE_LOCAL_SUBKEY",
    "GALAXY_OBJECT_STUB_GENERATOR_VERSION",
    "MAX_GALAXY_OBJECT_STUBS_PER_CELL",
    "RNG_WORLDGEN_GALAXY_OBJECTS",
    "build_galaxy_object_stub_row",
    "galaxy_object_stub_hash_chain",
    "generate_galaxy_object_stub_payload",
    "normalize_galaxy_object_stub_rows",
]

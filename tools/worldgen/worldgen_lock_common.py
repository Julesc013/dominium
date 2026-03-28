"""Shared helpers for the Omega worldgen lock baseline."""

from __future__ import annotations

import json
import os
from typing import Iterable, List, Mapping, Sequence

from geo import build_worldgen_request, generate_worldgen_result, worldgen_cache_clear
from worldgen.galaxy import galaxy_object_stub_hash_chain
from worldgen.mw import (
    SOL_ANCHOR_CELL_INDEX_TUPLE,
    build_planet_surface_cell_key,
    normalize_star_system_seed_rows,
    planet_basic_artifact_hash_chain,
    planet_orbit_artifact_hash_chain,
    resolve_sol_anchor_cell_key,
    sol_anchor_object_ids,
    star_artifact_hash_chain,
    star_system_artifact_hash_chain,
    surface_tile_artifact_hash_chain,
    system_l2_summary_hash_chain,
)
from tools.mvp.runtime_bundle import (
    build_default_universe_identity,
    build_pack_lock_payload,
    build_profile_bundle_payload,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


WORLDGEN_LOCK_ID = "worldgen_lock.v0_0_0"
WORLDGEN_LOCK_VERSION = 0
WORLDGEN_LOCK_BASELINE_SCHEMA_ID = "dominium.schema.governance" + ".worldgen_lock_baseline"
WORLDGEN_LOCK_REGISTRY_REL = os.path.join("data", "registries", "worldgen_lock_registry.json")
WORLDGEN_BASELINE_SEED_REL = os.path.join("data", "baselines", "worldgen", "baseline_seed.txt")
WORLDGEN_BASELINE_SNAPSHOT_REL = os.path.join("data", "baselines", "worldgen", "baseline_worldgen_snapshot.json")
WORLDGEN_VERIFY_JSON_REL = os.path.join("data", "audit", "worldgen_lock_verify.json")
WORLDGEN_VERIFY_DOC_REL = os.path.join("docs", "audit", "WORLDGEN_LOCK_VERIFY.md")

WORLD_CELL_SAMPLE_INDEX_TUPLES = (
    [0, 0, 0],
    [400, 0, 0],
    [800, 0, 0],
    [4200, 0, 0],
)
SURFACE_TILE_SAMPLE_ORDER = (
    {"chart_id": "chart.atlas.north", "index_tuple": [0, 0]},
    {"chart_id": "chart.atlas.north", "index_tuple": [8, 0]},
    {"chart_id": "chart.atlas.north", "index_tuple": [16, 2]},
    {"chart_id": "chart.atlas.north", "index_tuple": [24, 4]},
    {"chart_id": "chart.atlas.south", "index_tuple": [0, 0]},
    {"chart_id": "chart.atlas.south", "index_tuple": [8, 0]},
    {"chart_id": "chart.atlas.south", "index_tuple": [16, 2]},
    {"chart_id": "chart.atlas.south", "index_tuple": [24, 4]},
)
GALAXY_NODE_ID_COUNT = 12
EARTH_TILE_HASH_COUNT = 8
ELEVATION_HASH_COUNT = 8
CLIMATE_PROXY_HASH_COUNT = 8


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, str(rel_path).replace("/", os.sep))))


def _ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return path


def _write_text(path: str, text: str) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))
    return path


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _diff_values(expected: object, observed: object, *, path: str = "$", out: List[str] | None = None, limit: int = 64) -> List[str]:
    rows = out if out is not None else []
    if len(rows) >= int(limit):
        return rows
    if isinstance(expected, Mapping) and isinstance(observed, Mapping):
        keys = sorted(set(list(expected.keys()) + list(observed.keys())))
        for key in keys:
            token = str(key)
            if key not in expected:
                rows.append("{}.{}: unexpected key".format(path, token))
            elif key not in observed:
                rows.append("{}.{}: missing key".format(path, token))
            else:
                _diff_values(expected.get(key), observed.get(key), path="{}.{}".format(path, token), out=rows, limit=limit)
            if len(rows) >= int(limit):
                break
        return rows
    if isinstance(expected, list) and isinstance(observed, list):
        if len(expected) != len(observed):
            rows.append("{}: list length {} != {}".format(path, len(expected), len(observed)))
            return rows
        for index, (left, right) in enumerate(zip(expected, observed)):
            _diff_values(left, right, path="{}[{}]".format(path, index), out=rows, limit=limit)
            if len(rows) >= int(limit):
                break
        return rows
    if expected != observed:
        rows.append(path)
    return rows


def load_worldgen_lock_registry(repo_root: str) -> dict:
    return _load_json(_repo_abs(repo_root, WORLDGEN_LOCK_REGISTRY_REL))


def load_worldgen_lock_snapshot(repo_root: str, snapshot_path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    path = os.path.normpath(os.path.abspath(snapshot_path)) if str(snapshot_path or "").strip() else _repo_abs(repo_root_abs, WORLDGEN_BASELINE_SNAPSHOT_REL)
    return _load_json(path)


def read_worldgen_baseline_seed(repo_root: str, seed_text: str = "") -> str:
    explicit = str(seed_text or "").strip()
    if explicit:
        return explicit
    seed_path = _repo_abs(repo_root, WORLDGEN_BASELINE_SEED_REL)
    try:
        token = open(seed_path, "r", encoding="utf-8").read().strip()
    except OSError:
        token = ""
    return token or "DOMINIUM_MVP_BASELINE_SEED_0"


def seed_text_hash(seed_text: str) -> str:
    return canonical_sha256({"seed_text": str(seed_text)})


def snapshot_record_hash(record: Mapping[str, object]) -> str:
    payload = dict(record or {})
    payload["deterministic_fingerprint"] = ""
    return canonical_sha256(payload)


def registry_record_hash(record: Mapping[str, object]) -> str:
    payload = dict(record or {})
    payload["deterministic_fingerprint"] = ""
    return canonical_sha256(payload)


def build_locked_identity_context(repo_root: str, seed_text: str) -> dict:
    profile_bundle = build_profile_bundle_payload(repo_root=repo_root)
    pack_lock = build_pack_lock_payload(repo_root=repo_root, profile_bundle_payload=profile_bundle)
    universe_identity = build_default_universe_identity(
        repo_root=repo_root,
        seed=str(seed_text),
        authority_mode="dev",
        pack_lock_payload=pack_lock,
        profile_bundle_payload=profile_bundle,
    )
    return {
        "profile_bundle": dict(profile_bundle),
        "pack_lock": dict(pack_lock),
        "universe_identity": dict(universe_identity),
    }


def world_cell_key(index_tuple: Sequence[int]) -> dict:
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.r3_infinite",
        "chart_id": "chart.global.r3",
        "index_tuple": [int(item) for item in list(index_tuple or [])],
        "refinement_level": 0,
        "extensions": {},
    }


def _worldgen_request(*, request_id: str, geo_cell_key: Mapping[str, object], refinement_level: int) -> dict:
    return build_worldgen_request(
        request_id=str(request_id),
        geo_cell_key=dict(geo_cell_key),
        refinement_level=int(refinement_level),
        reason="query",
        extensions={"source": "omega.worldgen_lock"},
    )


def _run_worldgen(
    *,
    universe_identity: Mapping[str, object],
    request_id: str,
    geo_cell_key: Mapping[str, object],
    refinement_level: int,
    current_tick: int = 0,
) -> dict:
    return generate_worldgen_result(
        universe_identity=dict(universe_identity or {}),
        worldgen_request=_worldgen_request(
            request_id=request_id,
            geo_cell_key=geo_cell_key,
            refinement_level=refinement_level,
        ),
        current_tick=int(current_tick),
        cache_enabled=False,
    )


def _elevation_hash(result: Mapping[str, object]) -> str:
    surface_rows = [dict(row) for row in _as_list(_as_map(result).get("generated_surface_tile_artifact_rows")) if isinstance(row, Mapping)]
    tile_row = dict(surface_rows[0]) if surface_rows else {}
    payload = {
        "tile_object_id": str(tile_row.get("tile_object_id", "")).strip(),
        "elevation_params_ref": _as_map(tile_row.get("elevation_params_ref")),
        "geometry_initializations": [dict(row) for row in _as_list(_as_map(result).get("geometry_initializations")) if isinstance(row, Mapping)],
    }
    return canonical_sha256(payload)


def _climate_proxy_hash(result: Mapping[str, object]) -> str:
    summary = _as_map(_as_map(result).get("surface_summary"))
    payload = {
        "tile_object_id": str(summary.get("tile_object_id", "")).strip(),
        "temperature_value": int(summary.get("temperature_value", 0) or 0),
        "daylight_value": int(summary.get("daylight_value", 0) or 0),
        "pressure_value": int(summary.get("pressure_value", 0) or 0),
        "insolation_value": int(summary.get("insolation_value", 0) or 0),
        "field_initializations": [dict(row) for row in _as_list(_as_map(result).get("field_initializations")) if isinstance(row, Mapping)],
    }
    return canonical_sha256(payload)


def _ordered_surface_samples() -> List[dict]:
    return [
        {
            "chart_id": str(row.get("chart_id", "")).strip(),
            "index_tuple": [int(item) for item in list(row.get("index_tuple") or [])],
        }
        for row in SURFACE_TILE_SAMPLE_ORDER
    ]


def build_worldgen_lock_snapshot(repo_root: str, seed_text: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    registry_payload = load_worldgen_lock_registry(repo_root_abs)
    registry_record = _as_map(registry_payload.get("record"))
    resolved_seed = read_worldgen_baseline_seed(repo_root_abs, seed_text=seed_text)

    worldgen_cache_clear()
    context = build_locked_identity_context(repo_root_abs, resolved_seed)
    universe_identity = _as_map(context.get("universe_identity"))
    anchor_cell_key = resolve_sol_anchor_cell_key(None)

    l0_rows: List[dict] = []
    l1_rows: List[dict] = []
    flattened_galaxy_node_ids: List[str] = []

    for cell_index, index_tuple in enumerate(WORLD_CELL_SAMPLE_INDEX_TUPLES):
        cell_key = world_cell_key(index_tuple)
        l0_result = _run_worldgen(
            universe_identity=universe_identity,
            request_id="omega.worldgen_lock.l0.{}".format(cell_index),
            geo_cell_key=cell_key,
            refinement_level=0,
        )
        l1_result = _run_worldgen(
            universe_identity=universe_identity,
            request_id="omega.worldgen_lock.l1.{}".format(cell_index),
            geo_cell_key=cell_key,
            refinement_level=1,
        )
        l0_rows.append(
            {
                "index_tuple": [int(item) for item in list(index_tuple)],
                "mw_cell_summary_hash": canonical_sha256(_as_map(l0_result.get("mw_cell_summary"))),
                "system_seed_hash": canonical_sha256(normalize_star_system_seed_rows(l0_result.get("generated_system_seed_rows"))),
                "worldgen_result_hash": str(_as_map(l0_result.get("worldgen_result")).get("deterministic_fingerprint", "")).strip(),
            }
        )
        l1_star_rows = [dict(row) for row in _as_list(l1_result.get("generated_star_system_artifact_rows")) if isinstance(row, Mapping)]
        flattened_galaxy_node_ids.extend(str(row.get("object_id", "")).strip() for row in l1_star_rows if str(row.get("object_id", "")).strip())
        l1_rows.append(
            {
                "index_tuple": [int(item) for item in list(index_tuple)],
                "star_system_hash": star_system_artifact_hash_chain(l1_star_rows),
                "galaxy_object_stub_hash": galaxy_object_stub_hash_chain(l1_result.get("generated_galaxy_object_stub_artifact_rows")),
                "worldgen_result_hash": str(_as_map(l1_result.get("worldgen_result")).get("deterministic_fingerprint", "")).strip(),
            }
        )

    sol_ids = sol_anchor_object_ids(universe_identity_hash=str(universe_identity.get("identity_hash", "")).strip())
    earth_object_id = str(sol_ids.get("sol.planet.earth", "")).strip()
    l2_result = _run_worldgen(
        universe_identity=universe_identity,
        request_id="omega.worldgen_lock.l2.anchor",
        geo_cell_key=anchor_cell_key,
        refinement_level=2,
    )

    l3_rows: List[dict] = []
    earth_tile_hashes: List[str] = []
    elevation_hashes: List[str] = []
    climate_proxy_hashes: List[str] = []
    for sample_index, sample in enumerate(_ordered_surface_samples()):
        surface_cell_key = build_planet_surface_cell_key(
            planet_object_id=earth_object_id,
            ancestor_world_cell_key=anchor_cell_key,
            chart_id=str(sample.get("chart_id", "")).strip(),
            index_tuple=list(sample.get("index_tuple") or []),
            refinement_level=1,
            planet_tags=["planet.earth", "sol.planet.earth"],
        )
        l3_result = _run_worldgen(
            universe_identity=universe_identity,
            request_id="omega.worldgen_lock.l3.{}".format(sample_index),
            geo_cell_key=surface_cell_key,
            refinement_level=3,
        )
        tile_hash = surface_tile_artifact_hash_chain(l3_result.get("generated_surface_tile_artifact_rows"))
        elevation_hash = _elevation_hash(l3_result)
        climate_hash = _climate_proxy_hash(l3_result)
        earth_tile_hashes.append(tile_hash)
        elevation_hashes.append(elevation_hash)
        climate_proxy_hashes.append(climate_hash)
        l3_rows.append(
            {
                "chart_id": str(sample.get("chart_id", "")).strip(),
                "index_tuple": [int(item) for item in list(sample.get("index_tuple") or [])],
                "surface_tile_hash": tile_hash,
                "elevation_hash": elevation_hash,
                "climate_proxy_hash": climate_hash,
                "worldgen_result_hash": str(_as_map(l3_result.get("worldgen_result")).get("deterministic_fingerprint", "")).strip(),
            }
        )

    record = {
        "worldgen_lock_id": str(registry_record.get("worldgen_lock_id", "")).strip() or WORLDGEN_LOCK_ID,
        "worldgen_lock_version": int(registry_record.get("worldgen_lock_version", WORLDGEN_LOCK_VERSION) or WORLDGEN_LOCK_VERSION),
        "stability_class": str(registry_record.get("stability_class", "stable")).strip() or "stable",
        "baseline_seed": resolved_seed,
        "baseline_seed_hash": seed_text_hash(resolved_seed),
        "seed_hash_algorithm": str(registry_record.get("seed_hash_algorithm", "")).strip(),
        "generator_version_id": str(universe_identity.get("generator_version_id", "")).strip(),
        "realism_profile_id": str(universe_identity.get("realism_profile_id", "")).strip(),
        "universe_identity_hash": str(universe_identity.get("identity_hash", "")).strip(),
        "profile_bundle_hash": str(_as_map(context.get("profile_bundle")).get("profile_bundle_hash", "")).strip(),
        "pack_lock_hash": str(_as_map(context.get("pack_lock")).get("pack_lock_hash", "")).strip(),
        "rng_streams": [str(item).strip() for item in _as_list(registry_record.get("rng_streams")) if str(item).strip()],
        "refinement_stages": [str(item).strip() for item in _as_list(registry_record.get("refinement_stages")) if str(item).strip()],
        "sample_windows": {
            "galaxy_cell_index_tuples": [[int(item) for item in list(row)] for row in WORLD_CELL_SAMPLE_INDEX_TUPLES],
            "surface_tiles": _ordered_surface_samples(),
            "galaxy_node_id_count": GALAXY_NODE_ID_COUNT,
            "earth_tile_hash_count": EARTH_TILE_HASH_COUNT,
            "elevation_hash_count": ELEVATION_HASH_COUNT,
            "climate_proxy_hash_count": CLIMATE_PROXY_HASH_COUNT,
        },
        "galaxy_node_ids": flattened_galaxy_node_ids[:GALAXY_NODE_ID_COUNT],
        "sol_system_id": str(sol_ids.get("sol.system", "")).strip(),
        "earth_planet_id": earth_object_id,
        "earth_tile_hashes": earth_tile_hashes[:EARTH_TILE_HASH_COUNT],
        "elevation_field_hashes": elevation_hashes[:ELEVATION_HASH_COUNT],
        "initial_climate_proxy_hashes": climate_proxy_hashes[:CLIMATE_PROXY_HASH_COUNT],
        "refinement_stage_hashes": {
            "l0_galaxy_coarse_structure": canonical_sha256(l0_rows),
            "l1_star_distribution": canonical_sha256(l1_rows),
            "l2_sol_system_derivation": canonical_sha256(
                {
                    "sol_anchor_ids": dict((str(key), str(value)) for key, value in sorted(sol_ids.items())),
                    "star_hash": star_artifact_hash_chain(l2_result.get("generated_star_artifact_rows")),
                    "planet_orbit_hash": planet_orbit_artifact_hash_chain(l2_result.get("generated_planet_orbit_artifact_rows")),
                    "planet_basic_hash": planet_basic_artifact_hash_chain(l2_result.get("generated_planet_basic_artifact_rows")),
                    "system_summary_hash": system_l2_summary_hash_chain(l2_result.get("generated_system_l2_summary_rows")),
                }
            ),
            "l3_earth_terrain_projection": canonical_sha256(l3_rows),
        },
        "stage_samples": {
            "l0": l0_rows,
            "l1": l1_rows,
            "l2": {
                "anchor_cell_index_tuple": [int(item) for item in list(SOL_ANCHOR_CELL_INDEX_TUPLE)],
                "star_hash": star_artifact_hash_chain(l2_result.get("generated_star_artifact_rows")),
                "planet_orbit_hash": planet_orbit_artifact_hash_chain(l2_result.get("generated_planet_orbit_artifact_rows")),
                "planet_basic_hash": planet_basic_artifact_hash_chain(l2_result.get("generated_planet_basic_artifact_rows")),
                "system_summary_hash": system_l2_summary_hash_chain(l2_result.get("generated_system_l2_summary_rows")),
                "sol_anchor_ids_hash": canonical_sha256(dict((str(key), str(value)) for key, value in sorted(sol_ids.items()))),
                "worldgen_result_hash": str(_as_map(l2_result.get("worldgen_result")).get("deterministic_fingerprint", "")).strip(),
            },
            "l3": l3_rows,
        },
        "deterministic_fingerprint": "",
    }
    record["deterministic_fingerprint"] = snapshot_record_hash(record)
    return {
        "schema_id": WORLDGEN_LOCK_BASELINE_SCHEMA_ID,
        "schema_version": "1.0.0",
        "record": record,
    }


def write_worldgen_lock_snapshot(repo_root: str, payload: Mapping[str, object], output_path: str = "") -> str:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    target = os.path.normpath(os.path.abspath(output_path)) if str(output_path or "").strip() else _repo_abs(repo_root_abs, WORLDGEN_BASELINE_SNAPSHOT_REL)
    return _write_canonical_json(target, payload)


def write_worldgen_seed_file(repo_root: str, seed_text: str) -> str:
    return _write_text(_repo_abs(repo_root, WORLDGEN_BASELINE_SEED_REL), "{}\n".format(str(seed_text)))


def verify_worldgen_lock(repo_root: str, seed_text: str = "", snapshot_path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    expected_snapshot = load_worldgen_lock_snapshot(repo_root_abs, snapshot_path=snapshot_path)
    resolved_seed = read_worldgen_baseline_seed(repo_root_abs, seed_text=seed_text)
    observed_snapshot = build_worldgen_lock_snapshot(repo_root_abs, seed_text=resolved_seed)
    expected_record = _as_map(expected_snapshot.get("record"))
    observed_record = _as_map(observed_snapshot.get("record"))
    mismatched_fields = _diff_values(expected_snapshot, observed_snapshot)
    matches = not bool(mismatched_fields)
    report = {
        "result": "complete" if matches else "mismatch",
        "baseline_seed": resolved_seed,
        "expected_snapshot_rel": str(snapshot_path or WORLDGEN_BASELINE_SNAPSHOT_REL).replace("\\", "/"),
        "expected_snapshot_fingerprint": str(expected_record.get("deterministic_fingerprint", "")).strip(),
        "observed_snapshot_fingerprint": str(observed_record.get("deterministic_fingerprint", "")).strip(),
        "matches_snapshot": bool(matches),
        "mismatch_count": len(mismatched_fields),
        "mismatched_fields": list(mismatched_fields),
        "expected_refinement_stage_hashes": _as_map(expected_record.get("refinement_stage_hashes")),
        "observed_refinement_stage_hashes": _as_map(observed_record.get("refinement_stage_hashes")),
        "expected_sol_system_id": str(expected_record.get("sol_system_id", "")).strip(),
        "observed_sol_system_id": str(observed_record.get("sol_system_id", "")).strip(),
        "expected_earth_planet_id": str(expected_record.get("earth_planet_id", "")).strip(),
        "observed_earth_planet_id": str(observed_record.get("earth_planet_id", "")).strip(),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_worldgen_lock_verify_report(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-24",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: OMEGA",
        "Replacement Target: WORLDGEN_LOCK_BASELINE final report and mock release archive",
        "",
        "# Worldgen Lock Verify",
        "",
        "- result: `{}`".format(str(payload.get("result", "")).strip()),
        "- baseline_seed: `{}`".format(str(payload.get("baseline_seed", "")).strip()),
        "- matches_snapshot: `{}`".format("true" if bool(payload.get("matches_snapshot")) else "false"),
        "- expected_snapshot_fingerprint: `{}`".format(str(payload.get("expected_snapshot_fingerprint", "")).strip()),
        "- observed_snapshot_fingerprint: `{}`".format(str(payload.get("observed_snapshot_fingerprint", "")).strip()),
        "- mismatch_count: `{}`".format(int(payload.get("mismatch_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(str(payload.get("deterministic_fingerprint", "")).strip()),
        "",
        "## Refinement Stage Hashes",
        "",
    ]
    expected_stage_hashes = _as_map(payload.get("expected_refinement_stage_hashes"))
    observed_stage_hashes = _as_map(payload.get("observed_refinement_stage_hashes"))
    for key in sorted(set(list(expected_stage_hashes.keys()) + list(observed_stage_hashes.keys()))):
        lines.append("- `{}` expected=`{}` observed=`{}`".format(
            str(key),
            str(expected_stage_hashes.get(key, "")).strip(),
            str(observed_stage_hashes.get(key, "")).strip(),
        ))
    lines.extend(
        [
            "",
            "## Identity Anchors",
            "",
            "- expected_sol_system_id: `{}`".format(str(payload.get("expected_sol_system_id", "")).strip()),
            "- observed_sol_system_id: `{}`".format(str(payload.get("observed_sol_system_id", "")).strip()),
            "- expected_earth_planet_id: `{}`".format(str(payload.get("expected_earth_planet_id", "")).strip()),
            "- observed_earth_planet_id: `{}`".format(str(payload.get("observed_earth_planet_id", "")).strip()),
            "",
            "## Mismatches",
            "",
        ]
    )
    mismatches = [str(item).strip() for item in _as_list(payload.get("mismatched_fields")) if str(item).strip()]
    if not mismatches:
        lines.append("- none")
    else:
        for token in mismatches[:32]:
            lines.append("- `{}`".format(token))
    return "\n".join(lines).rstrip() + "\n"


def write_worldgen_lock_verify_outputs(
    repo_root: str,
    report: Mapping[str, object],
    *,
    json_path: str = "",
    doc_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    resolved_json = os.path.normpath(os.path.abspath(json_path)) if str(json_path or "").strip() else _repo_abs(repo_root_abs, WORLDGEN_VERIFY_JSON_REL)
    resolved_doc = os.path.normpath(os.path.abspath(doc_path)) if str(doc_path or "").strip() else _repo_abs(repo_root_abs, WORLDGEN_VERIFY_DOC_REL)
    return {
        "json_path": _write_canonical_json(resolved_json, dict(report or {})),
        "doc_path": _write_text(resolved_doc, render_worldgen_lock_verify_report(report)),
    }


__all__ = [
    "CLIMATE_PROXY_HASH_COUNT",
    "EARTH_TILE_HASH_COUNT",
    "ELEVATION_HASH_COUNT",
    "GALAXY_NODE_ID_COUNT",
    "SURFACE_TILE_SAMPLE_ORDER",
    "WORLDGEN_BASELINE_SEED_REL",
    "WORLDGEN_BASELINE_SNAPSHOT_REL",
    "WORLDGEN_LOCK_BASELINE_SCHEMA_ID",
    "WORLDGEN_LOCK_ID",
    "WORLDGEN_LOCK_REGISTRY_REL",
    "WORLDGEN_LOCK_VERSION",
    "WORLDGEN_VERIFY_DOC_REL",
    "WORLDGEN_VERIFY_JSON_REL",
    "WORLD_CELL_SAMPLE_INDEX_TUPLES",
    "build_locked_identity_context",
    "build_worldgen_lock_snapshot",
    "load_worldgen_lock_registry",
    "load_worldgen_lock_snapshot",
    "read_worldgen_baseline_seed",
    "registry_record_hash",
    "render_worldgen_lock_verify_report",
    "seed_text_hash",
    "snapshot_record_hash",
    "verify_worldgen_lock",
    "world_cell_key",
    "write_worldgen_lock_verify_outputs",
    "write_worldgen_lock_snapshot",
    "write_worldgen_seed_file",
]

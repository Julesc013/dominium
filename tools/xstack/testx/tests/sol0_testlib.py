"""Shared deterministic Sol pin overlay fixtures."""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Mapping


SOL_PACK_MANIFEST_REL = os.path.join("packs", "official", "pack.sol.pin_minimal", "pack.json")
SOL_OVERLAY_LAYER_REL = os.path.join(
    "packs",
    "official",
    "pack.sol.pin_minimal",
    "data",
    "overlay",
    "overlay.layer.sol_pin_minimal.json",
)
SOL_PATCH_DOCUMENT_REL = os.path.join(
    "packs",
    "official",
    "pack.sol.pin_minimal",
    "data",
    "overlay",
    "sol_pin_patches.json",
)


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    with open(abs_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError("expected object JSON at {}".format(rel_path.replace("\\", "/")))
    return dict(payload)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _quantity_value(value: object, default_value: int = 0) -> int:
    row = _as_map(value)
    try:
        return int(row.get("value", default_value))
    except (TypeError, ValueError):
        return int(default_value)


def _normalized_generated_rows(result: Mapping[str, object], key: str) -> List[dict]:
    direct = result.get(key)
    if isinstance(direct, list):
        return [dict(row) for row in direct if isinstance(row, Mapping)]
    ext = _as_map(result.get("extensions"))
    rows = ext.get(key)
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _rows_by_key(rows: object, key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _as_list(rows):
        if not isinstance(row, Mapping):
            continue
        token = str(dict(row).get(key, "")).strip()
        if token:
            out[token] = dict(row)
    return dict((token, dict(out[token])) for token in sorted(out.keys()))


def _targeted_base_properties(
    *,
    object_row: Mapping[str, object],
    system_artifacts_by_id: Mapping[str, dict],
    star_artifacts_by_id: Mapping[str, dict],
    planet_orbits_by_id: Mapping[str, dict],
    planet_basics_by_id: Mapping[str, dict],
) -> dict:
    object_id = str(object_row.get("object_id_hash", "")).strip()
    object_kind_id = str(object_row.get("object_kind_id", "")).strip()
    if object_kind_id == "kind.star_system":
        artifact = dict(system_artifacts_by_id.get(object_id) or {})
        ext = _as_map(artifact.get("extensions"))
        return {
            "display_name": "Procedural System {}".format(int(ext.get("local_index", 0))),
            "galaxy_position_ref": _as_map(artifact.get("galaxy_position_ref")),
            "metallicity_proxy": _as_map(artifact.get("metallicity_proxy")),
            "system_seed_value": str(artifact.get("system_seed_value", "")).strip(),
            "tags": ["procedural", "system.seeded"],
        }
    if object_kind_id == "kind.star":
        artifact = dict(star_artifacts_by_id.get(object_id) or {})
        return {
            "display_name": "Procedural Primary",
            "physical": {
                "mass_milli_solar": _quantity_value(artifact.get("star_mass"), 0),
            },
            "luminosity_proxy": _as_map(artifact.get("luminosity_proxy")),
            "age_proxy": _as_map(artifact.get("age_proxy")),
            "metallicity_proxy": _as_map(artifact.get("metallicity_proxy")),
            "tags": ["procedural", "star.primary"],
        }
    if object_kind_id == "kind.planet":
        orbit = dict(planet_orbits_by_id.get(object_id) or {})
        basic = dict(planet_basics_by_id.get(object_id) or {})
        basic_ext = _as_map(basic.get("extensions"))
        planet_index = int(basic_ext.get("planet_index", _as_map(orbit.get("extensions")).get("planet_index", 0)) or 0)
        tags = ["procedural"]
        planet_class_id = str(basic_ext.get("planet_class_id", "")).strip()
        if planet_class_id:
            tags.append(planet_class_id)
        return {
            "display_name": "Procedural Planet {}".format(planet_index),
            "physical": {
                "radius_km": _quantity_value(basic.get("radius"), 0),
                "density_class_id": str(basic.get("density_class_id", "")).strip(),
            },
            "surface": {
                "body_albedo_proxy_permille": _quantity_value(basic.get("body_albedo_proxy"), 0),
            },
            "spin": {
                "axial_tilt_mdeg": _quantity_value(basic.get("axial_tilt"), 0),
                "rotation_period_hours_milli": _quantity_value(basic.get("rotation_period"), 0),
            },
            "orbit": {
                "semi_major_axis_milli_au": _quantity_value(orbit.get("semi_major_axis"), 0),
                "eccentricity_permille": _quantity_value(orbit.get("eccentricity"), 0),
                "inclination_mdeg": _quantity_value(orbit.get("inclination"), 0),
                "parent_object_id": str(orbit.get("star_object_id", "")).strip(),
            },
            "atmosphere_class_id": str(basic.get("atmosphere_class_id", "")).strip(),
            "ocean_fraction_permille": _quantity_value(basic.get("ocean_fraction"), 0),
            "tags": sorted(set(tag for tag in tags if tag)),
        }
    if object_kind_id == "kind.moon":
        return {
            "display_name": "Procedural Moon Stub",
            "surface": {
                "body_albedo_proxy_permille": 120,
            },
            "tags": ["moon.stub", "procedural"],
        }
    return {
        "display_name": "Procedural Object",
        "tags": ["procedural"],
    }


def load_sol_pack_fixture_payloads(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.mvp.runtime_bundle import (
        build_default_universe_identity,
        build_pack_lock_payload,
        build_profile_bundle_payload,
    )
    from worldgen.mw.sol_anchor import sol_anchor_object_ids

    profile_bundle = build_profile_bundle_payload()
    pack_lock = build_pack_lock_payload(repo_root=repo_root, profile_bundle_payload=profile_bundle)
    universe_identity = build_default_universe_identity(
        repo_root=repo_root,
        seed="0",
        authority_mode="dev",
        pack_lock_payload=pack_lock,
        profile_bundle_payload=profile_bundle,
    )
    pack_manifest = _load_json(repo_root, SOL_PACK_MANIFEST_REL)
    overlay_layer = _load_json(repo_root, SOL_OVERLAY_LAYER_REL)
    patch_document = _load_json(repo_root, SOL_PATCH_DOCUMENT_REL)
    derived_slot_ids = sol_anchor_object_ids(universe_identity_hash=str(universe_identity.get("identity_hash", "")).strip())
    return {
        "profile_bundle": profile_bundle,
        "pack_lock": pack_lock,
        "universe_identity": universe_identity,
        "pack_manifest": pack_manifest,
        "overlay_layer": overlay_layer,
        "patch_document": patch_document,
        "derived_slot_object_ids": derived_slot_ids,
    }


def build_sol_overlay_fixture(repo_root: str, *, refinement_level: int = 2) -> dict:
    _ensure_repo_root(repo_root)
    from geo import (
        build_default_overlay_manifest,
        build_effective_object_view,
        generate_worldgen_result,
        merge_overlay_view,
        overlay_cache_clear,
        worldgen_cache_clear,
    )
    from worldgen.mw.sol_anchor import SOL_ANCHOR_CELL_INDEX_TUPLE
    from tools.xstack.testx.tests.geo8_testlib import worldgen_request_row

    payloads = load_sol_pack_fixture_payloads(repo_root)
    patch_document = dict(payloads.get("patch_document") or {})
    slot_object_ids = dict(patch_document.get("slot_object_ids") or {})
    if slot_object_ids != dict(payloads.get("derived_slot_object_ids") or {}):
        raise RuntimeError("Sol pin slot_object_ids drifted from derived GEO identities")

    worldgen_cache_clear()
    overlay_cache_clear()
    request = worldgen_request_row(
        request_id="sol0.fixture.anchor.l{}".format(int(refinement_level)),
        index_tuple=SOL_ANCHOR_CELL_INDEX_TUPLE,
        refinement_level=int(refinement_level),
        reason="query",
    )
    result = generate_worldgen_result(
        universe_identity=payloads.get("universe_identity"),
        worldgen_request=request,
        cache_enabled=False,
    )
    if str(result.get("result", "")).strip() != "complete":
        raise RuntimeError("Sol anchor worldgen fixture did not complete")

    generated_object_rows = _normalized_generated_rows(result, "generated_object_rows")
    system_artifacts_by_id = _rows_by_key(_normalized_generated_rows(result, "generated_star_system_artifact_rows"), "object_id")
    star_artifacts_by_id = _rows_by_key(_normalized_generated_rows(result, "generated_star_artifact_rows"), "object_id")
    planet_orbits_by_id = _rows_by_key(_normalized_generated_rows(result, "generated_planet_orbit_artifact_rows"), "planet_object_id")
    planet_basics_by_id = _rows_by_key(_normalized_generated_rows(result, "generated_planet_basic_artifact_rows"), "object_id")
    object_rows_by_id = _rows_by_key(generated_object_rows, "object_id_hash")

    base_objects = []
    existing_slot_ids = []
    missing_slot_ids = []
    for slot_id, object_id in sorted(slot_object_ids.items()):
        object_row = dict(object_rows_by_id.get(str(object_id).strip()) or {})
        if not object_row:
            missing_slot_ids.append(str(slot_id))
            continue
        existing_slot_ids.append(str(slot_id))
        base_objects.append(
            build_effective_object_view(
                object_id=str(object_id).strip(),
                object_kind_id=str(object_row.get("object_kind_id", "")).strip(),
                geo_cell_key=_as_map(object_row.get("geo_cell_key")),
                properties=_targeted_base_properties(
                    object_row=object_row,
                    system_artifacts_by_id=system_artifacts_by_id,
                    star_artifacts_by_id=star_artifacts_by_id,
                    planet_orbits_by_id=planet_orbits_by_id,
                    planet_basics_by_id=planet_basics_by_id,
                ),
                extensions={
                    "slot_id": str(slot_id),
                    "source_layer_id": "base.worldgen",
                    "source": "SOL0-4",
                },
            )
        )
    overlay_layer = dict(payloads.get("overlay_layer") or {})
    overlay_manifest = build_default_overlay_manifest(
        universe_id=str(payloads["universe_identity"].get("universe_id", "")).strip(),
        pack_lock_hash=str(payloads["pack_lock"].get("pack_lock_hash", "")).strip(),
        save_id="save.sol0.fixture",
        generator_version_id=str(payloads["universe_identity"].get("generator_version_id", "")).strip(),
        official_layer_specs=[
            {
                "layer_id": str(overlay_layer.get("layer_id", "")).strip(),
                "pack_id": str(_as_map(overlay_layer.get("extensions")).get("pack_id", "")).strip(),
                "pack_hash": str(_as_map(overlay_layer.get("extensions")).get("pack_hash", "")).strip(),
                "signature_status": str(_as_map(overlay_layer.get("extensions")).get("signature_status", "")).strip(),
            }
        ],
        mod_layer_specs=[],
        overlay_policy_id="overlay.default",
    )
    unpinned_manifest = build_default_overlay_manifest(
        universe_id=str(payloads["universe_identity"].get("universe_id", "")).strip(),
        pack_lock_hash=str(payloads["pack_lock"].get("pack_lock_hash", "")).strip(),
        save_id="save.sol0.fixture",
        generator_version_id=str(payloads["universe_identity"].get("generator_version_id", "")).strip(),
        official_layer_specs=[],
        mod_layer_specs=[],
        overlay_policy_id="overlay.default",
    )
    resolved_packs = [dict(row) for row in _as_list(payloads["pack_lock"].get("ordered_packs")) if isinstance(row, Mapping)]
    merge_result = merge_overlay_view(
        base_objects=base_objects,
        overlay_manifest=overlay_manifest,
        property_patches=patch_document.get("property_patches"),
        resolved_packs=resolved_packs,
        expected_pack_lock_hash=str(payloads["pack_lock"].get("pack_lock_hash", "")).strip(),
    )
    unpinned_merge_result = merge_overlay_view(
        base_objects=base_objects,
        overlay_manifest=unpinned_manifest,
        property_patches=[],
        resolved_packs=resolved_packs,
        expected_pack_lock_hash=str(payloads["pack_lock"].get("pack_lock_hash", "")).strip(),
    )
    return {
        **payloads,
        "worldgen_request": request,
        "worldgen_result": result,
        "base_objects": base_objects,
        "existing_slot_ids": existing_slot_ids,
        "missing_slot_ids": missing_slot_ids,
        "overlay_manifest": overlay_manifest,
        "unpinned_manifest": unpinned_manifest,
        "resolved_packs": resolved_packs,
        "merge_result": merge_result,
        "unpinned_merge_result": unpinned_merge_result,
    }


def effective_object_map(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _as_list(rows):
        if not isinstance(row, Mapping):
            continue
        object_id = str(dict(row).get("object_id", "")).strip()
        if object_id:
            out[object_id] = dict(row)
    return dict((object_id, dict(out[object_id])) for object_id in sorted(out.keys()))


def sol_overlay_target_hash(fixture: Mapping[str, object]) -> str:
    from tools.xstack.compatx.canonical_json import canonical_sha256

    slot_ids = dict(_as_map(_as_map(fixture).get("patch_document")).get("slot_object_ids") or {})
    effective_rows = effective_object_map(_as_map(fixture.get("merge_result")).get("effective_object_views"))
    targeted = [
        {
            "slot_id": str(slot_id),
            "object_id": str(object_id),
            "effective_object": dict(effective_rows.get(str(object_id)) or {}),
        }
        for slot_id, object_id in sorted(slot_ids.items())
    ]
    return canonical_sha256(targeted)


def verify_sol_pin_overlay(repo_root: str) -> dict:
    fixture = build_sol_overlay_fixture(repo_root, refinement_level=2)
    merge_result = _as_map(fixture.get("merge_result"))
    unpinned_merge_result = _as_map(fixture.get("unpinned_merge_result"))
    patch_document = _as_map(fixture.get("patch_document"))
    slot_ids = dict(patch_document.get("slot_object_ids") or {})
    effective_rows = effective_object_map(merge_result.get("effective_object_views"))
    unpinned_rows = effective_object_map(unpinned_merge_result.get("effective_object_views"))
    base_rows = effective_object_map(fixture.get("base_objects"))
    violations: List[str] = []

    if str(merge_result.get("result", "")).strip() != "complete":
        violations.append("overlay merge did not complete")
    if str(unpinned_merge_result.get("result", "")).strip() != "complete":
        violations.append("unpinned overlay merge did not complete")
    if "sol.system" not in fixture.get("existing_slot_ids", []):
        violations.append("base procedural Sol system was not generated at the anchor")
    for slot_id in fixture.get("existing_slot_ids", []):
        object_id = str(slot_ids.get(slot_id, "")).strip()
        if object_id and object_id not in effective_rows:
            violations.append("overlay result lost base object {}".format(slot_id))
        if object_id and object_id not in unpinned_rows:
            violations.append("unpinned merge lost base object {}".format(slot_id))
    sol_system = _as_map(effective_rows.get(str(slot_ids.get("sol.system", "")).strip())).get("properties", {})
    sol_star = _as_map(effective_rows.get(str(slot_ids.get("sol.star", "")).strip())).get("properties", {})
    earth = _as_map(effective_rows.get(str(slot_ids.get("sol.planet.earth", "")).strip())).get("properties", {})
    luna = _as_map(effective_rows.get(str(slot_ids.get("sol.moon.luna", "")).strip())).get("properties", {})
    if str(_as_map(sol_system).get("display_name", "")).strip() != "Sol":
        violations.append("official overlay did not pin the Sol system display name")
    if int(_as_map(_as_map(sol_star).get("physical")).get("radius_km", 0) or 0) != 695700:
        violations.append("official overlay did not pin the Sol star radius")
    if int(_as_map(_as_map(earth).get("physical")).get("radius_km", 0) or 0) != 6371:
        violations.append("official overlay did not pin the Earth radius")
    if str(_as_map(luna).get("display_name", "")).strip() != "Luna":
        violations.append("official overlay did not materialize Luna")
    for slot_id in fixture.get("existing_slot_ids", []):
        object_id = str(slot_ids.get(slot_id, "")).strip()
        if object_id and object_id in base_rows and object_id in unpinned_rows:
            if dict(unpinned_rows[object_id]) != dict(base_rows[object_id]):
                violations.append("unpinned merge did not revert to base view for {}".format(slot_id))

    report = {
        "result": "complete" if not violations else "violation",
        "existing_slot_ids": list(fixture.get("existing_slot_ids") or []),
        "missing_slot_ids": list(fixture.get("missing_slot_ids") or []),
        "pack_patch_count": len(_as_list(patch_document.get("property_patches"))),
        "overlay_merge_result_hash_chain": str(merge_result.get("overlay_merge_result_hash_chain", "")).strip(),
        "sol_overlay_target_hash": sol_overlay_target_hash(fixture),
        "violations": violations,
    }
    return report

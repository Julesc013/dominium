"""Shared deterministic GEO-9 overlay fixtures for TestX."""

from __future__ import annotations

import copy

from src.geo import (
    build_default_overlay_manifest,
    build_effective_object_view,
    build_property_patch,
    merge_overlay_view,
    overlay_cache_clear,
    overlay_proof_surface,
)
from tools.xstack.sessionx.common import identity_hash_for_payload
from tools.xstack.sessionx.process_runtime import execute_intent
from tools.xstack.testx.tests.mobility_free_testlib import (
    authority_context,
    law_profile,
    policy_context,
    seed_free_state,
)


ALLOWED_OVERLAY_PROCESSES = ["process.overlay_save_patch"]
UNIVERSE_ID = "universe.test.geo9"
SAVE_ID = "save.test.geo9"
PACK_LOCK_HASH = "a" * 64
OFFICIAL_PACK_HASH = "b" * 64
MOD_ALPHA_HASH = "c" * 64
MOD_BETA_HASH = "d" * 64
OBJECT_ID_EARTH = "object.earth"


def base_effective_objects():
    return [
        build_effective_object_view(
            object_id=OBJECT_ID_EARTH,
            object_kind_id="kind.planet",
            properties={
                "display_name": "Procedural Earth",
                "radius_km": 6300,
                "surface": {
                    "albedo_permille": 300,
                },
                "tags": ["procedural"],
            },
            extensions={"source": "geo9_testlib"},
        )
    ]


def official_layer_specs():
    return [
        {
            "layer_id": "official.reality.earth",
            "pack_id": "org.dominium.reality.earth",
            "pack_hash": OFFICIAL_PACK_HASH,
            "signature_status": "signed",
        }
    ]


def mod_layer_specs(*, reverse_order: bool = False):
    rows = [
        {
            "layer_id": "mod.alpha",
            "pack_id": "org.example.overlay.alpha",
            "pack_hash": MOD_ALPHA_HASH,
            "signature_status": "unsigned",
        },
        {
            "layer_id": "mod.beta",
            "pack_id": "org.example.overlay.beta",
            "pack_hash": MOD_BETA_HASH,
            "signature_status": "unsigned",
        },
    ]
    if reverse_order:
        rows = list(reversed(rows))
    return [dict(row) for row in rows]


def overlay_manifest(
    *,
    include_mods: bool = True,
    reverse_mod_order: bool = False,
    overlay_policy_id: str = "overlay.default",
    overlay_conflict_policy_id: str = "",
):
    return build_default_overlay_manifest(
        universe_id=UNIVERSE_ID,
        pack_lock_hash=PACK_LOCK_HASH,
        save_id=SAVE_ID,
        generator_version_id="gen.v0_stub",
        official_layer_specs=official_layer_specs(),
        mod_layer_specs=mod_layer_specs(reverse_order=reverse_mod_order) if include_mods else [],
        overlay_policy_id=overlay_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
    )


def resolved_packs(*, include_mods: bool = True, reverse_order: bool = False):
    rows = [
        {
            "pack_id": "org.dominium.reality.earth",
            "canonical_hash": OFFICIAL_PACK_HASH,
            "signature_status": "signed",
        }
    ]
    if include_mods:
        rows.extend(
            [
                {
                    "pack_id": "org.example.overlay.alpha",
                    "canonical_hash": MOD_ALPHA_HASH,
                    "signature_status": "unsigned",
                },
                {
                    "pack_id": "org.example.overlay.beta",
                    "canonical_hash": MOD_BETA_HASH,
                    "signature_status": "unsigned",
                },
            ]
        )
    if reverse_order:
        rows = list(reversed(rows))
    return [dict(row) for row in rows]


def official_property_patches():
    return [
        build_property_patch(
            target_object_id=OBJECT_ID_EARTH,
            property_path="display_name",
            operation="set",
            value="Earth",
            originating_layer_id="official.reality.earth",
            extensions={"reason": "official earth anchor"},
        ),
        build_property_patch(
            target_object_id=OBJECT_ID_EARTH,
            property_path="radius_km",
            operation="set",
            value=6371,
            originating_layer_id="official.reality.earth",
            extensions={"reason": "official measured radius"},
        ),
    ]


def mod_property_patches(*, reverse_order: bool = False):
    rows = [
        build_property_patch(
            target_object_id=OBJECT_ID_EARTH,
            property_path="display_name",
            operation="set",
            value="Terra",
            originating_layer_id="mod.alpha",
            extensions={"reason": "modded naming override"},
        ),
        build_property_patch(
            target_object_id=OBJECT_ID_EARTH,
            property_path="display_name",
            operation="set",
            value="Gaia",
            originating_layer_id="mod.beta",
            extensions={"reason": "modded naming override"},
        ),
    ]
    if reverse_order:
        rows = list(reversed(rows))
    return [dict(row) for row in rows]


def save_property_patch(value: str = "New Earth"):
    return build_property_patch(
        target_object_id=OBJECT_ID_EARTH,
        property_path="display_name",
        operation="set",
        value=str(value),
        originating_layer_id="save.patch",
        extensions={"reason": "player rename"},
    )


def all_property_patches(
    *,
    include_mods: bool = True,
    include_save: bool = False,
    save_value: str = "New Earth",
    reverse_order: bool = False,
):
    rows = official_property_patches()
    if include_mods:
        rows.extend(mod_property_patches())
    if include_save:
        rows.append(save_property_patch(value=save_value))
    if reverse_order:
        rows = list(reversed(rows))
    return [dict(row) for row in rows]


def overlay_fixture_merge_result(
    *,
    include_mods: bool = True,
    include_save: bool = False,
    save_value: str = "New Earth",
    reverse_mod_order: bool = False,
    reverse_patch_order: bool = False,
    reverse_resolved_packs: bool = False,
    overlay_policy_id: str = "overlay.default",
    overlay_conflict_policy_id: str = "",
):
    overlay_cache_clear()
    manifest = overlay_manifest(
        include_mods=include_mods,
        reverse_mod_order=reverse_mod_order,
        overlay_policy_id=overlay_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
    )
    property_patches = all_property_patches(
        include_mods=include_mods,
        include_save=include_save,
        save_value=save_value,
        reverse_order=reverse_patch_order,
    )
    packs = resolved_packs(include_mods=include_mods, reverse_order=reverse_resolved_packs)
    merge_result = merge_overlay_view(
        base_objects=base_effective_objects(),
        overlay_manifest=manifest,
        property_patches=property_patches,
        resolved_packs=packs,
        expected_pack_lock_hash=PACK_LOCK_HASH,
        overlay_policy_id=overlay_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
    )
    return {
        "base_objects": base_effective_objects(),
        "overlay_manifest": manifest,
        "property_patches": property_patches,
        "resolved_packs": packs,
        "merge_result": merge_result,
    }


def seed_overlay_state(
    *,
    include_mods: bool = True,
    overlay_policy_id: str = "overlay.default",
    overlay_conflict_policy_id: str = "",
):
    state = seed_free_state(initial_velocity_x=0)
    identity = {
        "schema_version": "1.0.0",
        "universe_id": UNIVERSE_ID,
        "global_seed": "seed.geo9.fixture.001",
        "domain_binding_ids": ["domain.navigation", "domain.astronomy"],
        "physics_profile_id": "physics.null",
        "topology_profile_id": "geo.topology.r3_infinite",
        "metric_profile_id": "geo.metric.euclidean",
        "partition_profile_id": "geo.partition.grid_zd",
        "projection_profile_id": "geo.projection.perspective_3d",
        "generator_version_id": "gen.v0_stub",
        "realism_profile_id": "realism.realistic_default_milkyway_stub",
        "base_scenario_id": "scenario.lab.galaxy_nav",
        "initial_pack_set_hash_expectation": PACK_LOCK_HASH,
        "compatibility_schema_refs": [
            "generator_version@1.0.0",
            "realism_profile@1.0.0",
            "overlay_manifest@1.0.0",
            "property_patch@1.0.0",
            "space_topology_profile@1.0.0",
            "metric_profile@1.0.0",
            "partition_profile@1.0.0",
            "projection_profile@1.0.0",
            "universe_identity@1.0.0",
        ],
        "immutable_after_create": True,
        "extensions": {},
        "identity_hash": "",
    }
    identity["identity_hash"] = identity_hash_for_payload(identity)
    manifest = overlay_manifest(
        include_mods=include_mods,
        overlay_policy_id=overlay_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
    )
    state["universe_identity"] = identity
    state["universe_id"] = UNIVERSE_ID
    state["save_id"] = SAVE_ID
    state["overlay_manifest"] = dict(manifest)
    state["save_property_patches"] = []
    state["overlay_merge_results"] = []
    surface = overlay_proof_surface(
        overlay_manifest=manifest,
        property_patches=[],
        effective_object_views=[],
        overlay_conflict_artifacts=[],
    )
    state["overlay_manifest_hash"] = str(surface.get("overlay_manifest_hash", "")).strip()
    state["property_patch_hash_chain"] = str(surface.get("property_patch_hash_chain", "")).strip()
    state["overlay_merge_result_hash_chain"] = str(surface.get("overlay_merge_result_hash_chain", "")).strip()
    state["overlay_conflict_artifact_hash_chain"] = str(surface.get("overlay_conflict_artifact_hash_chain", "")).strip()
    return state


def overlay_contexts(*, include_mods: bool = True):
    law = copy.deepcopy(law_profile(ALLOWED_OVERLAY_PROCESSES))
    auth = copy.deepcopy(authority_context())
    policy = copy.deepcopy(policy_context())
    policy["pack_lock_hash"] = PACK_LOCK_HASH
    policy["resolved_packs"] = resolved_packs(include_mods=include_mods)
    return law, auth, policy


def run_overlay_save_patch_process(*, state, property_patch=None, value: str = "New Earth"):
    law, auth, policy = overlay_contexts()
    intent = {
        "intent_id": "intent.process.overlay_save_patch.{}".format(len(list(state.get("events") or []))),
        "process_id": "process.overlay_save_patch",
        "inputs": {},
    }
    if property_patch is not None:
        intent["inputs"]["property_patch"] = dict(property_patch)
    else:
        intent["inputs"] = {
            "target_object_id": OBJECT_ID_EARTH,
            "property_path": "display_name",
            "operation": "set",
            "value": str(value),
            "originating_layer_id": "save.patch",
            "reason": "player rename",
        }
    return execute_intent(
        state=state,
        intent=intent,
        law_profile=law,
        authority_context=auth,
        navigation_indices={},
        policy_context=policy,
    )


def merge_state_overlay(
    *,
    state,
    include_mods: bool = True,
    overlay_policy_id: str = "",
    overlay_conflict_policy_id: str = "",
):
    overlay_cache_clear()
    property_patches = official_property_patches()
    if include_mods:
        property_patches.extend(mod_property_patches())
    property_patches.extend(copy.deepcopy(list(state.get("save_property_patches") or [])))
    merge_result = merge_overlay_view(
        base_objects=base_effective_objects(),
        overlay_manifest=state.get("overlay_manifest"),
        property_patches=property_patches,
        resolved_packs=resolved_packs(include_mods=include_mods),
        expected_pack_lock_hash=PACK_LOCK_HASH,
        overlay_policy_id=overlay_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
    )
    return {
        "property_patches": property_patches,
        "merge_result": merge_result,
    }

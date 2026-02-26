"""Universe physics profile + null boot helper utilities."""

from __future__ import annotations

import copy
import json
import os
from typing import Dict, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.registry_compile.constants import (
    DEFAULT_COMPATIBILITY_VERSION,
    REGISTRY_OUTPUT_FILENAMES,
)
from tools.xstack.registry_compile.lockfile import compute_pack_lock_hash, validate_lockfile_payload

from .common import refusal


NULL_BUNDLE_ID = "bundle.null"
NULL_PHYSICS_PROFILE_ID = "physics.null"
NULL_BUILTIN_PACK_ID = "pack.core.null_boot"
NULL_BUILTIN_PATH = "builtin://null_boot"


_NULL_TIME_MODEL = {
    "schema_version": "1.0.0",
    "time_model_id": "default_single_tick",
    "single_tick_axis": True,
    "allow_variable_dt": False,
    "allow_branching": False,
    "allow_retroactive_mutation": False,
    "extensions": {},
}

_NULL_PRECISION_POLICY = {
    "schema_version": "1.0.0",
    "policy_id": "default_null",
    "invariant_numeric_type": "fixed_point",
    "solver_numeric_type": "fixed_point",
    "quantization_rules": {},
    "error_accumulation_strategy": "none",
    "extensions": {},
}

_NULL_TIER_TAXONOMY = {
    "schema_version": "1.0.0",
    "taxonomy_id": "default_minimal",
    "tiers": ["macro", "render"],
    "collapse_required_invariants": ["inv.epistemic_invariance"],
    "expand_redaction_rules": ["redaction.default"],
    "extensions": {},
}

_NULL_BOUNDARY_MODEL = {
    "schema_version": "1.0.0",
    "boundary_model_id": "procedural_infinite",
    "universe_type": "procedural_infinite",
    "allow_boundary_flux": False,
    "extensions": {},
}

_NULL_PHYSICS_PROFILE = {
    "schema_version": "1.0.0",
    "physics_profile_id": NULL_PHYSICS_PROFILE_ID,
    "description": "Built-in null profile for deterministic zero-pack boot.",
    "enabled_domain_ids": [],
    "conservation_contract_set_id": "none",
    "allowed_exception_types": [],
    "numeric_precision_policy_id": "default_null",
    "tier_taxonomy_id": "default_minimal",
    "time_model_id": "default_single_tick",
    "boundary_model_id": "procedural_infinite",
    "error_budget": {},
    "version_introduced": "1.0.0",
    "deprecated": False,
    "extensions": {},
}

_NULL_LAW_PROFILE = {
    "law_profile_id": "law.lab.unrestricted",
    "epistemic_policy_id": "ep.policy.lab_broad",
    "pack_id": NULL_BUILTIN_PACK_ID,
    "path": NULL_BUILTIN_PATH,
    "allowed_processes": [
        "process.region_management_tick",
    ],
    "forbidden_processes": [],
    "allowed_lenses": ["lens.diegetic.sensor"],
    "epistemic_limits": {
        "max_view_radius_km": 0,
        "allow_hidden_state_access": False,
    },
    "debug_allowances": {
        "allow_nondiegetic_overlays": False,
        "allow_time_dilation_controls": False,
    },
    "process_entitlement_requirements": {},
    "process_privilege_requirements": {},
}

_NULL_EXPERIENCE_PROFILE = {
    "experience_id": "profile.lab.developer",
    "pack_id": NULL_BUILTIN_PACK_ID,
    "path": NULL_BUILTIN_PATH,
    "default_lens_id": "lens.diegetic.sensor",
    "presentation_defaults": {
        "default_lens_id": "lens.diegetic.sensor",
        "hud_layout_id": "hud.none",
    },
    "allowed_lenses": ["lens.diegetic.sensor"],
    "suggested_parameter_bundles": ["params.lab.placeholder"],
    "allowed_transitions": [],
    "default_law_profile_id": "law.lab.unrestricted",
}

_NULL_LENS = {
    "lens_id": "lens.diegetic.sensor",
    "lens_type": "diegetic",
    "pack_id": NULL_BUILTIN_PACK_ID,
    "path": NULL_BUILTIN_PATH,
    "transform_description": "Null boot diegetic lens for deterministic empty-world observation.",
    "required_entitlements": [],
    "observation_channels": [
        "ch.core.time",
        "ch.camera.state",
    ],
    "epistemic_constraints": {
        "visibility_policy": "policy.visibility.null",
        "max_resolution_tier": 0,
    },
}

_NULL_ACTIVATION_POLICY = {
    "policy_id": "policy.activation.default_lab",
    "pack_id": NULL_BUILTIN_PACK_ID,
    "path": NULL_BUILTIN_PATH,
    "interest_radius_rules": [
        {
            "kind": "*",
            "priority": 0,
            "activation_distance_mm": 0,
            "deactivation_distance_mm": 0,
            "anchor_spacing_mm": 1,
        }
    ],
    "activation_thresholds": {
        "distance_metric": "camera_manhattan_mm",
        "distance_bands_mm": [
            {
                "band_id": "near",
                "max_distance_mm": 0,
            }
        ],
    },
    "hysteresis": {
        "enter_margin_mm": 0,
        "exit_margin_mm": 0,
    },
    "deterministic_inputs": [
        "camera.position_mm",
    ],
}

_NULL_BUDGET_POLICY = {
    "policy_id": "policy.budget.default_lab",
    "activation_policy_id": "policy.activation.default_lab",
    "pack_id": NULL_BUILTIN_PACK_ID,
    "path": NULL_BUILTIN_PATH,
    "max_compute_units_per_tick": 0,
    "max_entities_micro": 0,
    "max_regions_micro": 0,
    "fallback_behavior": "degrade_fidelity",
    "logging_level": 0,
    "tier_compute_weights": {
        "coarse": 1,
        "medium": 1,
        "fine": 1,
    },
    "entity_compute_weight": 1,
}

_NULL_FIDELITY_POLICY = {
    "policy_id": "policy.fidelity.default_lab",
    "pack_id": NULL_BUILTIN_PACK_ID,
    "path": NULL_BUILTIN_PATH,
    "tiers": [
        {
            "tier_id": "fine",
            "max_distance_mm": 0,
            "micro_entities_target": 0,
        },
        {
            "tier_id": "medium",
            "max_distance_mm": 0,
            "micro_entities_target": 0,
        },
        {
            "tier_id": "coarse",
            "max_distance_mm": 0,
            "micro_entities_target": 0,
        }
    ],
    "switching_rules": {
        "upgrade_hysteresis_mm": 0,
        "degrade_hysteresis_mm": 0,
        "degrade_order": ["fine", "medium", "coarse"],
        "upgrade_order": ["coarse", "medium", "fine"],
    },
    "minimum_tier_by_kind": {},
}

_NULL_EPISTEMIC_POLICY = {
    "epistemic_policy_id": "ep.policy.lab_broad",
    "description": "Null boot epistemic policy for deterministic empty-world operation.",
    "allowed_observation_channels": [
        "ch.core.time",
        "ch.camera.state",
    ],
    "forbidden_channels": [],
    "retention_policy_id": "ep.retention.none",
    "inference_policy_id": "ep.infer.none",
    "max_precision_rules": [],
    "deterministic_filters": [
        "filter.channel_allow_deny.v1",
        "filter.quantize_precision.v1",
    ],
    "extensions": {},
}

_NULL_RETENTION_POLICY = {
    "retention_policy_id": "ep.retention.none",
    "memory_allowed": False,
    "max_memory_items": 0,
    "decay_model_id": "ep.decay.none",
    "eviction_rule_id": "evict.none",
    "deterministic_eviction_rule_id": "evict.none",
    "extensions": {},
}

_NULL_DECAY_MODEL = {
    "decay_model_id": "ep.decay.none",
    "description": "Null boot decay model with no retained memory.",
    "ttl_rules": [],
    "refresh_rules": [],
    "eviction_rule_id": "evict.none",
    "extensions": {},
}

_NULL_EVICTION_RULE = {
    "eviction_rule_id": "evict.none",
    "description": "Null boot eviction rule with no retained memory entries.",
    "algorithm_id": "evict.none",
    "priority_by_channel": {},
    "priority_by_subject_kind": {},
    "extensions": {},
}

_NULL_REGISTRY_LIST_KEYS = {
    "domain_registry": "domains",
    "law_registry": "law_profiles",
    "experience_registry": "experience_profiles",
    "lens_registry": "lenses",
    "control_action_registry": "actions",
    "controller_type_registry": "controller_types",
    "governance_type_registry": "governance_types",
    "diplomatic_state_registry": "states",
    "cohort_mapping_policy_registry": "policies",
    "order_type_registry": "order_types",
    "role_registry": "roles",
    "institution_type_registry": "institution_types",
    "demography_policy_registry": "policies",
    "death_model_registry": "death_models",
    "birth_model_registry": "birth_models",
    "migration_model_registry": "migration_models",
    "body_shape_registry": "shape_types",
    "view_mode_registry": "view_modes",
    "instrument_type_registry": "instrument_types",
    "calibration_model_registry": "calibration_models",
    "render_proxy_registry": "render_proxies",
    "cosmetic_registry": "cosmetics",
    "cosmetic_policy_registry": "policies",
    "render_primitive_registry": "primitives",
    "procedural_material_template_registry": "material_templates",
    "label_policy_registry": "label_policies",
    "lod_policy_registry": "lod_policies",
    "representation_rule_registry": "representation_rules",
    "net_replication_policy_registry": "policies",
    "net_resync_strategy_registry": "strategies",
    "net_server_policy_registry": "policies",
    "securex_policy_registry": "policies",
    "server_profile_registry": "profiles",
    "shard_map_registry": "shard_maps",
    "perception_interest_policy_registry": "policies",
    "epistemic_policy_registry": "policies",
    "retention_policy_registry": "policies",
    "decay_model_registry": "decay_models",
    "eviction_rule_registry": "eviction_rules",
    "anti_cheat_policy_registry": "policies",
    "anti_cheat_module_registry": "modules",
    "activation_policy_registry": "activation_policies",
    "budget_policy_registry": "budget_policies",
    "fidelity_policy_registry": "fidelity_policies",
    "worldgen_constraints_registry": "constraints",
    "astronomy_catalog_index": "entries",
    "site_registry_index": "sites",
    "ephemeris_registry": "tables",
    "terrain_tile_registry": "tiles",
    "ui_registry": "windows",
    "universe_physics_profile_registry": "physics_profiles",
    "time_model_registry": "time_models",
    "numeric_precision_policy_registry": "precision_policies",
    "tier_taxonomy_registry": "taxonomies",
    "boundary_model_registry": "boundary_models",
}


def _finalize_registry_payload(payload: dict) -> dict:
    out = dict(payload)
    out["registry_hash"] = canonical_sha256(payload)
    return out


def _empty_registry_payload(*, list_key: str) -> dict:
    return {
        "format_version": "1.0.0",
        "generated_from": [],
        list_key: [],
    }


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def default_null_physics_profile() -> dict:
    return copy.deepcopy(_NULL_PHYSICS_PROFILE)


def default_null_runtime_registries() -> Dict[str, dict]:
    payloads: Dict[str, dict] = {}
    for schema_key, list_key in sorted(_NULL_REGISTRY_LIST_KEYS.items(), key=lambda item: item[0]):
        payloads[schema_key] = _empty_registry_payload(list_key=str(list_key))

    payloads["universe_physics_profile_registry"]["physics_profiles"] = [copy.deepcopy(_NULL_PHYSICS_PROFILE)]
    payloads["time_model_registry"]["time_models"] = [copy.deepcopy(_NULL_TIME_MODEL)]
    payloads["numeric_precision_policy_registry"]["precision_policies"] = [copy.deepcopy(_NULL_PRECISION_POLICY)]
    payloads["tier_taxonomy_registry"]["taxonomies"] = [copy.deepcopy(_NULL_TIER_TAXONOMY)]
    payloads["boundary_model_registry"]["boundary_models"] = [copy.deepcopy(_NULL_BOUNDARY_MODEL)]

    payloads["law_registry"]["law_profiles"] = [copy.deepcopy(_NULL_LAW_PROFILE)]
    payloads["experience_registry"]["experience_profiles"] = [copy.deepcopy(_NULL_EXPERIENCE_PROFILE)]
    payloads["lens_registry"]["lenses"] = [copy.deepcopy(_NULL_LENS)]
    payloads["activation_policy_registry"]["activation_policies"] = [copy.deepcopy(_NULL_ACTIVATION_POLICY)]
    payloads["budget_policy_registry"]["budget_policies"] = [copy.deepcopy(_NULL_BUDGET_POLICY)]
    payloads["fidelity_policy_registry"]["fidelity_policies"] = [copy.deepcopy(_NULL_FIDELITY_POLICY)]
    payloads["epistemic_policy_registry"]["policies"] = [copy.deepcopy(_NULL_EPISTEMIC_POLICY)]
    payloads["retention_policy_registry"]["policies"] = [copy.deepcopy(_NULL_RETENTION_POLICY)]
    payloads["decay_model_registry"]["decay_models"] = [copy.deepcopy(_NULL_DECAY_MODEL)]
    payloads["eviction_rule_registry"]["eviction_rules"] = [copy.deepcopy(_NULL_EVICTION_RULE)]

    payloads["astronomy_catalog_index"]["reference_frames"] = []
    payloads["astronomy_catalog_index"]["search_index"] = {}
    payloads["site_registry_index"]["search_index"] = {}

    return dict((key, _finalize_registry_payload(value)) for key, value in sorted(payloads.items(), key=lambda item: item[0]))


def default_null_lockfile_payload(bundle_id: str = NULL_BUNDLE_ID) -> Tuple[dict, Dict[str, dict], Dict[str, object]]:
    registry_payloads = default_null_runtime_registries()
    registry_hashes: Dict[str, str] = {}
    for schema_key in sorted(REGISTRY_OUTPUT_FILENAMES.keys()):
        payload = registry_payloads.get(schema_key)
        if not isinstance(payload, dict):
            return {}, {}, refusal(
                "refusal.physics_profile_missing",
                "null boot registry payload is missing required registry '{}'".format(schema_key),
                "Restore null runtime registry mapping and retry.",
                {"registry_id": schema_key},
                "$.registries",
            )
        registry_hashes["{}_hash".format(schema_key)] = str(payload.get("registry_hash", "")).strip()

    lockfile_payload = {
        "lockfile_version": "1.0.0",
        "bundle_id": str(bundle_id).strip() or NULL_BUNDLE_ID,
        "resolved_packs": [],
        "registries": dict(registry_hashes),
        "compatibility_version": DEFAULT_COMPATIBILITY_VERSION,
        "pack_lock_hash": compute_pack_lock_hash([]),
    }
    semantic = validate_lockfile_payload(lockfile_payload)
    if str(semantic.get("result", "")) != "complete":
        return {}, {}, refusal(
            "refusal.physics_profile_missing",
            "null boot lockfile payload failed deterministic validation",
            "Restore null lockfile builder mapping and retry.",
            {"bundle_id": str(lockfile_payload.get("bundle_id", ""))},
            "$.lockfile",
        )
    return lockfile_payload, registry_payloads, {}


def is_null_bundle_profile(bundle_profile: dict) -> bool:
    row = dict(bundle_profile or {})
    required = [str(item).strip() for item in (row.get("pack_ids") or []) if str(item).strip()]
    optional = [str(item).strip() for item in (row.get("optional_pack_ids") or []) if str(item).strip()]
    return (not required) and (not optional)


def normalize_physics_profile_id(profile_id: str) -> str:
    token = str(profile_id or "").strip()
    return token or NULL_PHYSICS_PROFILE_ID


def select_physics_profile(
    *,
    physics_profile_id: str,
    profile_registry: dict,
) -> Tuple[dict, Dict[str, object]]:
    requested = normalize_physics_profile_id(physics_profile_id)
    if requested == NULL_PHYSICS_PROFILE_ID:
        return default_null_physics_profile(), {}

    rows = profile_registry.get("physics_profiles")
    if isinstance(rows, list):
        for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("physics_profile_id", ""))):
            if str(row.get("physics_profile_id", "")).strip() == requested:
                return dict(row), {}

    return {}, refusal(
        "refusal.physics_profile_missing",
        "requested physics_profile_id is not present in available universe physics profiles",
        "Install/select a pack that provides the profile or use physics.null.",
        {"physics_profile_id": requested},
        "$.physics_profile_id",
    )


def write_null_boot_artifacts(
    *,
    repo_root: str,
    out_dir_rel: str = "build/registries",
    lockfile_out_rel: str = "build/lockfile.json",
    bundle_id: str = NULL_BUNDLE_ID,
    schema_repo_root: str = "",
) -> Dict[str, object]:
    schema_root = os.path.abspath(schema_repo_root) if str(schema_repo_root).strip() else os.path.abspath(repo_root)
    out_dir = os.path.join(repo_root, out_dir_rel)
    lockfile_out = os.path.join(repo_root, lockfile_out_rel)
    _ensure_dir(out_dir)

    lockfile_payload, registry_payloads, lockfile_error = default_null_lockfile_payload(bundle_id=str(bundle_id))
    if lockfile_error:
        return dict(lockfile_error)

    output_files = []
    for registry_key in sorted(REGISTRY_OUTPUT_FILENAMES.keys()):
        payload = dict(registry_payloads.get(registry_key) or {})
        if not payload:
            return refusal(
                "refusal.physics_profile_missing",
                "null boot registry payload is missing '{}'".format(registry_key),
                "Restore null runtime registry mapping and retry.",
                {"registry_id": registry_key},
                "$.registries",
            )
        schema_check = validate_instance(
            repo_root=schema_root,
            schema_name=registry_key,
            payload=payload,
            strict_top_level=True,
        )
        if not bool(schema_check.get("valid", False)):
            return refusal(
                "refusal.physics_profile_missing",
                "null boot registry '{}' failed schema validation".format(registry_key),
                "Fix null registry payload structure and retry.",
                {"registry_id": registry_key},
                "$.registries",
            )
        out_path = os.path.join(out_dir, REGISTRY_OUTPUT_FILENAMES[registry_key])
        _write_json(out_path, payload)
        output_files.append(out_path)

    lock_schema_check = validate_instance(
        repo_root=schema_root,
        schema_name="bundle_lockfile",
        payload=lockfile_payload,
        strict_top_level=True,
    )
    if not bool(lock_schema_check.get("valid", False)):
        return refusal(
            "refusal.physics_profile_missing",
            "null boot lockfile failed schema validation",
            "Restore null lockfile payload fields and retry.",
            {"bundle_id": str(lockfile_payload.get("bundle_id", ""))},
            "$.lockfile",
        )
    lock_semantic = validate_lockfile_payload(lockfile_payload)
    if str(lock_semantic.get("result", "")) != "complete":
        return refusal(
            "refusal.physics_profile_missing",
            "null boot lockfile failed deterministic semantic validation",
            "Restore null lockfile deterministic hashing contract and retry.",
            {"bundle_id": str(lockfile_payload.get("bundle_id", ""))},
            "$.lockfile",
        )
    _write_json(lockfile_out, lockfile_payload)

    return {
        "result": "complete",
        "bundle_id": str(lockfile_payload.get("bundle_id", "")),
        "cache_key": "",
        "cache_hit": False,
        "out_dir": str(out_dir_rel).replace("\\", "/"),
        "lockfile_path": str(lockfile_out_rel).replace("\\", "/"),
        "ordered_pack_ids": [],
        "registry_hashes": dict(lockfile_payload.get("registries") or {}),
        "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
        "output_files": [str(os.path.relpath(path, repo_root)).replace("\\", "/") for path in output_files],
    }

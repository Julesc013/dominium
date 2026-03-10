"""Deterministic minimal boot/shutdown path for SessionSpec v1."""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from src.net.policies.policy_server_authoritative import (
    POLICY_ID_SERVER_AUTHORITATIVE,
    initialize_authoritative_runtime,
    join_client_midstream,
    prepare_server_authoritative_baseline,
)
from src.net.policies.policy_srz_hybrid import (
    POLICY_ID_SRZ_HYBRID,
    initialize_hybrid_runtime,
    join_client_hybrid,
    prepare_hybrid_baseline,
)
from src.modding import DEFAULT_MOD_POLICY_ID, proof_bundle_from_lockfile, validate_saved_mod_policy
from src.universe import enforce_session_contract_bundle
from src.compat.data_format_loader import load_versioned_artifact

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.registry_compile.compiler import compile_bundle
from tools.xstack.registry_compile.constants import (
    DEFAULT_BUNDLE_ID,
    REGISTRY_OUTPUT_FILENAMES,
)
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload

from .common import identity_hash_for_payload, norm, now_utc_iso, read_json_object, refusal, write_canonical_json
from .net_handshake import run_loopback_handshake
from .observation import build_truth_model, observe_truth
from .pipeline_contract import DEFAULT_PIPELINE_ID, load_session_pipeline_contract
from .render_model import build_render_model
from .universe_physics import select_physics_profile


DEFAULT_GENERATOR_VERSION_ID = "gen.v0_stub"
DEFAULT_REALISM_PROFILE_ID = "realism.realistic_default_milkyway_stub"


REGISTRY_HASH_KEY_MAP = {
    "universe_physics_profile_registry_hash": "universe_physics_profile_registry",
    "time_control_policy_registry_hash": "time_control_policy_registry",
    "dt_quantization_rule_registry_hash": "dt_quantization_rule_registry",
    "compaction_policy_registry_hash": "compaction_policy_registry",
    "time_model_registry_hash": "time_model_registry",
    "numeric_precision_policy_registry_hash": "numeric_precision_policy_registry",
    "tier_taxonomy_registry_hash": "tier_taxonomy_registry",
    "transition_policy_registry_hash": "transition_policy_registry",
    "arbitration_rule_registry_hash": "arbitration_rule_registry",
    "budget_envelope_registry_hash": "budget_envelope_registry",
    "arbitration_policy_registry_hash": "arbitration_policy_registry",
    "inspection_cache_policy_registry_hash": "inspection_cache_policy_registry",
    "inspection_section_registry_hash": "inspection_section_registry",
    "boundary_model_registry_hash": "boundary_model_registry",
    "conservation_contract_set_registry_hash": "conservation_contract_set_registry",
    "quantity_registry_hash": "quantity_registry",
    "exception_type_registry_hash": "exception_type_registry",
    "base_dimension_registry_hash": "base_dimension_registry",
    "dimension_registry_hash": "dimension_registry",
    "unit_registry_hash": "unit_registry",
    "quantity_type_registry_hash": "quantity_type_registry",
    "element_registry_hash": "element_registry",
    "compound_registry_hash": "compound_registry",
    "mixture_registry_hash": "mixture_registry",
    "material_class_registry_hash": "material_class_registry",
    "quality_distribution_registry_hash": "quality_distribution_registry",
    "part_class_registry_hash": "part_class_registry",
    "connection_type_registry_hash": "connection_type_registry",
    "blueprint_registry_hash": "blueprint_registry",
    "interior_volume_type_registry_hash": "interior_volume_type_registry",
    "portal_type_registry_hash": "portal_type_registry",
    "compartment_flow_policy_registry_hash": "compartment_flow_policy_registry",
    "portal_flow_template_registry_hash": "portal_flow_template_registry",
    "logistics_routing_rule_registry_hash": "logistics_routing_rule_registry",
    "logistics_graph_registry_hash": "logistics_graph_registry",
    "provenance_event_type_registry_hash": "provenance_event_type_registry",
    "construction_policy_registry_hash": "construction_policy_registry",
    "failure_mode_registry_hash": "failure_mode_registry",
    "maintenance_policy_registry_hash": "maintenance_policy_registry",
    "backlog_growth_rule_registry_hash": "backlog_growth_rule_registry",
    "commitment_type_registry_hash": "commitment_type_registry",
    "causality_strictness_registry_hash": "causality_strictness_registry",
    "domain_registry_hash": "domain_registry",
    "law_registry_hash": "law_registry",
    "experience_registry_hash": "experience_registry",
    "lens_registry_hash": "lens_registry",
    "control_action_registry_hash": "control_action_registry",
    "control_policy_registry_hash": "control_policy_registry",
    "effect_type_registry_hash": "effect_type_registry",
    "stacking_policy_registry_hash": "stacking_policy_registry",
    "safety_pattern_registry_hash": "safety_pattern_registry",
    "spec_type_registry_hash": "spec_type_registry",
    "tolerance_policy_registry_hash": "tolerance_policy_registry",
    "compliance_check_registry_hash": "compliance_check_registry",
    "formalization_target_registry_hash": "formalization_target_registry",
    "formalization_policy_registry_hash": "formalization_policy_registry",
    "interaction_action_registry_hash": "interaction_action_registry",
    "surface_type_registry_hash": "surface_type_registry",
    "posture_registry_hash": "posture_registry",
    "mount_tag_registry_hash": "mount_tag_registry",
    "control_binding_registry_hash": "control_binding_registry",
    "geometry_type_registry_hash": "geometry_type_registry",
    "junction_type_registry_hash": "junction_type_registry",
    "geometry_snap_policy_registry_hash": "geometry_snap_policy_registry",
    "mobility_vehicle_class_registry_hash": "mobility_vehicle_class_registry",
    "mobility_constraint_type_registry_hash": "mobility_constraint_type_registry",
    "mobility_signal_type_registry_hash": "mobility_signal_type_registry",
    "signal_type_registry_hash": "signal_type_registry",
    "signal_rule_policy_registry_hash": "signal_rule_policy_registry",
    "mobility_speed_policy_registry_hash": "mobility_speed_policy_registry",
    "port_type_registry_hash": "port_type_registry",
    "tool_tag_registry_hash": "tool_tag_registry",
    "tool_type_registry_hash": "tool_type_registry",
    "tool_effect_model_registry_hash": "tool_effect_model_registry",
    "surface_visibility_policy_registry_hash": "surface_visibility_policy_registry",
    "port_visibility_policy_registry_hash": "port_visibility_policy_registry",
    "machine_type_registry_hash": "machine_type_registry",
    "machine_operation_registry_hash": "machine_operation_registry",
    "task_type_registry_hash": "task_type_registry",
    "progress_model_registry_hash": "progress_model_registry",
    "controller_type_registry_hash": "controller_type_registry",
    "governance_type_registry_hash": "governance_type_registry",
    "diplomatic_state_registry_hash": "diplomatic_state_registry",
    "cohort_mapping_policy_registry_hash": "cohort_mapping_policy_registry",
    "order_type_registry_hash": "order_type_registry",
    "role_registry_hash": "role_registry",
    "institution_type_registry_hash": "institution_type_registry",
    "demography_policy_registry_hash": "demography_policy_registry",
    "death_model_registry_hash": "death_model_registry",
    "birth_model_registry_hash": "birth_model_registry",
    "migration_model_registry_hash": "migration_model_registry",
    "body_shape_registry_hash": "body_shape_registry",
    "view_mode_registry_hash": "view_mode_registry",
    "view_policy_registry_hash": "view_policy_registry",
    "instrument_type_registry_hash": "instrument_type_registry",
    "calibration_model_registry_hash": "calibration_model_registry",
    "render_proxy_registry_hash": "render_proxy_registry",
    "cosmetic_registry_hash": "cosmetic_registry",
    "cosmetic_policy_registry_hash": "cosmetic_policy_registry",
    "render_primitive_registry_hash": "render_primitive_registry",
    "procedural_material_template_registry_hash": "procedural_material_template_registry",
    "label_policy_registry_hash": "label_policy_registry",
    "lod_policy_registry_hash": "lod_policy_registry",
    "representation_rule_registry_hash": "representation_rule_registry",
    "net_replication_policy_registry_hash": "net_replication_policy_registry",
    "net_resync_strategy_registry_hash": "net_resync_strategy_registry",
    "net_server_policy_registry_hash": "net_server_policy_registry",
    "securex_policy_registry_hash": "securex_policy_registry",
    "server_profile_registry_hash": "server_profile_registry",
    "shard_map_registry_hash": "shard_map_registry",
    "perception_interest_policy_registry_hash": "perception_interest_policy_registry",
    "epistemic_policy_registry_hash": "epistemic_policy_registry",
    "retention_policy_registry_hash": "retention_policy_registry",
    "decay_model_registry_hash": "decay_model_registry",
    "eviction_rule_registry_hash": "eviction_rule_registry",
    "anti_cheat_policy_registry_hash": "anti_cheat_policy_registry",
    "anti_cheat_module_registry_hash": "anti_cheat_module_registry",
    "activation_policy_registry_hash": "activation_policy_registry",
    "budget_policy_registry_hash": "budget_policy_registry",
    "fidelity_policy_registry_hash": "fidelity_policy_registry",
    "worldgen_constraints_registry_hash": "worldgen_constraints_registry",
    "astronomy_catalog_index_hash": "astronomy_catalog_index",
    "site_registry_index_hash": "site_registry_index",
    "ephemeris_registry_hash": "ephemeris_registry",
    "terrain_tile_registry_hash": "terrain_tile_registry",
    "ui_registry_hash": "ui_registry",
}
REGISTRY_FILE_MAP = {
    "universe_physics_profile_registry_hash": "universe_physics_profile.registry.json",
    "time_control_policy_registry_hash": "time_control_policy.registry.json",
    "dt_quantization_rule_registry_hash": "dt_quantization_rule.registry.json",
    "compaction_policy_registry_hash": "compaction_policy.registry.json",
    "time_model_registry_hash": "time_model.registry.json",
    "numeric_precision_policy_registry_hash": "numeric_precision_policy.registry.json",
    "tier_taxonomy_registry_hash": "tier_taxonomy.registry.json",
    "transition_policy_registry_hash": "transition_policy.registry.json",
    "arbitration_rule_registry_hash": "arbitration_rule.registry.json",
    "budget_envelope_registry_hash": "budget_envelope.registry.json",
    "arbitration_policy_registry_hash": "arbitration_policy.registry.json",
    "inspection_cache_policy_registry_hash": "inspection_cache_policy.registry.json",
    "inspection_section_registry_hash": "inspection_section.registry.json",
    "boundary_model_registry_hash": "boundary_model.registry.json",
    "conservation_contract_set_registry_hash": "conservation_contract_set.registry.json",
    "quantity_registry_hash": "quantity.registry.json",
    "exception_type_registry_hash": "exception_type.registry.json",
    "base_dimension_registry_hash": "base_dimension.registry.json",
    "dimension_registry_hash": "dimension.registry.json",
    "unit_registry_hash": "unit.registry.json",
    "quantity_type_registry_hash": "quantity_type.registry.json",
    "element_registry_hash": "element.registry.json",
    "compound_registry_hash": "compound.registry.json",
    "mixture_registry_hash": "mixture.registry.json",
    "material_class_registry_hash": "material_class.registry.json",
    "quality_distribution_registry_hash": "quality_distribution.registry.json",
    "part_class_registry_hash": "part_class.registry.json",
    "connection_type_registry_hash": "connection_type.registry.json",
    "blueprint_registry_hash": "blueprint.registry.json",
    "interior_volume_type_registry_hash": "interior_volume_type.registry.json",
    "portal_type_registry_hash": "portal_type.registry.json",
    "compartment_flow_policy_registry_hash": "compartment_flow_policy.registry.json",
    "portal_flow_template_registry_hash": "portal_flow_template.registry.json",
    "logistics_routing_rule_registry_hash": "logistics_routing_rule.registry.json",
    "logistics_graph_registry_hash": "logistics_graph.registry.json",
    "provenance_event_type_registry_hash": "provenance_event_type.registry.json",
    "construction_policy_registry_hash": "construction_policy.registry.json",
    "failure_mode_registry_hash": "failure_mode.registry.json",
    "maintenance_policy_registry_hash": "maintenance_policy.registry.json",
    "backlog_growth_rule_registry_hash": "backlog_growth_rule.registry.json",
    "commitment_type_registry_hash": "commitment_type.registry.json",
    "causality_strictness_registry_hash": "causality_strictness.registry.json",
    "domain_registry_hash": "domain.registry.json",
    "law_registry_hash": "law.registry.json",
    "experience_registry_hash": "experience.registry.json",
    "lens_registry_hash": "lens.registry.json",
    "control_action_registry_hash": "control_action.registry.json",
    "control_policy_registry_hash": "control_policy.registry.json",
    "effect_type_registry_hash": "effect_type.registry.json",
    "stacking_policy_registry_hash": "stacking_policy.registry.json",
    "safety_pattern_registry_hash": "safety_pattern.registry.json",
    "spec_type_registry_hash": "spec_type.registry.json",
    "tolerance_policy_registry_hash": "tolerance_policy.registry.json",
    "compliance_check_registry_hash": "compliance_check.registry.json",
    "formalization_target_registry_hash": "formalization_target.registry.json",
    "formalization_policy_registry_hash": "formalization_policy.registry.json",
    "interaction_action_registry_hash": "interaction_action.registry.json",
    "surface_type_registry_hash": "surface_type.registry.json",
    "posture_registry_hash": "posture.registry.json",
    "mount_tag_registry_hash": "mount_tag.registry.json",
    "control_binding_registry_hash": "control_binding.registry.json",
    "geometry_type_registry_hash": "geometry_type.registry.json",
    "junction_type_registry_hash": "junction_type.registry.json",
    "geometry_snap_policy_registry_hash": "geometry_snap_policy.registry.json",
    "mobility_vehicle_class_registry_hash": "mobility_vehicle_class.registry.json",
    "mobility_constraint_type_registry_hash": "mobility_constraint_type.registry.json",
    "mobility_signal_type_registry_hash": "mobility_signal_type.registry.json",
    "signal_type_registry_hash": "signal_type.registry.json",
    "signal_rule_policy_registry_hash": "signal_rule_policy.registry.json",
    "mobility_speed_policy_registry_hash": "mobility_speed_policy.registry.json",
    "port_type_registry_hash": "port_type.registry.json",
    "tool_tag_registry_hash": "tool_tag.registry.json",
    "tool_type_registry_hash": "tool_type.registry.json",
    "tool_effect_model_registry_hash": "tool_effect_model.registry.json",
    "surface_visibility_policy_registry_hash": "surface_visibility_policy.registry.json",
    "port_visibility_policy_registry_hash": "port_visibility_policy.registry.json",
    "machine_type_registry_hash": "machine_type.registry.json",
    "machine_operation_registry_hash": "machine_operation.registry.json",
    "task_type_registry_hash": "task_type.registry.json",
    "progress_model_registry_hash": "progress_model.registry.json",
    "controller_type_registry_hash": "controller_type.registry.json",
    "governance_type_registry_hash": "governance_type.registry.json",
    "diplomatic_state_registry_hash": "diplomatic_state.registry.json",
    "cohort_mapping_policy_registry_hash": "cohort_mapping_policy.registry.json",
    "order_type_registry_hash": "order_type.registry.json",
    "role_registry_hash": "role.registry.json",
    "institution_type_registry_hash": "institution_type.registry.json",
    "demography_policy_registry_hash": "demography_policy.registry.json",
    "death_model_registry_hash": "death_model.registry.json",
    "birth_model_registry_hash": "birth_model.registry.json",
    "migration_model_registry_hash": "migration_model.registry.json",
    "body_shape_registry_hash": "body_shape.registry.json",
    "view_mode_registry_hash": "view_mode.registry.json",
    "view_policy_registry_hash": "view_policy.registry.json",
    "instrument_type_registry_hash": "instrument_type.registry.json",
    "calibration_model_registry_hash": "calibration_model.registry.json",
    "render_proxy_registry_hash": "render_proxy.registry.json",
    "cosmetic_registry_hash": "cosmetic.registry.json",
    "cosmetic_policy_registry_hash": "cosmetic_policy.registry.json",
    "render_primitive_registry_hash": "render_primitive.registry.json",
    "procedural_material_template_registry_hash": "procedural_material_template.registry.json",
    "label_policy_registry_hash": "label_policy.registry.json",
    "lod_policy_registry_hash": "lod_policy.registry.json",
    "representation_rule_registry_hash": "representation_rule.registry.json",
    "net_replication_policy_registry_hash": "net_replication_policy.registry.json",
    "net_resync_strategy_registry_hash": "net_resync_strategy.registry.json",
    "net_server_policy_registry_hash": "net_server_policy.registry.json",
    "securex_policy_registry_hash": "securex_policy.registry.json",
    "server_profile_registry_hash": "server_profile.registry.json",
    "shard_map_registry_hash": "shard_map.registry.json",
    "perception_interest_policy_registry_hash": "perception_interest_policy.registry.json",
    "epistemic_policy_registry_hash": "epistemic_policy.registry.json",
    "retention_policy_registry_hash": "retention_policy.registry.json",
    "decay_model_registry_hash": "decay_model.registry.json",
    "eviction_rule_registry_hash": "eviction_rule.registry.json",
    "anti_cheat_policy_registry_hash": "anti_cheat_policy.registry.json",
    "anti_cheat_module_registry_hash": "anti_cheat_module.registry.json",
    "activation_policy_registry_hash": "activation_policy.registry.json",
    "budget_policy_registry_hash": "budget_policy.registry.json",
    "fidelity_policy_registry_hash": "fidelity_policy.registry.json",
    "worldgen_constraints_registry_hash": "worldgen_constraints.registry.json",
    "astronomy_catalog_index_hash": "astronomy.catalog.index.json",
    "site_registry_index_hash": "site.registry.index.json",
    "ephemeris_registry_hash": "ephemeris.registry.json",
    "terrain_tile_registry_hash": "terrain.tile.registry.json",
    "ui_registry_hash": "ui.registry.json",
}


def _load_schema_validated(repo_root: str, schema_name: str, path: str) -> Tuple[dict, Dict[str, object]]:
    artifact_kind = {
        "universe_state": "save_file",
        "pack_lock": "pack_lock",
    }.get(str(schema_name or "").strip(), "")
    if artifact_kind:
        payload, _meta, error = load_versioned_artifact(
            repo_root=repo_root,
            artifact_kind=artifact_kind,
            path=path,
            allow_read_only=False,
            strip_loaded_metadata=(artifact_kind == "save_file"),
        )
        if error:
            return {}, error
        return payload, {}
    payload, err = read_json_object(path)
    if err:
        return {}, refusal(
            "REFUSE_JSON_LOAD_FAILED",
            "unable to parse required JSON file",
            "Ensure the file exists and contains valid JSON object content.",
            {"path": norm(path)},
            "$",
        )
    valid = validate_instance(repo_root=repo_root, schema_name=schema_name, payload=payload, strict_top_level=True)
    if not bool(valid.get("valid", False)):
        return {}, refusal(
            "REFUSE_SCHEMA_INVALID",
            "payload failed schema validation for '{}'".format(schema_name),
            "Fix file fields to satisfy schema validation and retry.",
            {"schema_id": schema_name, "path": norm(path)},
            "$",
        )
    return payload, {}


def _resolve_lockfile_path(repo_root: str, lockfile_path: str) -> str:
    token = str(lockfile_path or "").strip()
    if not token:
        return os.path.join(repo_root, "build", "lockfile.json")
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(repo_root, token))


def _resolve_registries_dir(repo_root: str, registries_dir: str) -> str:
    token = str(registries_dir or "").strip()
    if not token:
        return os.path.join(repo_root, "build", "registries")
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(repo_root, token))


def _latest_run_meta(save_dir: str) -> Tuple[dict, str]:
    run_meta_dir = os.path.join(save_dir, "run_meta")
    if not os.path.isdir(run_meta_dir):
        return {}, ""
    names = sorted(name for name in os.listdir(run_meta_dir) if str(name).endswith(".json"))
    if not names:
        return {}, ""
    best_payload = {}
    best_path = ""
    best_key = ("", "", "", "")
    for rel_name in names:
        abs_path = os.path.join(run_meta_dir, rel_name)
        payload, err = read_json_object(abs_path)
        if err:
            continue
        key = (
            str(payload.get("stopped_utc", "")),
            str(payload.get("started_utc", "")),
            str(payload.get("run_id", "")),
            str(rel_name),
        )
        if key >= best_key:
            best_key = key
            best_payload = payload
            best_path = abs_path
    if not best_path:
        return {}, ""
    return best_payload, best_path


def _load_lockfile(
    repo_root: str,
    compile_if_missing: bool,
    bundle_id: str,
    mod_policy_id: str = DEFAULT_MOD_POLICY_ID,
    lockfile_path: str = "",
) -> Tuple[dict, Dict[str, object]]:
    lock_path = _resolve_lockfile_path(repo_root, lockfile_path)
    default_lock_path = _resolve_lockfile_path(repo_root, "")
    if not os.path.isfile(lock_path):
        if not compile_if_missing:
            return {}, refusal(
                "REFUSE_LOCKFILE_MISSING",
                "{} is missing".format(norm(os.path.relpath(lock_path, repo_root))),
                "Run tools/xstack/lockfile_build --bundle {} --out {}.".format(
                    bundle_id,
                    norm(os.path.relpath(lock_path, repo_root)),
                ),
                {"bundle_id": bundle_id},
                "$.lockfile",
            )
        if os.path.normcase(lock_path) != os.path.normcase(default_lock_path):
            return {}, refusal(
                "REFUSE_LOCKFILE_MISSING",
                "explicit lockfile path is missing and cannot be auto-generated",
                "Generate lockfile at the requested path before boot, or omit lockfile override.",
                {"bundle_id": bundle_id},
                "$.lockfile",
            )
        compiled = compile_bundle(
            repo_root=repo_root,
            bundle_id=bundle_id,
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            mod_policy_id=str(mod_policy_id or DEFAULT_MOD_POLICY_ID),
            use_cache=True,
        )
        if compiled.get("result") != "complete":
            return {}, refusal(
                "REFUSE_LOCKFILE_GENERATION_FAILED",
                "unable to generate lockfile for bundle '{}'".format(bundle_id),
                "Resolve registry compile refusal and rerun boot.",
                {"bundle_id": bundle_id},
                "$.lockfile",
            )
    return _load_schema_validated(repo_root=repo_root, schema_name="bundle_lockfile", path=lock_path)


def _validate_registry_hashes(
    repo_root: str,
    lockfile_payload: dict,
    compile_if_missing: bool,
    bundle_id: str,
    mod_policy_id: str = DEFAULT_MOD_POLICY_ID,
    registries_dir: str = "",
) -> Dict[str, object]:
    registries_abs = _resolve_registries_dir(repo_root, registries_dir)
    default_registries_abs = _resolve_registries_dir(repo_root, "")
    registries = lockfile_payload.get("registries")
    if not isinstance(registries, dict):
        return refusal(
            "REFUSE_LOCKFILE_REGISTRY_SECTION_MISSING",
            "lockfile registries section is missing",
            "Rebuild lockfile and ensure registries section exists.",
            {"bundle_id": bundle_id},
            "$.registries",
        )

    missing_files = []
    for key in sorted(REGISTRY_HASH_KEY_MAP.keys()):
        schema_key = REGISTRY_HASH_KEY_MAP[key]
        name = REGISTRY_OUTPUT_FILENAMES[schema_key]
        abs_path = os.path.join(registries_abs, name)
        if not os.path.isfile(abs_path):
            missing_files.append(abs_path)
    if missing_files and compile_if_missing:
        if os.path.normcase(registries_abs) != os.path.normcase(default_registries_abs):
            return refusal(
                "REFUSE_REGISTRY_MISSING",
                "explicit registries path is missing required files and cannot be auto-generated",
                "Generate registries at the requested path before boot, or omit registries override.",
                {"bundle_id": bundle_id},
                "$.registries",
            )
        compiled = compile_bundle(
            repo_root=repo_root,
            bundle_id=bundle_id,
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            mod_policy_id=str(mod_policy_id or DEFAULT_MOD_POLICY_ID),
            use_cache=True,
        )
        if compiled.get("result") != "complete":
            return refusal(
                "REFUSE_REGISTRY_COMPILE_FAILED",
                "unable to compile missing registries",
                "Resolve registry compile refusal and retry boot.",
                {"bundle_id": bundle_id},
                "$.registries",
            )
        # Reload lockfile since compile may regenerate it.
        lock_reloaded, lock_error = _load_schema_validated(
            repo_root=repo_root,
            schema_name="bundle_lockfile",
            path=os.path.join(repo_root, "build", "lockfile.json"),
        )
        if lock_error:
            return lock_error
        lockfile_payload.clear()
        lockfile_payload.update(lock_reloaded)
        registries = lockfile_payload.get("registries") or {}

    for key in sorted(REGISTRY_HASH_KEY_MAP.keys()):
        schema_key = REGISTRY_HASH_KEY_MAP[key]
        file_name = REGISTRY_OUTPUT_FILENAMES[schema_key]
        abs_path = os.path.join(registries_abs, file_name)
        if not os.path.isfile(abs_path):
            return refusal(
                "REFUSE_REGISTRY_MISSING",
                "required registry file '{}' is missing".format(norm(os.path.relpath(abs_path, repo_root))),
                "Run tools/xstack/registry_compile --bundle {} and retry.".format(bundle_id),
                {"registry_file": file_name},
                "$.registries",
            )
        payload, err = read_json_object(abs_path)
        if err:
            return refusal(
                "REFUSE_REGISTRY_INVALID_JSON",
                "registry file '{}' is invalid JSON".format(norm(os.path.relpath(abs_path, repo_root))),
                "Rebuild registries and retry.",
                {"registry_file": file_name},
                "$.registries",
            )
        expected = str(registries.get(key, "")).strip()
        actual = str(payload.get("registry_hash", "")).strip() or canonical_sha256(payload)
        if expected != actual:
            return refusal(
                "REFUSE_REGISTRY_HASH_MISMATCH",
                "registry hash mismatch for '{}'".format(file_name),
                "Rebuild lockfile and registries from the same bundle inputs.",
                {
                    "registry_file": file_name,
                    "expected_hash": expected,
                    "actual_hash": actual,
                },
                "$.registries.{}".format(key),
            )
    return {"result": "complete"}


def _load_registry_payload(
    repo_root: str,
    file_name: str,
    expected_hash: str,
    registries_dir: str = "",
) -> Tuple[dict, Dict[str, object]]:
    abs_path = os.path.join(_resolve_registries_dir(repo_root, registries_dir), file_name)
    payload, err = read_json_object(abs_path)
    if err:
        return {}, refusal(
            "REFUSE_REGISTRY_INVALID_JSON",
            "registry file '{}' is invalid JSON".format(norm(os.path.relpath(abs_path, repo_root))),
            "Rebuild registries and retry.",
            {"registry_file": file_name},
            "$.registries",
        )
    actual_hash = str(payload.get("registry_hash", "")).strip() or canonical_sha256(payload)
    if str(expected_hash).strip() != actual_hash:
        return {}, refusal(
            "REFUSE_REGISTRY_HASH_MISMATCH",
            "registry hash mismatch for '{}'".format(file_name),
            "Rebuild lockfile and registries from identical bundle inputs.",
            {"registry_file": file_name},
            "$.registries",
        )
    return payload, {}


def _select_law_profile(law_registry: dict, law_profile_id: str) -> Tuple[dict, Dict[str, object]]:
    for row in sorted((law_registry.get("law_profiles") or []), key=lambda item: str(item.get("law_profile_id", ""))):
        if str(row.get("law_profile_id", "")).strip() == str(law_profile_id).strip():
            return dict(row), {}
    return {}, refusal(
        "LAW_PROFILE_NOT_FOUND",
        "law profile '{}' is not present in compiled law registry".format(str(law_profile_id)),
        "Select a LawProfile listed in build/registries/law.registry.json and rebuild SessionSpec.",
        {"law_profile_id": str(law_profile_id)},
        "$.authority_context.law_profile_id",
    )


def _select_lens_profile(
    lens_registry: dict,
    experience_registry: dict,
    experience_id: str,
    law_profile: dict,
) -> Tuple[dict, Dict[str, object]]:
    default_lens_id = ""
    for row in sorted((experience_registry.get("experience_profiles") or []), key=lambda item: str(item.get("experience_id", ""))):
        if str(row.get("experience_id", "")).strip() == str(experience_id).strip():
            default_lens_id = str(row.get("default_lens_id", "")).strip()
            if not default_lens_id:
                allowed = sorted(str(item).strip() for item in (law_profile.get("allowed_lenses") or []) if str(item).strip())
                default_lens_id = allowed[0] if allowed else ""
            break
    if not default_lens_id:
        allowed = sorted(str(item).strip() for item in (law_profile.get("allowed_lenses") or []) if str(item).strip())
        default_lens_id = allowed[0] if allowed else ""

    if not default_lens_id:
        return {}, refusal(
            "LENS_NOT_FOUND",
            "no default lens could be resolved for experience '{}'".format(str(experience_id)),
            "Set experience default_lens_id or allow at least one lens in the active LawProfile.",
            {"experience_id": str(experience_id)},
            "$.experience_id",
        )

    for row in sorted((lens_registry.get("lenses") or []), key=lambda item: str(item.get("lens_id", ""))):
        if str(row.get("lens_id", "")).strip() == default_lens_id:
            return dict(row), {}
    return {}, refusal(
        "LENS_NOT_FOUND",
        "lens '{}' is not present in compiled lens registry".format(default_lens_id),
        "Select a lens listed in build/registries/lens.registry.json.",
        {"lens_id": default_lens_id},
        "$.lens_id",
    )


def _select_policy_entry(registry_payload: dict, key: str, policy_id: str, refusal_code: str, registry_file: str) -> Tuple[dict, Dict[str, object]]:
    rows = registry_payload.get(key)
    if not isinstance(rows, list):
        return {}, refusal(
            refusal_code,
            "policy registry '{}' is missing key '{}'".format(registry_file, key),
            "Rebuild registries and ensure policy rows are present.",
            {"registry_file": registry_file, "policy_id": policy_id},
            "$.{}".format(key),
        )
    for row in sorted(rows, key=lambda item: str(item.get("policy_id", ""))):
        if str(row.get("policy_id", "")).strip() == str(policy_id).strip():
            return dict(row), {}
    return {}, refusal(
        refusal_code,
        "policy '{}' is not present in compiled registry '{}'".format(str(policy_id), registry_file),
        "Select a policy ID listed in '{}' and rebuild SessionSpec.".format(registry_file),
        {"policy_id": str(policy_id)},
        "$.policy_id",
    )


def _select_time_control_policy(
    *,
    time_control_policy_registry: dict,
    dt_quantization_rule_registry: dict,
    compaction_policy_registry: dict,
    time_model_registry: dict,
    selected_physics_profile: dict,
    requested_time_control_policy_id: str,
) -> Tuple[dict, dict, dict, dict, Dict[str, object]]:
    policy_rows = list(time_control_policy_registry.get("policies") or [])
    if not isinstance(policy_rows, list):
        return {}, {}, {}, {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_FOUND",
            "time control policy registry is missing policies list",
            "Rebuild registries and ensure time control policies are present.",
            {"registry_file": REGISTRY_FILE_MAP["time_control_policy_registry_hash"]},
            "$.policies",
        )
    requested_policy_id = str(requested_time_control_policy_id or "").strip()
    policy_id = requested_policy_id or "time.policy.null"
    selected_policy = {}
    for row in sorted((item for item in policy_rows if isinstance(item, dict)), key=lambda item: str(item.get("time_control_policy_id", ""))):
        if str(row.get("time_control_policy_id", "")).strip() == policy_id:
            selected_policy = dict(row)
            break
    if not selected_policy and (not requested_policy_id):
        for row in sorted((item for item in policy_rows if isinstance(item, dict)), key=lambda item: str(item.get("time_control_policy_id", ""))):
            selected_policy = dict(row)
            policy_id = str(selected_policy.get("time_control_policy_id", "")).strip()
            if policy_id:
                break
    if not selected_policy:
        return {}, {}, {}, {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_FOUND",
            "time control policy '{}' is not present in compiled registry".format(policy_id or "<empty>"),
            "Select a policy ID listed in '{}' and rebuild SessionSpec.".format(REGISTRY_FILE_MAP["time_control_policy_registry_hash"]),
            {"time_control_policy_id": policy_id},
            "$.time_control_policy_id",
        )

    dt_rule_id = str(selected_policy.get("dt_quantization_rule_id", "")).strip()
    dt_rows = list(dt_quantization_rule_registry.get("rules") or [])
    selected_dt_rule = {}
    for row in sorted((item for item in dt_rows if isinstance(item, dict)), key=lambda item: str(item.get("dt_rule_id", ""))):
        if str(row.get("dt_rule_id", "")).strip() == dt_rule_id:
            selected_dt_rule = dict(row)
            break
    if not selected_dt_rule:
        return {}, {}, {}, {}, refusal(
            "REFUSE_DT_RULE_NOT_FOUND",
            "time control policy '{}' references unknown dt_quantization_rule_id '{}'".format(policy_id, dt_rule_id or "<empty>"),
            "Select a valid dt quantization rule from '{}'.".format(REGISTRY_FILE_MAP["dt_quantization_rule_registry_hash"]),
            {"time_control_policy_id": policy_id, "dt_quantization_rule_id": dt_rule_id},
            "$.time_control_policy_id",
        )

    compaction_policy_id = str(selected_policy.get("compaction_policy_id", "")).strip()
    compaction_rows = list(compaction_policy_registry.get("policies") or [])
    selected_compaction_policy = {}
    for row in sorted((item for item in compaction_rows if isinstance(item, dict)), key=lambda item: str(item.get("compaction_policy_id", ""))):
        if str(row.get("compaction_policy_id", "")).strip() == compaction_policy_id:
            selected_compaction_policy = dict(row)
            break
    if not selected_compaction_policy:
        return {}, {}, {}, {}, refusal(
            "REFUSE_COMPACTION_POLICY_NOT_FOUND",
            "time control policy '{}' references unknown compaction_policy_id '{}'".format(policy_id, compaction_policy_id or "<empty>"),
            "Select a valid compaction policy from '{}'.".format(REGISTRY_FILE_MAP["compaction_policy_registry_hash"]),
            {"time_control_policy_id": policy_id, "compaction_policy_id": compaction_policy_id},
            "$.time_control_policy_id",
        )

    time_model_id = str((selected_physics_profile or {}).get("time_model_id", "")).strip()
    time_model_rows = list(time_model_registry.get("time_models") or [])
    selected_time_model = {}
    for row in sorted((item for item in time_model_rows if isinstance(item, dict)), key=lambda item: str(item.get("time_model_id", ""))):
        if str(row.get("time_model_id", "")).strip() == time_model_id:
            selected_time_model = dict(row)
            break
    if not selected_time_model:
        return {}, {}, {}, {}, refusal(
            "REFUSE_TIME_MODEL_NOT_FOUND",
            "physics profile references unknown time_model_id '{}'".format(time_model_id or "<empty>"),
            "Select a valid UniversePhysicsProfile time_model_id.",
            {"time_model_id": time_model_id},
            "$.physics_profile_id",
        )

    extensions = dict(selected_policy.get("extensions") or {})
    allowed_models = sorted(
        set(str(item).strip() for item in (extensions.get("allowed_time_model_ids") or []) if str(item).strip())
    )
    if allowed_models and time_model_id not in set(allowed_models):
        return {}, {}, {}, {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_ALLOWED_BY_PHYSICS",
            "time control policy '{}' is not allowed for time_model_id '{}'".format(policy_id, time_model_id),
            "Select a compatible time_control_policy_id for the active physics profile.",
            {
                "time_control_policy_id": policy_id,
                "time_model_id": time_model_id,
            },
            "$.time_control_policy_id",
        )

    allow_variable_dt = bool(selected_policy.get("allow_variable_dt", False))
    if allow_variable_dt and not bool(selected_time_model.get("allow_variable_dt", False)):
        return {}, {}, {}, {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_ALLOWED_BY_PHYSICS",
            "time control policy '{}' requires variable dt but active time model forbids it".format(policy_id),
            "Choose a non-variable-dt policy or a compatible physics profile time model.",
            {
                "time_control_policy_id": policy_id,
                "time_model_id": time_model_id,
            },
            "$.time_control_policy_id",
        )

    allow_branching = bool(extensions.get("allow_branching", False))
    if allow_branching and not bool(selected_time_model.get("allow_branching", False)):
        return {}, {}, {}, {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_ALLOWED_BY_PHYSICS",
            "time control policy '{}' enables branching while active time model forbids it".format(policy_id),
            "Choose a compatible policy/time_model combination.",
            {
                "time_control_policy_id": policy_id,
                "time_model_id": time_model_id,
            },
            "$.time_control_policy_id",
        )

    return selected_policy, selected_dt_rule, selected_compaction_policy, selected_time_model, {}


def _select_transition_policy(
    *,
    transition_policy_registry: dict,
    selected_physics_profile: dict,
    requested_transition_policy_id: str = "",
) -> Tuple[dict, Dict[str, object]]:
    policy_rows = list(transition_policy_registry.get("policies") or [])
    if not isinstance(policy_rows, list):
        return {}, refusal(
            "REFUSE_TRANSITION_POLICY_NOT_FOUND",
            "transition policy registry is missing policies list",
            "Rebuild registries and ensure transition policies are present.",
            {"registry_file": REGISTRY_FILE_MAP["transition_policy_registry_hash"]},
            "$.policies",
        )

    profile_extensions = dict((selected_physics_profile or {}).get("extensions") or {})
    requested_policy_id = str(requested_transition_policy_id or "").strip()
    default_policy_id = str(profile_extensions.get("default_transition_policy_id", "")).strip()
    policy_id = requested_policy_id or default_policy_id or "transition.policy.null"

    selected_policy = {}
    for row in sorted(
        (item for item in policy_rows if isinstance(item, dict)),
        key=lambda item: str(item.get("transition_policy_id", "")),
    ):
        if str(row.get("transition_policy_id", "")).strip() == policy_id:
            selected_policy = dict(row)
            break

    if not selected_policy and (not requested_policy_id):
        for row in sorted(
            (item for item in policy_rows if isinstance(item, dict)),
            key=lambda item: str(item.get("transition_policy_id", "")),
        ):
            selected_policy = dict(row)
            policy_id = str(selected_policy.get("transition_policy_id", "")).strip()
            if policy_id:
                break

    if not selected_policy:
        return {}, refusal(
            "REFUSE_TRANSITION_POLICY_NOT_FOUND",
            "transition policy '{}' is not present in compiled registry".format(policy_id or "<empty>"),
            "Select a policy ID listed in '{}'.".format(REGISTRY_FILE_MAP["transition_policy_registry_hash"]),
            {"transition_policy_id": policy_id},
            "$.transition_policy_id",
        )

    allowed_policy_ids = sorted(
        set(str(item).strip() for item in (profile_extensions.get("allowed_transition_policy_ids") or []) if str(item).strip())
    )
    selected_policy_id = str(selected_policy.get("transition_policy_id", "")).strip()
    if allowed_policy_ids and selected_policy_id not in set(allowed_policy_ids):
        return {}, refusal(
            "REFUSE_TRANSITION_POLICY_NOT_ALLOWED_BY_PHYSICS",
            "transition policy '{}' is not allowed by the selected physics profile".format(selected_policy_id),
            "Select a transition policy listed in profile.extensions.allowed_transition_policy_ids.",
            {
                "transition_policy_id": selected_policy_id,
                "physics_profile_id": str((selected_physics_profile or {}).get("physics_profile_id", "")),
            },
            "$.transition_policy_id",
        )

    return selected_policy, {}


def _stage_command_for_transition(stage_id: str) -> str:
    if str(stage_id) == "stage.acquire_world":
        return "client.session.acquire.local"
    if str(stage_id) == "stage.verify_world":
        return "client.session.verify"
    if str(stage_id) == "stage.net_handshake":
        return "client.session.net.handshake"
    if str(stage_id) == "stage.net_sync_baseline":
        return "client.session.net.sync_baseline"
    if str(stage_id) == "stage.net_join_world":
        return "client.session.net.join_world"
    if str(stage_id) == "stage.warmup_simulation":
        return "client.session.warmup.simulation"
    if str(stage_id) == "stage.warmup_presentation":
        return "client.session.warmup.presentation"
    if str(stage_id) == "stage.session_ready":
        return "client.session.ready"
    if str(stage_id) == "stage.session_running":
        return "client.session.begin"
    if str(stage_id) == "stage.suspend_session":
        return "client.session.suspend"
    if str(stage_id) == "stage.resume_session":
        return "client.session.resume"
    if str(stage_id) == "stage.teardown_session":
        return "client.session.abort"
    return "client.session.stage"


def _simulate_boot_stage_log(
    pipeline_contract: dict,
    authority_context: dict,
    simulation_tick: int,
    stage_executor=None,
) -> Tuple[List[dict], str, Dict[str, object]]:
    pipeline = dict(pipeline_contract.get("pipeline") or {})
    stage_map = dict(pipeline_contract.get("stage_map") or {})
    stage_order = list(pipeline_contract.get("stage_order") or [])
    entry_stage_id = str(pipeline.get("entry_stage_id", "stage.resolve_session"))
    ready_stage_id = str(pipeline.get("ready_stage_id", "stage.session_ready"))
    if entry_stage_id not in stage_map or ready_stage_id not in stage_map:
        return [], "", refusal(
            "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
            "pipeline entry/ready stages are missing from stage registry map",
            "Fix session stage and pipeline registries so canonical stage IDs resolve.",
            {
                "entry_stage_id": entry_stage_id,
                "ready_stage_id": ready_stage_id,
            },
            "$.pipeline",
        )
    if entry_stage_id not in stage_order or ready_stage_id not in stage_order:
        return [], "", refusal(
            "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
            "pipeline stage order does not contain entry/ready stage IDs",
            "Fix pipeline stage ordering in data/registries/session_pipeline_registry.json.",
            {
                "entry_stage_id": entry_stage_id,
                "ready_stage_id": ready_stage_id,
            },
            "$.pipeline.stages",
        )
    start_index = int(stage_order.index(entry_stage_id))
    stop_index = int(stage_order.index(ready_stage_id))
    if stop_index < start_index:
        return [], "", refusal(
            "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
            "pipeline ready stage precedes entry stage",
            "Fix stage ordering so entry precedes ready.",
            {
                "entry_stage_id": entry_stage_id,
                "ready_stage_id": ready_stage_id,
            },
            "$.pipeline.stages",
        )

    current_stage_id = entry_stage_id
    observer_watermark = "OBSERVER MODE" if str(authority_context.get("privilege_level", "")).strip() == "observer" else ""
    stage_log: List[dict] = [
        {
            "stage_index": 0,
            "command_id": "client.boot.start",
            "from_stage_id": entry_stage_id,
            "to_stage_id": entry_stage_id,
            "status": "pass",
            "reason_code": "",
            "observer_watermark": observer_watermark,
        }
    ]
    for target_stage_id in stage_order[start_index + 1 : stop_index + 1]:
        stage_desc = dict(stage_map.get(current_stage_id) or {})
        allowed = sorted(set(str(item).strip() for item in (stage_desc.get("allowed_next_stage_ids") or []) if str(item).strip()))
        if str(target_stage_id) not in allowed:
            return [], "", refusal(
                "refusal.stage_invalid_transition",
                "stage transition '{}' -> '{}' is not allowed by stage registry".format(current_stage_id, target_stage_id),
                "Advance only through allowed_next_stage_ids from session_stage_registry.",
                {
                    "from_stage_id": current_stage_id,
                    "to_stage_id": str(target_stage_id),
                },
                "$.pipeline",
            )
        if str(target_stage_id) == "stage.session_ready" and int(simulation_tick) != 0:
            return [], "", refusal(
                "refusal.session_ready_time_nonzero",
                "SessionReady requires simulation_time.tick == 0",
                "Reset to tick=0 before entering stage.session_ready.",
                {"simulation_tick": str(int(simulation_tick))},
                "$.universe_state.simulation_time.tick",
            )
        stage_result = {"result": "complete"}
        if stage_executor is not None:
            stage_result = stage_executor(str(target_stage_id))
            if not isinstance(stage_result, dict):
                return [], "", refusal(
                    "refusal.stage_invalid_transition",
                    "stage executor returned invalid payload for '{}'".format(str(target_stage_id)),
                    "Fix stage executor contract to return deterministic object payloads.",
                    {"stage_id": str(target_stage_id)},
                    "$.stage_executor",
                )
            if str(stage_result.get("result", "")).strip() != "complete":
                return [], "", stage_result
        stage_log.append(
            {
                "stage_index": len(stage_log),
                "command_id": _stage_command_for_transition(str(target_stage_id)),
                "from_stage_id": current_stage_id,
                "to_stage_id": str(target_stage_id),
                "status": "pass",
                "reason_code": "",
                "details": dict(stage_result.get("details") or {}),
                "observer_watermark": observer_watermark,
            }
        )
        current_stage_id = str(target_stage_id)
    return stage_log, current_stage_id, {}


def boot_session_spec(
    repo_root: str,
    session_spec_path: str,
    bundle_id: str = "",
    compile_if_missing: bool = False,
    lockfile_path: str = "",
    registries_dir: str = "",
) -> Dict[str, object]:
    spec_abs = os.path.normpath(os.path.abspath(session_spec_path))
    session_spec, spec_error = _load_schema_validated(repo_root=repo_root, schema_name="session_spec", path=spec_abs)
    if spec_error:
        return spec_error
    pipeline_contract = load_session_pipeline_contract(
        repo_root=repo_root,
        pipeline_id=str(session_spec.get("pipeline_id", "")),
    )
    if pipeline_contract.get("result") != "complete":
        return pipeline_contract
    selected_pipeline_id = str(pipeline_contract.get("pipeline_id", DEFAULT_PIPELINE_ID))
    if str(session_spec.get("pipeline_id", "")).strip() and str(session_spec.get("pipeline_id", "")).strip() != selected_pipeline_id:
        return refusal(
            "REFUSE_SESSION_PIPELINE_UNKNOWN",
            "SessionSpec pipeline_id does not resolve in session pipeline registry",
            "Set SessionSpec pipeline_id to a declared pipeline identifier.",
            {
                "pipeline_id": str(session_spec.get("pipeline_id", "")).strip(),
            },
            "$.pipeline_id",
        )

    bundle_token = str(bundle_id).strip() or str(session_spec.get("bundle_id", "")).strip() or DEFAULT_BUNDLE_ID
    selected_mod_policy_id = str(session_spec.get("mod_policy_id", "")).strip() or DEFAULT_MOD_POLICY_ID
    lock_payload, lock_error = _load_lockfile(
        repo_root=repo_root,
        compile_if_missing=bool(compile_if_missing),
        bundle_id=bundle_token,
        mod_policy_id=selected_mod_policy_id,
        lockfile_path=lockfile_path,
    )
    if lock_error:
        return lock_error
    lock_semantic = validate_lockfile_payload(lock_payload)
    if lock_semantic.get("result") != "complete":
        return refusal(
            "REFUSE_LOCKFILE_HASH_INVALID",
            "lockfile failed deterministic pack_lock_hash validation",
            "Rebuild lockfile and retry boot.",
            {"bundle_id": bundle_token},
            "$.pack_lock_hash",
        )
    if str(lock_payload.get("bundle_id", "")).strip() != bundle_token:
        return refusal(
            "REFUSE_LOCKFILE_BUNDLE_MISMATCH",
            "lockfile bundle_id does not match requested/session bundle_id",
            "Regenerate lockfile with matching --bundle id.",
            {
                "bundle_id": bundle_token,
                "lockfile_bundle_id": str(lock_payload.get("bundle_id", "")),
            },
            "$.bundle_id",
        )

    registry_check = _validate_registry_hashes(
        repo_root=repo_root,
        lockfile_payload=lock_payload,
        compile_if_missing=bool(compile_if_missing),
        bundle_id=bundle_token,
        mod_policy_id=selected_mod_policy_id,
        registries_dir=registries_dir,
    )
    if registry_check.get("result") != "complete":
        return registry_check
    mod_policy_proof_bundle = proof_bundle_from_lockfile(lock_payload)
    mod_policy_enforcement = validate_saved_mod_policy(
        expected_mod_policy_id=selected_mod_policy_id,
        expected_registry_hash=str(session_spec.get("mod_policy_registry_hash", "")).strip(),
        actual_proof_bundle=mod_policy_proof_bundle,
    )
    if mod_policy_enforcement.get("result") != "complete":
        return mod_policy_enforcement

    registries = lock_payload.get("registries")
    if not isinstance(registries, dict):
        return refusal(
            "REFUSE_LOCKFILE_REGISTRY_SECTION_MISSING",
            "lockfile registries section is missing",
            "Rebuild lockfile with registry hashes and retry.",
            {"bundle_id": bundle_token},
            "$.registries",
        )

    universe_physics_profile_registry, universe_physics_profile_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["universe_physics_profile_registry_hash"],
        expected_hash=str(registries.get("universe_physics_profile_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if universe_physics_profile_registry_error:
        return universe_physics_profile_registry_error
    time_model_registry, time_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["time_model_registry_hash"],
        expected_hash=str(registries.get("time_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if time_model_registry_error:
        return time_model_registry_error
    time_control_policy_registry, time_control_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["time_control_policy_registry_hash"],
        expected_hash=str(registries.get("time_control_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if time_control_policy_registry_error:
        return time_control_policy_registry_error
    dt_quantization_rule_registry, dt_quantization_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["dt_quantization_rule_registry_hash"],
        expected_hash=str(registries.get("dt_quantization_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if dt_quantization_rule_registry_error:
        return dt_quantization_rule_registry_error
    compaction_policy_registry, compaction_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["compaction_policy_registry_hash"],
        expected_hash=str(registries.get("compaction_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if compaction_policy_registry_error:
        return compaction_policy_registry_error
    numeric_precision_policy_registry, numeric_precision_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["numeric_precision_policy_registry_hash"],
        expected_hash=str(registries.get("numeric_precision_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if numeric_precision_policy_registry_error:
        return numeric_precision_policy_registry_error
    tier_taxonomy_registry, tier_taxonomy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["tier_taxonomy_registry_hash"],
        expected_hash=str(registries.get("tier_taxonomy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if tier_taxonomy_registry_error:
        return tier_taxonomy_registry_error
    transition_policy_registry, transition_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["transition_policy_registry_hash"],
        expected_hash=str(registries.get("transition_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if transition_policy_registry_error:
        return transition_policy_registry_error
    arbitration_rule_registry, arbitration_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["arbitration_rule_registry_hash"],
        expected_hash=str(registries.get("arbitration_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if arbitration_rule_registry_error:
        return arbitration_rule_registry_error
    budget_envelope_registry, budget_envelope_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["budget_envelope_registry_hash"],
        expected_hash=str(registries.get("budget_envelope_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if budget_envelope_registry_error:
        return budget_envelope_registry_error
    arbitration_policy_registry, arbitration_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["arbitration_policy_registry_hash"],
        expected_hash=str(registries.get("arbitration_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if arbitration_policy_registry_error:
        return arbitration_policy_registry_error
    inspection_cache_policy_registry, inspection_cache_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["inspection_cache_policy_registry_hash"],
        expected_hash=str(registries.get("inspection_cache_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if inspection_cache_policy_registry_error:
        return inspection_cache_policy_registry_error
    inspection_section_registry, inspection_section_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["inspection_section_registry_hash"],
        expected_hash=str(registries.get("inspection_section_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if inspection_section_registry_error:
        return inspection_section_registry_error
    boundary_model_registry, boundary_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["boundary_model_registry_hash"],
        expected_hash=str(registries.get("boundary_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if boundary_model_registry_error:
        return boundary_model_registry_error
    conservation_contract_set_registry, conservation_contract_set_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["conservation_contract_set_registry_hash"],
        expected_hash=str(registries.get("conservation_contract_set_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if conservation_contract_set_registry_error:
        return conservation_contract_set_registry_error
    quantity_registry, quantity_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["quantity_registry_hash"],
        expected_hash=str(registries.get("quantity_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if quantity_registry_error:
        return quantity_registry_error
    exception_type_registry, exception_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["exception_type_registry_hash"],
        expected_hash=str(registries.get("exception_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if exception_type_registry_error:
        return exception_type_registry_error
    base_dimension_registry, base_dimension_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["base_dimension_registry_hash"],
        expected_hash=str(registries.get("base_dimension_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if base_dimension_registry_error:
        return base_dimension_registry_error
    dimension_registry, dimension_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["dimension_registry_hash"],
        expected_hash=str(registries.get("dimension_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if dimension_registry_error:
        return dimension_registry_error
    unit_registry, unit_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["unit_registry_hash"],
        expected_hash=str(registries.get("unit_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if unit_registry_error:
        return unit_registry_error
    quantity_type_registry, quantity_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["quantity_type_registry_hash"],
        expected_hash=str(registries.get("quantity_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if quantity_type_registry_error:
        return quantity_type_registry_error
    element_registry, element_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["element_registry_hash"],
        expected_hash=str(registries.get("element_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if element_registry_error:
        return element_registry_error
    compound_registry, compound_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["compound_registry_hash"],
        expected_hash=str(registries.get("compound_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if compound_registry_error:
        return compound_registry_error
    mixture_registry, mixture_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["mixture_registry_hash"],
        expected_hash=str(registries.get("mixture_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if mixture_registry_error:
        return mixture_registry_error
    material_class_registry, material_class_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["material_class_registry_hash"],
        expected_hash=str(registries.get("material_class_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if material_class_registry_error:
        return material_class_registry_error
    quality_distribution_registry, quality_distribution_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["quality_distribution_registry_hash"],
        expected_hash=str(registries.get("quality_distribution_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if quality_distribution_registry_error:
        return quality_distribution_registry_error
    part_class_registry, part_class_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["part_class_registry_hash"],
        expected_hash=str(registries.get("part_class_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if part_class_registry_error:
        return part_class_registry_error
    connection_type_registry, connection_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["connection_type_registry_hash"],
        expected_hash=str(registries.get("connection_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if connection_type_registry_error:
        return connection_type_registry_error
    blueprint_registry, blueprint_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["blueprint_registry_hash"],
        expected_hash=str(registries.get("blueprint_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if blueprint_registry_error:
        return blueprint_registry_error
    interior_volume_type_registry, interior_volume_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["interior_volume_type_registry_hash"],
        expected_hash=str(registries.get("interior_volume_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if interior_volume_type_registry_error:
        return interior_volume_type_registry_error
    portal_type_registry, portal_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["portal_type_registry_hash"],
        expected_hash=str(registries.get("portal_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if portal_type_registry_error:
        return portal_type_registry_error
    compartment_flow_policy_registry, compartment_flow_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["compartment_flow_policy_registry_hash"],
        expected_hash=str(registries.get("compartment_flow_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if compartment_flow_policy_registry_error:
        return compartment_flow_policy_registry_error
    portal_flow_template_registry, portal_flow_template_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["portal_flow_template_registry_hash"],
        expected_hash=str(registries.get("portal_flow_template_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if portal_flow_template_registry_error:
        return portal_flow_template_registry_error
    logistics_routing_rule_registry, logistics_routing_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["logistics_routing_rule_registry_hash"],
        expected_hash=str(registries.get("logistics_routing_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if logistics_routing_rule_registry_error:
        return logistics_routing_rule_registry_error
    logistics_graph_registry, logistics_graph_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["logistics_graph_registry_hash"],
        expected_hash=str(registries.get("logistics_graph_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if logistics_graph_registry_error:
        return logistics_graph_registry_error
    provenance_event_type_registry, provenance_event_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["provenance_event_type_registry_hash"],
        expected_hash=str(registries.get("provenance_event_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if provenance_event_type_registry_error:
        return provenance_event_type_registry_error
    construction_policy_registry, construction_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["construction_policy_registry_hash"],
        expected_hash=str(registries.get("construction_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if construction_policy_registry_error:
        return construction_policy_registry_error
    failure_mode_registry, failure_mode_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["failure_mode_registry_hash"],
        expected_hash=str(registries.get("failure_mode_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if failure_mode_registry_error:
        return failure_mode_registry_error
    maintenance_policy_registry, maintenance_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["maintenance_policy_registry_hash"],
        expected_hash=str(registries.get("maintenance_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if maintenance_policy_registry_error:
        return maintenance_policy_registry_error
    backlog_growth_rule_registry, backlog_growth_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["backlog_growth_rule_registry_hash"],
        expected_hash=str(registries.get("backlog_growth_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if backlog_growth_rule_registry_error:
        return backlog_growth_rule_registry_error
    commitment_type_registry, commitment_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["commitment_type_registry_hash"],
        expected_hash=str(registries.get("commitment_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if commitment_type_registry_error:
        return commitment_type_registry_error
    causality_strictness_registry, causality_strictness_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["causality_strictness_registry_hash"],
        expected_hash=str(registries.get("causality_strictness_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if causality_strictness_registry_error:
        return causality_strictness_registry_error

    law_registry, law_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["law_registry_hash"],
        expected_hash=str(registries.get("law_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if law_registry_error:
        return law_registry_error
    lens_registry, lens_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["lens_registry_hash"],
        expected_hash=str(registries.get("lens_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if lens_registry_error:
        return lens_registry_error
    experience_registry, experience_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["experience_registry_hash"],
        expected_hash=str(registries.get("experience_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if experience_registry_error:
        return experience_registry_error
    control_action_registry, control_action_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["control_action_registry_hash"],
        expected_hash=str(registries.get("control_action_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if control_action_registry_error:
        return control_action_registry_error
    control_policy_registry, control_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["control_policy_registry_hash"],
        expected_hash=str(registries.get("control_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if control_policy_registry_error:
        return control_policy_registry_error
    interaction_action_registry, interaction_action_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["interaction_action_registry_hash"],
        expected_hash=str(registries.get("interaction_action_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if interaction_action_registry_error:
        return interaction_action_registry_error
    surface_type_registry, surface_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["surface_type_registry_hash"],
        expected_hash=str(registries.get("surface_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if surface_type_registry_error:
        return surface_type_registry_error
    posture_registry, posture_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["posture_registry_hash"],
        expected_hash=str(registries.get("posture_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if posture_registry_error:
        return posture_registry_error
    mount_tag_registry, mount_tag_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["mount_tag_registry_hash"],
        expected_hash=str(registries.get("mount_tag_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if mount_tag_registry_error:
        return mount_tag_registry_error
    control_binding_registry, control_binding_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["control_binding_registry_hash"],
        expected_hash=str(registries.get("control_binding_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if control_binding_registry_error:
        return control_binding_registry_error
    geometry_type_registry, geometry_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["geometry_type_registry_hash"],
        expected_hash=str(registries.get("geometry_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if geometry_type_registry_error:
        return geometry_type_registry_error
    junction_type_registry, junction_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["junction_type_registry_hash"],
        expected_hash=str(registries.get("junction_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if junction_type_registry_error:
        return junction_type_registry_error
    geometry_snap_policy_registry, geometry_snap_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["geometry_snap_policy_registry_hash"],
        expected_hash=str(registries.get("geometry_snap_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if geometry_snap_policy_registry_error:
        return geometry_snap_policy_registry_error
    mobility_vehicle_class_registry, mobility_vehicle_class_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["mobility_vehicle_class_registry_hash"],
        expected_hash=str(registries.get("mobility_vehicle_class_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if mobility_vehicle_class_registry_error:
        return mobility_vehicle_class_registry_error
    mobility_constraint_type_registry, mobility_constraint_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["mobility_constraint_type_registry_hash"],
        expected_hash=str(registries.get("mobility_constraint_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if mobility_constraint_type_registry_error:
        return mobility_constraint_type_registry_error
    mobility_signal_type_registry, mobility_signal_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["mobility_signal_type_registry_hash"],
        expected_hash=str(registries.get("mobility_signal_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if mobility_signal_type_registry_error:
        return mobility_signal_type_registry_error
    signal_type_registry, signal_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["signal_type_registry_hash"],
        expected_hash=str(registries.get("signal_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if signal_type_registry_error:
        return signal_type_registry_error
    signal_rule_policy_registry, signal_rule_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["signal_rule_policy_registry_hash"],
        expected_hash=str(registries.get("signal_rule_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if signal_rule_policy_registry_error:
        return signal_rule_policy_registry_error
    mobility_speed_policy_registry, mobility_speed_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["mobility_speed_policy_registry_hash"],
        expected_hash=str(registries.get("mobility_speed_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if mobility_speed_policy_registry_error:
        return mobility_speed_policy_registry_error
    port_type_registry, port_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["port_type_registry_hash"],
        expected_hash=str(registries.get("port_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if port_type_registry_error:
        return port_type_registry_error
    tool_tag_registry, tool_tag_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["tool_tag_registry_hash"],
        expected_hash=str(registries.get("tool_tag_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if tool_tag_registry_error:
        return tool_tag_registry_error
    tool_type_registry, tool_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["tool_type_registry_hash"],
        expected_hash=str(registries.get("tool_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if tool_type_registry_error:
        return tool_type_registry_error
    tool_effect_model_registry, tool_effect_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["tool_effect_model_registry_hash"],
        expected_hash=str(registries.get("tool_effect_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if tool_effect_model_registry_error:
        return tool_effect_model_registry_error
    surface_visibility_policy_registry, surface_visibility_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["surface_visibility_policy_registry_hash"],
        expected_hash=str(registries.get("surface_visibility_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if surface_visibility_policy_registry_error:
        return surface_visibility_policy_registry_error
    port_visibility_policy_registry, port_visibility_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["port_visibility_policy_registry_hash"],
        expected_hash=str(registries.get("port_visibility_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if port_visibility_policy_registry_error:
        return port_visibility_policy_registry_error
    machine_type_registry, machine_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["machine_type_registry_hash"],
        expected_hash=str(registries.get("machine_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if machine_type_registry_error:
        return machine_type_registry_error
    machine_operation_registry, machine_operation_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["machine_operation_registry_hash"],
        expected_hash=str(registries.get("machine_operation_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if machine_operation_registry_error:
        return machine_operation_registry_error
    task_type_registry, task_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["task_type_registry_hash"],
        expected_hash=str(registries.get("task_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if task_type_registry_error:
        return task_type_registry_error
    progress_model_registry, progress_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["progress_model_registry_hash"],
        expected_hash=str(registries.get("progress_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if progress_model_registry_error:
        return progress_model_registry_error
    governance_type_registry, governance_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["governance_type_registry_hash"],
        expected_hash=str(registries.get("governance_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if governance_type_registry_error:
        return governance_type_registry_error
    diplomatic_state_registry, diplomatic_state_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["diplomatic_state_registry_hash"],
        expected_hash=str(registries.get("diplomatic_state_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if diplomatic_state_registry_error:
        return diplomatic_state_registry_error
    cohort_mapping_policy_registry, cohort_mapping_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["cohort_mapping_policy_registry_hash"],
        expected_hash=str(registries.get("cohort_mapping_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if cohort_mapping_policy_registry_error:
        return cohort_mapping_policy_registry_error
    order_type_registry, order_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["order_type_registry_hash"],
        expected_hash=str(registries.get("order_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if order_type_registry_error:
        return order_type_registry_error
    role_registry, role_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["role_registry_hash"],
        expected_hash=str(registries.get("role_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if role_registry_error:
        return role_registry_error
    institution_type_registry, institution_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["institution_type_registry_hash"],
        expected_hash=str(registries.get("institution_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if institution_type_registry_error:
        return institution_type_registry_error
    demography_policy_registry, demography_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["demography_policy_registry_hash"],
        expected_hash=str(registries.get("demography_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if demography_policy_registry_error:
        return demography_policy_registry_error
    death_model_registry, death_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["death_model_registry_hash"],
        expected_hash=str(registries.get("death_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if death_model_registry_error:
        return death_model_registry_error
    birth_model_registry, birth_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["birth_model_registry_hash"],
        expected_hash=str(registries.get("birth_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if birth_model_registry_error:
        return birth_model_registry_error
    migration_model_registry, migration_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["migration_model_registry_hash"],
        expected_hash=str(registries.get("migration_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if migration_model_registry_error:
        return migration_model_registry_error
    astronomy_registry, astronomy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["astronomy_catalog_index_hash"],
        expected_hash=str(registries.get("astronomy_catalog_index_hash", "")),
        registries_dir=registries_dir,
    )
    if astronomy_registry_error:
        return astronomy_registry_error
    site_registry, site_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["site_registry_index_hash"],
        expected_hash=str(registries.get("site_registry_index_hash", "")),
        registries_dir=registries_dir,
    )
    if site_registry_error:
        return site_registry_error
    ephemeris_registry, ephemeris_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["ephemeris_registry_hash"],
        expected_hash=str(registries.get("ephemeris_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if ephemeris_registry_error:
        return ephemeris_registry_error
    terrain_tile_registry, terrain_tile_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["terrain_tile_registry_hash"],
        expected_hash=str(registries.get("terrain_tile_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if terrain_tile_registry_error:
        return terrain_tile_registry_error
    activation_policy_registry, activation_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["activation_policy_registry_hash"],
        expected_hash=str(registries.get("activation_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if activation_policy_registry_error:
        return activation_policy_registry_error
    budget_policy_registry, budget_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["budget_policy_registry_hash"],
        expected_hash=str(registries.get("budget_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if budget_policy_registry_error:
        return budget_policy_registry_error
    fidelity_policy_registry, fidelity_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["fidelity_policy_registry_hash"],
        expected_hash=str(registries.get("fidelity_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if fidelity_policy_registry_error:
        return fidelity_policy_registry_error
    net_replication_policy_registry, net_replication_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["net_replication_policy_registry_hash"],
        expected_hash=str(registries.get("net_replication_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if net_replication_policy_registry_error:
        return net_replication_policy_registry_error
    anti_cheat_policy_registry, anti_cheat_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["anti_cheat_policy_registry_hash"],
        expected_hash=str(registries.get("anti_cheat_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if anti_cheat_policy_registry_error:
        return anti_cheat_policy_registry_error
    anti_cheat_module_registry, anti_cheat_module_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["anti_cheat_module_registry_hash"],
        expected_hash=str(registries.get("anti_cheat_module_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if anti_cheat_module_registry_error:
        return anti_cheat_module_registry_error
    net_server_policy_registry, net_server_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["net_server_policy_registry_hash"],
        expected_hash=str(registries.get("net_server_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if net_server_policy_registry_error:
        return net_server_policy_registry_error
    securex_policy_registry, securex_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["securex_policy_registry_hash"],
        expected_hash=str(registries.get("securex_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if securex_policy_registry_error:
        return securex_policy_registry_error
    server_profile_registry, server_profile_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["server_profile_registry_hash"],
        expected_hash=str(registries.get("server_profile_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if server_profile_registry_error:
        return server_profile_registry_error
    shard_map_registry, shard_map_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["shard_map_registry_hash"],
        expected_hash=str(registries.get("shard_map_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if shard_map_registry_error:
        return shard_map_registry_error
    perception_interest_policy_registry, perception_interest_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["perception_interest_policy_registry_hash"],
        expected_hash=str(registries.get("perception_interest_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if perception_interest_policy_registry_error:
        return perception_interest_policy_registry_error
    epistemic_policy_registry, epistemic_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["epistemic_policy_registry_hash"],
        expected_hash=str(registries.get("epistemic_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if epistemic_policy_registry_error:
        return epistemic_policy_registry_error
    retention_policy_registry, retention_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["retention_policy_registry_hash"],
        expected_hash=str(registries.get("retention_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if retention_policy_registry_error:
        return retention_policy_registry_error
    decay_model_registry, decay_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["decay_model_registry_hash"],
        expected_hash=str(registries.get("decay_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if decay_model_registry_error:
        return decay_model_registry_error
    eviction_rule_registry, eviction_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["eviction_rule_registry_hash"],
        expected_hash=str(registries.get("eviction_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if eviction_rule_registry_error:
        return eviction_rule_registry_error
    view_mode_registry, view_mode_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["view_mode_registry_hash"],
        expected_hash=str(registries.get("view_mode_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if view_mode_registry_error:
        return view_mode_registry_error
    view_policy_registry, view_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["view_policy_registry_hash"],
        expected_hash=str(registries.get("view_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if view_policy_registry_error:
        return view_policy_registry_error
    instrument_type_registry, instrument_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["instrument_type_registry_hash"],
        expected_hash=str(registries.get("instrument_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if instrument_type_registry_error:
        return instrument_type_registry_error
    calibration_model_registry, calibration_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["calibration_model_registry_hash"],
        expected_hash=str(registries.get("calibration_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if calibration_model_registry_error:
        return calibration_model_registry_error
    render_proxy_registry, render_proxy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["render_proxy_registry_hash"],
        expected_hash=str(registries.get("render_proxy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if render_proxy_registry_error:
        return render_proxy_registry_error
    cosmetic_registry, cosmetic_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["cosmetic_registry_hash"],
        expected_hash=str(registries.get("cosmetic_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if cosmetic_registry_error:
        return cosmetic_registry_error
    cosmetic_policy_registry, cosmetic_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["cosmetic_policy_registry_hash"],
        expected_hash=str(registries.get("cosmetic_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if cosmetic_policy_registry_error:
        return cosmetic_policy_registry_error
    render_primitive_registry, render_primitive_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["render_primitive_registry_hash"],
        expected_hash=str(registries.get("render_primitive_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if render_primitive_registry_error:
        return render_primitive_registry_error
    procedural_material_template_registry, procedural_material_template_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["procedural_material_template_registry_hash"],
        expected_hash=str(registries.get("procedural_material_template_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if procedural_material_template_registry_error:
        return procedural_material_template_registry_error
    label_policy_registry, label_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["label_policy_registry_hash"],
        expected_hash=str(registries.get("label_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if label_policy_registry_error:
        return label_policy_registry_error
    lod_policy_registry, lod_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["lod_policy_registry_hash"],
        expected_hash=str(registries.get("lod_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if lod_policy_registry_error:
        return lod_policy_registry_error
    representation_rule_registry, representation_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["representation_rule_registry_hash"],
        expected_hash=str(registries.get("representation_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if representation_rule_registry_error:
        return representation_rule_registry_error

    save_id = str(session_spec.get("save_id", "")).strip()
    if not save_id:
        return refusal(
            "REFUSE_SAVE_ID_MISSING",
            "SessionSpec save_id is missing",
            "Fix session_spec.json save_id and retry.",
            {"schema_id": "session_spec"},
            "$.save_id",
        )
    save_dir = os.path.join(repo_root, "saves", save_id)
    identity_path = os.path.join(save_dir, "universe_identity.json")
    state_path = os.path.join(save_dir, "universe_state.json")
    previous_run_meta, previous_run_meta_path = _latest_run_meta(save_dir)
    previous_last_stage_id = str(previous_run_meta.get("last_stage_id", "")).strip()

    universe_identity, identity_error = _load_schema_validated(
        repo_root=repo_root,
        schema_name="universe_identity",
        path=identity_path,
    )
    if identity_error:
        return identity_error
    expected_identity_hash = identity_hash_for_payload(universe_identity)
    if str(universe_identity.get("identity_hash", "")).strip() != expected_identity_hash:
        return refusal(
            "REFUSE_UNIVERSE_IDENTITY_MUTATION",
            "UniverseIdentity identity_hash mismatch detected",
            "Restore canonical universe_identity.json or regenerate the save.",
            {"save_id": save_id},
            "$.identity_hash",
        )
    contract_enforcement = enforce_session_contract_bundle(
        repo_root=repo_root,
        session_spec=session_spec,
        universe_identity=universe_identity,
        identity_path=identity_path,
        replay_mode=False,
    )
    if contract_enforcement.get("result") != "complete":
        return contract_enforcement
    identity_physics_profile_id = str(universe_identity.get("physics_profile_id", "")).strip()
    if not identity_physics_profile_id:
        return refusal(
            "refusal.physics_profile_missing",
            "UniverseIdentity is missing physics_profile_id",
            "Regenerate universe identity with an explicit physics profile id.",
            {"save_id": save_id},
            "$.physics_profile_id",
        )
    identity_generator_version_id = (
        str(universe_identity.get("generator_version_id", "")).strip() or DEFAULT_GENERATOR_VERSION_ID
    )
    identity_realism_profile_id = (
        str(universe_identity.get("realism_profile_id", "")).strip() or DEFAULT_REALISM_PROFILE_ID
    )
    selected_physics_profile, selected_physics_profile_error = select_physics_profile(
        physics_profile_id=identity_physics_profile_id,
        profile_registry=universe_physics_profile_registry,
    )
    if selected_physics_profile_error:
        return selected_physics_profile_error
    previous_physics_profile_id = str((previous_run_meta or {}).get("physics_profile_id", "")).strip()
    if previous_physics_profile_id and previous_physics_profile_id != identity_physics_profile_id:
        return refusal(
            "refusal.physics_profile_mismatch",
            "physics_profile_id does not match the previously booted universe lineage for this save",
            "Create a new save id for a new physics lineage or restore the original identity.",
            {
                "save_id": save_id,
                "previous_physics_profile_id": previous_physics_profile_id,
                "identity_physics_profile_id": identity_physics_profile_id,
            },
            "$.physics_profile_id",
        )
    previous_generator_version_id = str((previous_run_meta or {}).get("generator_version_id", "")).strip()
    if previous_generator_version_id and previous_generator_version_id != identity_generator_version_id:
        return refusal(
            "refusal.generator_version_mismatch",
            "generator_version_id does not match the previously booted universe lineage for this save",
            "Create a new save id for a new generator lineage or restore the original identity.",
            {
                "save_id": save_id,
                "previous_generator_version_id": previous_generator_version_id,
                "identity_generator_version_id": identity_generator_version_id,
            },
            "$.generator_version_id",
        )
    previous_realism_profile_id = str((previous_run_meta or {}).get("realism_profile_id", "")).strip()
    if previous_realism_profile_id and previous_realism_profile_id != identity_realism_profile_id:
        return refusal(
            "refusal.realism_profile_mismatch",
            "realism_profile_id does not match the previously booted universe lineage for this save",
            "Create a new save id for a new realism lineage or restore the original identity.",
            {
                "save_id": save_id,
                "previous_realism_profile_id": previous_realism_profile_id,
                "identity_realism_profile_id": identity_realism_profile_id,
            },
            "$.realism_profile_id",
        )
    identity_conservation_contract_set_id = (
        str(selected_physics_profile.get("conservation_contract_set_id", "")).strip() or "contracts.null"
    )
    identity_time_control_policy_id = str(session_spec.get("time_control_policy_id", "")).strip()
    (
        selected_time_control_policy,
        selected_dt_quantization_rule,
        selected_compaction_policy,
        selected_time_model,
        selected_time_control_policy_error,
    ) = _select_time_control_policy(
        time_control_policy_registry=time_control_policy_registry,
        dt_quantization_rule_registry=dt_quantization_rule_registry,
        compaction_policy_registry=compaction_policy_registry,
        time_model_registry=time_model_registry,
        selected_physics_profile=selected_physics_profile,
        requested_time_control_policy_id=identity_time_control_policy_id,
    )
    if selected_time_control_policy_error:
        return selected_time_control_policy_error
    selected_transition_policy, selected_transition_policy_error = _select_transition_policy(
        transition_policy_registry=transition_policy_registry,
        selected_physics_profile=selected_physics_profile,
        requested_transition_policy_id=str(session_spec.get("transition_policy_id", "")).strip(),
    )
    if selected_transition_policy_error:
        return selected_transition_policy_error
    selected_transition_policy_id = str(selected_transition_policy.get("transition_policy_id", "")).strip() or "transition.policy.null"
    selected_tier_taxonomy_id = str(selected_physics_profile.get("tier_taxonomy_id", "")).strip() or "tiers.null"
    selected_budget_envelope_id = str(selected_physics_profile.get("budget_envelope_id", "")).strip() or "budget.null"
    selected_arbitration_policy_id = str(selected_physics_profile.get("arbitration_policy_id", "")).strip() or "arb.equal_share"
    selected_inspection_cache_policy_id = str(selected_physics_profile.get("inspection_cache_policy_id", "")).strip() or "cache.off"

    _state_payload, state_error = _load_schema_validated(repo_root=repo_root, schema_name="universe_state", path=state_path)
    if state_error:
        return state_error

    session_context = session_spec.get("authority_context")
    if not isinstance(session_context, dict):
        return refusal(
            "REFUSE_AUTHORITY_CONTEXT_MISSING",
            "SessionSpec authority_context is missing",
            "Populate authority_context in session_spec.json.",
            {"schema_id": "session_spec"},
            "$.authority_context",
        )

    authority_origin = str(session_context.get("authority_origin", "")).strip()
    if authority_origin != "client":
        return refusal(
            "REFUSE_AUTHORITY_ORIGIN_INVALID",
            "authority_origin must be 'client' for headless client boot",
            "Set authority_context.authority_origin to client.",
            {"authority_origin": authority_origin or "<empty>"},
            "$.authority_context.authority_origin",
        )

    boot_authority_context = {
        "authority_origin": "client",
        "experience_id": str(session_spec.get("experience_id", "")),
        "law_profile_id": str(session_context.get("law_profile_id", "")),
        "entitlements": sorted(
            set(str(item).strip() for item in (session_context.get("entitlements") or []) if str(item).strip())
        ),
        "epistemic_scope": dict(session_context.get("epistemic_scope") or {}),
        "privilege_level": str(session_context.get("privilege_level", "")),
    }
    authority_schema_payload = dict(boot_authority_context)
    authority_schema_payload["schema_version"] = "1.0.0"
    authority_check = validate_instance(
        repo_root=repo_root,
        schema_name="authority_context",
        payload=authority_schema_payload,
        strict_top_level=True,
    )
    if not bool(authority_check.get("valid", False)):
        return refusal(
            "REFUSE_AUTHORITY_CONTEXT_INVALID",
            "constructed AuthorityContext failed schema validation",
            "Fix SessionSpec authority_context fields and retry.",
            {"schema_id": "authority_context"},
            "$.authority_context",
        )

    stage_order = list(pipeline_contract.get("stage_order") or [])
    has_network_payload = isinstance(session_spec.get("network"), dict)
    has_net_stage = "stage.net_handshake" in stage_order
    if has_network_payload and not has_net_stage:
        return refusal(
            "refusal.net.handshake_policy_not_allowed",
            "SessionSpec includes network config but selected pipeline omits net handshake stage",
            "Select pipeline.client.multiplayer_stub when network endpoint is declared.",
            {"pipeline_id": selected_pipeline_id},
            "$.pipeline_id",
        )
    if (not has_network_payload) and has_net_stage:
        return refusal(
            "refusal.net.handshake_policy_not_allowed",
            "selected pipeline requires net stages but SessionSpec network payload is missing",
            "Populate SessionSpec network fields or use pipeline.client.default.",
            {"pipeline_id": selected_pipeline_id},
            "$.network",
        )

    handshake_stage_result: Dict[str, object] = {}
    net_sync_baseline_stage_result: Dict[str, object] = {}
    net_join_stage_result: Dict[str, object] = {}
    server_authoritative_runtime: Dict[str, object] = {}
    hybrid_runtime: Dict[str, object] = {}
    server_authoritative_law_profile: Dict[str, object] = {}
    server_authoritative_lens_profile: Dict[str, object] = {}

    def _resolve_server_authoritative_profiles() -> Tuple[dict, dict, Dict[str, object]]:
        nonlocal server_authoritative_law_profile
        nonlocal server_authoritative_lens_profile
        if server_authoritative_law_profile and server_authoritative_lens_profile:
            return dict(server_authoritative_law_profile), dict(server_authoritative_lens_profile), {}
        negotiated_law_profile_id = (
            str(handshake_stage_result.get("server_law_profile_id", "")).strip()
            or str(boot_authority_context.get("law_profile_id", "")).strip()
        )
        law_profile_row, law_profile_error = _select_law_profile(
            law_registry=law_registry,
            law_profile_id=str(negotiated_law_profile_id),
        )
        if law_profile_error:
            return {}, {}, law_profile_error
        lens_profile_row, lens_profile_error = _select_lens_profile(
            lens_registry=lens_registry,
            experience_registry=experience_registry,
            experience_id=str(session_spec.get("experience_id", "")),
            law_profile=law_profile_row,
        )
        if lens_profile_error:
            return {}, {}, lens_profile_error
        server_authoritative_law_profile = dict(law_profile_row)
        server_authoritative_lens_profile = dict(lens_profile_row)
        return dict(server_authoritative_law_profile), dict(server_authoritative_lens_profile), {}

    def _ensure_server_authoritative_runtime() -> Tuple[dict, Dict[str, object]]:
        nonlocal server_authoritative_runtime
        if server_authoritative_runtime:
            return server_authoritative_runtime, {}
        selected_law_profile, selected_lens_profile, selected_profile_error = _resolve_server_authoritative_profiles()
        if selected_profile_error:
            return {}, selected_profile_error
        runtime_session_spec = dict(session_spec if isinstance(session_spec, dict) else {})
        runtime_session_spec["transition_policy_id"] = str(selected_transition_policy_id)
        initialized = initialize_authoritative_runtime(
            repo_root=repo_root,
            save_id=save_id,
            session_spec=runtime_session_spec,
            lock_payload=lock_payload,
            universe_identity=universe_identity,
            universe_state=_state_payload,
            law_profile=selected_law_profile,
            lens_profile=selected_lens_profile,
            authority_context=boot_authority_context,
            anti_cheat_policy_registry=anti_cheat_policy_registry,
            anti_cheat_module_registry=anti_cheat_module_registry,
            replication_policy_registry=net_replication_policy_registry,
            registry_payloads={
                "universe_physics_profile_registry": universe_physics_profile_registry,
                "time_model_registry": time_model_registry,
                "time_control_policy_registry": time_control_policy_registry,
                "dt_quantization_rule_registry": dt_quantization_rule_registry,
                "compaction_policy_registry": compaction_policy_registry,
                "numeric_precision_policy_registry": numeric_precision_policy_registry,
                "tier_taxonomy_registry": tier_taxonomy_registry,
                "transition_policy_registry": transition_policy_registry,
                "arbitration_rule_registry": arbitration_rule_registry,
                "budget_envelope_registry": budget_envelope_registry,
                "arbitration_policy_registry": arbitration_policy_registry,
                "inspection_cache_policy_registry": inspection_cache_policy_registry,
                "inspection_section_registry": inspection_section_registry,
                "boundary_model_registry": boundary_model_registry,
                "conservation_contract_set_registry": conservation_contract_set_registry,
                "quantity_registry": quantity_registry,
                "exception_type_registry": exception_type_registry,
                "base_dimension_registry": base_dimension_registry,
                "dimension_registry": dimension_registry,
                "unit_registry": unit_registry,
                "quantity_type_registry": quantity_type_registry,
                "element_registry": element_registry,
                "compound_registry": compound_registry,
                "mixture_registry": mixture_registry,
                "material_class_registry": material_class_registry,
                "quality_distribution_registry": quality_distribution_registry,
                "part_class_registry": part_class_registry,
                "connection_type_registry": connection_type_registry,
                "blueprint_registry": blueprint_registry,
                "interior_volume_type_registry": interior_volume_type_registry,
                "portal_type_registry": portal_type_registry,
                "compartment_flow_policy_registry": compartment_flow_policy_registry,
                "portal_flow_template_registry": portal_flow_template_registry,
                "logistics_routing_rule_registry": logistics_routing_rule_registry,
                "logistics_graph_registry": logistics_graph_registry,
                "provenance_event_type_registry": provenance_event_type_registry,
                "construction_policy_registry": construction_policy_registry,
                "failure_mode_registry": failure_mode_registry,
                "maintenance_policy_registry": maintenance_policy_registry,
                "backlog_growth_rule_registry": backlog_growth_rule_registry,
                "commitment_type_registry": commitment_type_registry,
                "causality_strictness_registry": causality_strictness_registry,
                "astronomy_catalog_index": astronomy_registry,
                "site_registry_index": site_registry,
                "ephemeris_registry": ephemeris_registry,
                "terrain_tile_registry": terrain_tile_registry,
                "control_action_registry": control_action_registry,
                "control_policy_registry": control_policy_registry,
                "interaction_action_registry": interaction_action_registry,
                "surface_type_registry": surface_type_registry,
                "posture_registry": posture_registry,
                "mount_tag_registry": mount_tag_registry,
                "control_binding_registry": control_binding_registry,
                "geometry_type_registry": geometry_type_registry,
                "junction_type_registry": junction_type_registry,
                "geometry_snap_policy_registry": geometry_snap_policy_registry,
                "mobility_vehicle_class_registry": mobility_vehicle_class_registry,
                "mobility_constraint_type_registry": mobility_constraint_type_registry,
                "mobility_signal_type_registry": mobility_signal_type_registry,
                "signal_type_registry": signal_type_registry,
                "signal_rule_policy_registry": signal_rule_policy_registry,
                "mobility_speed_policy_registry": mobility_speed_policy_registry,
                "port_type_registry": port_type_registry,
                "tool_tag_registry": tool_tag_registry,
                "tool_type_registry": tool_type_registry,
                "tool_effect_model_registry": tool_effect_model_registry,
                "surface_visibility_policy_registry": surface_visibility_policy_registry,
                "port_visibility_policy_registry": port_visibility_policy_registry,
                "machine_type_registry": machine_type_registry,
                "machine_operation_registry": machine_operation_registry,
                "task_type_registry": task_type_registry,
                "progress_model_registry": progress_model_registry,
                "governance_type_registry": governance_type_registry,
                "diplomatic_state_registry": diplomatic_state_registry,
                "cohort_mapping_policy_registry": cohort_mapping_policy_registry,
                "order_type_registry": order_type_registry,
                "role_registry": role_registry,
                "institution_type_registry": institution_type_registry,
                "demography_policy_registry": demography_policy_registry,
                "death_model_registry": death_model_registry,
                "birth_model_registry": birth_model_registry,
                "migration_model_registry": migration_model_registry,
                "activation_policy_registry": activation_policy_registry,
                "budget_policy_registry": budget_policy_registry,
                "fidelity_policy_registry": fidelity_policy_registry,
                "perception_interest_policy_registry": perception_interest_policy_registry,
                "epistemic_policy_registry": epistemic_policy_registry,
                "retention_policy_registry": retention_policy_registry,
                "decay_model_registry": decay_model_registry,
                "eviction_rule_registry": eviction_rule_registry,
                "view_mode_registry": view_mode_registry,
                "view_policy_registry": view_policy_registry,
                "render_proxy_registry": render_proxy_registry,
                "cosmetic_registry": cosmetic_registry,
                "cosmetic_policy_registry": cosmetic_policy_registry,
                "render_primitive_registry": render_primitive_registry,
                "procedural_material_template_registry": procedural_material_template_registry,
                "label_policy_registry": label_policy_registry,
                "lod_policy_registry": lod_policy_registry,
                "representation_rule_registry": representation_rule_registry,
                "server_profile_registry": server_profile_registry,
                "net_server_policy_registry": net_server_policy_registry,
            },
            snapshot_cadence_ticks=0,
        )
        if str(initialized.get("result", "")) != "complete":
            return {}, initialized
        server_authoritative_runtime = dict(initialized.get("runtime") or {})
        server_authoritative_runtime["selected_transition_policy"] = dict(selected_transition_policy)
        server_authoritative_runtime["selected_tier_taxonomy_id"] = str(selected_tier_taxonomy_id)
        return server_authoritative_runtime, {}

    def _ensure_hybrid_runtime() -> Tuple[dict, Dict[str, object]]:
        nonlocal hybrid_runtime
        if hybrid_runtime:
            return hybrid_runtime, {}
        selected_law_profile, selected_lens_profile, selected_profile_error = _resolve_server_authoritative_profiles()
        if selected_profile_error:
            return {}, selected_profile_error
        runtime_session_spec = dict(session_spec if isinstance(session_spec, dict) else {})
        runtime_session_spec["transition_policy_id"] = str(selected_transition_policy_id)
        initialized = initialize_hybrid_runtime(
            repo_root=repo_root,
            save_id=save_id,
            session_spec=runtime_session_spec,
            lock_payload=lock_payload,
            universe_identity=universe_identity,
            universe_state=_state_payload,
            law_profile=selected_law_profile,
            lens_profile=selected_lens_profile,
            authority_context=boot_authority_context,
            anti_cheat_policy_registry=anti_cheat_policy_registry,
            anti_cheat_module_registry=anti_cheat_module_registry,
            replication_policy_registry=net_replication_policy_registry,
            server_policy_registry=net_server_policy_registry,
            shard_map_registry=shard_map_registry,
            perception_interest_policy_registry=perception_interest_policy_registry,
            registry_payloads={
                "universe_physics_profile_registry": universe_physics_profile_registry,
                "time_model_registry": time_model_registry,
                "time_control_policy_registry": time_control_policy_registry,
                "dt_quantization_rule_registry": dt_quantization_rule_registry,
                "compaction_policy_registry": compaction_policy_registry,
                "numeric_precision_policy_registry": numeric_precision_policy_registry,
                "tier_taxonomy_registry": tier_taxonomy_registry,
                "transition_policy_registry": transition_policy_registry,
                "arbitration_rule_registry": arbitration_rule_registry,
                "budget_envelope_registry": budget_envelope_registry,
                "arbitration_policy_registry": arbitration_policy_registry,
                "inspection_cache_policy_registry": inspection_cache_policy_registry,
                "inspection_section_registry": inspection_section_registry,
                "boundary_model_registry": boundary_model_registry,
                "conservation_contract_set_registry": conservation_contract_set_registry,
                "quantity_registry": quantity_registry,
                "exception_type_registry": exception_type_registry,
                "base_dimension_registry": base_dimension_registry,
                "dimension_registry": dimension_registry,
                "unit_registry": unit_registry,
                "quantity_type_registry": quantity_type_registry,
                "element_registry": element_registry,
                "compound_registry": compound_registry,
                "mixture_registry": mixture_registry,
                "material_class_registry": material_class_registry,
                "quality_distribution_registry": quality_distribution_registry,
                "part_class_registry": part_class_registry,
                "connection_type_registry": connection_type_registry,
                "blueprint_registry": blueprint_registry,
                "interior_volume_type_registry": interior_volume_type_registry,
                "portal_type_registry": portal_type_registry,
                "compartment_flow_policy_registry": compartment_flow_policy_registry,
                "portal_flow_template_registry": portal_flow_template_registry,
                "logistics_routing_rule_registry": logistics_routing_rule_registry,
                "logistics_graph_registry": logistics_graph_registry,
                "provenance_event_type_registry": provenance_event_type_registry,
                "construction_policy_registry": construction_policy_registry,
                "failure_mode_registry": failure_mode_registry,
                "maintenance_policy_registry": maintenance_policy_registry,
                "backlog_growth_rule_registry": backlog_growth_rule_registry,
                "commitment_type_registry": commitment_type_registry,
                "causality_strictness_registry": causality_strictness_registry,
                "astronomy_catalog_index": astronomy_registry,
                "site_registry_index": site_registry,
                "ephemeris_registry": ephemeris_registry,
                "terrain_tile_registry": terrain_tile_registry,
                "control_action_registry": control_action_registry,
                "control_policy_registry": control_policy_registry,
                "interaction_action_registry": interaction_action_registry,
                "surface_type_registry": surface_type_registry,
                "posture_registry": posture_registry,
                "mount_tag_registry": mount_tag_registry,
                "control_binding_registry": control_binding_registry,
                "geometry_type_registry": geometry_type_registry,
                "junction_type_registry": junction_type_registry,
                "geometry_snap_policy_registry": geometry_snap_policy_registry,
                "mobility_vehicle_class_registry": mobility_vehicle_class_registry,
                "mobility_constraint_type_registry": mobility_constraint_type_registry,
                "mobility_signal_type_registry": mobility_signal_type_registry,
                "signal_type_registry": signal_type_registry,
                "signal_rule_policy_registry": signal_rule_policy_registry,
                "mobility_speed_policy_registry": mobility_speed_policy_registry,
                "port_type_registry": port_type_registry,
                "tool_tag_registry": tool_tag_registry,
                "tool_type_registry": tool_type_registry,
                "tool_effect_model_registry": tool_effect_model_registry,
                "surface_visibility_policy_registry": surface_visibility_policy_registry,
                "port_visibility_policy_registry": port_visibility_policy_registry,
                "machine_type_registry": machine_type_registry,
                "machine_operation_registry": machine_operation_registry,
                "task_type_registry": task_type_registry,
                "progress_model_registry": progress_model_registry,
                "governance_type_registry": governance_type_registry,
                "diplomatic_state_registry": diplomatic_state_registry,
                "cohort_mapping_policy_registry": cohort_mapping_policy_registry,
                "order_type_registry": order_type_registry,
                "role_registry": role_registry,
                "institution_type_registry": institution_type_registry,
                "demography_policy_registry": demography_policy_registry,
                "death_model_registry": death_model_registry,
                "birth_model_registry": birth_model_registry,
                "migration_model_registry": migration_model_registry,
                "activation_policy_registry": activation_policy_registry,
                "budget_policy_registry": budget_policy_registry,
                "fidelity_policy_registry": fidelity_policy_registry,
                "perception_interest_policy_registry": perception_interest_policy_registry,
                "epistemic_policy_registry": epistemic_policy_registry,
                "retention_policy_registry": retention_policy_registry,
                "decay_model_registry": decay_model_registry,
                "eviction_rule_registry": eviction_rule_registry,
                "view_mode_registry": view_mode_registry,
                "view_policy_registry": view_policy_registry,
                "render_proxy_registry": render_proxy_registry,
                "cosmetic_registry": cosmetic_registry,
                "cosmetic_policy_registry": cosmetic_policy_registry,
                "render_primitive_registry": render_primitive_registry,
                "procedural_material_template_registry": procedural_material_template_registry,
                "label_policy_registry": label_policy_registry,
                "lod_policy_registry": lod_policy_registry,
                "representation_rule_registry": representation_rule_registry,
                "server_profile_registry": server_profile_registry,
                "net_server_policy_registry": net_server_policy_registry,
            },
        )
        if str(initialized.get("result", "")) != "complete":
            return {}, initialized
        hybrid_runtime = dict(initialized.get("runtime") or {})
        hybrid_runtime["selected_transition_policy"] = dict(selected_transition_policy)
        hybrid_runtime["selected_tier_taxonomy_id"] = str(selected_tier_taxonomy_id)
        return hybrid_runtime, {}

    def _execute_stage(stage_id: str) -> Dict[str, object]:
        if str(stage_id) == "stage.net_handshake":
            handshake_result = run_loopback_handshake(
                repo_root=repo_root,
                session_spec=session_spec,
                lock_payload=lock_payload,
                replication_registry=net_replication_policy_registry,
                anti_cheat_registry=anti_cheat_policy_registry,
                server_policy_registry=net_server_policy_registry,
                securex_policy_registry=securex_policy_registry,
                server_profile_registry=server_profile_registry,
                authority_context=boot_authority_context,
                server_physics_profile_id=identity_physics_profile_id,
                client_physics_profile_id=identity_physics_profile_id,
                server_conservation_contract_set_id=identity_conservation_contract_set_id,
                client_conservation_contract_set_id=identity_conservation_contract_set_id,
                server_time_control_policy_id=str(selected_time_control_policy.get("time_control_policy_id", "")),
                client_time_control_policy_id=str(selected_time_control_policy.get("time_control_policy_id", "")),
                server_tier_taxonomy_id=str(selected_tier_taxonomy_id),
                client_tier_taxonomy_id=str(selected_tier_taxonomy_id),
                server_transition_policy_id=str(selected_transition_policy_id),
                client_transition_policy_id=str(selected_transition_policy_id),
                server_budget_envelope_id=str(selected_budget_envelope_id),
                client_budget_envelope_id=str(selected_budget_envelope_id),
                server_arbitration_policy_id=str(selected_arbitration_policy_id),
                client_arbitration_policy_id=str(selected_arbitration_policy_id),
            )
            if str(handshake_result.get("result", "")) != "complete":
                return handshake_result
            handshake_id = str(handshake_result.get("handshake_id", "")).strip()
            handshake_payload = {
                "schema_version": "1.0.0",
                "handshake_id": handshake_id,
                "request": dict(handshake_result.get("request") or {}),
                "response": dict(handshake_result.get("handshake") or {}),
                "proto_hashes": dict(handshake_result.get("proto_hashes") or {}),
                "handshake_artifact_hash": str(handshake_result.get("handshake_artifact_hash", "")),
                "deterministic_artifact": True,
                "extensions": {},
            }
            handshake_artifact_abs = os.path.join(save_dir, "run_meta", "handshake.{}.json".format(handshake_id))
            write_canonical_json(handshake_artifact_abs, handshake_payload)
            handshake_result["handshake_artifact_path"] = norm(os.path.relpath(handshake_artifact_abs, repo_root))
            handshake_stage_result.clear()
            handshake_stage_result.update(dict(handshake_result))
            control_capabilities = dict(handshake_result.get("control_capabilities") or {})
            return {
                "result": "complete",
                "details": {
                    "handshake_id": handshake_id,
                    "negotiated_replication_policy_id": str(handshake_result.get("negotiated_replication_policy_id", "")),
                    "anti_cheat_policy_id": str(handshake_result.get("anti_cheat_policy_id", "")),
                    "server_law_profile_id": str(handshake_result.get("server_law_profile_id", "")),
                    "server_physics_profile_id": str(handshake_result.get("physics_profile_id", "")),
                    "client_physics_profile_id": str(handshake_result.get("client_physics_profile_id", "")),
                    "server_conservation_contract_set_id": str(handshake_result.get("conservation_contract_set_id", "")),
                    "client_conservation_contract_set_id": str(handshake_result.get("client_conservation_contract_set_id", "")),
                    "server_time_control_policy_id": str(handshake_result.get("time_control_policy_id", "")),
                    "client_time_control_policy_id": str(handshake_result.get("client_time_control_policy_id", "")),
                    "server_budget_envelope_id": str(handshake_result.get("budget_envelope_id", "")),
                    "client_budget_envelope_id": str(handshake_result.get("client_budget_envelope_id", "")),
                    "server_arbitration_policy_id": str(handshake_result.get("arbitration_policy_id", "")),
                    "client_arbitration_policy_id": str(handshake_result.get("client_arbitration_policy_id", "")),
                    "server_profile_id": str(handshake_result.get("server_profile_id", "")),
                    "server_policy_id": str(handshake_result.get("server_policy_id", "")),
                    "control_capabilities": {
                        "camera_bind_allowed": bool(control_capabilities.get("camera_bind_allowed", False)),
                        "possession_allowed": bool(control_capabilities.get("possession_allowed", False)),
                        "lens_override_allowed": bool(control_capabilities.get("lens_override_allowed", False)),
                    },
                    "handshake_artifact_hash": str(handshake_result.get("handshake_artifact_hash", "")),
                    "handshake_artifact_path": str(handshake_result.get("handshake_artifact_path", "")),
                },
            }
        if str(stage_id) == "stage.net_sync_baseline":
            if not handshake_stage_result:
                return refusal(
                    "refusal.net.join_policy_mismatch",
                    "stage.net_sync_baseline requires completed stage.net_handshake",
                    "Run stage.net_handshake before baseline synchronization.",
                    {"stage_id": "stage.net_sync_baseline"},
                    "$.pipeline",
                )
            negotiated_policy_id = str(handshake_stage_result.get("negotiated_replication_policy_id", "")).strip()
            baseline_result: Dict[str, object] = {}
            if negotiated_policy_id == POLICY_ID_SERVER_AUTHORITATIVE:
                authoritative_runtime, runtime_error = _ensure_server_authoritative_runtime()
                if runtime_error:
                    return runtime_error
                baseline_result = prepare_server_authoritative_baseline(
                    repo_root=repo_root,
                    runtime=authoritative_runtime,
                )
            elif negotiated_policy_id == POLICY_ID_SRZ_HYBRID:
                selected_hybrid_runtime, runtime_error = _ensure_hybrid_runtime()
                if runtime_error:
                    return runtime_error
                baseline_result = prepare_hybrid_baseline(
                    repo_root=repo_root,
                    runtime=selected_hybrid_runtime,
                )
            else:
                return refusal(
                    "refusal.not_implemented.net_transport",
                    "stage.net_sync_baseline supports only negotiated server-authoritative or srz_hybrid policies",
                    "Select policy.net.server_authoritative or policy.net.srz_hybrid for baseline sync.",
                    {
                        "stage_id": "stage.net_sync_baseline",
                        "negotiated_replication_policy_id": negotiated_policy_id or "<empty>",
                    },
                    "$.network.requested_replication_policy_id",
                )
            if str(baseline_result.get("result", "")) != "complete":
                return baseline_result
            net_sync_baseline_stage_result.clear()
            net_sync_baseline_stage_result.update(dict(baseline_result))
            baseline_payload = dict(baseline_result.get("baseline") or {})
            snapshot_payload = dict(baseline_result.get("snapshot") or {})
            return {
                "result": "complete",
                "details": {
                    "policy_id": negotiated_policy_id,
                    "baseline_tick": int(baseline_payload.get("baseline_tick", 0) or 0),
                    "baseline_path": str(baseline_result.get("baseline_path", "")),
                    "snapshot_id": str(snapshot_payload.get("snapshot_id", "")),
                    "snapshot_payload_ref": str(snapshot_payload.get("payload_ref", "")),
                    "snapshot_hash": str(snapshot_payload.get("truth_snapshot_hash", "")),
                    "baseline_hash": canonical_sha256(baseline_payload),
                },
            }
        if str(stage_id) == "stage.net_join_world":
            if not handshake_stage_result:
                return refusal(
                    "refusal.net.join_policy_mismatch",
                    "stage.net_join_world requires completed stage.net_handshake",
                    "Run stage.net_handshake before attempting join.",
                    {"stage_id": "stage.net_join_world"},
                    "$.pipeline",
                )
            negotiated_policy_id = str(handshake_stage_result.get("negotiated_replication_policy_id", "")).strip()
            if not net_sync_baseline_stage_result:
                return refusal(
                    "refusal.net.join_snapshot_invalid",
                    "stage.net_join_world requires stage.net_sync_baseline snapshot artifacts",
                    "Run stage.net_sync_baseline before stage.net_join_world.",
                    {"stage_id": "stage.net_join_world"},
                    "$.pipeline",
                )
            selected_law_profile, selected_lens_profile, selected_profile_error = _resolve_server_authoritative_profiles()
            if selected_profile_error:
                return selected_profile_error
            network_payload = dict(session_spec.get("network") or {})
            peer_id = str(network_payload.get("client_peer_id", "")).strip()
            if not peer_id:
                return refusal(
                    "refusal.net.envelope_invalid",
                    "SessionSpec network.client_peer_id is required for network world join",
                    "Populate SessionSpec network client_peer_id before boot.",
                    {"schema_id": "session_spec"},
                    "$.network.client_peer_id",
                )
            baseline_snapshot = dict(net_sync_baseline_stage_result.get("snapshot") or {})
            join_result: Dict[str, object] = {}
            if negotiated_policy_id == POLICY_ID_SERVER_AUTHORITATIVE:
                authoritative_runtime, runtime_error = _ensure_server_authoritative_runtime()
                if runtime_error:
                    return runtime_error
                join_result = join_client_midstream(
                    repo_root=repo_root,
                    runtime=authoritative_runtime,
                    peer_id=peer_id,
                    authority_context=boot_authority_context,
                    law_profile=selected_law_profile,
                    lens_profile=selected_lens_profile,
                    negotiated_policy_id=negotiated_policy_id,
                    snapshot_id=str(baseline_snapshot.get("snapshot_id", "")),
                )
            elif negotiated_policy_id == POLICY_ID_SRZ_HYBRID:
                selected_hybrid_runtime, runtime_error = _ensure_hybrid_runtime()
                if runtime_error:
                    return runtime_error
                join_result = join_client_hybrid(
                    repo_root=repo_root,
                    runtime=selected_hybrid_runtime,
                    peer_id=peer_id,
                    authority_context=boot_authority_context,
                    law_profile=selected_law_profile,
                    lens_profile=selected_lens_profile,
                    negotiated_policy_id=negotiated_policy_id,
                    snapshot_id=str(baseline_snapshot.get("snapshot_id", "")),
                )
            else:
                return refusal(
                    "refusal.not_implemented.net_transport",
                    "stage.net_join_world supports only negotiated server-authoritative or srz_hybrid policies",
                    "Select policy.net.server_authoritative or policy.net.srz_hybrid for world join.",
                    {
                        "stage_id": "stage.net_join_world",
                        "negotiated_replication_policy_id": negotiated_policy_id or "<empty>",
                    },
                    "$.network.requested_replication_policy_id",
                )
            if str(join_result.get("result", "")) != "complete":
                return join_result
            net_join_stage_result.clear()
            net_join_stage_result.update(dict(join_result))
            return {
                "result": "complete",
                "details": {
                    "policy_id": negotiated_policy_id,
                    "peer_id": str(join_result.get("peer_id", "")),
                    "snapshot_id": str(join_result.get("snapshot_id", "")),
                    "perceived_hash": str(join_result.get("perceived_hash", "")),
                },
            }
        return {"result": "complete", "details": {}}

    stage_log, final_stage_id, stage_log_error = _simulate_boot_stage_log(
        pipeline_contract=pipeline_contract,
        authority_context=boot_authority_context,
        simulation_tick=int(((_state_payload.get("simulation_time") or {}).get("tick", 0)) if isinstance(_state_payload, dict) else 0),
        stage_executor=_execute_stage,
    )
    if stage_log_error:
        return stage_log_error
    if str(final_stage_id) != str((pipeline_contract.get("pipeline") or {}).get("ready_stage_id", "")):
        return refusal(
            "refusal.stage_invalid_transition",
            "boot pipeline did not end at ready stage",
            "Run explicit transitions until stage.session_ready before boot completion.",
            {
                "last_stage_id": str(final_stage_id),
            },
            "$.stage_log",
        )
    if previous_last_stage_id == "stage.session_running":
        stage_log.append(
            {
                "stage_index": len(stage_log),
                "command_id": "client.session.begin",
                "from_stage_id": str(final_stage_id),
                "to_stage_id": "stage.session_running",
                "status": "pass",
                "reason_code": "",
                "observer_watermark": "OBSERVER MODE" if str(boot_authority_context.get("privilege_level", "")).strip() == "observer" else "",
            }
        )
        final_stage_id = "stage.session_running"

    negotiated_law_profile_id = str(handshake_stage_result.get("server_law_profile_id", "")).strip()
    if negotiated_law_profile_id:
        boot_authority_context["law_profile_id"] = negotiated_law_profile_id

    law_profile, law_profile_error = _select_law_profile(
        law_registry=law_registry,
        law_profile_id=str(boot_authority_context.get("law_profile_id", "")),
    )
    if law_profile_error:
        return law_profile_error
    lens_profile, lens_profile_error = _select_lens_profile(
        lens_registry=lens_registry,
        experience_registry=experience_registry,
        experience_id=str(session_spec.get("experience_id", "")),
        law_profile=law_profile,
    )
    if lens_profile_error:
        return lens_profile_error
    budget_policy, budget_policy_error = _select_policy_entry(
        registry_payload=budget_policy_registry,
        key="budget_policies",
        policy_id=str(session_spec.get("budget_policy_id", "")),
        refusal_code="BUDGET_POLICY_NOT_FOUND",
        registry_file=REGISTRY_FILE_MAP["budget_policy_registry_hash"],
    )
    if budget_policy_error:
        return budget_policy_error
    fidelity_policy, fidelity_policy_error = _select_policy_entry(
        registry_payload=fidelity_policy_registry,
        key="fidelity_policies",
        policy_id=str(session_spec.get("fidelity_policy_id", "")),
        refusal_code="FIDELITY_POLICY_NOT_FOUND",
        registry_file=REGISTRY_FILE_MAP["fidelity_policy_registry_hash"],
    )
    if fidelity_policy_error:
        return fidelity_policy_error
    activation_policy, activation_policy_error = _select_policy_entry(
        registry_payload=activation_policy_registry,
        key="activation_policies",
        policy_id=str(budget_policy.get("activation_policy_id", "")),
        refusal_code="ACTIVATION_POLICY_NOT_FOUND",
        registry_file=REGISTRY_FILE_MAP["activation_policy_registry_hash"],
    )
    if activation_policy_error:
        return activation_policy_error

    truth_model = build_truth_model(
        universe_identity=universe_identity,
        universe_state=_state_payload,
        lockfile_payload=lock_payload,
        identity_path=norm(os.path.relpath(identity_path, repo_root)),
        state_path=norm(os.path.relpath(state_path, repo_root)),
        registry_payloads={
            "universe_physics_profile_registry": universe_physics_profile_registry,
            "time_model_registry": time_model_registry,
            "time_control_policy_registry": time_control_policy_registry,
            "dt_quantization_rule_registry": dt_quantization_rule_registry,
            "compaction_policy_registry": compaction_policy_registry,
            "numeric_precision_policy_registry": numeric_precision_policy_registry,
            "tier_taxonomy_registry": tier_taxonomy_registry,
            "transition_policy_registry": transition_policy_registry,
            "arbitration_rule_registry": arbitration_rule_registry,
            "boundary_model_registry": boundary_model_registry,
            "conservation_contract_set_registry": conservation_contract_set_registry,
            "quantity_registry": quantity_registry,
            "exception_type_registry": exception_type_registry,
            "base_dimension_registry": base_dimension_registry,
            "dimension_registry": dimension_registry,
            "unit_registry": unit_registry,
            "quantity_type_registry": quantity_type_registry,
            "element_registry": element_registry,
            "compound_registry": compound_registry,
            "mixture_registry": mixture_registry,
            "material_class_registry": material_class_registry,
            "quality_distribution_registry": quality_distribution_registry,
            "part_class_registry": part_class_registry,
            "connection_type_registry": connection_type_registry,
            "blueprint_registry": blueprint_registry,
            "interior_volume_type_registry": interior_volume_type_registry,
            "portal_type_registry": portal_type_registry,
            "compartment_flow_policy_registry": compartment_flow_policy_registry,
            "portal_flow_template_registry": portal_flow_template_registry,
            "logistics_routing_rule_registry": logistics_routing_rule_registry,
            "logistics_graph_registry": logistics_graph_registry,
            "provenance_event_type_registry": provenance_event_type_registry,
            "construction_policy_registry": construction_policy_registry,
            "failure_mode_registry": failure_mode_registry,
            "maintenance_policy_registry": maintenance_policy_registry,
            "backlog_growth_rule_registry": backlog_growth_rule_registry,
            "commitment_type_registry": commitment_type_registry,
            "causality_strictness_registry": causality_strictness_registry,
            "astronomy_catalog_index": astronomy_registry,
            "site_registry_index": site_registry,
            "ephemeris_registry": ephemeris_registry,
            "terrain_tile_registry": terrain_tile_registry,
            "control_action_registry": control_action_registry,
            "control_policy_registry": control_policy_registry,
            "interaction_action_registry": interaction_action_registry,
            "surface_type_registry": surface_type_registry,
            "posture_registry": posture_registry,
            "mount_tag_registry": mount_tag_registry,
            "control_binding_registry": control_binding_registry,
            "geometry_type_registry": geometry_type_registry,
            "junction_type_registry": junction_type_registry,
            "geometry_snap_policy_registry": geometry_snap_policy_registry,
            "mobility_vehicle_class_registry": mobility_vehicle_class_registry,
            "mobility_constraint_type_registry": mobility_constraint_type_registry,
            "mobility_signal_type_registry": mobility_signal_type_registry,
            "signal_type_registry": signal_type_registry,
            "signal_rule_policy_registry": signal_rule_policy_registry,
            "mobility_speed_policy_registry": mobility_speed_policy_registry,
            "port_type_registry": port_type_registry,
            "tool_tag_registry": tool_tag_registry,
            "tool_type_registry": tool_type_registry,
            "tool_effect_model_registry": tool_effect_model_registry,
            "surface_visibility_policy_registry": surface_visibility_policy_registry,
            "port_visibility_policy_registry": port_visibility_policy_registry,
            "machine_type_registry": machine_type_registry,
            "machine_operation_registry": machine_operation_registry,
            "task_type_registry": task_type_registry,
            "progress_model_registry": progress_model_registry,
            "governance_type_registry": governance_type_registry,
            "diplomatic_state_registry": diplomatic_state_registry,
            "cohort_mapping_policy_registry": cohort_mapping_policy_registry,
            "order_type_registry": order_type_registry,
            "role_registry": role_registry,
            "institution_type_registry": institution_type_registry,
            "demography_policy_registry": demography_policy_registry,
            "death_model_registry": death_model_registry,
            "birth_model_registry": birth_model_registry,
            "migration_model_registry": migration_model_registry,
            "activation_policy_registry": activation_policy_registry,
            "budget_policy_registry": budget_policy_registry,
            "fidelity_policy_registry": fidelity_policy_registry,
            "perception_interest_policy_registry": perception_interest_policy_registry,
            "epistemic_policy_registry": epistemic_policy_registry,
            "retention_policy_registry": retention_policy_registry,
            "decay_model_registry": decay_model_registry,
            "eviction_rule_registry": eviction_rule_registry,
            "view_mode_registry": view_mode_registry,
            "view_policy_registry": view_policy_registry,
            "instrument_type_registry": instrument_type_registry,
            "calibration_model_registry": calibration_model_registry,
            "render_proxy_registry": render_proxy_registry,
            "cosmetic_registry": cosmetic_registry,
            "cosmetic_policy_registry": cosmetic_policy_registry,
            "render_primitive_registry": render_primitive_registry,
            "procedural_material_template_registry": procedural_material_template_registry,
            "label_policy_registry": label_policy_registry,
            "lod_policy_registry": lod_policy_registry,
            "representation_rule_registry": representation_rule_registry,
        },
    )
    observation = observe_truth(
        truth_model=truth_model,
        lens=lens_profile,
        law_profile=law_profile,
        authority_context=boot_authority_context,
        viewpoint_id="viewpoint.client.{}".format(save_id),
    )
    if observation.get("result") != "complete":
        return observation
    perceived_model = dict(observation.get("perceived_model") or {})
    perceived_hash = str(observation.get("perceived_model_hash", ""))
    render = build_render_model(
        perceived_model,
        registry_payloads={
            "render_primitive_registry": render_primitive_registry,
            "procedural_material_template_registry": procedural_material_template_registry,
            "label_policy_registry": label_policy_registry,
            "lod_policy_registry": lod_policy_registry,
            "representation_rule_registry": representation_rule_registry,
        },
        pack_lock_hash=str(lock_payload.get("pack_lock_hash", "")),
        physics_profile_id=str(universe_identity.get("physics_profile_id", "")),
    )
    if render.get("result") != "complete":
        return refusal(
            "RENDER_MODEL_BUILD_FAILED",
            "failed to derive RenderModel from PerceivedModel",
            "Inspect observation outputs and renderer adapter contract.",
            {"save_id": save_id},
            "$.render_model",
        )
    render_hash = str(render.get("render_model_hash", ""))

    session_spec_hash = canonical_sha256(session_spec)
    registry_hashes = dict((lock_payload.get("registries") or {}))
    start_tick = 0
    stop_tick = 0
    handshake_control_capabilities = dict(handshake_stage_result.get("control_capabilities") or {})
    handshake_summary = {
        "executed": bool(handshake_stage_result),
        "handshake_id": str(handshake_stage_result.get("handshake_id", "")),
        "negotiated_replication_policy_id": str(handshake_stage_result.get("negotiated_replication_policy_id", "")),
        "anti_cheat_policy_id": str(handshake_stage_result.get("anti_cheat_policy_id", "")),
        "server_profile_id": str(handshake_stage_result.get("server_profile_id", "")),
        "server_policy_id": str(handshake_stage_result.get("server_policy_id", "")),
        "server_law_profile_id": str(handshake_stage_result.get("server_law_profile_id", "")),
        "server_physics_profile_id": str(handshake_stage_result.get("physics_profile_id", "")),
        "client_physics_profile_id": str(handshake_stage_result.get("client_physics_profile_id", "")),
        "server_conservation_contract_set_id": str(handshake_stage_result.get("conservation_contract_set_id", "")),
        "client_conservation_contract_set_id": str(handshake_stage_result.get("client_conservation_contract_set_id", "")),
        "server_time_control_policy_id": str(handshake_stage_result.get("time_control_policy_id", "")),
        "client_time_control_policy_id": str(handshake_stage_result.get("client_time_control_policy_id", "")),
        "server_tier_taxonomy_id": str(handshake_stage_result.get("tier_taxonomy_id", "")),
        "client_tier_taxonomy_id": str(handshake_stage_result.get("client_tier_taxonomy_id", "")),
        "server_transition_policy_id": str(handshake_stage_result.get("transition_policy_id", "")),
        "client_transition_policy_id": str(handshake_stage_result.get("client_transition_policy_id", "")),
        "server_budget_envelope_id": str(handshake_stage_result.get("budget_envelope_id", "")),
        "client_budget_envelope_id": str(handshake_stage_result.get("client_budget_envelope_id", "")),
        "server_arbitration_policy_id": str(handshake_stage_result.get("arbitration_policy_id", "")),
        "client_arbitration_policy_id": str(handshake_stage_result.get("client_arbitration_policy_id", "")),
        "control_capabilities": {
            "camera_bind_allowed": bool(handshake_control_capabilities.get("camera_bind_allowed", False)),
            "possession_allowed": bool(handshake_control_capabilities.get("possession_allowed", False)),
            "lens_override_allowed": bool(handshake_control_capabilities.get("lens_override_allowed", False)),
        },
        "handshake_artifact_hash": str(handshake_stage_result.get("handshake_artifact_hash", "")),
    }
    baseline_payload = dict(net_sync_baseline_stage_result.get("baseline") or {})
    baseline_snapshot_payload = dict(net_sync_baseline_stage_result.get("snapshot") or {})
    net_sync_baseline_summary = {
        "executed": bool(net_sync_baseline_stage_result),
        "policy_id": str((baseline_payload.get("policy_id", "") or handshake_summary.get("negotiated_replication_policy_id", ""))),
        "baseline_tick": int(baseline_payload.get("baseline_tick", 0) or 0),
        "baseline_path": str(net_sync_baseline_stage_result.get("baseline_path", "")),
        "baseline_hash": canonical_sha256(baseline_payload) if baseline_payload else "",
        "snapshot_id": str(baseline_snapshot_payload.get("snapshot_id", "")),
        "snapshot_payload_ref": str(baseline_snapshot_payload.get("payload_ref", "")),
        "truth_snapshot_hash": str(baseline_snapshot_payload.get("truth_snapshot_hash", "")),
    }
    net_join_summary = {
        "executed": bool(net_join_stage_result),
        "peer_id": str(net_join_stage_result.get("peer_id", "")),
        "snapshot_id": str(net_join_stage_result.get("snapshot_id", "")),
        "perceived_hash": str(net_join_stage_result.get("perceived_hash", "")),
    }
    deterministic_fields = {
        "schema_version": "1.0.0",
        "save_id": save_id,
        "bundle_id": bundle_token,
        "pipeline_id": selected_pipeline_id,
        "session_spec_hash": session_spec_hash,
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "contract_bundle_hash": str(contract_enforcement.get("contract_bundle_hash", "")),
        "semantic_contract_registry_hash": str(contract_enforcement.get("semantic_contract_registry_hash", "")),
        "semantic_contract_proof_bundle": dict(contract_enforcement.get("proof_bundle") or {}),
        "mod_policy_id": selected_mod_policy_id,
        "mod_policy_registry_hash": str(mod_policy_proof_bundle.get("mod_policy_registry_hash", "")).strip(),
        "mod_policy_proof_bundle": dict(mod_policy_proof_bundle),
        "overlay_manifest_hash": str(universe_state.get("overlay_manifest_hash", "")).strip(),
        "worldgen_request_hash_chain": str(universe_state.get("worldgen_request_hash_chain", "")).strip(),
        "worldgen_result_hash_chain": str(universe_state.get("worldgen_result_hash_chain", "")).strip(),
        "refinement_request_hash_chain": str(universe_state.get("refinement_request_hash_chain", "")).strip(),
        "refinement_cache_hash_chain": str(universe_state.get("refinement_cache_hash_chain", "")).strip(),
        "registry_hashes": registry_hashes,
        "session_stage_registry_hash": str(pipeline_contract.get("stage_registry_hash", "")),
        "session_pipeline_registry_hash": str(pipeline_contract.get("pipeline_registry_hash", "")),
        "stage_log": stage_log,
        "last_stage_id": str(final_stage_id),
        "universe_identity_hash": str(universe_identity.get("identity_hash", "")),
        "physics_profile_id": identity_physics_profile_id,
        "generator_version_id": identity_generator_version_id,
        "realism_profile_id": identity_realism_profile_id,
        "conservation_contract_set_id": identity_conservation_contract_set_id,
        "time_control_policy_id": str(selected_time_control_policy.get("time_control_policy_id", "")),
        "dt_quantization_rule_id": str(selected_dt_quantization_rule.get("dt_rule_id", "")),
        "compaction_policy_id": str(selected_compaction_policy.get("compaction_policy_id", "")),
        "time_model_id": str(selected_time_model.get("time_model_id", "")),
        "tier_taxonomy_id": str(selected_tier_taxonomy_id),
        "transition_policy_id": str(selected_transition_policy_id),
        "budget_envelope_id": str(selected_budget_envelope_id),
        "arbitration_policy_id": str(selected_arbitration_policy_id),
        "inspection_cache_policy_id": str(selected_inspection_cache_policy_id),
        "selected_lens_id": str(lens_profile.get("lens_id", "")),
        "budget_policy_id": str(budget_policy.get("policy_id", "")),
        "fidelity_policy_id": str(fidelity_policy.get("policy_id", "")),
        "activation_policy_id": str(activation_policy.get("policy_id", "")),
        "perceived_model_hash": perceived_hash,
        "render_model_hash": render_hash,
        "network_handshake": handshake_summary,
        "network_sync_baseline": net_sync_baseline_summary,
        "network_join_world": net_join_summary,
        "start_tick": start_tick,
        "stop_tick": stop_tick,
        "authority_context": boot_authority_context,
    }
    deterministic_fields_hash = canonical_sha256(deterministic_fields)
    run_id = "run.{}".format(deterministic_fields_hash[:16])

    handshake_artifact_rel = str(handshake_stage_result.get("handshake_artifact_path", "")).strip()
    if handshake_stage_result and not handshake_artifact_rel:
        handshake_id = str(handshake_summary.get("handshake_id", "")).strip() or run_id
        handshake_payload = {
            "schema_version": "1.0.0",
            "handshake_id": handshake_id,
            "request": dict(handshake_stage_result.get("request") or {}),
            "response": dict(handshake_stage_result.get("handshake") or {}),
            "proto_hashes": dict(handshake_stage_result.get("proto_hashes") or {}),
            "handshake_artifact_hash": str(handshake_summary.get("handshake_artifact_hash", "")),
            "deterministic_artifact": True,
            "extensions": {},
        }
        handshake_artifact_abs = os.path.join(save_dir, "run_meta", "handshake.{}.json".format(handshake_id))
        write_canonical_json(handshake_artifact_abs, handshake_payload)
        handshake_artifact_rel = norm(os.path.relpath(handshake_artifact_abs, repo_root))

    now = now_utc_iso()
    run_meta = dict(deterministic_fields)
    lock_path_for_meta = _resolve_lockfile_path(repo_root, lockfile_path)
    run_meta.update(
        {
            "run_id": run_id,
            "session_spec_path": norm(os.path.relpath(spec_abs, repo_root)),
            "universe_identity_path": norm(os.path.relpath(identity_path, repo_root)),
            "universe_state_path": norm(os.path.relpath(state_path, repo_root)),
            "lockfile_path": norm(os.path.relpath(lock_path_for_meta, repo_root)),
            "session_stage_registry_path": str(pipeline_contract.get("stage_registry_path", "")),
            "session_pipeline_registry_path": str(pipeline_contract.get("pipeline_registry_path", "")),
            "reentry_source_run_meta_path": norm(os.path.relpath(previous_run_meta_path, repo_root))
            if previous_run_meta_path
            else "",
            "reentry_detected": bool(previous_run_meta_path),
            "reentry_source_run_id": str(previous_run_meta.get("run_id", "")) if isinstance(previous_run_meta, dict) else "",
            "reentry_source_last_stage_id": previous_last_stage_id,
            "handshake_artifact_path": handshake_artifact_rel,
            "started_utc": now,
            "stopped_utc": now_utc_iso(),
            "deterministic_fields_hash": deterministic_fields_hash,
        }
    )

    run_meta_dir = os.path.join(save_dir, "run_meta")
    run_meta_path = os.path.join(run_meta_dir, "{}.json".format(run_id))
    write_canonical_json(run_meta_path, run_meta)
    return {
        "result": "complete",
        "save_id": save_id,
        "bundle_id": bundle_token,
        "pipeline_id": selected_pipeline_id,
        "run_id": run_id,
        "run_meta_path": norm(os.path.relpath(run_meta_path, repo_root)),
        "session_spec_hash": session_spec_hash,
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "contract_bundle_hash": str(contract_enforcement.get("contract_bundle_hash", "")),
        "semantic_contract_registry_hash": str(contract_enforcement.get("semantic_contract_registry_hash", "")),
        "semantic_contract_proof_bundle": dict(contract_enforcement.get("proof_bundle") or {}),
        "mod_policy_id": selected_mod_policy_id,
        "mod_policy_registry_hash": str(mod_policy_proof_bundle.get("mod_policy_registry_hash", "")).strip(),
        "mod_policy_proof_bundle": dict(mod_policy_proof_bundle),
        "overlay_manifest_hash": str(universe_state.get("overlay_manifest_hash", "")).strip(),
        "worldgen_request_hash_chain": str(universe_state.get("worldgen_request_hash_chain", "")).strip(),
        "worldgen_result_hash_chain": str(universe_state.get("worldgen_result_hash_chain", "")).strip(),
        "refinement_request_hash_chain": str(universe_state.get("refinement_request_hash_chain", "")).strip(),
        "refinement_cache_hash_chain": str(universe_state.get("refinement_cache_hash_chain", "")).strip(),
        "registry_hashes": registry_hashes,
        "physics_profile_id": identity_physics_profile_id,
        "conservation_contract_set_id": identity_conservation_contract_set_id,
        "time_control_policy_id": str(selected_time_control_policy.get("time_control_policy_id", "")),
        "tier_taxonomy_id": str(selected_tier_taxonomy_id),
        "transition_policy_id": str(selected_transition_policy_id),
        "budget_envelope_id": str(selected_budget_envelope_id),
        "arbitration_policy_id": str(selected_arbitration_policy_id),
        "inspection_cache_policy_id": str(selected_inspection_cache_policy_id),
        "selected_lens_id": str(lens_profile.get("lens_id", "")),
        "perceived_model_hash": perceived_hash,
        "render_model_hash": render_hash,
        "reentry_detected": bool(previous_run_meta_path),
        "reentry_source_run_id": str(previous_run_meta.get("run_id", "")) if isinstance(previous_run_meta, dict) else "",
        "last_stage_id": str(final_stage_id),
        "stage_log": stage_log,
        "network_handshake": handshake_summary,
        "network_sync_baseline": net_sync_baseline_summary,
        "network_join_world": net_join_summary,
        "handshake_artifact_path": handshake_artifact_rel,
        "start_tick": start_tick,
        "stop_tick": stop_tick,
        "deterministic_fields_hash": deterministic_fields_hash,
    }

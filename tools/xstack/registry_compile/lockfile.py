"""Lockfile hashing + validation for deterministic bundle composition."""

from __future__ import annotations

import re
from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256


HASH_RE = re.compile(r"^[A-Fa-f0-9]{64}$")


def compute_pack_lock_hash(resolved_packs: List[dict]) -> str:
    rows = []
    for row in sorted(
        resolved_packs or [],
        key=lambda item: (
            str(item.get("pack_id", "")),
            str(item.get("version", "")),
            str(item.get("canonical_hash", "")),
            str(item.get("signature_status", "")),
        ),
    ):
        rows.append(
            {
                "pack_id": str(row.get("pack_id", "")),
                "version": str(row.get("version", "")),
                "canonical_hash": str(row.get("canonical_hash", "")),
                "signature_status": str(row.get("signature_status", "")),
            }
        )
    return canonical_sha256(rows)


def validate_lockfile_payload(payload: Dict[str, object]) -> Dict[str, object]:
    errors = []
    if not isinstance(payload, dict):
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refuse.lockfile.invalid_root",
                    "message": "lockfile root must be an object",
                    "path": "$",
                }
            ],
        }

    required_fields = (
        "lockfile_version",
        "bundle_id",
        "resolved_packs",
        "registries",
        "compatibility_version",
        "pack_lock_hash",
    )
    for key in required_fields:
        if key not in payload:
            errors.append(
                {
                    "code": "refuse.lockfile.missing_required_field",
                    "message": "missing required field '{}'".format(key),
                    "path": "$.{}".format(key),
                }
            )

    lockfile_version = str(payload.get("lockfile_version", ""))
    if lockfile_version != "1.0.0":
        errors.append(
            {
                "code": "refuse.lockfile.invalid_lockfile_version",
                "message": "lockfile_version must equal '1.0.0'",
                "path": "$.lockfile_version",
            }
        )

    resolved = payload.get("resolved_packs")
    if not isinstance(resolved, list):
        errors.append(
            {
                "code": "refuse.lockfile.invalid_resolved_packs",
                "message": "resolved_packs must be a list",
                "path": "$.resolved_packs",
            }
        )
        resolved = []

    for idx, row in enumerate(resolved):
        if not isinstance(row, dict):
            errors.append(
                {
                    "code": "refuse.lockfile.invalid_resolved_pack_entry",
                    "message": "resolved_packs entry must be object",
                    "path": "$.resolved_packs[{}]".format(idx),
                }
            )
            continue
        for field in ("pack_id", "version", "canonical_hash", "signature_status"):
            if not str(row.get(field, "")).strip():
                errors.append(
                    {
                        "code": "refuse.lockfile.invalid_resolved_pack_field",
                        "message": "resolved_packs entry missing '{}'".format(field),
                        "path": "$.resolved_packs[{}].{}".format(idx, field),
                    }
                )

    registries = payload.get("registries")
    if not isinstance(registries, dict):
        errors.append(
            {
                "code": "refuse.lockfile.invalid_registries",
                "message": "registries must be an object",
                "path": "$.registries",
            }
        )
    else:
        expected_keys = (
            "conservation_contract_set_registry_hash",
            "quantity_registry_hash",
            "exception_type_registry_hash",
            "base_dimension_registry_hash",
            "dimension_registry_hash",
            "unit_registry_hash",
            "quantity_type_registry_hash",
            "element_registry_hash",
            "compound_registry_hash",
            "mixture_registry_hash",
            "material_class_registry_hash",
            "quality_distribution_registry_hash",
            "part_class_registry_hash",
            "connection_type_registry_hash",
            "blueprint_registry_hash",
            "interior_volume_type_registry_hash",
            "portal_type_registry_hash",
            "compartment_flow_policy_registry_hash",
            "portal_flow_template_registry_hash",
            "core_routing_policy_registry_hash",
            "core_flow_solver_policy_registry_hash",
            "core_constraint_type_registry_hash",
            "core_state_machine_type_registry_hash",
            "core_hazard_type_registry_hash",
            "core_schedule_policy_registry_hash",
            "logistics_routing_rule_registry_hash",
            "logistics_graph_registry_hash",
            "provenance_event_type_registry_hash",
            "construction_policy_registry_hash",
            "failure_mode_registry_hash",
            "maintenance_policy_registry_hash",
            "backlog_growth_rule_registry_hash",
            "commitment_type_registry_hash",
            "causality_strictness_registry_hash",
            "universe_physics_profile_registry_hash",
            "time_model_registry_hash",
            "time_control_policy_registry_hash",
            "dt_quantization_rule_registry_hash",
            "compaction_policy_registry_hash",
            "numeric_precision_policy_registry_hash",
            "tier_taxonomy_registry_hash",
            "transition_policy_registry_hash",
            "arbitration_rule_registry_hash",
            "budget_envelope_registry_hash",
            "arbitration_policy_registry_hash",
            "inspection_cache_policy_registry_hash",
            "inspection_section_registry_hash",
            "boundary_model_registry_hash",
            "domain_registry_hash",
            "law_registry_hash",
            "experience_registry_hash",
            "lens_registry_hash",
            "control_action_registry_hash",
            "capability_registry_hash",
            "control_policy_registry_hash",
            "interaction_action_registry_hash",
            "surface_type_registry_hash",
            "posture_registry_hash",
            "mount_tag_registry_hash",
            "control_binding_registry_hash",
            "port_type_registry_hash",
            "tool_tag_registry_hash",
            "tool_type_registry_hash",
            "tool_effect_model_registry_hash",
            "surface_visibility_policy_registry_hash",
            "port_visibility_policy_registry_hash",
            "machine_type_registry_hash",
            "machine_operation_registry_hash",
            "task_type_registry_hash",
            "progress_model_registry_hash",
            "controller_type_registry_hash",
            "governance_type_registry_hash",
            "diplomatic_state_registry_hash",
            "cohort_mapping_policy_registry_hash",
            "order_type_registry_hash",
            "role_registry_hash",
            "institution_type_registry_hash",
            "demography_policy_registry_hash",
            "death_model_registry_hash",
            "birth_model_registry_hash",
            "migration_model_registry_hash",
            "body_shape_registry_hash",
            "view_mode_registry_hash",
            "view_policy_registry_hash",
            "instrument_type_registry_hash",
            "calibration_model_registry_hash",
            "render_proxy_registry_hash",
            "cosmetic_registry_hash",
            "cosmetic_policy_registry_hash",
            "render_primitive_registry_hash",
            "procedural_material_template_registry_hash",
            "label_policy_registry_hash",
            "lod_policy_registry_hash",
            "representation_rule_registry_hash",
            "net_replication_policy_registry_hash",
            "net_resync_strategy_registry_hash",
            "net_server_policy_registry_hash",
            "securex_policy_registry_hash",
            "server_profile_registry_hash",
            "shard_map_registry_hash",
            "perception_interest_policy_registry_hash",
            "epistemic_policy_registry_hash",
            "retention_policy_registry_hash",
            "decay_model_registry_hash",
            "eviction_rule_registry_hash",
            "anti_cheat_policy_registry_hash",
            "anti_cheat_module_registry_hash",
            "activation_policy_registry_hash",
            "budget_policy_registry_hash",
            "fidelity_policy_registry_hash",
            "worldgen_constraints_registry_hash",
            "astronomy_catalog_index_hash",
            "site_registry_index_hash",
            "ephemeris_registry_hash",
            "terrain_tile_registry_hash",
            "ui_registry_hash",
        )
        for key in expected_keys:
            token = str(registries.get(key, "")).strip()
            if not HASH_RE.fullmatch(token):
                errors.append(
                    {
                        "code": "refuse.lockfile.invalid_registry_hash",
                        "message": "registries.{} must be sha256 hex".format(key),
                        "path": "$.registries.{}".format(key),
                    }
                )

    declared_hash = str(payload.get("pack_lock_hash", "")).strip()
    computed_hash = compute_pack_lock_hash(resolved)
    if declared_hash != computed_hash:
        errors.append(
            {
                "code": "refuse.lockfile.pack_lock_hash_mismatch",
                "message": "pack_lock_hash mismatch",
                "path": "$.pack_lock_hash",
            }
        )

    if errors:
        return {
            "result": "refused",
            "errors": sorted(errors, key=lambda row: (row["code"], row["path"], row["message"])),
            "computed_pack_lock_hash": computed_hash,
        }
    return {
        "result": "complete",
        "errors": [],
        "computed_pack_lock_hash": computed_hash,
    }

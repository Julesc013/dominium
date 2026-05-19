"""Utility helpers for TestX tool-suite tests."""

from __future__ import annotations

import os
import shutil
import tempfile


FIXTURE_SOURCE_REGISTRY_FILES = (
    ("contracts/registry/net_replication_policy_registry.json", "contracts/registry/net_replication_policy_registry.json"),
    ("contracts/registry/net_resync_strategy_registry.json", "contracts/registry/net_resync_strategy_registry.json"),
    # Fixture uses law.test.default; copy fixture-specific server policy registry to keep compile deterministic.
    ("tools/xstack/testcontracts/registry/net_server_policy_registry.json", "contracts/registry/net_server_policy_registry.json"),
    ("contracts/registry/securex_policy_registry.json", "contracts/registry/securex_policy_registry.json"),
    ("tools/xstack/testcontracts/registry/server_profile_registry.json", "contracts/registry/server_profile_registry.json"),
    ("contracts/registry/shard_map_registry.json", "contracts/registry/shard_map_registry.json"),
    ("contracts/registry/perception_interest_policy_registry.json", "contracts/registry/perception_interest_policy_registry.json"),
    ("contracts/registry/universe_physics_profile_registry.json", "contracts/registry/universe_physics_profile_registry.json"),
    ("contracts/registry/time_model_registry.json", "contracts/registry/time_model_registry.json"),
    ("contracts/registry/numeric_precision_policy_registry.json", "contracts/registry/numeric_precision_policy_registry.json"),
    ("contracts/registry/tier_taxonomy_registry.json", "contracts/registry/tier_taxonomy_registry.json"),
    ("contracts/registry/boundary_model_registry.json", "contracts/registry/boundary_model_registry.json"),
    ("contracts/registry/control_action_registry.json", "contracts/registry/control_action_registry.json"),
    ("contracts/registry/controller_type_registry.json", "contracts/registry/controller_type_registry.json"),
    ("contracts/registry/governance_type_registry.json", "contracts/registry/governance_type_registry.json"),
    ("contracts/registry/diplomatic_state_registry.json", "contracts/registry/diplomatic_state_registry.json"),
    ("contracts/registry/cohort_mapping_policy_registry.json", "contracts/registry/cohort_mapping_policy_registry.json"),
    ("contracts/registry/order_type_registry.json", "contracts/registry/order_type_registry.json"),
    ("contracts/registry/role_registry.json", "contracts/registry/role_registry.json"),
    ("contracts/registry/institution_type_registry.json", "contracts/registry/institution_type_registry.json"),
    ("contracts/registry/body_shape_registry.json", "contracts/registry/body_shape_registry.json"),
    ("contracts/registry/view_mode_registry.json", "contracts/registry/view_mode_registry.json"),
    ("contracts/registry/instrument_type_registry.json", "contracts/registry/instrument_type_registry.json"),
    ("contracts/registry/calibration_model_registry.json", "contracts/registry/calibration_model_registry.json"),
    ("contracts/registry/render_proxy_registry.json", "contracts/registry/render_proxy_registry.json"),
    ("contracts/registry/cosmetic_registry.json", "contracts/registry/cosmetic_registry.json"),
    ("contracts/registry/cosmetic_policy_registry.json", "contracts/registry/cosmetic_policy_registry.json"),
    ("contracts/registry/render_primitive_registry.json", "contracts/registry/render_primitive_registry.json"),
    (
        "contracts/registry/procedural_material_template_registry.json",
        "contracts/registry/procedural_material_template_registry.json",
    ),
    ("contracts/registry/label_policy_registry.json", "contracts/registry/label_policy_registry.json"),
    ("contracts/registry/lod_policy_registry.json", "contracts/registry/lod_policy_registry.json"),
    ("contracts/registry/representation_rule_registry.json", "contracts/registry/representation_rule_registry.json"),
    ("contracts/registry/epistemic_policy_registry.json", "contracts/registry/epistemic_policy_registry.json"),
    ("contracts/registry/retention_policy_registry.json", "contracts/registry/retention_policy_registry.json"),
    ("contracts/registry/decay_model_registry.json", "contracts/registry/decay_model_registry.json"),
    ("contracts/registry/eviction_rule_registry.json", "contracts/registry/eviction_rule_registry.json"),
    ("contracts/registry/anti_cheat_policy_registry.json", "contracts/registry/anti_cheat_policy_registry.json"),
    ("contracts/registry/anti_cheat_module_registry.json", "contracts/registry/anti_cheat_module_registry.json"),
)


def _copy_rel_file(source_repo_root: str, temp_root: str, src_rel_path: str, dst_rel_path: str) -> None:
    src = os.path.join(source_repo_root, src_rel_path.replace("/", os.sep))
    dst = os.path.join(temp_root, dst_rel_path.replace("/", os.sep))
    parent = os.path.dirname(dst)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copy2(src, dst)


def make_temp_repo_with_test_packs(source_repo_root: str) -> str:
    fixture_root = os.path.join(source_repo_root, ".xstack_cache", "testx", "fixtures")
    os.makedirs(fixture_root, exist_ok=True)
    temp_root = tempfile.mkdtemp(prefix="xstack_testx_fixture_", dir=fixture_root)
    src_packs = os.path.join(source_repo_root, "tools", "xstack", "testdata", "packs")
    dst_packs = os.path.join(temp_root, "packs")
    shutil.copytree(src_packs, dst_packs)
    # MAT-3 baseline adds blueprint registries whose entries resolve into packs/blueprints.
    # Fixture repos must include these pack paths so registry compile remains deterministic.
    src_blueprints = os.path.join(source_repo_root, "packs", "blueprints")
    if os.path.isdir(src_blueprints):
        dst_blueprints = os.path.join(dst_packs, "blueprints")
        shutil.copytree(src_blueprints, dst_blueprints)
    src_bundles = os.path.join(source_repo_root, "tools", "xstack", "testdata", "bundles")
    dst_bundles = os.path.join(temp_root, "bundles")
    shutil.copytree(src_bundles, dst_bundles)
    src_registries = os.path.join(source_repo_root, "contracts", "registry")
    dst_registries = os.path.join(temp_root, "contracts", "registry")
    shutil.copytree(src_registries, dst_registries)
    src_meta = os.path.join(source_repo_root, "data", "meta")
    if os.path.isdir(src_meta):
        dst_meta = os.path.join(temp_root, "data", "meta")
        shutil.copytree(src_meta, dst_meta)
    for src_rel_path, dst_rel_path in FIXTURE_SOURCE_REGISTRY_FILES:
        _copy_rel_file(
            source_repo_root=source_repo_root,
            temp_root=temp_root,
            src_rel_path=src_rel_path,
            dst_rel_path=dst_rel_path,
        )
    return temp_root

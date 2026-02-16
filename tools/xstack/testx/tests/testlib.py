"""Utility helpers for TestX tool-suite tests."""

from __future__ import annotations

import os
import shutil
import tempfile


FIXTURE_SOURCE_REGISTRY_FILES = (
    ("data/registries/net_replication_policy_registry.json", "data/registries/net_replication_policy_registry.json"),
    ("data/registries/net_resync_strategy_registry.json", "data/registries/net_resync_strategy_registry.json"),
    # Fixture uses law.test.default; copy fixture-specific server policy registry to keep compile deterministic.
    ("tools/xstack/testdata/registries/net_server_policy_registry.json", "data/registries/net_server_policy_registry.json"),
    ("data/registries/securex_policy_registry.json", "data/registries/securex_policy_registry.json"),
    ("tools/xstack/testdata/registries/server_profile_registry.json", "data/registries/server_profile_registry.json"),
    ("data/registries/shard_map_registry.json", "data/registries/shard_map_registry.json"),
    ("data/registries/perception_interest_policy_registry.json", "data/registries/perception_interest_policy_registry.json"),
    ("data/registries/control_action_registry.json", "data/registries/control_action_registry.json"),
    ("data/registries/controller_type_registry.json", "data/registries/controller_type_registry.json"),
    ("data/registries/body_shape_registry.json", "data/registries/body_shape_registry.json"),
    ("data/registries/epistemic_policy_registry.json", "data/registries/epistemic_policy_registry.json"),
    ("data/registries/retention_policy_registry.json", "data/registries/retention_policy_registry.json"),
    ("data/registries/anti_cheat_policy_registry.json", "data/registries/anti_cheat_policy_registry.json"),
    ("data/registries/anti_cheat_module_registry.json", "data/registries/anti_cheat_module_registry.json"),
)


def _copy_rel_file(source_repo_root: str, temp_root: str, src_rel_path: str, dst_rel_path: str) -> None:
    src = os.path.join(source_repo_root, src_rel_path.replace("/", os.sep))
    dst = os.path.join(temp_root, dst_rel_path.replace("/", os.sep))
    parent = os.path.dirname(dst)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copy2(src, dst)


def make_temp_repo_with_test_packs(source_repo_root: str) -> str:
    temp_root = tempfile.mkdtemp(prefix="xstack_testx_fixture_")
    src_packs = os.path.join(source_repo_root, "tools", "xstack", "testdata", "packs")
    dst_packs = os.path.join(temp_root, "packs")
    shutil.copytree(src_packs, dst_packs)
    src_bundles = os.path.join(source_repo_root, "tools", "xstack", "testdata", "bundles")
    dst_bundles = os.path.join(temp_root, "bundles")
    shutil.copytree(src_bundles, dst_bundles)
    for src_rel_path, dst_rel_path in FIXTURE_SOURCE_REGISTRY_FILES:
        _copy_rel_file(
            source_repo_root=source_repo_root,
            temp_root=temp_root,
            src_rel_path=src_rel_path,
            dst_rel_path=dst_rel_path,
        )
    return temp_root

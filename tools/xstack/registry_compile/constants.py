"""Registry compile constants and output naming contract."""

REGISTRY_FORMAT_VERSION = "1.0.0"
COMPILER_VERSION = "1.10.0"
DEFAULT_BUNDLE_ID = "bundle.base.lab"
DEFAULT_REGISTRY_OUT_DIR_REL = "build/registries"
DEFAULT_LOCKFILE_OUT_REL = "build/lockfile.json"
DEFAULT_COMPATIBILITY_VERSION = "1.0.0"


REGISTRY_OUTPUT_FILENAMES = {
    "domain_registry": "domain.registry.json",
    "law_registry": "law.registry.json",
    "experience_registry": "experience.registry.json",
    "lens_registry": "lens.registry.json",
    "net_replication_policy_registry": "net_replication_policy.registry.json",
    "net_resync_strategy_registry": "net_resync_strategy.registry.json",
    "net_server_policy_registry": "net_server_policy.registry.json",
    "securex_policy_registry": "securex_policy.registry.json",
    "server_profile_registry": "server_profile.registry.json",
    "shard_map_registry": "shard_map.registry.json",
    "perception_interest_policy_registry": "perception_interest_policy.registry.json",
    "control_action_registry": "control_action.registry.json",
    "controller_type_registry": "controller_type.registry.json",
    "body_shape_registry": "body_shape.registry.json",
    "view_mode_registry": "view_mode.registry.json",
    "render_proxy_registry": "render_proxy.registry.json",
    "cosmetic_registry": "cosmetic.registry.json",
    "cosmetic_policy_registry": "cosmetic_policy.registry.json",
    "epistemic_policy_registry": "epistemic_policy.registry.json",
    "retention_policy_registry": "retention_policy.registry.json",
    "anti_cheat_policy_registry": "anti_cheat_policy.registry.json",
    "anti_cheat_module_registry": "anti_cheat_module.registry.json",
    "activation_policy_registry": "activation_policy.registry.json",
    "budget_policy_registry": "budget_policy.registry.json",
    "fidelity_policy_registry": "fidelity_policy.registry.json",
    "worldgen_constraints_registry": "worldgen_constraints.registry.json",
    "astronomy_catalog_index": "astronomy.catalog.index.json",
    "site_registry_index": "site.registry.index.json",
    "ephemeris_registry": "ephemeris.registry.json",
    "terrain_tile_registry": "terrain.tile.registry.json",
    "ui_registry": "ui.registry.json",
}

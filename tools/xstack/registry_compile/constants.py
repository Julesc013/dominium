"""Registry compile constants and output naming contract."""

REGISTRY_FORMAT_VERSION = "1.0.0"
COMPILER_VERSION = "1.4.0"
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

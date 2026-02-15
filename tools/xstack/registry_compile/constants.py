"""Registry compile constants and output naming contract."""

REGISTRY_FORMAT_VERSION = "1.0.0"
COMPILER_VERSION = "1.1.0"
DEFAULT_BUNDLE_ID = "bundle.base.lab"
DEFAULT_REGISTRY_OUT_DIR_REL = "build/registries"
DEFAULT_LOCKFILE_OUT_REL = "build/lockfile.json"
DEFAULT_COMPATIBILITY_VERSION = "1.0.0"


REGISTRY_OUTPUT_FILENAMES = {
    "domain_registry": "domain.registry.json",
    "law_registry": "law.registry.json",
    "experience_registry": "experience.registry.json",
    "lens_registry": "lens.registry.json",
    "activation_policy_registry": "activation_policy.registry.json",
    "budget_policy_registry": "budget_policy.registry.json",
    "fidelity_policy_registry": "fidelity_policy.registry.json",
    "astronomy_catalog_index": "astronomy.catalog.index.json",
    "site_registry_index": "site.registry.index.json",
    "ui_registry": "ui.registry.json",
}

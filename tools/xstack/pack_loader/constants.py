"""Pack System v1 constants bound to canonical contract vocabulary."""

PACKS_ROOT_REL = "packs"
PACK_MANIFEST_NAME = "pack.json"

PACK_CATEGORIES = (
    "core",
    "domain",
    "derived",
    "experience",
    "law",
    "physics",
    "representation",
    "specs",
    "source",
    "tool",
)

SUPPORTED_CONTRIBUTION_TYPES = (
    "assets",
    "dem_source",
    "domain",
    "ephemeris_source",
    "experience_profile",
    "law_profile",
    "lens",
    "registry_entries",
    "scenario_spec",
    "ui_windows",
    "worldgen_constraints",
)

FORBIDDEN_PACK_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".com",
    ".cpl",
    ".dll",
    ".exe",
    ".js",
    ".msi",
    ".ps1",
    ".py",
    ".pyd",
    ".pyw",
    ".sh",
    ".so",
}

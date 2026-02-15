"""Pack System v1 constants bound to canonical contract vocabulary."""

PACKS_ROOT_REL = "packs"
PACK_MANIFEST_NAME = "pack.json"

PACK_CATEGORIES = (
    "core",
    "domain",
    "experience",
    "law",
    "tool",
)

SUPPORTED_CONTRIBUTION_TYPES = (
    "assets",
    "domain",
    "experience_profile",
    "law_profile",
    "lens",
    "registry_entries",
    "scenario_spec",
    "ui_windows",
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


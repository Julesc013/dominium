"""Extension discipline helpers for deterministic normalization and access."""

from src.meta_extensions_engine import (
    DEFAULT_EXTENSION_POLICY_ID,
    EXTENSION_INTERPRETATION_REGISTRY_REL,
    STRICT_EXTENSION_POLICY_ID,
    WARN_EXTENSION_POLICY_ID,
    extension_interpretation_registry_hash,
    extensions_get,
    legacy_alias_for_key,
    load_extension_interpretation_registry,
    normalize_extension_interpretation_rows,
    normalize_extensions_map,
    normalize_extensions_tree,
    validate_extensions_map,
    validate_extensions_tree,
)

__all__ = [
    "DEFAULT_EXTENSION_POLICY_ID",
    "WARN_EXTENSION_POLICY_ID",
    "STRICT_EXTENSION_POLICY_ID",
    "EXTENSION_INTERPRETATION_REGISTRY_REL",
    "load_extension_interpretation_registry",
    "normalize_extension_interpretation_rows",
    "extension_interpretation_registry_hash",
    "legacy_alias_for_key",
    "normalize_extensions_map",
    "normalize_extensions_tree",
    "validate_extensions_map",
    "validate_extensions_tree",
    "extensions_get",
]

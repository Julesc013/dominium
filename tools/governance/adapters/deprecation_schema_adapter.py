"""Adapter helper for legacy deprecation schema metadata locations."""

from __future__ import annotations

from typing import Dict


LEGACY_SCHEMA_ID = "dominium.schema.deprecation.entry"
GOVERNANCE_SCHEMA_ID = "dominium.schema.governance.deprecation_entry"


def schema_alias_map() -> Dict[str, str]:
    """Return deterministic schema-id aliases used by migration tooling."""
    return {
        LEGACY_SCHEMA_ID: GOVERNANCE_SCHEMA_ID,
    }


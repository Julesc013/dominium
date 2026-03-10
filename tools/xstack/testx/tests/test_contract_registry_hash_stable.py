"""FAST test: semantic contract registry hash is deterministic and pinned."""

from __future__ import annotations

import sys


TEST_ID = "test_contract_registry_hash_stable"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "hash"]

EXPECTED_REGISTRY_HASH = "a996c8327410bd3965108401f98c0d0aacd1fb173b9e7bcbace0da6241f5625b"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.compatx.core.semantic_contract_validator import (
        load_semantic_contract_registry,
        registry_hash,
        validate_semantic_contract_registry,
    )

    payload, error = load_semantic_contract_registry(repo_root)
    if error:
        return {"status": "fail", "message": "semantic contract registry load failed: {}".format(error)}
    errors = validate_semantic_contract_registry(payload)
    if errors:
        return {"status": "fail", "message": "semantic contract registry validation failed: {}".format(", ".join(errors))}
    first = registry_hash(payload)
    second = registry_hash(payload)
    if first != second:
        return {"status": "fail", "message": "semantic contract registry hash drifted across repeated reads"}
    if first != EXPECTED_REGISTRY_HASH:
        return {"status": "fail", "message": "semantic contract registry hash changed without explicit update"}
    return {"status": "pass", "message": "semantic contract registry hash stable"}

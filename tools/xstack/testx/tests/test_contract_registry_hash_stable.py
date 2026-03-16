"""FAST test: semantic contract registry hash is deterministic and pinned."""

from __future__ import annotations

import sys


TEST_ID = "test_contract_registry_hash_stable"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "hash"]

def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.release.scope_freeze_common import FROZEN_SEMANTIC_CONTRACT_REGISTRY_HASH
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
    if first != FROZEN_SEMANTIC_CONTRACT_REGISTRY_HASH:
        return {"status": "fail", "message": "semantic contract registry hash changed without explicit update"}
    return {"status": "pass", "message": "semantic contract registry hash stable"}

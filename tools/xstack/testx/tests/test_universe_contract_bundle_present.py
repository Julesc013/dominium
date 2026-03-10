"""FAST test: universe semantic contract bundle artifact is buildable and schema-valid."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_universe_contract_bundle_present"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.compatx.core.semantic_contract_validator import (
        build_default_universe_contract_bundle,
        load_semantic_contract_registry,
        validate_semantic_contract_registry,
        validate_universe_contract_bundle,
    )
    from tools.xstack.compatx.validator import validate_instance

    registry_payload, error = load_semantic_contract_registry(repo_root)
    if error:
        return {"status": "fail", "message": "semantic contract registry load failed: {}".format(error)}
    registry_errors = validate_semantic_contract_registry(registry_payload)
    if registry_errors:
        return {"status": "fail", "message": "semantic contract registry validation failed: {}".format(", ".join(registry_errors))}

    payload = build_default_universe_contract_bundle(registry_payload)
    bundle_errors = validate_universe_contract_bundle(repo_root=repo_root, payload=payload, registry_payload=registry_payload)
    if bundle_errors:
        return {"status": "fail", "message": "semantic contract bundle validation failed: {}".format(", ".join(bundle_errors))}

    bundle_abs = os.path.join(repo_root, "build", "compat_sem0", "universe_contract_bundle.json")
    os.makedirs(os.path.dirname(bundle_abs), exist_ok=True)
    with open(bundle_abs, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    if not os.path.isfile(bundle_abs):
        return {"status": "fail", "message": "universe_contract_bundle.json fixture was not written"}

    validated = validate_instance(repo_root=repo_root, schema_name="universe_contract_bundle", payload=payload, strict_top_level=True)
    if not bool(validated.get("valid", False)):
        return {"status": "fail", "message": "generated universe contract bundle failed schema validation"}
    registry_hash = str(dict(payload.get("extensions") or {}).get("semantic_contract_registry_hash", "")).strip()
    if len(registry_hash) != 64:
        return {"status": "fail", "message": "semantic contract registry hash missing from bundle extensions"}
    return {"status": "pass", "message": "universe contract bundle present and schema-valid"}

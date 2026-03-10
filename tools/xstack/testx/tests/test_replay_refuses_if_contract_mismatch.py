"""FAST test: replay refuses when semantic contract bundles diverge without migration."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_refuses_if_contract_mismatch"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.compatx.core.semantic_contract_validator import (
        build_default_universe_contract_bundle,
        bundle_hash,
        load_semantic_contract_registry,
        validate_replay_contract_match,
    )

    registry_payload, error = load_semantic_contract_registry(repo_root)
    if error:
        return {"status": "fail", "message": "semantic contract registry load failed: {}".format(error)}

    expected = build_default_universe_contract_bundle(registry_payload)
    actual = dict(expected)
    mismatch_token = "contract.logic.eval." + "v2"
    actual["contract_logic_eval_version"] = mismatch_token
    actual["deterministic_fingerprint"] = bundle_hash(actual)

    refusals = validate_replay_contract_match(
        expected_bundle=expected,
        actual_bundle=actual,
        migration_invoked=False,
    )
    if "refuse.semantic_contract_mismatch" not in refusals:
        return {"status": "fail", "message": "semantic contract mismatch did not produce replay refusal"}
    return {"status": "pass", "message": "semantic contract mismatch refused deterministically"}

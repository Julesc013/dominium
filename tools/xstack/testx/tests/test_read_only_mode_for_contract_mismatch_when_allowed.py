"""FAST test: contract mismatch can degrade to read-only mode when explicitly allowed."""

from __future__ import annotations


TEST_ID = "test_read_only_applied_for_contract_mismatch_when_allowed"
TEST_TAGS = ["fast", "compat", "cap_neg"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg_testlib import build_default_pair, negotiate

    client, server = build_default_pair(repo_root)
    client["semantic_contract_versions_supported"] = [
        {"contract_category_id": "contract.worldgen.refinement", "min_version": 1, "max_version": 1},
    ]
    server["semantic_contract_versions_supported"] = [
        {"contract_category_id": "contract.worldgen.refinement", "min_version": 2, "max_version": 2},
    ]
    result = negotiate(repo_root, client, server, allow_read_only=True)
    record = dict(result.get("negotiation_record") or {})
    extensions = dict(record.get("extensions") or {})
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "read-only negotiation did not complete"}
    if str(record.get("compatibility_mode_id", "")) != "compat.read_only":
        return {"status": "fail", "message": "contract mismatch did not select read-only compatibility"}
    if str(extensions.get("official.compat.read_only_law_profile_id", "")) != "law.observer.default":
        return {"status": "fail", "message": "read-only compatibility did not bind observer law profile"}
    return {"status": "pass", "message": "contract mismatch degrades to read-only when allowed"}

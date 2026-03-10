"""FAST test: CAP-NEG-2 read-only fallback is selected for contract mismatch when allowed."""

from __future__ import annotations


TEST_ID = "test_readonly_mode_for_contract_mismatch"
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
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "read-only negotiation did not complete"}
    if str(record.get("compatibility_mode_id", "")) != "compat.read_only":
        return {"status": "fail", "message": "contract mismatch did not negotiate read-only mode"}
    return {"status": "pass", "message": "contract mismatch negotiates read-only mode when allowed"}

"""FAST test: endpoint descriptors include target ids, os/abi/arch ids, and tier."""

from __future__ import annotations


TEST_ID = "test_endpoint_descriptor_includes_target_ids"
TEST_TAGS = ["fast", "release", "platform", "arch-matrix", "descriptor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.arch_matrix_testlib import build_report

    descriptor_row = dict(build_report(repo_root).get("descriptor_row") or {})
    if list(descriptor_row.get("missing_fields") or []):
        return {"status": "fail", "message": "descriptor target fields are missing"}
    for key in ("target_id", "os_id", "arch_id", "abi_id"):
        if str(descriptor_row.get(key, "")).strip():
            continue
        return {"status": "fail", "message": "descriptor field '{}' is blank".format(key)}
    if int(descriptor_row.get("target_tier", 0) or 0) <= 0:
        return {"status": "fail", "message": "descriptor target tier must be positive"}
    return {"status": "pass", "message": "descriptor includes target ids and tier"}

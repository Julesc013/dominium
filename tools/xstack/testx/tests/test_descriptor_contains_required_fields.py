"""FAST test: emitted descriptors contain the required CAP-NEG-1 fields."""

from __future__ import annotations


TEST_ID = "test_descriptor_contains_required_fields"
TEST_TAGS = ["fast", "compat", "descriptor"]


REQUIRED_FIELDS = (
    "product_id",
    "product_version",
    "protocol_versions_supported",
    "semantic_contract_versions_supported",
    "feature_capabilities",
    "required_capabilities",
    "optional_capabilities",
    "degrade_ladders",
    "deterministic_fingerprint",
)


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg1_testlib import emit_descriptor

    payload = emit_descriptor(repo_root, "server")
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        return {"status": "fail", "message": "descriptor missing required fields: {}".format(", ".join(missing))}
    return {"status": "pass", "message": "emitted descriptors carry the required CAP-NEG-1 fields"}

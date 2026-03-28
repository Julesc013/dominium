"""FAST test: negotiation selects the highest mutually supported protocol version."""

from __future__ import annotations


TEST_ID = "test_highest_common_protocol_selected"
TEST_TAGS = ["fast", "compat", "cap_neg"]


def run(repo_root: str):
    from compat import build_endpoint_descriptor, negotiate_endpoint_descriptors

    protocol_rows_a = [
        {"protocol_id": "protocol.loopback.session", "min_version": "1.0.0", "max_version": "1.2.0"},
    ]
    protocol_rows_b = [
        {"protocol_id": "protocol.loopback.session", "min_version": "1.1.0", "max_version": "1.3.0"},
    ]
    contract_rows = [
        {"contract_category_id": "contract.worldgen.refinement", "min_version": 1, "max_version": 1},
    ]
    client = build_endpoint_descriptor(
        product_id="client",
        product_version="0.0.0+test",
        protocol_versions_supported=protocol_rows_a,
        semantic_contract_versions_supported=contract_rows,
        feature_capabilities=["cap.ui.tui"],
        required_capabilities=[],
        optional_capabilities=[],
        degrade_ladders=[],
    )
    server = build_endpoint_descriptor(
        product_id="server",
        product_version="0.0.0+test",
        protocol_versions_supported=protocol_rows_b,
        semantic_contract_versions_supported=contract_rows,
        feature_capabilities=["cap.ui.tui"],
        required_capabilities=[],
        optional_capabilities=[],
        degrade_ladders=[],
    )
    result = negotiate_endpoint_descriptors(repo_root, client, server)
    chosen = dict((result.get("negotiation_record") or {}))
    if str(chosen.get("chosen_protocol_version", "")) != "1.2.0":
        return {"status": "fail", "message": "highest common protocol version was not selected"}
    return {"status": "pass", "message": "highest common protocol version selected"}

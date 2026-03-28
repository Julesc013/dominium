"""FAST test: SYS-1 interface validation refuses unregistered spec references."""

from __future__ import annotations

import sys


TEST_ID = "test_spec_limit_validation"
TEST_TAGS = ["fast", "system", "sys1", "validation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from system import validate_interface_signature
    from tools.xstack.testx.tests.sys1_testlib import cloned_state, validation_payloads

    state = cloned_state()
    interface_rows = list(state.get("system_interface_signature_rows") or [])
    if not interface_rows:
        return {"status": "fail", "message": "fixture missing interface signature rows"}
    interface_rows[0]["spec_compliance_ref"] = "spec.nonexistent"

    registries = validation_payloads(repo_root=repo_root)
    result = validate_interface_signature(
        system_id="system.engine.alpha",
        system_rows=state.get("system_rows") or [],
        interface_signature_rows=interface_rows,
        quantity_bundle_registry_payload=registries.get("quantity_bundle_registry_payload"),
        spec_type_registry_payload=registries.get("spec_type_registry_payload"),
        signal_channel_type_registry_payload=registries.get("signal_channel_type_registry_payload"),
    )
    if str(result.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "expected refused result for unregistered spec compliance ref"}
    failed = list(result.get("failed_checks") or [])
    check_ids = set(str(row.get("check_id", "")).strip() for row in failed if isinstance(row, dict))
    if "interface.spec_compliance_ref.registered" not in check_ids:
        return {"status": "fail", "message": "missing spec compliance registration failure check"}
    return {"status": "pass", "message": "spec registration validation enforced"}

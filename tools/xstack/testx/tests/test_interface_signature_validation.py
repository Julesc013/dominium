"""FAST test: SYS-1 interface signatures validate when complete and registered."""

from __future__ import annotations

import sys


TEST_ID = "test_interface_signature_validation"
TEST_TAGS = ["fast", "system", "sys1", "validation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from system import validate_interface_signature
    from tools.xstack.testx.tests.sys1_testlib import cloned_state, validation_payloads

    state = cloned_state()
    registries = validation_payloads(repo_root=repo_root)
    result = validate_interface_signature(
        system_id="system.engine.alpha",
        system_rows=state.get("system_rows") or [],
        interface_signature_rows=state.get("system_interface_signature_rows") or [],
        quantity_bundle_registry_payload=registries.get("quantity_bundle_registry_payload"),
        spec_type_registry_payload=registries.get("spec_type_registry_payload"),
        signal_channel_type_registry_payload=registries.get("signal_channel_type_registry_payload"),
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "expected complete interface validation result"}
    if list(result.get("failed_checks") or []):
        return {"status": "fail", "message": "interface validation reported failed checks for valid fixture"}
    return {"status": "pass", "message": "interface validation accepts complete registered signature"}

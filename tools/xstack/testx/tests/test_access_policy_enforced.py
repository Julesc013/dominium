"""FAST test: META-INSTR0 control access policy is enforced deterministically."""

from __future__ import annotations

import os
import sys


TEST_ID = "test_access_policy_enforced"
TEST_TAGS = ["fast", "meta", "instrumentation", "access"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from meta_instr0_testlib import authority_context, instrumentation_inputs
    from meta.instrumentation import REFUSAL_INSTRUMENTATION_ACCESS_DENIED, validate_control_access

    payloads = instrumentation_inputs(repo_root)
    denied = validate_control_access(
        owner_kind="domain",
        owner_id="domain.elec",
        control_point_id="control.elec.breaker.reset",
        authority_context=authority_context(privilege_level="observer", entitlements=["session.boot"]),
        has_physical_access=True,
        instrumentation_surface_registry_payload=payloads["instrumentation_surface_registry_payload"],
        access_policy_registry_payload=payloads["access_policy_registry_payload"],
    )
    if str(denied.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "expected observer without inspect entitlement to be refused"}
    if str(denied.get("reason_code", "")).strip() != REFUSAL_INSTRUMENTATION_ACCESS_DENIED:
        return {"status": "fail", "message": "unexpected refusal reason for denied control access"}

    allowed = validate_control_access(
        owner_kind="domain",
        owner_id="domain.elec",
        control_point_id="control.elec.breaker.reset",
        authority_context=authority_context(privilege_level="operator", entitlements=["session.boot", "entitlement.inspect"]),
        has_physical_access=True,
        instrumentation_surface_registry_payload=payloads["instrumentation_surface_registry_payload"],
        access_policy_registry_payload=payloads["access_policy_registry_payload"],
    )
    if str(allowed.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "expected operator with inspect entitlement to pass control access"}
    return {"status": "pass", "message": "control access policy enforced deterministically"}


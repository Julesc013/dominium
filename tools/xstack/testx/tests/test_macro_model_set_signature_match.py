"""FAST test: SYS-1 macro model set validation enforces interface signature compatibility."""

from __future__ import annotations

import sys


TEST_ID = "test_macro_model_set_signature_match"
TEST_TAGS = ["fast", "system", "sys1", "validation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from system import validate_macro_model_set
    from tools.xstack.testx.tests.sys1_testlib import macro_validation_fixture

    fixture = macro_validation_fixture(repo_root=repo_root)
    state = dict(fixture.get("state") or {})
    registries = dict(fixture.get("registries") or {})
    result = validate_macro_model_set(
        capsule_id=str(fixture.get("capsule_id", "")).strip(),
        system_rows=state.get("system_rows") or [],
        interface_signature_rows=state.get("system_interface_signature_rows") or [],
        system_macro_capsule_rows=state.get("system_macro_capsule_rows") or [],
        macro_model_set_registry_payload=registries.get("macro_model_set_registry_payload"),
        constitutive_model_registry_payload=registries.get("constitutive_model_registry_payload"),
        tolerance_policy_registry_payload=registries.get("tolerance_policy_registry_payload"),
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "expected macro model set validation to pass for matching fixture"}
    if list(result.get("failed_checks") or []):
        return {"status": "fail", "message": "macro model set validation reported failed checks unexpectedly"}
    return {"status": "pass", "message": "macro model set signature validation accepts matching bindings"}

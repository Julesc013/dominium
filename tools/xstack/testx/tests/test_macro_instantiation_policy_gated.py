"""FAST test: SYS-4 macro instantiation is policy-gated."""

from __future__ import annotations

import sys


TEST_ID = "test_macro_instantiation_policy_gated"
TEST_TAGS = ["fast", "system", "sys4", "template"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.system import REFUSAL_TEMPLATE_FORBIDDEN_MODE
    from tools.xstack.testx.tests.sys4_testlib import cloned_state, execute_template_instantiate

    denied_state = cloned_state()
    denied = execute_template_instantiate(
        repo_root=repo_root,
        state=denied_state,
        template_id="template.generator.diesel_stub",
        instantiation_mode="macro",
        target_spatial_id="cell.sys4.test.macro.denied",
        allow_macro=False,
    )
    if str(denied.get("result", "")).strip() not in {"refusal", "refused"}:
        return {"status": "fail", "message": "macro instantiation should be refused when policy gate is closed"}
    reason_code = str(denied.get("reason_code", "")).strip() or str(
        dict(denied.get("refusal") or {}).get("reason_code", "")
    ).strip()
    if reason_code != REFUSAL_TEMPLATE_FORBIDDEN_MODE:
        return {"status": "fail", "message": "macro instantiation refusal reason code mismatch"}

    allowed_state = cloned_state()
    allowed = execute_template_instantiate(
        repo_root=repo_root,
        state=allowed_state,
        template_id="template.generator.diesel_stub",
        instantiation_mode="macro",
        target_spatial_id="cell.sys4.test.macro.allowed",
        allow_macro=True,
    )
    if str(allowed.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "macro instantiation did not complete when policy gate opened"}
    system_rows = [
        dict(row)
        for row in list(allowed_state.get("system_rows") or [])
        if isinstance(row, dict)
    ]
    if not any(str(row.get("current_tier", "")).strip() == "macro" for row in system_rows):
        return {"status": "fail", "message": "macro instantiation did not produce macro-tier system row"}
    return {"status": "pass", "message": "macro template instantiation policy gate is enforced deterministically"}

"""FAST test: SYS-1 collapse is refused when interface signature is invalid."""

from __future__ import annotations

import sys


TEST_ID = "test_collapse_refused_on_invalid_interface"
TEST_TAGS = ["fast", "system", "sys1", "validation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from system import REFUSAL_SYSTEM_COLLAPSE_INVALID_INTERFACE
    from tools.xstack.testx.tests.sys0_testlib import cloned_state, execute_system_process

    state = cloned_state()
    interface_rows = list(state.get("system_interface_signature_rows") or [])
    if not interface_rows:
        return {"status": "fail", "message": "fixture missing interface signature rows"}
    ports = list((interface_rows[0] or {}).get("port_list") or [])
    if not ports:
        return {"status": "fail", "message": "fixture missing interface ports"}
    ports[0]["allowed_bundle_ids"] = []

    result = execute_system_process(
        state=state,
        process_id="process.system_collapse",
        inputs={"system_id": "system.engine.alpha"},
    )
    if str(result.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "collapse should refuse when interface validation fails"}
    reason_code = str(dict(result.get("refusal") or {}).get("reason_code", "")).strip()
    if reason_code != str(REFUSAL_SYSTEM_COLLAPSE_INVALID_INTERFACE):
        return {
            "status": "fail",
            "message": "unexpected refusal reason for invalid interface: {}".format(reason_code or "<empty>"),
        }
    return {"status": "pass", "message": "invalid interface path returns deterministic collapse refusal"}

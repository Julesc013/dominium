"""FAST test: CAP-NEG-4 refuses when endpoints share no common protocol."""

from __future__ import annotations


TEST_ID = "test_refusal_on_no_common_protocol"
TEST_TAGS = ["fast", "compat", "cap_neg", "interop"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg4_testlib import interop_stress_report, scenario_row

    row = scenario_row(interop_stress_report(repo_root), "interop.client_server.no_common_protocol")
    if str(row.get("compatibility_mode_id", "")) != "compat.refuse":
        return {"status": "fail", "message": "expected compat.refuse for no-common-protocol scenario"}
    if str(row.get("actual_refusal_code", "")) != "refusal.compat.no_common_protocol":
        return {"status": "fail", "message": "unexpected refusal code for no-common-protocol scenario"}
    return {"status": "pass", "message": "no-common-protocol refusal is stable"}

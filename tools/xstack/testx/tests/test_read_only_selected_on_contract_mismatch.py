"""FAST test: CAP-NEG-4 selects read-only on safe contract mismatch fallback."""

from __future__ import annotations


TEST_ID = "test_read_only_selected_on_contract_mismatch"
TEST_TAGS = ["fast", "compat", "cap_neg", "interop"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg4_testlib import interop_stress_report, scenario_row

    row = scenario_row(interop_stress_report(repo_root), "interop.client_server.contract_mismatch_read_only")
    if str(row.get("compatibility_mode_id", "")) != "compat.read_only":
        return {"status": "fail", "message": "expected compat.read_only for contract mismatch fallback"}
    if str(row.get("actual_refusal_code", "")):
        return {"status": "fail", "message": "read-only fallback unexpectedly refused"}
    return {"status": "pass", "message": "read-only fallback selected deterministically"}

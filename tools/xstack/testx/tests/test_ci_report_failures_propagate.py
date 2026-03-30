from __future__ import annotations

TEST_ID = "test_ci_report_failures_propagate"
TEST_TAGS = ["fast", "xi7", "ci", "guardrails"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.ci.ci_common import _apply_gate_report_payload

    refused = _apply_gate_report_payload(
        {"gate_id": "validate_strict", "status": "pass"},
        {"deterministic_fingerprint": "fp0", "result": "refused"},
        report_refreshed=True,
    )
    if str(refused.get("status", "")).strip() != "fail":
        return {"status": "fail", "message": "refused gate report did not fail Xi-7 gate status"}

    stale = _apply_gate_report_payload(
        {"gate_id": "validate_strict", "status": "pass"},
        {"deterministic_fingerprint": "fp1", "result": "complete"},
        report_refreshed=False,
    )
    if str(stale.get("status", "")).strip() != "fail":
        return {"status": "fail", "message": "stale gate report did not fail Xi-7 gate status"}

    blocking = _apply_gate_report_payload(
        {"gate_id": "arch_audit_2", "status": "pass"},
        {"blocking_finding_count": 1, "deterministic_fingerprint": "fp2", "result": "complete"},
        report_refreshed=True,
    )
    if str(blocking.get("status", "")).strip() != "fail":
        return {"status": "fail", "message": "blocking findings did not fail Xi-7 gate status"}

    return {"status": "pass", "message": "Xi-7 gate status propagates refused, stale, and blocking gate reports"}

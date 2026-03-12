"""FAST test: portable and linked installs preserve the same truth-facing MVP artifacts."""

from __future__ import annotations


TEST_ID = "test_portable_linked_parity"
TEST_TAGS = ["fast", "mvp", "cross-platform", "portable"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mvp_cross_platform_testlib import load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    parity = dict(report.get("portable_linked_parity") or {})
    if str(parity.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "MVP cross-platform portable-vs-linked parity is not complete"}
    assertions = dict(parity.get("assertions") or {})
    for key in (
        "scenario_fingerprint_match",
        "proof_anchors_match",
        "pack_locks_match",
        "negotiation_records_match",
        "repro_bundles_match",
    ):
        if bool(assertions.get(key, False)):
            continue
        return {"status": "fail", "message": "MVP cross-platform portable parity assertion '{}' failed".format(key)}
    portable = dict(parity.get("portable") or {})
    linked = dict(parity.get("linked") or {})
    for key in ("proof_anchor_fingerprint", "pack_lock_fingerprint", "negotiation_record_fingerprint", "repro_bundle_fingerprint"):
        if str(portable.get(key, "")).strip() == str(linked.get(key, "")).strip():
            continue
        return {"status": "fail", "message": "MVP cross-platform portable/link parity drifted for {}".format(key)}
    portable_scenario = dict(portable.get("scenario_artifacts") or {})
    linked_scenario = dict(linked.get("scenario_artifacts") or {})
    if str(portable_scenario.get("scenario_fingerprint", "")).strip() != str(linked_scenario.get("scenario_fingerprint", "")).strip():
        return {"status": "fail", "message": "MVP cross-platform scenario fingerprint drifted between portable and linked installs"}
    return {"status": "pass", "message": "Portable and linked installs preserve the same truth-facing MVP artifacts"}

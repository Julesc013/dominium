"""FAST test: MVP smoke repro bundle replay validates deterministically."""

from __future__ import annotations


TEST_ID = "test_replay_bundle_validates"
TEST_TAGS = ["fast", "mvp", "smoke", "diag"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mvp_smoke_testlib import load_complete_report

    report, error = load_complete_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    diag_verify = dict(report.get("diag_verify") or {})
    replay_result = dict(diag_verify.get("replay_result") or {})
    if str(diag_verify.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "MVP smoke diag replay verification did not complete"}
    if not bool(replay_result.get("hash_match", False)):
        return {"status": "fail", "message": "MVP smoke diag replay reported a bundle hash mismatch"}
    if not bool(replay_result.get("proof_hash_match", False)):
        return {"status": "fail", "message": "MVP smoke diag replay reported a proof-window hash mismatch"}
    if str(dict(report.get("diag_bundle") or {}).get("bundle_hash", "")).strip() != str(diag_verify.get("bundle_hash", "")).strip():
        return {"status": "fail", "message": "MVP smoke diag replay did not validate the recorded bundle hash"}
    return {"status": "pass", "message": "MVP smoke repro bundle replay validates deterministically"}

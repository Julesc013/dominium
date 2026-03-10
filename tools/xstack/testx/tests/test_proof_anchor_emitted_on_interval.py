"""FAST test: SERVER-MVP-0 emits proof anchors on the configured interval."""

from __future__ import annotations


TEST_ID = "test_proof_anchor_emitted_on_interval"
TEST_TAGS = ["fast", "server", "proof"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp0_testlib import run_window

    report = run_window(repo_root, suffix="proof_anchor_interval", ticks=8)
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "server proof-anchor window did not complete"}
    interval = int(report.get("proof_anchor_interval_ticks", 0) or 0)
    final_tick = int(report.get("final_tick", 0) or 0)
    if interval < 1:
        return {"status": "fail", "message": "proof_anchor_interval_ticks must be >= 1"}
    expected_ticks = list(range(interval, final_tick + 1, interval))
    actual_ticks = list(report.get("proof_anchor_ticks") or [])
    if actual_ticks != expected_ticks:
        return {
            "status": "fail",
            "message": "expected proof anchor ticks {}, got {}".format(expected_ticks, actual_ticks),
        }
    return {"status": "pass", "message": "server emits proof anchors on the configured deterministic interval"}

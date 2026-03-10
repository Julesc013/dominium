"""FAST test: APPSHELL-4 IPC frame sequence numbers remain monotonic per channel."""

from __future__ import annotations


TEST_ID = "test_seq_no_monotonic"
TEST_TAGS = ["fast", "appshell", "ipc", "framing"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import run_probe

    report = run_probe(repo_root, suffix="seq")
    monotonic = dict(report.get("seq_monotonic_by_channel") or {})
    if not monotonic:
        return {"status": "fail", "message": "probe did not capture any IPC sequence numbers"}
    failed = [channel_id for channel_id, ok in sorted(monotonic.items()) if not bool(ok)]
    if failed:
        return {"status": "fail", "message": "non-monotonic IPC sequence numbers for {}".format(", ".join(failed))}
    return {"status": "pass", "message": "IPC sequence numbers remain monotonic per channel"}

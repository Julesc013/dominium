"""STRICT test: server-authoritative full-stack determinism under disorder with snapshot repair."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.mp_authoritative_full_stack"
TEST_TAGS = ["strict", "net", "session", "determinism", "multiplayer"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.net_mp9_testlib import run_authoritative_full_stack

    first = run_authoritative_full_stack(
        repo_root=repo_root,
        save_id="save.testx.net.mp9.authoritative",
        ticks=4,
        disorder_profile_id="disorder.reorder_light",
    )
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "authoritative first run refused unexpectedly"}
    second = run_authoritative_full_stack(
        repo_root=repo_root,
        save_id="save.testx.net.mp9.authoritative",
        ticks=4,
        disorder_profile_id="disorder.reorder_light",
    )
    if str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "authoritative second run refused unexpectedly"}

    if list(first.get("anchors") or []) != list(second.get("anchors") or []):
        return {"status": "fail", "message": "authoritative anchors diverged across deterministic rerun"}
    if str(first.get("final_composite_hash", "")) != str(second.get("final_composite_hash", "")):
        return {"status": "fail", "message": "authoritative final composite hash diverged across deterministic rerun"}
    if int(first.get("resync_count", 0) or 0) < 1:
        return {"status": "fail", "message": "authoritative delta-loss repair path did not trigger deterministic resync"}

    return {"status": "pass", "message": "server-authoritative full-stack deterministic baseline passed"}

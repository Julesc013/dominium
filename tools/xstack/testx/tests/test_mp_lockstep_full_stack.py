"""STRICT test: lockstep full-stack deterministic envelope with disorder + replay resync."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.mp_lockstep_full_stack"
TEST_TAGS = ["strict", "net", "session", "determinism", "multiplayer"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.net_mp9_testlib import run_lockstep_full_stack

    first = run_lockstep_full_stack(
        repo_root=repo_root,
        save_id="save.testx.net.mp9.lockstep",
        ticks=4,
        disorder_profile_id="disorder.reorder_light",
        induce_divergence_tick=2,
    )
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "lockstep first run refused unexpectedly"}
    second = run_lockstep_full_stack(
        repo_root=repo_root,
        save_id="save.testx.net.mp9.lockstep",
        ticks=4,
        disorder_profile_id="disorder.reorder_light",
        induce_divergence_tick=2,
    )
    if str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "lockstep second run refused unexpectedly"}

    if list(first.get("anchors") or []) != list(second.get("anchors") or []):
        return {"status": "fail", "message": "lockstep anchor sequence diverged across repeated deterministic runs"}
    if str(first.get("final_composite_hash", "")) != str(second.get("final_composite_hash", "")):
        return {"status": "fail", "message": "lockstep final composite hash diverged across deterministic rerun"}
    if int(first.get("resync_count", 0) or 0) < 1:
        return {"status": "fail", "message": "lockstep divergence injection did not trigger deterministic replay resync"}

    final_hash = str(first.get("final_composite_hash", ""))
    for peer_id, peer_hash in sorted(dict(first.get("peer_hashes") or {}).items(), key=lambda item: str(item[0])):
        if str(peer_hash) != final_hash:
            return {"status": "fail", "message": "lockstep peer '{}' did not converge to server composite hash".format(peer_id)}

    return {"status": "pass", "message": "lockstep full-stack deterministic envelope baseline passed"}

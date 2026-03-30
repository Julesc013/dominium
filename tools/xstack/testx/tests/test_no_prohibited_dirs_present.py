from __future__ import annotations

from tools.xstack.testx.tests.xi8_testlib import committed_structure_lock, live_snapshot

TEST_ID = "test_no_prohibited_dirs_present"
TEST_TAGS = ["fast", "xi8", "structure", "policy"]


def run(repo_root: str):
    lock_payload = committed_structure_lock(repo_root)
    snapshot = live_snapshot(repo_root)
    live_roots = list(snapshot.get("live_source_like_roots") or [])
    allowed_roots = list(lock_payload.get("allowed_source_like_roots") or [])
    if live_roots != allowed_roots:
        return {
            "status": "fail",
            "message": "live source-like roots do not match Xi-8 allowlist: live={} allowed={}".format(live_roots, allowed_roots),
        }
    for top_dir in list(snapshot.get("top_level_directories") or []):
        if top_dir in {"src", "source", "Source", "Sources"}:
            return {"status": "fail", "message": "forbidden top-level directory present: {}".format(top_dir)}
    return {"status": "pass", "message": "Xi-8 source-like roots are fully policy-classified and no prohibited top-level dirs remain"}

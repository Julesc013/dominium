"""FAST test: GEO-2 frame replay verifier produces stable graph and position hash chains."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_cross_platform_frame_hash_match"
TEST_TAGS = ["fast", "geo", "replay", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.geo.tool_replay_frame_window import verify_frame_window

    first = verify_frame_window()
    second = verify_frame_window()
    if dict(first) != dict(second):
        return {"status": "fail", "message": "frame replay verifier is not deterministic"}
    for key in ("frame_graph_hash_chain", "position_ref_hash_chain", "deterministic_fingerprint"):
        token = str(first.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "missing or invalid {}".format(key)}
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "frame replay verifier reported non-complete result"}
    return {"status": "pass", "message": "GEO-2 frame replay hash chains stable"}

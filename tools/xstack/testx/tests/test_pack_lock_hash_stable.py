"""FAST test: the canonical MVP pack lock hash is stable against regeneration."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_pack_lock_hash_stable"
TEST_TAGS = ["fast", "mvp", "pack", "lockfile", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.mvp.runtime_bundle import MVP_PACK_LOCK_REL, build_pack_lock_payload

    lock_path = os.path.join(repo_root, MVP_PACK_LOCK_REL.replace("/", os.sep))
    if not os.path.isfile(lock_path):
        return {"status": "fail", "message": "missing MVP pack lock artifact"}
    try:
        payload = json.load(open(lock_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid JSON in MVP pack lock artifact"}

    expected = build_pack_lock_payload(repo_root=repo_root)
    if payload != expected:
        return {"status": "fail", "message": "pack lock payload drifted from deterministic regeneration"}
    return {"status": "pass", "message": "MVP pack lock hash remains stable"}

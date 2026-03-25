"""FAST test: repeated MVP gameplay loop execution is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_gameplay_loop_reproducible"
TEST_TAGS = ["fast", "omega", "gameplay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.gameplay_loop_common import run_gameplay_loop

    first = dict(dict(run_gameplay_loop(repo_root, output_root_rel="build/tmp/testx_omega3_gameplay_a", write_outputs=False) or {}).get("snapshot_payload") or {})
    second = dict(dict(run_gameplay_loop(repo_root, output_root_rel="build/tmp/testx_omega3_gameplay_b", write_outputs=False) or {}).get("snapshot_payload") or {})
    if first != second:
        return {"status": "fail", "message": "MVP gameplay loop snapshot diverged across repeated runs"}
    record = dict(first.get("record") or {})
    return {
        "status": "pass",
        "message": "MVP gameplay loop stable across repeated runs ({})".format(
            str(record.get("deterministic_fingerprint", "")).strip() or "missing-fingerprint"
        ),
    }

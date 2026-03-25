"""STRICT test: repeated disaster suite execution is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_disaster_harness_deterministic"
TEST_TAGS = ["strict", "omega", "disaster", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.disaster_suite_common import run_disaster_suite

    first = dict(run_disaster_suite(repo_root, output_root_rel="build/tmp/testx_omega4_disaster_a", write_outputs=False) or {})
    second = dict(run_disaster_suite(repo_root, output_root_rel="build/tmp/testx_omega4_disaster_b", write_outputs=False) or {})
    if first != second:
        return {"status": "fail", "message": "disaster suite rerun diverged across identical inputs"}
    return {
        "status": "pass",
        "message": "disaster suite stable across repeated runs ({})".format(
            str(first.get("deterministic_fingerprint", "")).strip() or "missing-fingerprint"
        ),
    }

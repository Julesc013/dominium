"""FAST test: disaster suite can rerun against the same work root deterministically."""

from __future__ import annotations

import os
import shutil
import sys


TEST_ID = "test_disaster_harness_reuses_output_root"
TEST_TAGS = ["fast", "omega", "disaster", "cleanup"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.disaster_suite_common import run_disaster_suite

    output_root_rel = "build/tmp/testx_omega4_disaster_reuse"
    output_root_abs = os.path.join(repo_root, output_root_rel.replace("/", os.sep))
    shutil.rmtree(output_root_abs, ignore_errors=True)
    first = dict(run_disaster_suite(repo_root, output_root_rel=output_root_rel, write_outputs=False) or {})
    second = dict(run_disaster_suite(repo_root, output_root_rel=output_root_rel, write_outputs=False) or {})
    if first != second:
        return {"status": "fail", "message": "disaster suite rerun drifted when reusing the same output root"}
    return {
        "status": "pass",
        "message": "disaster suite reuses the same output root deterministically ({})".format(
            str(first.get("deterministic_fingerprint", "")).strip() or "missing-fingerprint"
        ),
    }

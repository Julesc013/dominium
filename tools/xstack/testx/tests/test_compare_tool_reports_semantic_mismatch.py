"""FAST test: Ω-9 compare tool refuses semantic drift for the same environment."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_compare_tool_reports_semantic_mismatch"
TEST_TAGS = ["fast", "omega", "toolchain", "compare"]


def run(repo_root: str):
    from tools.mvp.toolchain_matrix_common import compare_toolchain_runs
    from tools.xstack.testx.tests.toolchain_matrix_testlib import write_synthetic_run_root

    work_root = tempfile.mkdtemp(prefix="omega9_compare_")
    left_run = write_synthetic_run_root(os.path.join(work_root, "left", "run.synthetic"))
    right_run = write_synthetic_run_root(
        os.path.join(work_root, "right", "run.synthetic"),
        endpoint_semantic_hashes={"client": "sem.client.drift", "server": "sem.server"},
    )
    report = compare_toolchain_runs(repo_root, left_run, right_run)
    if str(report.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "compare tool must refuse semantic drift for same-env runs"}
    categories = {
        str((row or {}).get("category", "")).strip()
        for row in list(report.get("blocking_differences") or [])
    }
    if "semantic.endpoint_descriptors" not in categories:
        return {"status": "fail", "message": "compare tool did not report endpoint semantic drift"}
    return {"status": "pass", "message": "compare tool refuses same-env semantic drift"}

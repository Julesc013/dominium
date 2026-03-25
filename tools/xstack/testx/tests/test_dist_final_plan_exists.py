"""FAST test: Ω-10 final distribution plan surfaces exist."""

from __future__ import annotations

import os


TEST_ID = "test_dist_final_plan_exists"
TEST_TAGS = ["fast", "omega", "dist", "release"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist_final_testlib import required_plan_paths

    for rel_path in required_plan_paths():
        if os.path.exists(os.path.join(repo_root, rel_path.replace("/", os.sep))):
            continue
        return {"status": "fail", "message": "missing Ω-10 required surface '{}'".format(rel_path)}
    return {"status": "pass", "message": "Ω-10 final distribution plan surfaces exist"}

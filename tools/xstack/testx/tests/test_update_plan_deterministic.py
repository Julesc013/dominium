"""FAST test: update plan resolution is deterministic for identical inputs."""

from __future__ import annotations

import json


TEST_ID = "test_update_plan_deterministic"
TEST_TAGS = ["fast", "release", "update-model", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.update_model_testlib import build_plan

    left = build_plan(repo_root)
    right = build_plan(repo_root)
    left_plan = dict(left.get("update_plan") or {})
    right_plan = dict(right.get("update_plan") or {})
    if str(left.get("result", "")).strip() != "complete" or str(right.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "update plan resolution must complete for identical inputs"}
    if str(left_plan.get("deterministic_fingerprint", "")).strip() != str(right_plan.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "update plan fingerprint drifted across repeated identical runs"}
    if json.dumps(left_plan, sort_keys=True) != json.dumps(right_plan, sort_keys=True):
        return {"status": "fail", "message": "update plan payload drifted across repeated identical runs"}
    return {"status": "pass", "message": "update plan resolution is deterministic"}

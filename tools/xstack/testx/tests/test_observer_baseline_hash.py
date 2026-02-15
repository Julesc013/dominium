"""STRICT test: observer baseline lock composite hash remains stable."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.regression.observer_baseline_hash"
TEST_TAGS = ["strict", "regression", "session", "registry"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.packagingx import run_lab_build_validation

    baseline = _load_json(os.path.join(repo_root, "data", "regression", "observer_baseline.json"))
    result = run_lab_build_validation(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        dist_a="build/dist.testx.regression.baseline.a",
        dist_b="build/dist.testx.regression.baseline.b",
        save_id="save.testx.regression.baseline",
    )
    if result.get("result") != "complete":
        return {"status": "fail", "message": "lab build validation failed for baseline check"}

    if str(result.get("composite_hash_anchor", "")) != str(baseline.get("composite_hash_anchor", "")):
        return {"status": "fail", "message": "composite hash anchor differs from observer baseline lock"}
    if str(result.get("pack_lock_hash", "")) != str(baseline.get("pack_lock_hash", "")):
        return {"status": "fail", "message": "pack_lock_hash differs from observer baseline lock"}

    expected_regs = dict(baseline.get("registry_hashes") or {})
    actual_regs = dict(result.get("registry_hashes") or {})
    for key in sorted(expected_regs.keys()):
        if str(actual_regs.get(key, "")) != str(expected_regs.get(key, "")):
            return {"status": "fail", "message": "registry hash mismatch for '{}'".format(key)}
    return {"status": "pass", "message": "observer baseline hash regression lock passed"}

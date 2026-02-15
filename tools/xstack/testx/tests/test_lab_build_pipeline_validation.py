"""STRICT test: full lab dist pipeline produces stable composite hash anchors."""

from __future__ import annotations

import sys


TEST_ID = "testx.lab_build.pipeline_validation"
TEST_TAGS = ["strict", "session", "registry", "bundle"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.packagingx import run_lab_build_validation

    result = run_lab_build_validation(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        dist_a="build/dist.testx.lab.a",
        dist_b="build/dist.testx.lab.b",
        save_id="save.testx.lab_build_validation",
    )
    if result.get("result") != "complete":
        return {"status": "fail", "message": "lab build validation failed"}
    if str(result.get("lab_build_status", "")) != "pass":
        return {"status": "fail", "message": "lab build status is not pass"}
    if not str(result.get("composite_hash_anchor", "")).strip():
        return {"status": "fail", "message": "lab build validation missing composite hash anchor"}
    return {
        "status": "pass",
        "message": "lab build validation passed (composite_hash={})".format(
            str(result.get("composite_hash_anchor", ""))
        ),
    }


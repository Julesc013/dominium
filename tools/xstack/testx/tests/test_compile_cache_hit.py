"""FAST test: PROC-8 compile cache is hit on deterministic rebuild."""

from __future__ import annotations

import sys


TEST_ID = "test_compile_cache_hit"
TEST_TAGS = ["fast", "proc", "proc8", "software", "cache"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc8_testlib

    state = proc8_testlib.cloned_state()
    inputs = proc8_testlib.default_inputs()

    first = proc8_testlib.execute_pipeline(repo_root=repo_root, state=state, inputs=inputs)
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "initial pipeline execution failed"}
    if bool(first.get("compile_cache_hit", False)):
        return {"status": "fail", "message": "initial compile unexpectedly reported cache hit"}

    second = proc8_testlib.execute_pipeline(repo_root=repo_root, state=state, inputs=inputs)
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second pipeline execution failed"}
    if not bool(second.get("compile_cache_hit", False)):
        return {"status": "fail", "message": "second compile did not hit deterministic cache"}
    if str(first.get("build_cache_key", "")).strip() != str(second.get("build_cache_key", "")).strip():
        return {"status": "fail", "message": "build cache key changed across identical rebuilds"}

    cache_rows = list(state.get("software_build_cache_rows") or [])
    if not cache_rows:
        return {"status": "fail", "message": "software build cache rows missing after rebuild"}
    return {"status": "pass", "message": "compile cache hit verified"}

from __future__ import annotations

from tools.xstack.testx.tests.xi5x1_testlib import committed_postmove_report

TEST_ID = "test_no_dangerous_shadow_roots_after_xi5x1"
TEST_TAGS = ["fast", "xi5x1", "restructure"]


def run(repo_root: str):
    payload = committed_postmove_report(repo_root)
    if payload.get("dangerous_shadow_root_paths_remaining") != []:
        return {"status": "fail", "message": "dangerous shadow roots remain after Xi-5x1"}
    if payload.get("unexpected_runtime_critical_src_paths") != []:
        return {"status": "fail", "message": "unexpected runtime-critical src paths remain after Xi-5x1"}
    return {"status": "pass", "message": "Xi-5x1 removed dangerous shadow roots"}

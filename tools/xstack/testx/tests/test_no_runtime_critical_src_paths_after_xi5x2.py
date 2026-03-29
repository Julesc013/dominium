from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_postmove_report

TEST_ID = "test_no_runtime_critical_src_paths_after_xi5x2"
TEST_TAGS = ["fast", "xi5x2", "restructure"]


def run(repo_root: str):
    payload = committed_postmove_report(repo_root)
    runtime_paths = list(payload.get("unexpected_runtime_critical_src_paths") or [])
    dangerous_paths = list(payload.get("dangerous_shadow_root_paths_remaining") or [])
    root_counts = dict(payload.get("remaining_root_file_counts") or {})
    offenders = [name for name in ("src", "app/src") if int(root_counts.get(name, 0) or 0) != 0]
    if runtime_paths or dangerous_paths or offenders:
        return {
            "status": "fail",
            "message": "Xi-5x2 still has runtime-critical src residue: {}".format(", ".join(runtime_paths or dangerous_paths or offenders)),
        }
    return {"status": "pass", "message": "Xi-5x2 left no runtime-critical src paths or dangerous shadow roots"}

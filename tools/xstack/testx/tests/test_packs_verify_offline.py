"""FAST test: `packs verify` runs offline through the unified command registry."""

from __future__ import annotations


TEST_ID = "test_packs_verify_offline"
TEST_TAGS = ["fast", "appshell", "packs", "offline"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell1_testlib import run_wrapper_json

    report, payload = run_wrapper_json(repo_root, "setup", ["packs", "verify", "--root", "."])
    if int(report.get("returncode", 0)) not in {0, 20}:
        return {"status": "fail", "message": "packs verify returned unexpected exit code {}".format(int(report.get("returncode", 0)))}
    if str(payload.get("result", "")).strip() not in {"complete", "refused"}:
        return {"status": "fail", "message": "packs verify returned unexpected result"}
    if "dist_root" not in payload:
        return {"status": "fail", "message": "packs verify did not emit offline root metadata"}
    return {"status": "pass", "message": "packs verify runs offline through the registered command surface"}

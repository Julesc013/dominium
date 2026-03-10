"""FAST test: AppShell verify command executes offline and emits structured output."""

from __future__ import annotations


TEST_ID = "test_pack_verify_command_runs_offline"
TEST_TAGS = ["fast", "appshell", "packs", "offline"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell0_testlib import parse_json_output, run_wrapper

    report = run_wrapper(repo_root, "setup", ["verify", "--root", "."])
    if int(report.get("returncode", 0)) not in {0, 20}:
        return {
            "status": "fail",
            "message": "offline verify returned unexpected exit code {}".format(int(report.get("returncode", 0))),
        }
    if "Traceback" in str(report.get("stderr", "")) or "Traceback" in str(report.get("stdout", "")):
        return {"status": "fail", "message": "offline verify raised a traceback"}
    payload = parse_json_output(report)
    if str(payload.get("result", "")).strip() not in {"complete", "refused"}:
        return {"status": "fail", "message": "offline verify returned unexpected result"}
    if "dist_root" not in payload:
        return {"status": "fail", "message": "offline verify did not emit deterministic root metadata"}
    return {"status": "pass", "message": "AppShell verify command runs offline with structured output"}


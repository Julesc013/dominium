"""FAST test: every product wrapper exposes the AppShell descriptor command."""

from __future__ import annotations


TEST_ID = "test_descriptor_command_available"
TEST_TAGS = ["fast", "appshell", "descriptor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell0_testlib import parse_json_output, run_wrapper, wrapper_map

    failures = []
    for bin_name, product_id in sorted(wrapper_map(repo_root).items()):
        report = run_wrapper(repo_root, bin_name, ["descriptor"])
        if int(report.get("returncode", 0)) != 0:
            failures.append("{} exit {}".format(bin_name, int(report.get("returncode", 0))))
            continue
        payload = parse_json_output(report)
        if str(payload.get("product_id", "")).strip() != str(product_id):
            failures.append("{} returned product_id {}".format(bin_name, str(payload.get("product_id", "")).strip()))
            continue
        if str(payload.get("result", "")).strip() != "complete":
            failures.append("{} returned result {}".format(bin_name, str(payload.get("result", "")).strip()))
    if failures:
        return {"status": "fail", "message": "; ".join(failures)}
    return {"status": "pass", "message": "descriptor command is available for every product wrapper"}


"""FAST test: every product wrapper boots AppShell help.""" 

from __future__ import annotations


TEST_ID = "test_each_product_boots_help"
TEST_TAGS = ["fast", "appshell", "bootstrap"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell0_testlib import run_wrapper, wrapper_map

    failures = []
    for bin_name, product_id in sorted(wrapper_map(repo_root).items()):
        report = run_wrapper(repo_root, bin_name, ["--help"])
        if int(report.get("returncode", 0)) != 0:
            failures.append("{} exit {}".format(bin_name, int(report.get("returncode", 0))))
            continue
        stdout = str(report.get("stdout", ""))
        if "Dominium AppShell" not in stdout or "product_id: {}".format(product_id) not in stdout:
            failures.append("{} missing AppShell help markers".format(bin_name))
    if failures:
        return {"status": "fail", "message": "; ".join(failures)}
    return {"status": "pass", "message": "every product wrapper boots AppShell help"}


"""FAST test: AppShell help output is deterministic and registry-backed."""

from __future__ import annotations


TEST_ID = "test_help_output_deterministic"
TEST_TAGS = ["fast", "appshell", "help"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell0_testlib import run_wrapper

    first = run_wrapper(repo_root, "dominium_client", ["help"])
    second = run_wrapper(repo_root, "dominium_client", ["help"])
    via_flag = run_wrapper(repo_root, "dominium_client", ["--help"])

    if int(first.get("returncode", 0)) != 0 or int(second.get("returncode", 0)) != 0 or int(via_flag.get("returncode", 0)) != 0:
        return {"status": "fail", "message": "help surface returned non-zero exit code"}
    first_text = str(first.get("stdout", "")).replace("\r\n", "\n")
    second_text = str(second.get("stdout", "")).replace("\r\n", "\n")
    flag_text = str(via_flag.get("stdout", "")).replace("\r\n", "\n")
    if first_text != second_text:
        return {"status": "fail", "message": "help command drifted across repeated runs"}
    if first_text != flag_text:
        return {"status": "fail", "message": "help command and --help output diverged"}
    for token in ("compat-status", "packs verify", "profiles show", "console enter"):
        if token not in first_text:
            return {"status": "fail", "message": "help output missing {}".format(token)}
    return {"status": "pass", "message": "help output remains deterministic and registry-backed"}

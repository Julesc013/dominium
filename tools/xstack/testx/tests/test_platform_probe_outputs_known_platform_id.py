"""FAST test: platform probe canonicalizes explicit platform ids deterministically."""

from __future__ import annotations


TEST_ID = "test_platform_probe_outputs_known_platform_id"
TEST_TAGS = ["fast", "platform", "probe"]


def run(repo_root: str):
    from tools.xstack.testx.tests.platform_formalize_testlib import probe

    cases = {
        "windows": "platform.winnt",
        "win9x": "platform.win9x",
        "macos": "platform.macos_cocoa",
        "macos_classic": "platform.macos_classic",
        "linux": "platform.linux_gtk",
        "posix": "platform.posix_min",
        "sdl": "platform.sdl_stub",
    }
    for token, expected in sorted(cases.items()):
        payload = probe(repo_root, product_id="client", platform_id=token, tty=False, gui=False, tui=False)
        observed = str(payload.get("platform_id", "")).strip()
        if observed != expected:
            return {"status": "fail", "message": "platform probe canonicalized '{}' to '{}' instead of '{}'".format(token, observed, expected)}
    return {"status": "pass", "message": "platform probe emits known canonical platform ids"}

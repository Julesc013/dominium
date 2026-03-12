"""FAST test: platform capability registry is present and structurally valid."""

from __future__ import annotations


TEST_ID = "test_platform_registry_valid"
TEST_TAGS = ["fast", "platform", "registry"]


def run(repo_root: str):
    from tools.xstack.testx.tests.platform_formalize_testlib import load_registry

    payload = load_registry(repo_root)
    rows = list(dict(payload.get("record") or {}).get("entries") or [])
    ids = [str(dict(row).get("platform_id", "")).strip() for row in rows]
    expected = [
        "platform.win9x",
        "platform.winnt",
        "platform.macos_classic",
        "platform.macos_cocoa",
        "platform.linux_gtk",
        "platform.posix_min",
        "platform.sdl_stub",
    ]
    if ids != expected:
        return {"status": "fail", "message": "platform registry ids drifted from governed order"}
    required_keys = (
        "cap.ui.os_native",
        "cap.ui.rendered",
        "cap.ui.tui",
        "cap.ui.cli",
        "cap.ipc.local_socket",
        "cap.ipc.named_pipe",
        "cap.fs.symlink",
        "cap.renderer.null",
        "cap.renderer.software",
        "cap.renderer.opengl",
        "cap.renderer.directx",
        "cap.renderer.vulkan",
        "cap.renderer.metal",
    )
    for row in rows:
        row_map = dict(row or {})
        for key in required_keys:
            if key in row_map:
                continue
            return {"status": "fail", "message": "platform registry row '{}' is missing '{}'".format(row_map.get("platform_id", ""), key)}
    return {"status": "pass", "message": "platform capability registry rows are complete and ordered"}

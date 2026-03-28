"""FAST test: deterministic log events hash identically across repeated runs."""

from __future__ import annotations


TEST_ID = "test_cross_platform_log_hash_match"
TEST_TAGS = ["fast", "appshell", "logging", "cross_platform"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell2_testlib import canonical_hash, ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from appshell.logging import create_log_engine

    def emit_sequence() -> list[dict]:
        engine = create_log_engine(product_id="server", build_id="build.test", console_enabled=False)
        return [
            engine.emit(category="server", severity="info", message_key="server.listener.bound"),
            engine.emit(category="compat", severity="info", message_key="compat.negotiation.result", params={"compatibility_mode_id": "compat.full"}),
            engine.emit(category="server", severity="info", message_key="server.tick.advanced", tick=4, params={"tick_hash": "abc"}),
        ]

    first = emit_sequence()
    second = emit_sequence()
    if canonical_hash(first) != canonical_hash(second):
        return {"status": "fail", "message": "log event hash drifted across repeated deterministic runs"}
    return {"status": "pass", "message": "log event hashes remain stable across repeated runs"}

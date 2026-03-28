"""FAST test: structured log serialization uses sorted keys.""" 

from __future__ import annotations

import json
import os
import tempfile


TEST_ID = "test_log_serialization_sorted_keys"
TEST_TAGS = ["fast", "appshell", "logging"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell2_testlib import ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from appshell.logging import append_jsonl, build_log_event

    event = build_log_event(
        product_id="client",
        build_id="build.test",
        event_index=7,
        category="appshell",
        severity="info",
        message_key="appshell.bootstrap.start",
        params={"zeta": "z", "alpha": "a"},
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "log.jsonl")
        append_jsonl(path, event)
        written = open(path, "r", encoding="utf-8").read().strip()
    expected = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if written != expected:
        return {"status": "fail", "message": "log serialization drifted from sorted-key canonical form"}
    return {"status": "pass", "message": "log serialization remains sorted and deterministic"}


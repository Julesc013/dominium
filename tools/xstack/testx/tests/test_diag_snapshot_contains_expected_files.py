"""FAST test: diag snapshot writes the expected offline bundle files."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_diag_snapshot_contains_expected_files"
TEST_TAGS = ["fast", "appshell", "diag"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell1_testlib import run_wrapper_json

    with tempfile.TemporaryDirectory() as temp_dir:
        report, payload = run_wrapper_json(repo_root, "dominium_client", ["diag", "snapshot", "--out-dir", temp_dir])
        if int(report.get("returncode", 0)) != 0:
            return {"status": "fail", "message": "diag snapshot returned non-zero"}
        if str(payload.get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "diag snapshot did not complete"}
        expected = {
            "diag_manifest.json",
            "endpoint_descriptor.json",
            "session_spec.json",
            "pack_lock.json",
            "log_events.jsonl",
            "proof_anchors.json",
            "replay_instructions.txt",
        }
        present = set(os.listdir(temp_dir))
        missing = sorted(expected - present)
        if missing:
            return {"status": "fail", "message": "diag snapshot bundle is missing {}".format(", ".join(missing))}
    return {"status": "pass", "message": "diag snapshot bundle contains the expected files"}


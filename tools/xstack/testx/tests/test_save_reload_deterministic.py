"""FAST test: baseline universe save-reload is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_save_reload_deterministic"
TEST_TAGS = ["fast", "omega", "baseline_universe", "save"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.baseline_universe_common import verify_baseline_universe

    report = verify_baseline_universe(repo_root)
    if not bool(report.get("save_reload_matches")):
        return {"status": "fail", "message": "baseline universe save-reload drifted from frozen T2 anchor"}
    expected_record = dict(report.get("expected_record") or {})
    anchors = list(expected_record.get("proof_anchors") or [])
    expected_hash = str(dict(anchors[2] if len(anchors) > 2 and isinstance(anchors[2], dict) else {}).get("state_deterministic_fingerprint", "")).strip()
    observed_hash = str(report.get("loaded_save_hash", "")).strip()
    if expected_hash and observed_hash != expected_hash:
        return {"status": "fail", "message": "baseline universe loaded save hash mismatch"}
    return {"status": "pass", "message": "baseline universe save-reload is deterministic"}

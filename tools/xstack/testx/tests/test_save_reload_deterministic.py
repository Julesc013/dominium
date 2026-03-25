"""FAST test: baseline universe and gameplay save-reload are deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_save_reload_deterministic"
TEST_TAGS = ["fast", "omega", "baseline_universe", "gameplay", "save"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.baseline_universe_common import verify_baseline_universe
    from tools.mvp.gameplay_loop_common import verify_gameplay_loop

    report = verify_baseline_universe(repo_root)
    if not bool(report.get("save_reload_matches")):
        return {"status": "fail", "message": "baseline universe save-reload drifted from frozen T2 anchor"}
    expected_record = dict(report.get("expected_record") or {})
    anchors = list(expected_record.get("proof_anchors") or [])
    expected_hash = str(dict(anchors[2] if len(anchors) > 2 and isinstance(anchors[2], dict) else {}).get("state_deterministic_fingerprint", "")).strip()
    observed_hash = str(report.get("loaded_save_hash", "")).strip()
    if expected_hash and observed_hash != expected_hash:
        return {"status": "fail", "message": "baseline universe loaded save hash mismatch"}
    gameplay_report = verify_gameplay_loop(repo_root)
    if not bool(gameplay_report.get("save_reload_matches")):
        return {"status": "fail", "message": "MVP gameplay save-reload drifted from frozen post-edit anchor"}
    gameplay_save_reload = dict(dict(gameplay_report.get("observed_record") or {}).get("save_reload") or {})
    fresh_save_hash = str(gameplay_save_reload.get("fresh_save_hash", "")).strip()
    loaded_save_hash = str(gameplay_save_reload.get("loaded_save_hash", "")).strip()
    if fresh_save_hash and loaded_save_hash != fresh_save_hash:
        return {"status": "fail", "message": "MVP gameplay loaded save hash mismatch"}
    return {"status": "pass", "message": "baseline universe and gameplay save-reload are deterministic"}

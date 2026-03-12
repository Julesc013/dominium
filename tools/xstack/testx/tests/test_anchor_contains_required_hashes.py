"""FAST test: epoch anchors contain the required canonical hashes."""

from __future__ import annotations

import json
import os


TEST_ID = "test_anchor_contains_required_hashes"
TEST_TAGS = ["fast", "time", "anchor", "hash"]


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def run(repo_root: str):
    from tools.xstack.testx.tests.time_anchor_testlib import load_verify_report

    report, error = load_verify_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    checks = dict(report.get("checks") or {})
    if not bool(checks.get("interval_anchor_has_required_hashes", False)):
        return {"status": "fail", "message": "verify report did not confirm required anchor hashes"}
    anchor_path = str(dict(report.get("interval_anchor") or {}).get("anchor_path", "")).strip()
    if not anchor_path:
        return {"status": "fail", "message": "interval anchor path missing from verify report"}
    payload = _read_json(os.path.join(repo_root, anchor_path.replace("/", os.sep)))
    for field_name in ("truth_hash", "contract_bundle_hash", "pack_lock_hash", "overlay_manifest_hash"):
        token = str(payload.get(field_name, "")).strip().lower()
        if len(token) != 64:
            return {"status": "fail", "message": "anchor field '{}' is not a 64-hex hash".format(field_name)}
    return {"status": "pass", "message": "epoch anchors include the required canonical hashes"}

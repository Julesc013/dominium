"""FAST test: gc.safe moves unreachable artifacts into quarantine."""

from __future__ import annotations

import os


TEST_ID = "test_gc_safe_moves_to_quarantine"
TEST_TAGS = ["fast", "lib", "store", "gc", "quarantine"]


def run(repo_root: str):
    from tools.xstack.testx.tests.store_gc_testlib import gc_safe_result

    fixture, result = gc_safe_result(repo_root)
    report = dict(result.get("gc_report") or {})
    quarantined = list(report.get("quarantined_hashes") or [])
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "gc.safe did not complete"}
    if not quarantined:
        return {"status": "fail", "message": "gc.safe did not quarantine the unreachable fixture artifact"}
    orphan_hash = str(fixture.get("orphan_pack_hash", "")).strip()
    target = os.path.join(str(fixture.get("store_root", "")).strip(), "store", "quarantine", "packs", orphan_hash)
    if not os.path.isdir(target):
        return {"status": "fail", "message": "gc.safe did not move the unreachable pack into the quarantine directory"}
    if list(report.get("deleted_hashes") or []):
        return {"status": "fail", "message": "gc.safe deleted artifacts instead of quarantining them"}
    return {"status": "pass", "message": "gc.safe quarantines unreachable artifacts deterministically"}

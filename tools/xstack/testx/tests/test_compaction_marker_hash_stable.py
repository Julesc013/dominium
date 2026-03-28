"""STRICT test: compaction marker hash chain is stable across equivalent runs."""

from __future__ import annotations

import re
import sys

from tools.xstack.testx.tests.provenance_compaction_testlib import (
    build_compaction_fixture_state,
    read_provenance_classification_rows,
)


TEST_ID = "test_compaction_marker_hash_stable"
TEST_TAGS = ["strict", "provenance", "compaction", "hash", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from meta.provenance import compact_provenance_window

    classifications = read_provenance_classification_rows(repo_root)
    state = build_compaction_fixture_state("marker_hash")
    return compact_provenance_window(
        state_payload=state,
        classification_rows=classifications,
        shard_id="shard.marker_hash",
        start_tick=5,
        end_tick=8,
    )


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "first compaction run failed"}
    if str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "second compaction run failed"}

    marker_hash_a = str(first.get("compaction_marker_hash_chain", "")).strip().lower()
    marker_hash_b = str(second.get("compaction_marker_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(marker_hash_a)) or (not _HASH64.fullmatch(marker_hash_b)):
        return {"status": "fail", "message": "compaction marker hash chain missing or invalid"}
    if marker_hash_a != marker_hash_b:
        return {"status": "fail", "message": "compaction marker hash chain drifted across equivalent runs"}

    marker_a = dict(first.get("compaction_marker") or {})
    marker_b = dict(second.get("compaction_marker") or {})
    if str(marker_a.get("deterministic_fingerprint", "")).strip() != str(marker_b.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "compaction marker deterministic fingerprint drifted"}
    if str(first.get("pre_compaction_hash", "")).strip() != str(second.get("pre_compaction_hash", "")).strip():
        return {"status": "fail", "message": "pre-compaction anchor drifted across equivalent runs"}
    if str(first.get("post_compaction_hash", "")).strip() != str(second.get("post_compaction_hash", "")).strip():
        return {"status": "fail", "message": "post-compaction anchor drifted across equivalent runs"}
    return {"status": "pass", "message": "compaction marker hash chain and anchors are stable"}

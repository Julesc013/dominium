"""STRICT test: independent shard compaction is deterministic across runs."""

from __future__ import annotations

import sys

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.testx.tests.provenance_compaction_testlib import (
    build_compaction_fixture_state,
    read_provenance_classification_rows,
)


TEST_ID = "test_cross_shard_compaction_deterministic"
TEST_TAGS = ["strict", "provenance", "compaction", "shards", "determinism"]


def _run_pair(repo_root: str, shard_ids):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.provenance import compact_provenance_window

    classifications = read_provenance_classification_rows(repo_root)
    rows = {}
    for shard_id in list(shard_ids):
        token = str(shard_id).replace("shard.", "")
        state = build_compaction_fixture_state(token)
        compacted = compact_provenance_window(
            state_payload=state,
            classification_rows=classifications,
            shard_id=str(shard_id),
            start_tick=5,
            end_tick=8,
        )
        rows[str(shard_id)] = {
            "result": str(compacted.get("result", "")),
            "marker_hash_chain": str(compacted.get("compaction_marker_hash_chain", "")),
            "post_hash": str(compacted.get("post_replay_hash", "")),
            "state_projection_hash": canonical_sha256(dict(compacted.get("state") or {})),
        }
    return dict((key, rows[key]) for key in sorted(rows.keys()))


def run(repo_root: str):
    first = _run_pair(repo_root, ["shard.alpha", "shard.beta"])
    second = _run_pair(repo_root, ["shard.beta", "shard.alpha"])
    if first != second:
        return {"status": "fail", "message": "cross-shard compaction results drifted across deterministic runs"}
    if any(str(row.get("result", "")) != "complete" for row in first.values()):
        return {"status": "fail", "message": "cross-shard compaction run did not complete"}
    return {"status": "pass", "message": "cross-shard compaction remains deterministic and independent"}

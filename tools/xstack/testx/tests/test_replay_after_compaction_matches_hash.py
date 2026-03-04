"""STRICT test: replay from compaction anchor matches deterministic replay hash."""

from __future__ import annotations

import re
import sys

from tools.xstack.testx.tests.provenance_compaction_testlib import (
    build_compaction_fixture_state,
    read_provenance_classification_rows,
)


TEST_ID = "test_replay_after_compaction_matches_hash"
TEST_TAGS = ["strict", "provenance", "compaction", "replay", "hash"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.provenance import compact_provenance_window, verify_replay_from_compaction_anchor

    classifications = read_provenance_classification_rows(repo_root)
    state = build_compaction_fixture_state("replay")
    compacted = compact_provenance_window(
        state_payload=state,
        classification_rows=classifications,
        shard_id="shard.replay",
        start_tick=5,
        end_tick=8,
    )
    if str(compacted.get("result", "")) != "complete":
        return {"status": "fail", "message": "compaction failed in replay fixture"}
    if str(compacted.get("pre_replay_hash", "")).strip() != str(compacted.get("post_replay_hash", "")).strip():
        return {"status": "fail", "message": "replay hash changed during derived-only compaction"}
    marker = dict(compacted.get("compaction_marker") or {})
    marker_id = str(marker.get("marker_id", "")).strip()
    if not marker_id:
        return {"status": "fail", "message": "compaction marker id missing"}

    verify = verify_replay_from_compaction_anchor(
        state_payload=dict(compacted.get("state") or {}),
        marker_id=marker_id,
    )
    if str(verify.get("result", "")) != "complete":
        return {"status": "fail", "message": "replay verification from compaction marker failed"}
    if str(verify.get("replay_hash", "")).strip() != str(compacted.get("post_replay_hash", "")).strip():
        return {"status": "fail", "message": "replay hash from marker does not match post-compaction hash"}

    marker_chain = str(verify.get("compaction_marker_hash_chain", "")).strip().lower()
    if not _HASH64.fullmatch(marker_chain):
        return {"status": "fail", "message": "compaction marker hash chain missing or invalid"}
    return {"status": "pass", "message": "replay from compaction marker matches deterministic hash"}

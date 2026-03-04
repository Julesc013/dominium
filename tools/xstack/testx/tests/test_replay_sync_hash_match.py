"""STRICT test: TEMP-2 sync replay hash chain remains deterministic."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_replay_sync_hash_match"
TEST_TAGS = ["strict", "time", "temp2", "sync", "hash"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.time.tool_verify_sync_consistency import verify_sync_consistency

    report = verify_sync_consistency(
        sync_policy_id="sync.adjust_on_receipt",
        temporal_domain_id="time.civil",
        target_id="session.default",
        local_domain_time=100,
        remote_domain_time=130,
        max_adjust_per_tick=5,
        max_skew_allowed=40,
    )
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "sync consistency verification failed: {}".format(report)}
    first_hash = str(((report.get("first") or {}).get("time_adjust_event_hash_chain", ""))).strip().lower()
    second_hash = str(((report.get("second") or {}).get("time_adjust_event_hash_chain", ""))).strip().lower()
    if (not _HASH64.fullmatch(first_hash)) or (not _HASH64.fullmatch(second_hash)):
        return {"status": "fail", "message": "sync replay hash chain missing/invalid"}
    if first_hash != second_hash:
        return {"status": "fail", "message": "sync replay hash chain drifted across equivalent runs"}
    return {"status": "pass", "message": "sync replay hash chain stable"}

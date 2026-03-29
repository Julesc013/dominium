from __future__ import annotations

from tools.xstack.testx.tests.xi5x1_testlib import committed_execution_log

TEST_ID = "test_xi5x1_safe_batches_consumed"
TEST_TAGS = ["fast", "xi5x1", "restructure"]


def run(repo_root: str):
    payload = committed_execution_log(repo_root)
    executed = list(payload.get("executed_items") or [])
    batch_ids = {item.get("batch_id") for item in executed}
    missing = [batch_id for batch_id in ("BATCH_SAFE_1", "BATCH_SAFE_2", "BATCH_MERGE_1") if batch_id not in batch_ids]
    if missing:
        return {"status": "fail", "message": "Xi-5x1 missing executed batches: {}".format(", ".join(missing))}
    return {"status": "pass", "message": "Xi-5x1 consumed both safe batches and the merge batch"}

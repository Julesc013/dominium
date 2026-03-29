from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_manual_review_queue, committed_platform_adapter_review

TEST_ID = "test_xi5x2_platform_review_artifact_present"
TEST_TAGS = ["fast", "xi5x2", "platform"]


def run(repo_root: str):
    platform_review = committed_platform_adapter_review(repo_root)
    manual_queue = committed_manual_review_queue(repo_root)
    if int(platform_review.get("review_row_count", 0) or 0) == 0:
        return {"status": "fail", "message": "Xi-5x2 platform adapter review is empty"}
    if int(platform_review.get("remaining_manual_review_required_count", 0) or 0) != 0:
        return {"status": "fail", "message": "Xi-5x2 platform adapter review still requires manual follow-up"}
    if int(manual_queue.get("item_count", 0) or 0) != 0:
        return {"status": "fail", "message": "Xi-5x2 manual review queue is not empty"}
    return {"status": "pass", "message": "Xi-5x2 platform review artifact is present and closed"}

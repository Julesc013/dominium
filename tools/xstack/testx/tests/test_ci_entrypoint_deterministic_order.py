from __future__ import annotations

TEST_ID = "test_ci_entrypoint_deterministic_order"
TEST_TAGS = ["fast", "xi7", "ci", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi7_testlib import EXPECTED_STAGE_ORDER, PROFILE_IDS, committed_profile

    for profile_id in PROFILE_IDS:
        payload = committed_profile(repo_root, profile_id)
        if list(payload.get("execution_order") or []) != EXPECTED_STAGE_ORDER:
            return {"status": "fail", "message": "{} execution order drifted".format(profile_id)}
    return {"status": "pass", "message": "Xi-7 CI stage order is deterministic across FAST/STRICT/FULL"}

from __future__ import annotations

TEST_ID = "test_ci_profiles_exist"
TEST_TAGS = ["fast", "xi7", "ci", "profiles"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi7_testlib import PROFILE_IDS, committed_profile, recompute_fingerprint

    for profile_id in PROFILE_IDS:
        payload = committed_profile(repo_root, profile_id)
        if str(payload.get("profile_id", "")).strip() != profile_id:
            return {"status": "fail", "message": "{} profile_id drifted".format(profile_id)}
        if not str(payload.get("deterministic_fingerprint", "")).strip():
            return {"status": "fail", "message": "{} deterministic_fingerprint missing".format(profile_id)}
        if str(payload.get("deterministic_fingerprint", "")).strip() != recompute_fingerprint(payload):
            return {"status": "fail", "message": "{} deterministic_fingerprint drifted".format(profile_id)}
    return {"status": "pass", "message": "Xi-7 FAST/STRICT/FULL profiles exist and fingerprints are stable"}

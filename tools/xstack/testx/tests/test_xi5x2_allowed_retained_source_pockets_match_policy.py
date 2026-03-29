from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_postmove_report, committed_source_pocket_policy

TEST_ID = "test_xi5x2_allowed_retained_source_pockets_match_policy"
TEST_TAGS = ["fast", "xi5x2", "policy"]


def run(repo_root: str):
    postmove = committed_postmove_report(repo_root)
    policy = committed_source_pocket_policy(repo_root)
    policy_map = {str(item.get("path") or ""): dict(item or {}) for item in list(policy.get("policy_rows") or [])}
    missing = []
    invalid = []
    for row in list(postmove.get("remaining_rows") or []):
        entry = dict(row or {})
        if not bool(entry.get("allowed_to_remain")):
            invalid.append(str(entry.get("source_path") or ""))
            continue
        policy_entry = policy_map.get(str(entry.get("source_path") or ""))
        if not policy_entry or not bool(policy_entry.get("allowed_to_remain")):
            missing.append(str(entry.get("source_path") or ""))
    if missing or invalid:
        offenders = ", ".join(sorted(set(missing + invalid)))
        return {"status": "fail", "message": "Xi-5x2 retained pockets do not match policy allowlist: {}".format(offenders)}
    return {"status": "pass", "message": "Xi-5x2 retained source pockets match SOURCE_POCKET_POLICY_v1"}

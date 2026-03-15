from tools.xstack.testx.tests.governance_testlib import current_governance_hash, load_release_index_payload


def run(repo_root: str) -> dict:
    release_index = load_release_index_payload(repo_root)
    assert release_index["governance_profile_hash"] == current_governance_hash(repo_root)
    return {
        "status": "pass",
        "message": "release index records the active governance profile hash",
    }

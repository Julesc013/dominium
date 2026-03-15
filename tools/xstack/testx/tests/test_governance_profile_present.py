from tools.xstack.testx.tests.governance_testlib import build_report, load_profile


def run(repo_root: str) -> dict:
    report = build_report(repo_root)
    profile = load_profile(repo_root)
    assert report["result"] == "complete"
    assert profile["governance_mode_id"]
    assert report["governance_profile_hash"]
    return {
        "status": "pass",
        "message": "governance profile is present and linked into release governance outputs",
    }

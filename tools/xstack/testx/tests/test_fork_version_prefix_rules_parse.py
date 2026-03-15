from tools.xstack.testx.tests.governance_testlib import parse_tag


def run(repo_root: str) -> dict:
    del repo_root
    official = parse_tag("v0.0.0-mock")
    forked = parse_tag("fork.example.v0.0.0-mock")
    invalid = parse_tag("example.v0.0.0-mock")
    assert official["result"] == "complete"
    assert official["tag_kind"] == "official"
    assert forked["result"] == "complete"
    assert forked["tag_kind"] == "fork"
    assert forked["fork_namespace"] == "example"
    assert invalid["result"] == "refused"
    assert invalid["refusal_code"] == "refusal.governance.fork_prefix_required"
    return {
        "status": "pass",
        "message": "fork version prefix rules parse deterministically",
    }

from tools.xstack.testx.tests.performance_envelope_testlib import build_report


def run(repo_root: str) -> dict:
    first = build_report(repo_root)
    second = build_report(repo_root)
    first_guards = dict(first.get("determinism_guards") or {})
    second_guards = dict(second.get("determinism_guards") or {})
    assert first["result"] == "complete"
    assert second["result"] == "complete"
    assert first_guards["release_manifest_hash_unchanged"] is True
    assert second_guards["release_manifest_hash_unchanged"] is True
    assert first_guards["release_manifest_hash_before"] == first_guards["release_manifest_hash_after"]
    assert second_guards["release_manifest_hash_before"] == second_guards["release_manifest_hash_after"]
    assert first["deterministic_fingerprint"] == second["deterministic_fingerprint"]
    return {
        "status": "pass",
        "message": "performance measurement preserves canonical release manifest hashing and stable envelope identity",
    }

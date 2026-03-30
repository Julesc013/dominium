from __future__ import annotations

TEST_ID = "test_gate_definitions_valid"
TEST_TAGS = ["fast", "xi7", "ci", "schema"]


def run(repo_root: str):
    from tools.xstack.ci.ci_common import validate_gate_definitions
    from tools.xstack.testx.tests.xi7_testlib import committed_gate_definitions, recompute_fingerprint

    payload = committed_gate_definitions(repo_root)
    errors = validate_gate_definitions(payload)
    if errors:
        return {"status": "fail", "message": "; ".join(errors)}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "gate definitions missing deterministic_fingerprint"}
    if str(payload.get("deterministic_fingerprint", "")).strip() != recompute_fingerprint(payload):
        return {"status": "fail", "message": "gate definitions deterministic_fingerprint drifted"}
    return {"status": "pass", "message": "Xi-7 gate definitions expose the required RepoX/AuditX/TestX/Omega surface"}

"""FAST test: load must refuse when SessionSpec contract hash mismatches the pinned universe contract bundle."""

from __future__ import annotations

import sys


TEST_ID = "test_load_refuses_mismatch"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "load"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.testx.tests.compat_sem1_testlib import create_session, read_json, write_json

    fixture, created, spec_abs, _save_dir = create_session(repo_root, "load_mismatch")
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session creation failed before contract mismatch load test"}

    spec_payload = read_json(spec_abs)
    spec_payload["contract_bundle_hash"] = "0" * 64
    write_json(spec_abs, spec_payload)
    result = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "boot did not refuse contract bundle hash mismatch"}
    reason = str(dict(result.get("refusal") or {}).get("reason_code", ""))
    if reason != "refusal.contract.mismatch":
        return {"status": "fail", "message": "expected refusal.contract.mismatch, got {}".format(reason or "<empty>")}
    return {"status": "pass", "message": "load refuses deterministically on contract bundle hash mismatch"}

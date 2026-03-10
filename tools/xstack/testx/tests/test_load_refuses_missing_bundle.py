"""FAST test: load must refuse when the universe contract bundle sidecar is missing."""

from __future__ import annotations

import os
import sys


TEST_ID = "test_load_refuses_missing_bundle"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "load"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.testx.tests.compat_sem1_testlib import create_session

    fixture, created, spec_abs, save_dir = create_session(repo_root, "load_missing")
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session creation failed before missing-bundle load test"}

    bundle_abs = os.path.join(save_dir, "universe_contract_bundle.json")
    if os.path.isfile(bundle_abs):
        os.remove(bundle_abs)
    result = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "boot did not refuse after removing universe contract bundle sidecar"}
    reason = str(dict(result.get("refusal") or {}).get("reason_code", ""))
    if reason != "refusal.contract.missing_bundle":
        return {"status": "fail", "message": "expected refusal.contract.missing_bundle, got {}".format(reason or "<empty>")}
    return {"status": "pass", "message": "load refuses deterministically when universe contract bundle is missing"}

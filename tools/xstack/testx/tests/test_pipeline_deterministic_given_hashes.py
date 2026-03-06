"""FAST test: PROC-8 pipeline outputs are deterministic for identical hashes."""

from __future__ import annotations

import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_pipeline_deterministic_given_hashes"
TEST_TAGS = ["fast", "proc", "proc8", "software", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc8_testlib

    state_a = proc8_testlib.cloned_state()
    state_b = proc8_testlib.cloned_state()
    inputs = proc8_testlib.default_inputs()

    out_a = proc8_testlib.execute_pipeline(repo_root=repo_root, state=state_a, inputs=inputs)
    out_b = proc8_testlib.execute_pipeline(repo_root=repo_root, state=state_b, inputs=inputs)
    if str(out_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first pipeline execution did not complete"}
    if str(out_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second pipeline execution did not complete"}

    fields = (
        "build_cache_key",
        "binary_hash",
        "package_hash",
        "signature_hash",
        "build_artifact_hash_chain",
        "compiled_model_hash_chain",
        "signature_hash_chain",
        "deployment_hash_chain",
    )
    for key in fields:
        if str(out_a.get(key, "")).strip() != str(out_b.get(key, "")).strip():
            return {"status": "fail", "message": "mismatch for {}".format(key)}
    if list(out_a.get("selected_tests") or []) != list(out_b.get("selected_tests") or []):
        return {"status": "fail", "message": "selected_tests mismatch across deterministic runs"}

    fingerprint = canonical_sha256(
        {
            "a": {key: out_a.get(key) for key in fields},
            "b": {key: out_b.get(key) for key in fields},
            "tests_a": list(out_a.get("selected_tests") or []),
            "tests_b": list(out_b.get("selected_tests") or []),
        }
    )
    return {
        "status": "pass",
        "message": "software pipeline outputs are deterministic for identical hashes",
        "deterministic_fingerprint": fingerprint,
    }

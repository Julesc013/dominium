"""FAST test: DIAG-0 capture includes the required deterministic artifacts."""

from __future__ import annotations


TEST_ID = "test_capture_contains_required_artifacts"
TEST_TAGS = ["fast", "diag", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.diag0_testlib import cleanup_temp_dir, capture_bundle, list_bundle_files, make_temp_dir

    temp_dir = make_temp_dir("diag0_artifacts_")
    try:
        capture_bundle(repo_root, out_dir=temp_dir, include_views=True)
        present = set(list_bundle_files(temp_dir))
        expected = {
            "manifest.json",
            "bundle_index.json",
            "descriptors/endpoint_descriptor.01.json",
            "descriptors/endpoint_descriptor.02.json",
            "session/session_spec.json",
            "session/universe_contract_bundle.json",
            "session/session_context.json",
            "packs/pack_lock.json",
            "packs/pack_hashes.json",
            "run/run_manifest.json",
            "proofs/proof_anchors.json",
            "events/canonical_events.json",
            "events/ipc_attach_records.json",
            "events/negotiation_records.json",
            "logs/log_events.jsonl",
            "replay/replay_request.json",
            "views/view_fingerprints.json",
        }
        missing = sorted(expected - present)
        if missing:
            return {"status": "fail", "message": "capture bundle is missing {}".format(", ".join(missing))}
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "repro bundle capture includes the required artifacts"}

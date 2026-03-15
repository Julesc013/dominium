"""FAST test: DIAG bundles contain the observability minimum set."""

from __future__ import annotations

import os


TEST_ID = "test_diag_bundle_contains_minimum_set"
TEST_TAGS = ["fast", "observability", "diag"]


def run(repo_root: str):
    from tools.xstack.testx.tests.diag0_testlib import capture_bundle, cleanup_temp_dir, list_bundle_files, make_temp_dir

    temp_dir = make_temp_dir("diag_obs0_")
    try:
        report = capture_bundle(repo_root, out_dir=temp_dir, include_views=False)
        if str(report.get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "diag bundle capture did not complete"}
        bundle_dir = str(report.get("bundle_dir", "")).replace("/", os.sep)
        files = set(list_bundle_files(bundle_dir))
        expected = {
            "events/canonical_events.json",
            "events/negotiation_records.json",
            "logs/log_events.jsonl",
            "packs/pack_verification_report.json",
            "plans/install_plan.json",
            "plans/update_plan.json",
            "proofs/proof_anchors.json",
        }
        missing = sorted(expected - files)
        if missing:
            return {"status": "fail", "message": "diag bundle is missing {}".format(", ".join(missing))}
        return {"status": "pass", "message": "diag bundles contain the required observability minimum set"}
    finally:
        cleanup_temp_dir(temp_dir)

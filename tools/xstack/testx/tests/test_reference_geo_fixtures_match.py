"""FAST test: GEO-10 bounded GEO reference fixtures match runtime outputs exactly."""

from __future__ import annotations


TEST_ID = "test_reference_geo_fixtures_match"
TEST_TAGS = ["fast", "geo", "reference", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.geo10_testlib import GEO10_REFERENCE_EVALUATOR_IDS, geo10_reference_suite

    report = geo10_reference_suite(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GEO reference suite reported mismatch or violation"}
    if list(report.get("mismatches") or []):
        return {"status": "fail", "message": "GEO reference suite produced mismatches"}
    rows = list(report.get("reference_run_record_rows") or [])
    by_id = {str(dict(row).get("evaluator_id", "")).strip(): dict(row) for row in rows}
    for evaluator_id in GEO10_REFERENCE_EVALUATOR_IDS:
        row = dict(by_id.get(evaluator_id) or {})
        if not row:
            return {"status": "fail", "message": "missing GEO reference evaluator '{}'".format(evaluator_id)}
        if not bool(row.get("match", False)):
            return {"status": "fail", "message": "reference evaluator '{}' did not match".format(evaluator_id)}
        if str(row.get("runtime_output_hash", "")).strip() != str(row.get("reference_output_hash", "")).strip():
            return {"status": "fail", "message": "hash mismatch for reference evaluator '{}'".format(evaluator_id)}
    if not str(report.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "GEO reference suite missing deterministic fingerprint"}
    return {"status": "pass", "message": "GEO bounded reference fixtures match runtime outputs"}

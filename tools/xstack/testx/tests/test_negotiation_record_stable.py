"""FAST test: MVP cross-platform negotiation records stay deterministic across the matrix."""

from __future__ import annotations


TEST_ID = "test_negotiation_record_stable"
TEST_TAGS = ["fast", "mvp", "cross-platform", "negotiation"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mvp_cross_platform_testlib import load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    matrix = dict(report.get("negotiation_matrix") or {})
    if str(matrix.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "MVP cross-platform negotiation matrix is not complete"}
    assertions = dict(matrix.get("assertions") or {})
    for key in ("scenario_order_deterministic", "modes_match_expected", "records_stable", "records_verified", "no_refusals"):
        if bool(assertions.get(key, False)):
            continue
        return {"status": "fail", "message": "MVP cross-platform negotiation assertion '{}' failed".format(key)}
    scenario_results = [dict(item) for item in list(matrix.get("scenario_results") or [])]
    scenario_ids = [str(item.get("scenario_id", "")).strip() for item in scenario_results]
    if scenario_ids != [
        "client_build_a_server_build_a",
        "client_build_a_server_build_b",
        "client_older_minor_server_newer_minor",
    ]:
        return {"status": "fail", "message": "MVP cross-platform negotiation scenario order drifted"}
    pair_kinds = [str(item.get("pair_kind", "")).strip() for item in scenario_results]
    if pair_kinds != ["same_build", "same_version_rebuild", "minor_version_delta"]:
        return {"status": "fail", "message": "MVP cross-platform negotiation pair kinds drifted"}
    for row in scenario_results:
        if str(row.get("compatibility_mode_id", "")).strip() != str(row.get("expected_compatibility_mode_id", "")).strip():
            return {"status": "fail", "message": "MVP cross-platform compatibility mode drifted for {}".format(row.get("scenario_id"))}
        if str(row.get("first_negotiation_record_hash", "")).strip() != str(row.get("second_negotiation_record_hash", "")).strip():
            return {"status": "fail", "message": "MVP cross-platform negotiation record drifted for {}".format(row.get("scenario_id"))}
        if str(row.get("refusal_code", "")).strip():
            return {"status": "fail", "message": "MVP cross-platform negotiation refused unexpectedly for {}".format(row.get("scenario_id"))}
    return {"status": "pass", "message": "MVP cross-platform negotiation records stay deterministic across the matrix"}

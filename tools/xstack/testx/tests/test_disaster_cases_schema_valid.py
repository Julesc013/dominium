"""FAST test: disaster suite case registry structure and fingerprint are valid."""

from __future__ import annotations

import sys


TEST_ID = "test_disaster_cases_schema_valid"
TEST_TAGS = ["fast", "omega", "disaster", "schema"]

EXPECTED_SCENARIO_CATEGORIES = [
    "artifact_corruption",
    "compatibility_mismatches",
    "missing_components",
    "policy_conflicts",
    "trust_failures",
    "update_edge_cases",
]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.disaster_suite_common import (
        DISASTER_CASES_SCHEMA_ID,
        disaster_cases_record_hash,
        load_disaster_suite_cases,
    )

    payload = load_disaster_suite_cases(repo_root)
    record = dict(payload.get("record") or {})
    if str(payload.get("schema_id", "")).strip() != DISASTER_CASES_SCHEMA_ID:
        return {"status": "fail", "message": "disaster suite cases schema_id mismatch"}
    if str(payload.get("schema_version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "disaster suite cases schema_version mismatch"}
    try:
        disaster_suite_version = int(record.get("disaster_suite_version", -1))
    except (TypeError, ValueError):
        disaster_suite_version = -1
    if disaster_suite_version != 0:
        return {"status": "fail", "message": "disaster suite version mismatch"}
    if str(record.get("stability_class", "")).strip() != "stable":
        return {"status": "fail", "message": "disaster suite stability_class mismatch"}
    cases = [dict(item) for item in list(record.get("cases") or []) if isinstance(item, dict)]
    if int(record.get("case_count", 0) or 0) != len(cases):
        return {"status": "fail", "message": "disaster suite case_count does not match cases array length"}
    scenario_categories = sorted({str(item.get("scenario_category", "")).strip() for item in cases if str(item.get("scenario_category", "")).strip()})
    if scenario_categories != EXPECTED_SCENARIO_CATEGORIES:
        return {"status": "fail", "message": "disaster suite scenario category set mismatch"}
    if not all(str(item.get("expected_remediation_key", "")).strip() for item in cases):
        return {"status": "fail", "message": "disaster suite case missing expected_remediation_key"}
    fingerprint = str(record.get("deterministic_fingerprint", "")).strip()
    if fingerprint != disaster_cases_record_hash(record):
        return {"status": "fail", "message": "disaster suite cases deterministic_fingerprint mismatch"}
    return {"status": "pass", "message": "disaster suite cases structure valid"}

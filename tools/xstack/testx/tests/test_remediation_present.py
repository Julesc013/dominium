"""FAST test: disaster suite refused cases always carry remediation hints."""

from __future__ import annotations

import sys


TEST_ID = "test_remediation_present"
TEST_TAGS = ["fast", "omega", "disaster", "remediation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.audit.arch_audit_common import load_json_if_present
    from tools.mvp.disaster_suite_common import DISASTER_CASES_REL, DISASTER_RUN_JSON_REL

    cases_payload = load_json_if_present(repo_root, DISASTER_CASES_REL)
    run_payload = load_json_if_present(repo_root, DISASTER_RUN_JSON_REL)
    if not cases_payload or not run_payload:
        return {"status": "fail", "message": "disaster suite cases or run report missing"}
    expected_cases = [dict(item) for item in list(dict(cases_payload.get("record") or {}).get("cases") or []) if isinstance(item, dict)]
    actual_cases = [dict(item) for item in list(run_payload.get("cases") or []) if isinstance(item, dict)]
    expected_refused = sorted(
        str(item.get("case_id", "")).strip()
        for item in expected_cases
        if str(item.get("expected_result", "")).strip() == "refused"
    )
    missing_expected = [
        str(item.get("case_id", "")).strip()
        for item in expected_cases
        if str(item.get("expected_result", "")).strip() == "refused"
        and not str(item.get("expected_remediation_hint", "")).strip()
    ]
    missing_actual = [
        str(item.get("case_id", "")).strip()
        for item in actual_cases
        if str(item.get("result", "")).strip() == "refused"
        and not str(item.get("remediation_hint", "")).strip()
    ]
    if missing_expected:
        return {"status": "fail", "message": "disaster suite expected remediation hints missing for {}".format(", ".join(missing_expected[:8]))}
    if missing_actual:
        return {"status": "fail", "message": "disaster suite actual remediation hints missing for {}".format(", ".join(missing_actual[:8]))}
    if sorted(set(expected_refused)) != sorted(
        str(item.get("case_id", "")).strip() for item in actual_cases if str(item.get("result", "")).strip() == "refused"
    ):
        return {"status": "fail", "message": "disaster suite refused-case set drifted from expected remediation coverage"}
    return {"status": "pass", "message": "disaster suite refused cases all include remediation hints"}

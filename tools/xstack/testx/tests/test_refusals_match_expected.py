"""FAST test: disaster suite refusals match the frozen baseline expectations."""

from __future__ import annotations

import sys


TEST_ID = "test_refusals_match_expected"
TEST_TAGS = ["fast", "omega", "disaster", "refusal"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.audit.arch_audit_common import load_json_if_present
    from tools.mvp.disaster_suite_common import DISASTER_RUN_JSON_REL

    report = load_json_if_present(repo_root, DISASTER_RUN_JSON_REL)
    if not report:
        return {"status": "fail", "message": "disaster suite run report missing"}
    if str(report.get("result", "")).strip() != "complete":
        mismatch = ", ".join(str(item).strip() for item in list(report.get("mismatched_fields") or [])[:8] if str(item).strip())
        return {"status": "fail", "message": "disaster suite run report is not passing{}".format(": {}".format(mismatch) if mismatch else "")}
    if not bool(report.get("cases_match_expected")):
        return {"status": "fail", "message": "disaster suite cases do not match expected refusals"}
    if list(report.get("silent_success_case_ids") or []):
        return {"status": "fail", "message": "disaster suite recorded silent success cases"}
    return {"status": "pass", "message": "disaster suite refusals match frozen expectations"}

from __future__ import annotations

from tools.xstack.testx.tests.xi8_testlib import (
    AUDITX_DETECTOR_IDS,
    EXPECTED_STAGE_ORDER,
    REPOX_RULE_IDS,
    committed_ci_run_report,
)

TEST_ID = "test_xstack_ci_strict_passes"
TEST_TAGS = ["fast", "xi8", "ci", "smoke"]


def run(repo_root: str):
    report = committed_ci_run_report(repo_root)
    if str(report.get("profile", "")).strip() != "STRICT":
        return {"status": "fail", "message": "ci_run_report.json is not a STRICT run"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "STRICT CI report is not complete"}
    stages = list(report.get("stages") or [])
    stage_order = [str(dict(stage or {}).get("stage_id", "")).strip() for stage in stages]
    if stage_order != EXPECTED_STAGE_ORDER:
        return {"status": "fail", "message": "STRICT CI stage order drifted: {}".format(stage_order)}
    repox_stage = next((dict(stage or {}) for stage in stages if str(dict(stage or {}).get("stage_id", "")).strip() == "repox"), {})
    auditx_stage = next((dict(stage or {}) for stage in stages if str(dict(stage or {}).get("stage_id", "")).strip() == "auditx"), {})
    repox_rules = sorted(str(item) for item in list(repox_stage.get("rule_ids") or []))
    auditx_detectors = sorted(str(item) for item in list(auditx_stage.get("detector_ids") or []))
    if repox_rules != sorted(REPOX_RULE_IDS):
        return {"status": "fail", "message": "STRICT RepoX rule set drifted: {}".format(repox_rules)}
    if auditx_detectors != sorted(AUDITX_DETECTOR_IDS):
        return {"status": "fail", "message": "STRICT AuditX detector set drifted: {}".format(auditx_detectors)}
    return {"status": "pass", "message": "Xi-8 STRICT CI report is complete and includes the frozen RepoX/AuditX guard surface"}

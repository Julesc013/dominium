"""FAST test: MW-4 viewer status stays nonblocking and reflects queued -> present transitions."""

from __future__ import annotations

import sys


TEST_ID = "test_nonblocking_refinement_status_changes"
TEST_TAGS = ["fast", "mw4", "viewer", "worldgen", "nonblocking"]


def _status_tokens(status_view: dict) -> set[str]:
    return set(str(dict(row).get("status", "")).strip() for row in list(dict(status_view).get("status_per_level") or []) if isinstance(row, dict))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.mw4_testlib import refinement_stress_report

    report = refinement_stress_report(repo_root)
    before = dict(report.get("viewer_before_status") or {})
    after = dict(report.get("viewer_after_second_status") or {})
    before_tokens = _status_tokens(before)
    after_tokens = _status_tokens(after)
    if "queued" not in before_tokens:
        return {"status": "fail", "message": "viewer refinement status did not expose queued coarse state before scheduling"}
    if "present" not in after_tokens:
        return {"status": "fail", "message": "viewer refinement status did not expose present refinement after scheduling"}
    if str((dict(report.get("viewer_after_second_status") or {}).get("extensions") or {}).get("nonblocking", "")).lower() not in {"true", "1"}:
        return {"status": "fail", "message": "viewer refinement status lost the nonblocking marker"}
    return {"status": "pass", "message": "MW-4 viewer refinement status remains nonblocking and transitions deterministically"}

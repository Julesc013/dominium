"""FAST test: tick_t remains the canonical 64-bit tick type in scoped paths."""

from __future__ import annotations


TEST_ID = "test_tick_type_64bit_enforced"
TEST_TAGS = ["fast", "time", "tick", "repox"]


def run(repo_root: str):
    from src.time.tick_t import TICK_BITS, TICK_MAX
    from tools.time.time_anchor_common import scan_tick_width_violations
    from tools.xstack.testx.tests.time_anchor_testlib import load_verify_report

    if int(TICK_BITS) != 64:
        return {"status": "fail", "message": "tick_t must remain 64-bit"}
    if int(TICK_MAX) <= 0:
        return {"status": "fail", "message": "tick_t max must remain positive"}
    violations = scan_tick_width_violations(repo_root)
    if violations:
        first = dict(violations[0] or {})
        return {
            "status": "fail",
            "message": "mixed-width tick violation at {}:{}".format(
                str(first.get("path", "")),
                int(first.get("line", 0) or 0),
            ),
        }
    report, error = load_verify_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    if not bool(dict(report.get("checks") or {}).get("tick_width_clean", False)):
        return {"status": "fail", "message": "verify report did not confirm tick-width cleanliness"}
    return {"status": "pass", "message": "tick_t 64-bit enforcement is clean in TIME-ANCHOR scope"}

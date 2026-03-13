"""FAST test: DIST-4 simulated mode selections match the declared product policies."""

from __future__ import annotations


TEST_ID = "test_mode_selection_matches_policy"
TEST_TAGS = ["fast", "dist", "release", "platform", "mode_selection"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist4_testlib import context_rows, load_report

    report = load_report(repo_root)
    rows = context_rows(report)
    if not rows:
        return {"status": "fail", "message": "DIST-4 context rows are missing"}
    for row in rows:
        if not bool(row.get("passed")):
            return {
                "status": "fail",
                "message": "DIST-4 mode selection mismatch for {} {}".format(
                    str(row.get("product_id", "")).strip(),
                    str(row.get("context_id", "")).strip(),
                ),
            }

    expectations = {
        ("client", "tty"): "tui",
        ("client", "headless"): "cli",
        ("server", "tty"): "tui",
        ("server", "headless"): "cli",
        ("launcher", "tty"): "tui",
        ("setup", "tty"): "tui",
    }
    by_key = {
        (str(row.get("product_id", "")).strip(), str(row.get("context_id", "")).strip()): row
        for row in rows
    }
    for key, expected_mode in expectations.items():
        row = by_key.get(key)
        if not row:
            return {"status": "fail", "message": "missing DIST-4 row for {} {}".format(*key)}
        if str(row.get("selected_mode_id", "")).strip() != expected_mode:
            return {
                "status": "fail",
                "message": "{} {} selected {} instead of {}".format(
                    key[0],
                    key[1],
                    str(row.get("selected_mode_id", "")).strip(),
                    expected_mode,
                ),
            }
    return {"status": "pass", "message": "DIST-4 simulated mode selections match policy"}

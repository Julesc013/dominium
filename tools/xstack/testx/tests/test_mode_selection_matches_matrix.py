"""FAST test: governed products resolve the expected UI modes in the boot matrix."""

from __future__ import annotations


TEST_ID = "test_mode_selection_matches_matrix"
TEST_TAGS = ["fast", "mvp", "products", "appshell", "mode_selection"]


def run(repo_root: str):
    from tools.xstack.testx.tests.prod_gate0_testlib import load_report, mode_row

    report, error = load_report(repo_root, prefer_cached=True)
    if error:
        return {"status": "fail", "message": error}

    for row in list(report.get("mode_rows") or []):
        row_map = dict(row or {})
        if not bool(row_map.get("passed")):
            return {
                "status": "fail",
                "message": "mode selection mismatch for {} {} {}".format(
                    str(row_map.get("product_id", "")).strip(),
                    str(row_map.get("invocation_kind", "")).strip(),
                    str(row_map.get("scenario_id", "")).strip(),
                ),
            }

    expectations = {
        ("client", "portable", "tty"): "tui",
        ("client", "portable", "gui"): "rendered",
        ("server", "portable", "tty"): "tui",
        ("server", "portable", "headless"): "cli",
        ("engine", "portable", "tty"): "cli",
        ("game", "portable", "tty"): "tui",
        ("launcher", "portable", "gui"): "cli",
        ("setup", "portable", "gui"): "cli",
    }
    for key, expected_mode in expectations.items():
        row = mode_row(report, *key)
        if not row:
            return {"status": "fail", "message": "missing mode row for {} {} {}".format(*key)}
        if str(row.get("observed_selected_mode_id", "")).strip() != expected_mode:
            return {
                "status": "fail",
                "message": "{} {} {} resolved to {} instead of {}".format(
                    key[0],
                    key[1],
                    key[2],
                    str(row.get("observed_selected_mode_id", "")).strip(),
                    expected_mode,
                ),
            }
    return {"status": "pass", "message": "mode selection matches the standalone product matrix"}

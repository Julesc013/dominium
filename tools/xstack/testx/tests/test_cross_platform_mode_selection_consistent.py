"""FAST test: equivalent platform contexts resolve to the same selected mode."""

from __future__ import annotations


TEST_ID = "test_cross_platform_mode_selection_consistent"
TEST_TAGS = ["fast", "appshell", "platform", "cross_platform"]


def run(repo_root: str):
    from tools.xstack.testx.tests.ui_mode_resolution_testlib import probe, selection

    results = []
    for platform_id in ("windows", "macos", "linux"):
        payload = selection(
            repo_root,
            product_id="server",
            probe_payload=probe(
                repo_root,
                product_id="server",
                platform_id=platform_id,
                tty=True,
                gui=True,
                native=False,
                rendered=False,
                tui=True,
            ),
        )
        results.append(dict(payload))
    selected_modes = {str(row.get("selected_mode_id", "")).strip() for row in results}
    compat_modes = {str(row.get("compatibility_mode_id", "")).strip() for row in results}
    degrade_lengths = {int(len(list(row.get("degrade_chain") or []))) for row in results}
    if selected_modes != {"tui"}:
        return {"status": "fail", "message": "cross-platform tty selection drifted: {}".format(sorted(selected_modes))}
    if compat_modes != {"compat.full"}:
        return {"status": "fail", "message": "cross-platform compatibility mode drifted: {}".format(sorted(compat_modes))}
    if degrade_lengths != {0}:
        return {"status": "fail", "message": "cross-platform degrade chains drifted"}
    return {"status": "pass", "message": "equivalent platform contexts resolve to the same selected mode"}

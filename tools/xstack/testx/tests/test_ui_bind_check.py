"""STRICT test: ui_bind --check validates ui registry/window descriptor bindings."""

from __future__ import annotations

import sys


TEST_ID = "testx.ui.bind.check"
TEST_TAGS = ["strict", "session", "smoke"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.ui_bind import run_ui_bind_check

    checked = run_ui_bind_check(
        repo_root=repo_root,
        ui_registry_path="build/registries/ui.registry.json",
    )
    if checked.get("result") != "complete":
        reason = str((checked.get("refusal") or {}).get("reason_code", ""))
        return {"status": "fail", "message": "ui_bind check refused ({})".format(reason)}
    if int(checked.get("checked_windows", 0) or 0) <= 0:
        return {"status": "fail", "message": "ui_bind check did not validate any windows"}
    return {"status": "pass", "message": "ui_bind check passed"}

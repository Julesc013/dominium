"""STRICT test: electrical breaker toggles must go through control intent pathways."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile


TEST_ID = "test_breaker_toggle_requires_control_intent"
TEST_TAGS = ["strict", "electric", "control", "repox"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    temp_root = tempfile.mkdtemp(prefix="xstack_repox_elec_breaker_control_intent_")
    try:
        fixture_files = {
            os.path.join(temp_root, "src", "client", "interaction", "elec_panel_ui.py"): "\n".join(
                [
                    "def on_breaker_toggle_click(device_id):",
                    "    run_process('process.elec.flip_breaker', {'device_id': device_id})",
                    "    return True",
                    "",
                ]
            ),
            os.path.join(temp_root, "tools", "xstack", "sessionx", "interaction.py"): (
                "def dispatch_breaker_toggle(device_id):\n"
                "    run_process('process.elec.flip_breaker', {'device_id': device_id})\n"
            ),
        }
        for abs_path, content in fixture_files.items():
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)

        result = run_repox_check(repo_root=temp_root, profile="STRICT")
        findings = [dict(row) for row in list(result.get("findings") or []) if isinstance(row, dict)]
        for row in findings:
            if str(row.get("rule_id", "")).strip() != "INV-CONTROL-INTENT-REQUIRED":
                continue
            file_path = str(row.get("file_path", "")).replace("\\", "/")
            if file_path.endswith("src/client/interaction/elec_panel_ui.py"):
                return {
                    "status": "pass",
                    "message": "direct electrical breaker process calls are blocked without control intent mapping",
                }
        return {
            "status": "fail",
            "message": "expected INV-CONTROL-INTENT-REQUIRED finding for direct breaker process call",
        }
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


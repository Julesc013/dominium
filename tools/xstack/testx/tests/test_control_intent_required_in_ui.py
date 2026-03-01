"""STRICT test: UI interaction modules must not call process.* directly."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile


TEST_ID = "testx.repox.control_intent_required_in_ui"
TEST_TAGS = ["strict", "repox", "control"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    temp_root = tempfile.mkdtemp(prefix="xstack_repox_ctrl_intent_required_")
    try:
        fixture_files = {
            os.path.join(temp_root, "src", "client", "interaction", "interaction_dispatch.py"): "\n".join(
                [
                    "def build_interaction_control_intent():",
                    "    build_control_intent()",
                    "    return {}",
                    "",
                    "def run_interaction_command():",
                    "    build_control_resolution()",
                    "    return {}",
                    "",
                ]
            ),
            os.path.join(temp_root, "tools", "interaction", "interaction_cli.py"): "def main():\n    run_interaction_command()\n",
            os.path.join(temp_root, "tools", "xstack", "sessionx", "interaction.py"): "def run():\n    run_interaction_command()\n",
            os.path.join(temp_root, "src", "client", "interaction", "bad_ui_direct_process.py"): (
                "result = run_process(\"process.camera_set_view_mode\")\n"
            ),
        }
        for abs_path, content in fixture_files.items():
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)

        result = run_repox_check(repo_root=temp_root, profile="STRICT")
        findings = [
            dict(row)
            for row in list(result.get("findings") or [])
            if isinstance(row, dict)
        ]
        for row in findings:
            if str(row.get("rule_id", "")).strip() != "INV-CONTROL-INTENT-REQUIRED":
                continue
            if str(row.get("file_path", "")).replace("\\", "/").endswith("src/client/interaction/bad_ui_direct_process.py"):
                return {
                    "status": "pass",
                    "message": "direct process.* UI call was blocked by INV-CONTROL-INTENT-REQUIRED",
                }
        return {
            "status": "fail",
            "message": "expected INV-CONTROL-INTENT-REQUIRED finding for direct UI process call",
        }
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

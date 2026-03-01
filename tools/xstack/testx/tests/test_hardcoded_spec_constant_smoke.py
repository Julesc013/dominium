"""FAST test: RepoX blocks hardcoded infrastructure spec constants."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile


TEST_ID = "testx.specs.hardcoded_spec_constant_smoke"
TEST_TAGS = ["fast", "repox", "specs"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    temp_root = tempfile.mkdtemp(prefix="xstack_repox_spec_hardcode_")
    try:
        fixture_files = {
            os.path.join(temp_root, "src", "specs", "spec_engine.py"): "SPEC_ENGINE_PRESENT = True\n",
            os.path.join(temp_root, "tools", "xstack", "sessionx", "process_runtime.py"): "\n".join(
                [
                    "import os",
                    "",
                    "def _spec_pack_payload_rows(policy_context):",
                    "    default_pack_abs = ''",
                    "    if os.path.isfile(default_pack_abs):",
                    "        return []",
                    "    return []",
                    "",
                    "def _spec_sheet_rows():",
                    "    load_spec_sheet_rows(",
                    "    )",
                    "    return []",
                    "",
                ]
            ),
            os.path.join(temp_root, "tools", "xstack", "sessionx", "bad_spec_constants.py"): "gauge_mm = 1435\n",
        }
        for abs_path, content in fixture_files.items():
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)

        result = run_repox_check(repo_root=temp_root, profile="STRICT")
        findings = [dict(row) for row in list(result.get("findings") or []) if isinstance(row, dict)]
        for row in findings:
            if str(row.get("rule_id", "")).strip() != "INV-NO-HARDCODED-GAUGE-WIDTH-SPECS":
                continue
            file_path = str(row.get("file_path", "")).replace("\\", "/")
            if file_path.endswith("tools/xstack/sessionx/bad_spec_constants.py"):
                return {
                    "status": "pass",
                    "message": "hardcoded spec constants are blocked by INV-NO-HARDCODED-GAUGE-WIDTH-SPECS",
                }
        return {
            "status": "fail",
            "message": "expected INV-NO-HARDCODED-GAUGE-WIDTH-SPECS finding for hardcoded gauge_mm constant",
        }
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

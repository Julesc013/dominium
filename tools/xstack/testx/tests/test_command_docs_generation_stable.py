"""FAST test: command docs generation is deterministic."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_command_docs_generation_stable"
TEST_TAGS = ["fast", "appshell", "docs"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell1_testlib import generate_cli_reference_text

    first = generate_cli_reference_text(repo_root)
    second = generate_cli_reference_text(repo_root)
    if first != second:
        return {"status": "fail", "message": "CLI reference generation drifted across repeated runs"}
    if "## Shared Commands" not in first or "## Refusal To Exit Mapping" not in first:
        return {"status": "fail", "message": "CLI reference is missing required sections"}

    with tempfile.TemporaryDirectory() as temp_dir:
        out_path = os.path.join(temp_dir, "CLI_REFERENCE.md")
        from tools.appshell.tool_generate_command_docs import main as docs_main

        result = int(docs_main(["--repo-root", repo_root, "--output-path", out_path]))
        if result != 0:
            return {"status": "fail", "message": "CLI reference generator returned non-zero"}
        with open(out_path, "r", encoding="utf-8") as handle:
            written = handle.read()
    if written != first:
        return {"status": "fail", "message": "CLI reference file output drifted from generated text"}
    return {"status": "pass", "message": "CLI reference generation remains deterministic"}

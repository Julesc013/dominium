"""STRICT test: RepoX must detect renderer imports of TruthModel headers."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile


TEST_ID = "testx.repox.renderer_truth_boundary"
TEST_TAGS = ["strict", "repox", "observation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    temp_root = tempfile.mkdtemp(prefix="xstack_repox_renderer_truth_")
    try:
        target_dir = os.path.join(temp_root, "client", "presentation")
        os.makedirs(target_dir, exist_ok=True)
        bad_file = os.path.join(target_dir, "forbidden_truth_include.c")
        with open(bad_file, "w", encoding="utf-8", newline="\n") as handle:
            handle.write('#include "domino/truth_model_v1.h"\n')
            handle.write("int x(void){return 0;}\n")

        result = run_repox_check(repo_root=temp_root, profile="STRICT")
        if str(result.get("status", "")) != "refusal":
            return {"status": "fail", "message": "STRICT RepoX must refuse renderer truth include/import"}
        findings = list(result.get("findings") or [])
        for row in findings:
            if str(row.get("rule_id", "")) == "repox.renderer_truth_import":
                return {"status": "pass", "message": "renderer truth boundary scan check passed"}
        return {"status": "fail", "message": "expected repox.renderer_truth_import finding not emitted"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

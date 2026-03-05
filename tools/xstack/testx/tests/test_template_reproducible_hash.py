"""FAST test: SYS-4 template reproducibility tool returns stable fingerprints."""

from __future__ import annotations

import sys


TEST_ID = "test_template_reproducible_hash"
TEST_TAGS = ["fast", "system", "sys4", "template"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.system.tool_verify_template_reproducible import verify_template_reproducible

    report = verify_template_reproducible(
        repo_root=repo_root,
        template_id="template.pump_basic",
        instantiation_mode="micro",
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "template reproducibility verification reported violation"}
    if not str(report.get("compiled_template_fingerprint", "")).strip():
        return {"status": "fail", "message": "template reproducibility verification missing compiled fingerprint"}
    return {"status": "pass", "message": "template reproducibility hash verification is stable"}


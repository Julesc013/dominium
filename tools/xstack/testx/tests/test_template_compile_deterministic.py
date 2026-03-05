"""FAST test: SYS-4 template compiler output is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_template_compile_deterministic"
TEST_TAGS = ["fast", "system", "sys4", "template"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys4_testlib import compile_template

    compiled_a = compile_template(
        repo_root=repo_root,
        template_id="template.engine.ice_stub",
        instantiation_mode="micro",
    )
    compiled_b = compile_template(
        repo_root=repo_root,
        template_id="template.engine.ice_stub",
        instantiation_mode="micro",
    )
    if str(compiled_a.get("compiled_template_fingerprint", "")).strip() != str(
        compiled_b.get("compiled_template_fingerprint", "")
    ).strip():
        return {"status": "fail", "message": "compiled template fingerprint differs across equivalent compile runs"}
    if [str(token).strip() for token in list(compiled_a.get("resolved_template_order") or [])] != [
        str(token).strip() for token in list(compiled_b.get("resolved_template_order") or [])
    ]:
        return {"status": "fail", "message": "resolved template order differs across equivalent compile runs"}
    return {"status": "pass", "message": "template compiler output is deterministic"}


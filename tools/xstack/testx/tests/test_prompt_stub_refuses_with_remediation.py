"""FAST test: overlay prompt_stub policy refuses with resolver remediation."""

from __future__ import annotations

import sys


TEST_ID = "test_prompt_stub_refuses_with_remediation"
TEST_TAGS = ["fast", "geo", "overlay", "compat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo9_testlib import overlay_fixture_merge_result

    merge = dict(
        overlay_fixture_merge_result(include_mods=True, overlay_conflict_policy_id="overlay.conflict.prompt_stub").get(
            "merge_result"
        )
        or {}
    )
    if str(merge.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "prompt_stub policy did not refuse conflicting overlay merge"}
    if str(merge.get("remediation_hint", "")).strip() != "remedy.overlay.add_explicit_resolver_layer":
        return {"status": "fail", "message": "prompt_stub policy did not emit explicit resolver remediation"}
    return {"status": "pass", "message": "overlay prompt_stub policy refuses with resolver remediation"}

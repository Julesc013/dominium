"""FAST test: EMB-1 scan summaries are deterministic derived artifacts."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_scan_output_deterministic"
TEST_TAGS = ["fast", "embodiment", "toolbelt", "scanner"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from embodiment import build_scan_result
    from tools.xstack.testx.tests.emb1_testlib import authority_context, field_values, inspection_snapshot, property_origin_result, selection

    auth = authority_context(entitlements=["ent.tool.scan"])
    first = build_scan_result(
        authority_context=copy.deepcopy(auth),
        selection=selection(),
        inspection_snapshot=inspection_snapshot(),
        field_values=field_values(),
        property_origin_result=property_origin_result(),
        has_physical_access=True,
    )
    second = build_scan_result(
        authority_context=copy.deepcopy(auth),
        selection=selection(),
        inspection_snapshot=inspection_snapshot(),
        field_values=field_values(),
        property_origin_result=property_origin_result(),
        has_physical_access=True,
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "scanner output drifted across equivalent runs"}
    return {"status": "pass", "message": "scanner output remains deterministic"}

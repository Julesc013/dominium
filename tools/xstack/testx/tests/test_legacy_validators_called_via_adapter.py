"""FAST test: legacy validators are mapped through unified suite adapters."""

from __future__ import annotations


TEST_ID = "test_legacy_validators_called_via_adapter"
TEST_TAGS = ["fast", "validation", "legacy"]


def run(repo_root: str):
    from tools.xstack.testx.tests.validation_unify_testlib import legacy_adapter_rows

    rows = legacy_adapter_rows(repo_root)
    if not rows:
        return {"status": "fail", "message": "no legacy validation surfaces were discovered"}
    unmapped = [row for row in rows if not str(dict(row or {}).get("mapped_suite_id", "")).strip()]
    if unmapped:
        first = dict(unmapped[0] or {})
        return {
            "status": "fail",
            "message": "legacy validation surface is not mapped through an adapter: {}".format(str(first.get("path", "")).strip()),
        }
    direct = [row for row in rows if str(dict(row or {}).get("adapter_mode", "")).strip() == "direct_python"]
    coverage = [row for row in rows if str(dict(row or {}).get("adapter_mode", "")).strip() == "coverage_adapter"]
    if not direct or not coverage:
        return {"status": "fail", "message": "legacy validation surfaces did not expose both direct and coverage adapters"}
    return {"status": "pass", "message": "legacy validation surfaces are mapped through unified adapters"}

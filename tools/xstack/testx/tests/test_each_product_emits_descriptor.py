"""FAST test: every governed product emits a descriptor in the boot matrix."""

from __future__ import annotations


TEST_ID = "test_each_product_emits_descriptor"
TEST_TAGS = ["fast", "mvp", "products", "descriptor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.prod_gate0_testlib import command_rows, load_report

    report, error = load_report(repo_root, prefer_cached=True)
    if error:
        return {"status": "fail", "message": error}
    rows = command_rows(report, "descriptor")
    if not rows:
        return {"status": "fail", "message": "descriptor rows are missing from the product boot matrix report"}
    failures = []
    for row in rows:
        row_map = dict(row or {})
        if not bool(row_map.get("passed")):
            failures.append("{} {}".format(str(row_map.get("product_id", "")).strip(), str(row_map.get("invocation_kind", "")).strip()))
            continue
        if str(row_map.get("descriptor_product_id", "")).strip() != str(row_map.get("product_id", "")).strip():
            failures.append("{} descriptor product_id mismatch".format(str(row_map.get("product_id", "")).strip()))
    if failures:
        return {"status": "fail", "message": "descriptor emission failed for: {}".format(", ".join(sorted(failures)))}
    return {"status": "pass", "message": "all governed products emit deterministic descriptors"}

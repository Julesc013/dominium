"""FAST test: every declared dist/bin product surface emits a descriptor."""

from __future__ import annotations


TEST_ID = "test_each_product_has_descriptor"
TEST_TAGS = ["fast", "compat", "descriptor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg1_testlib import emit_descriptor_via_wrapper, product_bin_map

    products = product_bin_map(repo_root)
    missing = []
    mismatched = []
    for bin_name, product_id in sorted(products.items()):
        try:
            payload = emit_descriptor_via_wrapper(repo_root, bin_name)
        except Exception:
            missing.append(bin_name)
            continue
        if str(payload.get("product_id", "")).strip() != str(product_id):
            mismatched.append("{}->{}".format(bin_name, str(payload.get("product_id", "")).strip()))
    if missing:
        return {"status": "fail", "message": "descriptor emission failed for {}".format(", ".join(missing))}
    if mismatched:
        return {"status": "fail", "message": "wrapper/product mismatch: {}".format(", ".join(mismatched))}
    return {"status": "pass", "message": "every dist/bin product surface emits a descriptor"}

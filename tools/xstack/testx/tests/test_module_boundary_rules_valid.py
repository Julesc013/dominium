from __future__ import annotations

from tools.xstack.testx.tests.xi6_testlib import committed_module_boundary_rules, recompute_fingerprint

TEST_ID = "test_module_boundary_rules_valid"
TEST_TAGS = ["fast", "xi6", "architecture"]


def run(repo_root: str):
    payload = committed_module_boundary_rules(repo_root)
    rows = list(payload.get("modules") or [])
    if payload.get("deterministic_fingerprint") != recompute_fingerprint(payload):
        return {"status": "fail", "message": "module boundary rules fingerprint mismatch"}
    if not rows:
        return {"status": "fail", "message": "module boundary rules are empty"}
    seen = set()
    for row in rows:
        item = dict(row or {})
        module_id = str(item.get("module_id", "")).strip()
        if not module_id:
            return {"status": "fail", "message": "module boundary rule missing module_id"}
        if module_id in seen:
            return {"status": "fail", "message": "duplicate module boundary rule '{}'".format(module_id)}
        seen.add(module_id)
        for key in (
            "allowed_dependency_modules",
            "forbidden_dependency_modules",
            "allowed_products",
            "forbidden_products",
            "allowed_platform_adapters",
            "stability_class",
            "deterministic_fingerprint",
        ):
            if key not in item:
                return {"status": "fail", "message": "module boundary rule '{}' missing '{}'".format(module_id, key)}
    return {"status": "pass", "message": "module boundary rules are populated and deterministic"}

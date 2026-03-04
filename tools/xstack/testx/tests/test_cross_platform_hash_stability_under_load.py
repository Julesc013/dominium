"""FAST test: numeric stability tool yields deterministic hash under load windows."""

from __future__ import annotations

import os
import sys


TEST_ID = "test_cross_platform_hash_stability_under_load"
TEST_TAGS = ["fast", "meta", "numeric", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.meta.tool_verify_numeric_stability import verify_numeric_stability

    registry_path = os.path.join(repo_root, "data", "registries", "quantity_tolerance_registry.json")
    try:
        import json

        payload = json.load(open(registry_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "unable to load quantity_tolerance_registry.json"}

    first = verify_numeric_stability(registry_payload=payload, window_ticks=2048, drift_scale=64)
    second = verify_numeric_stability(registry_payload=payload, window_ticks=2048, drift_scale=64)
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "numeric stability verification reported violation"}
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "numeric stability verification reported violation on replay"}
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "numeric stability fingerprint drift across repeated runs"}
    return {"status": "pass", "message": "numeric stability fingerprint is deterministic under load"}

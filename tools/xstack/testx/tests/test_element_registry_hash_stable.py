"""FAST test: LOGIC-2 element registry hash is stable under deterministic normalization."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_element_registry_hash_stable"
TEST_TAGS = ["fast", "logic", "registry", "determinism"]


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic import normalize_logic_element_definition_rows
    from tools.xstack.compatx.canonical_json import canonical_sha256

    payload = _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_element_registry.json")
    rows = list(payload.get("logic_elements") or [])
    if not rows:
        return {"status": "fail", "message": "logic element registry missing rows"}

    normalized_a = normalize_logic_element_definition_rows(rows)
    normalized_b = normalize_logic_element_definition_rows(list(reversed(rows)))
    if not normalized_a or normalized_a != normalized_b:
        return {"status": "fail", "message": "logic element normalization is order-sensitive"}

    hash_a = canonical_sha256(normalized_a)
    hash_b = canonical_sha256(normalized_b)
    if hash_a != hash_b:
        return {"status": "fail", "message": "logic element registry hash is order-sensitive"}
    if hash_a != canonical_sha256(normalize_logic_element_definition_rows(rows)):
        return {"status": "fail", "message": "logic element registry hash is not repeatable"}

    return {"status": "pass", "message": "LOGIC-2 element registry hash is stable"}
